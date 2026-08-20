#!/usr/bin/env python3
"""aidd-updates.py — detecte les plugins AIDD en retard, et garde le plan d'adaptation.

Usage
  aidd-updates.py --notify              chemin chaud : lit l'etat, rend le JSON du hook. JAMAIS de reseau.
  aidd-updates.py --refresh             chemin reseau : ls-remote, recalcule les cles, reecrit l'etat.
  aidd-updates.py --etat                rend le front-matter en JSON sur stdout (contrat du skill).
  aidd-updates.py --marquer-planifie    lit le corps du plan sur stdin, l'ecrit, statut=planifie.
  aidd-updates.py --marquer-applique    statut=applique, le hook se taira jusqu'a la prochaine version.

POURQUOI CE SCRIPT
  Claude Code ne sait pas repondre « des maj sont dispo » sans les appliquer. Son auto-update par
  marketplace applique dans les dix minutes apres le demarrage, donc la casse arrive decorrelee de sa
  cause. Or la casse est chez nous : 16 noms de skills AIDD sont cites dans ce repo, et la montee
  1.x -> 2.x en avait deja renomme trois (cf. CHANGELOG-aidd.md).

POURQUOI DEUX MODES, ET PAS DE RESEAU SUR --notify
  Le decoupage vient de la CLI AIDD elle-meme (cli/src/application/use-cases/check-update-use-case.ts,
  « Hot path: print the update notice from cached value only — fresh OR stale, never network »).
  Un SessionStart qui attend le reseau retarde CHAQUE ouverture de session, pour un service qui n'est
  que du confort. --notify lit donc le cache et detache --refresh quand le cache a plus de 24 h.

ECART ASSUME A « ECHOUE FERME » (cf. README, section des gardes)
  Ce script sort TOUJOURS en 0. Un garde refuse une action, lui ne fait qu'informer : echouer
  bruyamment polluerait chaque session, et une machine hors reseau n'a rien fait de mal.
  A LA PLACE du code de sortie, toute panne s'ecrit dans `derniere_erreur`, que /aidd-updates affiche
  en tete. Rien n'est silencieux pour de bon, rien ne bloque.

UN SEUL ECRIVAIN DU FRONT-MATTER
  Le skill ne parse ni n'ecrit le YAML : il lit --etat (du JSON) et ecrit par --marquer-*.
  Pourquoi : un LLM qui edite du YAML a la main le cassera un jour, et le symptome serait « il
  replanifie a chaque appel », sans lien visible avec la cause.

SURCHARGES D'ENVIRONNEMENT (calibrage, sur le modele de CLAUDE_RULES_DIR dans sync-rules.sh)
  AIDD_UPDATES_STATE_DIR      dossier d'etat, au lieu de $XDG_STATE_HOME/aidd-updates
  AIDD_UPDATES_PLUGINS_JSON   installed_plugins.json jetable, au lieu de celui de Claude Code
  AIDD_UPDATES_TAGS_FILE      remplace la sortie de `git ls-remote`, donc la batterie tourne hors reseau
  AIDD_UPDATES_NO_DETACH      coupe le refresh detache de --notify, pour que la batterie soit sequentielle
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

REPO_GIT = "https://github.com/ai-driven-dev/framework.git"
# HTTPS anonyme, pas SSH : mesure du 2026-08-19, 144 tags en 0,47 s sans aucune cle configuree.
# Une cle SSH absente ferait echouer le refresh sur une machine neuve, sans que rien ne le dise.

TTL_HEURES = 24
MARQUEUR = "---"
CHAMPS = (
    "cle_upstream",
    "cle_installe",
    "cassant",
    "verifie_le",
    "planifie_le",
    "dernier_affichage",
    "statut",
    "derniere_erreur",
)
TAG = re.compile(r"refs/tags/(aidd-[a-z]+)-v(\d+)\.(\d+)\.(\d+)$")


# --------------------------------------------------------------------------- chemins


def dossier_etat() -> Path:
    surcharge = os.environ.get("AIDD_UPDATES_STATE_DIR")
    if surcharge:
        return Path(surcharge)
    base = os.environ.get("XDG_STATE_HOME") or (Path.home() / ".local" / "state")
    return Path(base) / "aidd-updates"


def fichier_plan() -> Path:
    return dossier_etat() / "plan.md"


def fichier_plugins() -> Path:
    surcharge = os.environ.get("AIDD_UPDATES_PLUGINS_JSON")
    if surcharge:
        return Path(surcharge)
    return Path.home() / ".claude" / "plugins" / "installed_plugins.json"


# ------------------------------------------------------- front-matter, lecture / ecriture
# Sous-ensemble YAML ecrit par ce script seul, donc parse sans dependance. Deux formes :
#   cle: valeur          (vide = None)
#   cle: {a: 1, b: 2}    (map plate)  |  cle: [x, y]  (liste plate)


def _lire_scalaire(brut: str):
    brut = brut.strip()
    if brut in ("", "null", "~"):
        return None
    if brut.startswith("{") and brut.endswith("}"):
        corps = brut[1:-1].strip()
        if not corps:
            return {}
        paires = {}
        for morceau in corps.split(","):
            if ":" not in morceau:
                continue
            cle, valeur = morceau.split(":", 1)
            paires[cle.strip()] = valeur.strip()
        return paires
    if brut.startswith("[") and brut.endswith("]"):
        corps = brut[1:-1].strip()
        return [m.strip() for m in corps.split(",") if m.strip()] if corps else []
    return brut


def _ecrire_scalaire(valeur) -> str:
    if valeur is None:
        return "null"
    if isinstance(valeur, dict):
        return "{" + ", ".join(f"{c}: {v}" for c, v in sorted(valeur.items())) + "}"
    if isinstance(valeur, list):
        return "[" + ", ".join(valeur) + "]"
    return str(valeur)


def etat_vide() -> dict:
    return {c: None for c in CHAMPS} | {"statut": "inconnu"}


def lire() -> tuple[dict, str]:
    """Rend (front-matter, corps). Un fichier absent ou casse rend un etat vide, jamais une trace."""
    chemin = fichier_plan()
    if not chemin.is_file():
        return etat_vide(), ""
    try:
        texte = chemin.read_text(encoding="utf-8")
    except OSError:
        return etat_vide(), ""
    lignes = texte.splitlines()
    if not lignes or lignes[0].strip() != MARQUEUR:
        return etat_vide(), texte
    try:
        fin = lignes.index(MARQUEUR, 1)
    except ValueError:
        # Front-matter non ferme : fichier tronque. On ne devine pas, on repart d'un etat vide.
        return etat_vide(), ""
    etat = etat_vide()
    for ligne in lignes[1:fin]:
        if ":" not in ligne or ligne.lstrip().startswith("#"):
            continue
        cle, valeur = ligne.split(":", 1)
        cle = cle.strip()
        if cle in CHAMPS:
            etat[cle] = _lire_scalaire(valeur)
    return etat, "\n".join(lignes[fin + 1 :]).lstrip("\n")


def ecrire(etat: dict, corps: str) -> None:
    chemin = fichier_plan()
    chemin.parent.mkdir(parents=True, exist_ok=True)
    lignes = [MARQUEUR]
    lignes += [f"{c}: {_ecrire_scalaire(etat.get(c))}" for c in CHAMPS]
    lignes += [MARQUEUR, ""]
    chemin.write_text("\n".join(lignes) + ("\n" + corps.strip() + "\n" if corps.strip() else ""), encoding="utf-8")


# --------------------------------------------------------------------------- versions


def _tuple_version(v: str) -> tuple[int, int, int]:
    try:
        a, b, c = (int(x) for x in v.split("."))
        return a, b, c
    except (ValueError, AttributeError):
        return 0, 0, 0


def versions_installees() -> dict[str, str]:
    chemin = fichier_plugins()
    try:
        brut = json.loads(chemin.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as err:
        raise Panne(f"installed_plugins.json illisible ({chemin}) : {err}") from err
    trouvees = {}
    for identifiant, entrees in (brut.get("plugins") or {}).items():
        nom = identifiant.split("@")[0]
        if not nom.startswith("aidd-") or not entrees:
            continue
        trouvees[nom] = entrees[0].get("version", "0.0.0")
    return trouvees


def versions_upstream() -> dict[str, str]:
    surcharge = os.environ.get("AIDD_UPDATES_TAGS_FILE")
    if surcharge:
        try:
            sortie = Path(surcharge).read_text(encoding="utf-8")
        except OSError as err:
            raise Panne(f"AIDD_UPDATES_TAGS_FILE illisible : {err}") from err
    else:
        try:
            lance = subprocess.run(
                ["git", "ls-remote", "--tags", REPO_GIT],
                capture_output=True,
                text=True,
                timeout=30,
                env={**os.environ, "GIT_TERMINAL_PROMPT": "0", "GIT_ASKPASS": "true"},
            )
        except (OSError, subprocess.TimeoutExpired) as err:
            raise Panne(f"ls-remote injoignable : {err}") from err
        if lance.returncode != 0:
            raise Panne(f"ls-remote a echoue : {(lance.stderr or '').strip()[:200]}")
        sortie = lance.stdout
    dernieres: dict[str, str] = {}
    for ligne in sortie.splitlines():
        trouve = TAG.search(ligne.strip())
        if not trouve:
            continue
        nom = trouve.group(1)
        version = ".".join(trouve.group(2, 3, 4))
        if nom not in dernieres or _tuple_version(version) > _tuple_version(dernieres[nom]):
            dernieres[nom] = version
    if not dernieres:
        raise Panne("aucun tag `aidd-<plugin>-vX.Y.Z` reconnu dans la sortie")
    return dernieres


def en_retard(installe: dict[str, str], upstream: dict[str, str]) -> dict[str, tuple[str, str]]:
    """Ne compare que les plugins REELLEMENT installes. Un plugin upstream non installe n'est pas un retard."""
    retards = {}
    for nom, version in installe.items():
        cible = upstream.get(nom)
        if cible and _tuple_version(cible) > _tuple_version(version):
            retards[nom] = (version, cible)
    return retards


def cassants(retards: dict[str, tuple[str, str]]) -> list[str]:
    """Un majeur qui change est cassant. Deterministe, et suffisant pour alerter.
    Le detail de ce qui casse est de la prose de changelog, donc le travail du skill, pas du script."""
    return sorted(n for n, (de, vers) in retards.items() if _tuple_version(vers)[0] > _tuple_version(de)[0])


class Panne(Exception):
    """Panne attendue : elle part dans `derniere_erreur`, jamais dans le code de sortie."""


# --------------------------------------------------------------------------- modes


def maintenant() -> str:
    return datetime.now().replace(microsecond=0).isoformat()


def _perime(horodatage: str | None, heures: int) -> bool:
    if not horodatage:
        return True
    try:
        return datetime.fromisoformat(horodatage) < datetime.now() - timedelta(hours=heures)
    except ValueError:
        return True


def mode_refresh() -> int:
    etat, corps = lire()
    try:
        installe = versions_installees()
        upstream = versions_upstream()
    except Panne as err:
        etat["derniere_erreur"] = str(err).replace("\n", " ")[:300]
        etat["verifie_le"] = maintenant()
        ecrire(etat, corps)  # le plan existant survit a une panne de rafraichissement
        return 0
    retards = en_retard(installe, upstream)
    neuf = {"cle_upstream": {n: v for n, v in sorted(upstream.items()) if n in installe},
            "cle_installe": dict(sorted(installe.items()))}
    a_bouge = any(etat.get(c) != neuf[c] for c in neuf)
    etat.update(neuf)
    etat["cassant"] = cassants(retards)
    etat["verifie_le"] = maintenant()
    etat["derniere_erreur"] = None
    if a_bouge:
        # Une cle qui bouge invalide le plan, et lui seul. Sans cette condition, chaque refresh
        # effacerait un plan encore valable, et le skill replanifierait pour rien.
        etat["planifie_le"] = None
        etat["dernier_affichage"] = None
        etat["statut"] = "detecte" if retards else "a-jour"
        corps = ""
    elif not retards:
        etat["statut"] = "a-jour"
    ecrire(etat, corps)
    return 0


def mode_notify() -> int:
    etat, corps = lire()
    if _perime(etat.get("verifie_le"), TTL_HEURES):
        _detacher_refresh()
    retards = en_retard(etat.get("cle_installe") or {}, etat.get("cle_upstream") or {})
    if not retards or etat.get("statut") == "applique":
        return 0
    if not _perime(etat.get("dernier_affichage"), TTL_HEURES):
        return 0  # une fois par jour au maximum : c'est un rappel, pas une alarme
    total = len(retards)
    casse = etat.get("cassant") or []
    detail = ", ".join(f"{n} {de} vers {vers}" for n, (de, vers) in sorted(retards.items()))
    alerte = f", dont {' et '.join(casse)} CASSANT" if casse else ""
    humain = f"AIDD : {total} plugin(s) en retard{alerte}. Tape /aidd-updates pour voir le changelog."
    if etat.get("statut") == "planifie":
        humain = f"AIDD : un plan d'adaptation est en attente ({total} plugin(s)). Tape /aidd-updates."
    modele = (
        f"Plugins AIDD en retard : {detail}."
        + (f" Majeur cassant : {', '.join(casse)}." if casse else "")
        + (" Un plan d'adaptation existe deja, ne pas replanifier sans lire l'etat."
           if etat.get("statut") == "planifie" else "")
        + " Ne pas editer les skills qui citent un skill AIDD sans passer par /aidd-updates."
    )
    etat["dernier_affichage"] = maintenant()
    ecrire(etat, corps)
    json.dump(
        {"systemMessage": humain,
         "hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": modele}},
        sys.stdout,
        ensure_ascii=False,
    )
    print()
    return 0


def _detacher_refresh() -> None:
    """Detache le rafraichissement pour ne rien ajouter au temps de demarrage de la session."""
    if os.environ.get("AIDD_UPDATES_NO_DETACH"):
        return  # la batterie coupe le detachement : un refresh concurrent reecrirait l'etat sous ses pieds
    try:
        subprocess.Popen(
            [sys.executable, os.path.abspath(__file__), "--refresh"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            start_new_session=True,
        )
    except OSError:
        pass  # pas de refresh cette fois. Le cache reste affichable, la session ne voit rien.


def mode_etat() -> int:
    etat, corps = lire()
    retards = en_retard(etat.get("cle_installe") or {}, etat.get("cle_upstream") or {})
    json.dump(
        {**etat,
         "retards": {n: {"de": de, "vers": vers} for n, (de, vers) in sorted(retards.items())},
         "plan_a_refaire": etat.get("planifie_le") is None and bool(retards),
         "corps_present": bool(corps.strip()),
         "fichier": str(fichier_plan())},
        sys.stdout,
        ensure_ascii=False,
        indent=2,
    )
    print()
    return 0


def mode_marquer(statut: str) -> int:
    etat, corps = lire()
    if statut == "planifie":
        entree = sys.stdin.read()
        if entree.strip():
            corps = entree
        etat["planifie_le"] = maintenant()
    etat["statut"] = statut
    ecrire(etat, corps)
    print(f"statut={statut} ecrit dans {fichier_plan()}")
    return 0


def main(argv: list[str]) -> int:
    modes = {
        "--notify": mode_notify,
        "--refresh": mode_refresh,
        "--etat": mode_etat,
        "--marquer-planifie": lambda: mode_marquer("planifie"),
        "--marquer-applique": lambda: mode_marquer("applique"),
    }
    choix = argv[1] if len(argv) > 1 else ""
    if choix not in modes:
        print(__doc__.split("POURQUOI CE SCRIPT")[0].strip(), file=sys.stderr)
        return 2  # une invocation fautive est un bug d'appelant, pas une panne de service
    return modes[choix]()


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv))
    except Exception as err:  # noqa: BLE001 — filet : aucune trace ne doit atteindre une session
        try:
            etat, corps = lire()
            etat["derniere_erreur"] = f"panne inattendue : {type(err).__name__} {err}"[:300]
            ecrire(etat, corps)
        except Exception:  # noqa: BLE001
            pass
        sys.exit(0)
