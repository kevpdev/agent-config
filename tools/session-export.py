#!/usr/bin/env python3
"""session-export.py — une session OpenCode exportée, valeurs de secrets masquées.

POURQUOI cet outil existe : un agent qui a besoin de l'historique d'une session le lit
par `opencode session export`. Le transcript recopie tout ce que le modèle a vu, sorties
d'outils comprises, donc le relire renvoie au fournisseur chaque secret déjà sorti.
Mesuré le 2026-10-26 sur une session témoin : l'export brut garde une valeur `API_KEY=`,
un jeton `ghp_` et le texte libre. `--sanitize` masque tout le texte, titre et dossier
compris (`[redacted:text:msg_…]`), et ne garde que les métadonnées. Ici, le contexte
reste et les valeurs partent. Le nom de la variable reste visible : `API_KEY=***`.

CE QUI EST MASQUÉ, dans chaque chaîne du JSON :
  1. les valeurs des `.env` et `.env.*` (sauf `.env.example`) du dossier de la session,
     jusqu'à la profondeur 2, et des fichiers donnés par `--env`. Le script les lit
     lui-même, aucune ne sort. Une valeur de moins de 6 caractères est ignorée, pour ne
     pas masquer `0`, `true` ou `dev` partout ;
  2. les motifs de jetons connus (`ghp_`, `github_pat_`, `sk-`, `AKIA`, `xox?-`,
     `glpat-`, blocs `PRIVATE KEY`) ;
  3. la valeur d'une affectation dont la clé contient KEY, TOKEN, SECRET, PASSWORD,
     PASSWD ou CREDENTIAL, sans casse : `NOM=valeur`, `nom: valeur`, `"nom": "valeur"`.

CE QUE LE MASQUAGE NE VOIT PAS : un secret au format inconnu, cité sans nom de clé
parlant, ou venu d'un `.env` hors du dossier de la session. La règle 3 masque aussi
trop large, par exemple `token = get_token()` : elle perd du contexte, pas de secret.

Usage :
    python3 tools/session-export.py SESSION                  JSON masqué sur stdout
    python3 tools/session-export.py SESSION --texte          transcript lisible
    python3 tools/session-export.py SESSION --env FICHIER    une source de valeurs en plus
    python3 tools/session-export.py --depuis EXPORT.json     un export déjà posé

Le bilan, un compte par règle et jamais une valeur, sort sur stderr. Sortie 2, stdout
vide, si l'export échoue ou si son JSON est illisible.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import os
import re
import subprocess
import sys
from collections import Counter

MASQUE = "***"
LONGUEUR_MIN = 6
PROFONDEUR = 2
SAUTES = {".git", "node_modules", ".venv", "__pycache__"}
LIGNES_SORTIE = 20

JETONS = re.compile(
    r"-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----"
    r"|\b(?:ghp|gho|ghs|ghu|ghr)_[A-Za-z0-9]{20,}"
    r"|\bgithub_pat_[A-Za-z0-9_]{20,}"
    r"|\bsk-[A-Za-z0-9_-]{16,}"
    r"|\bAKIA[A-Z0-9]{16}\b"
    r"|\bxox[abposr]-[A-Za-z0-9-]{10,}"
    r"|\bglpat-[A-Za-z0-9_-]{20,}",
    re.DOTALL,
)
# Le nom, son guillemet fermant et le séparateur restent : seul le groupe `valeur` part.
AFFECTATION = re.compile(
    r"(?i)(?P<tete>\b[\w.-]*(?:key|token|secret|passw(?:or)?d|credential)[\w.-]*[\"']?\s*[=:]\s*[\"']?)"
    r"(?P<valeur>[^\s\"'`,;}]+)"
)
LIGNE_ENV = re.compile(r"^\s*(?:export\s+)?[A-Za-z_][A-Za-z0-9_]*\s*=\s*(.*?)\s*$")


def est_env(nom: str) -> bool:
    return (nom == ".env" or fnmatch.fnmatch(nom, ".env.*")) and nom != ".env.example"


def fichiers_env(dossier: str) -> list[str]:
    """Les .env du dossier, jusqu'à PROFONDEUR, sans .git ni node_modules."""
    trouves = []
    if not dossier or not os.path.isdir(dossier):
        return trouves
    base = dossier.rstrip("/").count("/")
    for racine, dossiers, fichiers in os.walk(dossier):
        dossiers[:] = [d for d in dossiers if d not in SAUTES]
        if racine.count("/") - base >= PROFONDEUR:
            dossiers[:] = []
        trouves += [os.path.join(racine, f) for f in fichiers if est_env(f)]
    return trouves


def valeurs_env(chemins: list[str]) -> set[str]:
    valeurs = set()
    for chemin in chemins:
        try:
            with open(chemin, encoding="utf-8", errors="replace") as f:
                lignes = f.read().splitlines()
        except OSError:
            continue
        for ligne in lignes:
            m = LIGNE_ENV.match(ligne)
            if m:
                v = m.group(1).strip().strip("\"'")
                if len(v) >= LONGUEUR_MIN:
                    valeurs.add(v)
    return valeurs


def masquer(texte: str, valeurs: list[str], bilan: Counter) -> str:
    for v in valeurs:
        n = texte.count(v)
        if n:
            texte = texte.replace(v, MASQUE)
            bilan["valeur .env"] += n

    def jeton(m):
        bilan["motif de jeton"] += 1
        return MASQUE
    texte = JETONS.sub(jeton, texte)

    def affectation(m):
        if m.group("valeur") == MASQUE:
            return m.group(0)
        bilan["affectation"] += 1
        return m.group("tete") + MASQUE
    return AFFECTATION.sub(affectation, texte)


def parcourir(o, valeurs: list[str], bilan: Counter):
    if isinstance(o, str):
        return masquer(o, valeurs, bilan)
    if isinstance(o, list):
        return [parcourir(x, valeurs, bilan) for x in o]
    if isinstance(o, dict):
        return {k: parcourir(v, valeurs, bilan) for k, v in o.items()}
    return o


def texte_lisible(export: dict) -> str:
    info = export.get("info") or {}
    modele = (info.get("model") or {}).get("id", "?")
    lignes = [f"# {info.get('id', '?')} — {info.get('title', '')} ({modele}, {info.get('cost', '?')} $)"]
    for m in export.get("messages") or []:
        genre = m.get("type")
        if genre == "user":
            lignes += ["", "## user", m.get("text", "")]
        elif genre == "assistant":
            lignes += ["", "## assistant"]
            for part in m.get("content") or []:
                if part.get("type") == "text":
                    lignes.append(part.get("text", ""))
                elif part.get("type") == "tool":
                    etat = part.get("state") or {}
                    entree = etat.get("input") or {}
                    cible = entree.get("command") or entree.get("path") or json.dumps(entree, ensure_ascii=False)
                    lignes.append(f"→ {part.get('name', '?')} {cible} [{etat.get('status', '?')}]")
                    sortie = "\n".join(c.get("text", "") for c in etat.get("content") or [] if isinstance(c, dict))
                    if not sortie and isinstance(etat.get("error"), dict):
                        sortie = etat["error"].get("message", "")
                    for s in sortie.splitlines()[:LIGNES_SORTIE]:
                        lignes.append(f"    {s}")
    return "\n".join(lignes) + "\n"


def lire_export(args) -> dict | None:
    if args.depuis:
        try:
            with open(args.depuis, encoding="utf-8") as f:
                return json.load(f)
        except (OSError, ValueError) as exc:
            print(f"session-export : {args.depuis} illisible ({exc}).", file=sys.stderr)
            return None
    try:
        r = subprocess.run(["opencode", "session", "export", "--standalone", args.session],
                           capture_output=True, text=True, timeout=120)
    except (OSError, subprocess.TimeoutExpired) as exc:
        print(f"session-export : opencode injoignable ({exc}).", file=sys.stderr)
        return None
    if r.returncode != 0:
        print(f"session-export : l'export a échoué (code {r.returncode}).", file=sys.stderr)
        return None
    try:
        return json.loads(r.stdout)
    except ValueError:
        print("session-export : l'export n'est pas du JSON.", file=sys.stderr)
        return None


def main() -> int:
    p = argparse.ArgumentParser(description="Exporte une session OpenCode, valeurs de secrets masquées.")
    p.add_argument("session", nargs="?")
    p.add_argument("--depuis", help="un export déjà posé, au lieu de lancer opencode")
    p.add_argument("--env", action="append", default=[], help="un fichier de valeurs à masquer en plus")
    p.add_argument("--texte", action="store_true", help="un transcript lisible au lieu du JSON")
    args = p.parse_args()
    if not args.session and not args.depuis:
        p.error("il faut un id de session ou --depuis")

    export = lire_export(args)
    if not isinstance(export, dict):
        return 2
    dossier = ((export.get("info") or {}).get("location") or {}).get("directory", "")
    # Les plus longues d'abord : une valeur qui en contient une autre part entière.
    valeurs = sorted(valeurs_env(fichiers_env(dossier) + args.env), key=len, reverse=True)
    bilan = Counter()
    masque = parcourir(export, valeurs, bilan)

    sys.stdout.write(texte_lisible(masque) if args.texte else json.dumps(masque, ensure_ascii=False, indent=2) + "\n")
    detail = ", ".join(f"{k} {v}" for k, v in sorted(bilan.items())) or "aucun"
    print(f"session-export : {sum(bilan.values())} remplacement(s) ({detail}), "
          f"{len(valeurs)} valeur(s) de .env connue(s).", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
