#!/usr/bin/env python3
"""Vérifie, ou installe, le harnais dans la config d'un agent.

POURQUOI CE SCRIPT
    L'installation tenait en deux scripts (`sync-rules.sh`, `sync-settings.py`) et
    47 liens posés à la main, que rien ne vérifiait. Les commandes de hooks de
    `wrappers/claude/settings.json` écrivent `~/.claude/scripts/…` en dur : un banc
    relocalisé par `CLAUDE_CONFIG_DIR` exécuterait donc les gardes du checkout
    principal (audits/2026-10-22-cadrage-harnais-agnostique.md, Q0).

    Ce script lit le manifeste de l'agent (`tools/manifests/<agent>.json`), pose un
    lien par entrée, et fusionne le fichier de config déclaré par sa clé `settings`.
    La cible porte le nom de la source : `settings.json` pour Claude, `opencode.json`
    pour OpenCode. Avant la fusion, deux réécritures : le préfixe `~/.claude/` des
    commandes vers la cible, et `{repo}` vers la racine des sources de liens. OpenCode
    s'en sert pour lire `rules/*.md` dans le repo par `instructions`.

    La clé `deny` du manifeste désigne `policy/deny.yaml`, traduit dans la forme de
    l'agent et ajouté au gabarit avant la fusion : `permissions.deny` pour Claude,
    `policies` pour OpenCode. Une action `read` devient `Read`/`read`, une action `write`
    devient `Edit`/`edit`.

    La clé `mcp` désigne `mcp/servers.yaml`. Pour OpenCode, chaque serveur devient une
    entrée de `mcp.servers`, ajoutée au gabarit comme `deny`. Pour Claude, install.py
    n'écrit rien : `--check` lit `.claude.json`, et `--fix` lance l'installateur déclaré
    du serveur avec `CLAUDE_CONFIG_DIR` sur la cible. Les raisons sont dans le fichier.

ÉCARTS, avec les mots de `sync-rules.sh`
    ABSENT          le lien attendu n'existe pas
    MAUVAISE CIBLE  le lien existe et vise ailleurs
    PAS UN LIEN     un vrai fichier ou dossier occupe la place du lien
    ORPHELIN        un lien vers le repo dont la source n'est plus attendue
    INTRUS          tout le reste, dans un dossier marqué `intrus` (rules/)

    `--fix` crée, redirige et retire les orphelins. Il ne supprime jamais un
    PAS UN LIEN ni un INTRUS : effacer ce que l'humain a déposé est destructif.

ÉCHOUE FERMÉ : tout écart rend un code de sortie non nul.

Usage
    python3 tools/install.py --agent claude --target ~/.claude            vérifie
    python3 tools/install.py --agent claude --target ~/.claude --fix      installe
    python3 tools/install.py --agent claude --target DIR --list           liens attendus

--repo remplace la racine des sources de liens, et `{repo}` avec elle. Le manifeste et
le gabarit de config se lisent toujours dans le repo du script. Sert à vérifier depuis un
worktree une config qui vise le checkout principal.
"""

from __future__ import annotations

import argparse
import glob
import importlib.util
import json
import os
import subprocess
import sys

import yaml

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFESTES = os.path.join(REPO, "tools", "manifests")
SYNC_SETTINGS = os.path.join(REPO, "wrappers", "claude", "scripts", "sync-settings.py")
PREFIXE = "~/.claude/"


def charger_manifeste(agent: str) -> dict:
    chemin = os.path.join(MANIFESTES, f"{agent}.json")
    if not os.path.exists(chemin):
        connus = sorted(f[:-5] for f in os.listdir(MANIFESTES) if f.endswith(".json"))
        raise SystemExit(f"install — agent inconnu : {agent}. Connus : {', '.join(connus)}.")
    with open(chemin, encoding="utf-8") as f:
        return json.load(f)


def liens_attendus(manifeste: dict, repo_liens: str) -> dict[str, str]:
    """Rend {chemin relatif dans la cible : source absolue}. Les globs se résolvent
    dans le repo du script, les sources se rendent sous `repo_liens`."""
    attendus: dict[str, str] = {}
    for e in manifeste["entrees"]:
        if e["mode"] == "link":
            relatifs = [e["source"]]
        else:
            trouves = sorted(glob.glob(os.path.join(REPO, e["source"])))
            garde = os.path.isdir if e["mode"] == "glob-dirs" else os.path.isfile
            relatifs = [os.path.relpath(t, REPO) for t in trouves if garde(t)]
        for rel in relatifs:
            cible = e["cible"] if e["mode"] == "link" else os.path.join(e["cible"], os.path.basename(rel))
            if cible in attendus:
                raise SystemExit(f"install — COLLISION : {cible} attendu deux fois dans le manifeste.")
            attendus[cible] = os.path.join(repo_liens, rel)
    return attendus


def dossiers_geres(manifeste: dict) -> dict[str, bool]:
    """Dossiers de la cible remplis par glob, avec leur drapeau `intrus`."""
    geres: dict[str, bool] = {}
    for e in manifeste["entrees"]:
        if e["mode"] != "link":
            geres[e["cible"]] = geres.get(e["cible"], False) or e.get("intrus", False)
    return geres


def verifier_liens(cible: str, manifeste: dict, attendus: dict[str, str], repo_liens: str, fix: bool):
    ecarts: list[str] = []
    faits: list[str] = []

    for rel, source in attendus.items():
        lien = os.path.join(cible, rel)
        actuel = os.readlink(lien) if os.path.islink(lien) else None
        if actuel == source:
            continue
        if actuel is None and os.path.lexists(lien):
            ecarts.append(f"PAS UN LIEN  {rel}")
            continue
        etat = "ABSENT" if actuel is None else f"MAUVAISE CIBLE ({actuel})"
        if fix:
            os.makedirs(os.path.dirname(lien), exist_ok=True)
            if actuel is not None:
                os.unlink(lien)
            os.symlink(source, lien)
            faits.append(f"réparé     {rel}")
        else:
            ecarts.append(f"{etat}  {rel} → {source}")

    exclus = set(manifeste.get("exclure", []))
    for dossier, intrus in dossiers_geres(manifeste).items():
        chemin = os.path.join(cible, dossier)
        if not os.path.isdir(chemin):
            continue
        for nom in sorted(os.listdir(chemin)):
            rel = os.path.join(dossier, nom)
            if rel in attendus or rel in exclus:
                continue
            entree = os.path.join(chemin, nom)
            vise = os.readlink(entree) if os.path.islink(entree) else None
            if vise is not None and (vise.startswith(repo_liens + os.sep) or vise.startswith(REPO + os.sep)):
                if fix:
                    os.unlink(entree)
                    faits.append(f"retiré     {rel} (plus de source)")
                else:
                    ecarts.append(f"ORPHELIN  {rel} pointe vers {vise}, qui n'est plus une source")
            elif intrus:
                quoi = "est un dossier" if os.path.isdir(entree) and vise is None else "n'est pas un lien vers une source de ce repo"
                ecarts.append(f"INTRUS  {rel} {quoi}")
    return ecarts, faits


def rendre_cible(cible: str) -> str:
    """`~/…` sous le home, absolu sinon : la forme que le shell du hook développe."""
    home = os.path.expanduser("~")
    if cible == home or cible.startswith(home + os.sep):
        return "~" + cible[len(home):]
    return cible


def reecrire_chemins(valeur, prefixe: str):
    """Réécrit le préfixe `~/.claude/` des clés `command`, à toute profondeur."""
    if isinstance(valeur, dict):
        return {k: (v.replace(PREFIXE, prefixe) if k == "command" and isinstance(v, str)
                    else reecrire_chemins(v, prefixe)) for k, v in valeur.items()}
    if isinstance(valeur, list):
        return [reecrire_chemins(v, prefixe) for v in valeur]
    return valeur


def reecrire_repo(valeur, repo: str):
    """Remplace `{repo}` par la racine des sources de liens, dans toutes les chaînes."""
    if isinstance(valeur, dict):
        return {k: reecrire_repo(v, repo) for k, v in valeur.items()}
    if isinstance(valeur, list):
        return [reecrire_repo(v, repo) for v in valeur]
    return valeur.replace("{repo}", repo) if isinstance(valeur, str) else valeur


def charger_sync_settings():
    spec = importlib.util.spec_from_file_location("sync_settings", SYNC_SETTINGS)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def charger_deny(chemin: str) -> list[dict]:
    """Lit `policy/deny.yaml` et refuse une entrée incomplète ou une action inconnue."""
    with open(chemin, encoding="utf-8") as f:
        entrees = yaml.safe_load(f) or []
    for e in entrees:
        manque = [c for c in ("id", "action", "fin", "raison") if not e.get(c)]
        if manque:
            raise SystemExit(f"install — {chemin} : entrée {e.get('id', '?')} sans {', '.join(manque)}.")
        if e["action"] not in OUTILS_CLAUDE:
            raise SystemExit(f"install — {chemin} : entrée {e['id']}, action {e['action']!r} inconnue (read ou write).")
    return entrees


# L'outil que chaque action interdit. `Edit` couvre tous les outils d'édition de Claude
# selon sa doc, et `edit` couvre l'écriture sous OpenCode.
OUTILS_CLAUDE = {"read": "Read", "write": "Edit"}
OUTILS_OPENCODE = {"read": "read", "write": "edit"}


def chemin_claude(fin: str) -> str:
    """Forme Claude d'une fin : `~/` reste ancré au home, `/` devient `//`, un suffixe `//**/`."""
    if fin.startswith("~/"):
        return fin
    if fin.startswith("/"):
        return "/" + fin
    return f"//**/{fin}"


def deny_claude(entrees: list[dict]) -> dict:
    # Un deny Claude gagne toujours sur un allow : une entrée à exception n'est pas traduite.
    return {"permissions": {"deny": [f"{OUTILS_CLAUDE[e['action']]}({chemin_claude(e['fin'])})"
                                     for e in entrees if not e.get("sauf")]}}


def deny_opencode(entrees: list[dict]) -> dict:
    # La ressource est relative sous le dossier de travail, absolue ailleurs. Une fin ancrée
    # n'a que sa forme absolue. Le `*` d'OpenCode traverse les `/`, d'où `**` réduit à `*`.
    def ressources(fin):
        fin = fin.replace("**", "*")
        if fin.startswith("~/"):
            return [os.path.expanduser("~") + fin[1:]]
        if fin.startswith("/"):
            return [fin]
        return [fin, f"*/{fin}"]

    policies = []
    for e in entrees:
        outil = OUTILS_OPENCODE[e["action"]]
        for effet, fins in (("deny", [e["fin"]]), ("allow", e.get("sauf") or [])):
            for fin in fins:
                policies += [{"action": "tool.use", "resource": f"{outil}:{r}", "effect": effet}
                             for r in ressources(fin)]
    return {"policies": policies}


TRADUCTIONS = {"claude": deny_claude, "opencode": deny_opencode}


def charger_mcp(chemin: str) -> list[dict]:
    """Lit `mcp/servers.yaml`. Un serveur sans installateur Claude est refusé :
    install.py n'écrit pas `.claude.json` lui-même."""
    with open(chemin, encoding="utf-8") as f:
        serveurs = yaml.safe_load(f) or []
    for s in serveurs:
        manque = [c for c in ("nom", "commande", "raison") if not s.get(c)]
        if not (s.get("installateur") or {}).get("claude"):
            manque.append("installateur.claude")
        if manque:
            raise SystemExit(f"install — {chemin} : serveur {s.get('nom', '?')} sans {', '.join(manque)}.")
    return serveurs


def mcp_opencode(serveurs: list[dict]) -> dict:
    return {"mcp": {"servers": {s["nom"]: {"type": "local", "command": s["commande"], "disabled": False,
                                           **(s.get("opencode") or {})} for s in serveurs}}}


def verifier_mcp_claude(cible: str, serveurs: list[dict], fix: bool):
    """Claude lit `~/.claude.json` pour `~/.claude`, `<cible>/.claude.json` sinon."""
    defaut = os.path.join(os.path.expanduser("~"), ".claude")
    fichier = defaut + ".json" if cible == defaut else os.path.join(cible, ".claude.json")

    def presents():
        if not os.path.exists(fichier):
            return set()
        with open(fichier, encoding="utf-8") as f:
            return set(json.load(f).get("mcpServers", {}))

    manquants = [s for s in serveurs if s["nom"] not in presents()]
    if not fix:
        return [f"ÉCART  .claude.json mcpServers.{s['nom']} : absent" for s in manquants], []
    env = dict(os.environ, CODEGRAPH_TELEMETRY="0")
    env.pop("CLAUDE_CONFIG_DIR", None)
    if cible != defaut:
        env["CLAUDE_CONFIG_DIR"] = cible
    ecarts, faits = [], []
    for s in manquants:
        r = subprocess.run(s["installateur"]["claude"], env=env, capture_output=True, text=True)
        if r.returncode == 0 and s["nom"] in presents():
            faits.append(f"installé   .claude.json mcpServers.{s['nom']}")
        else:
            ecarts.append(f"ÉCART  .claude.json mcpServers.{s['nom']} : l'installateur a échoué ({r.returncode})")
    return ecarts, faits


def ajouter(repo: dict, ajout: dict) -> dict:
    """Ajoute la traduction au gabarit, un niveau d'objet en profondeur."""
    for cle, valeur in ajout.items():
        if isinstance(valeur, dict) and isinstance(repo.get(cle), dict):
            repo[cle] = {**repo[cle], **valeur}
        else:
            repo[cle] = valeur
    return repo


def verifier_settings(cible: str, manifeste: dict, agent: str, repo_liens: str, fix: bool):
    # Un manifeste sans `settings` n'a rien à fusionner.
    if "settings" not in manifeste:
        return [], []
    sync = charger_sync_settings()
    nom = os.path.basename(manifeste["settings"])
    repo = sync.charger(os.path.join(REPO, manifeste["settings"]))
    if "deny" in manifeste:
        repo = ajouter(repo, TRADUCTIONS[agent](charger_deny(os.path.join(REPO, manifeste["deny"]))))
    if "mcp" in manifeste and agent == "opencode":
        repo = ajouter(repo, mcp_opencode(charger_mcp(os.path.join(REPO, manifeste["mcp"]))))
    repo = reecrire_repo(reecrire_chemins(repo, rendre_cible(cible) + "/"), repo_liens)
    fichier = os.path.join(cible, nom)
    machine = sync.charger(fichier, absent_ok=True)
    resultat, ecarts = sync.fusionner(repo, machine)
    if fix and ecarts:
        os.makedirs(cible, exist_ok=True)
        sync.ecrire(fichier, resultat)
        return [], [f"appliqué   {nom} {e}" for e in ecarts]
    return [f"ÉCART  {nom} {e}" for e in ecarts], []


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description="Vérifie ou installe le harnais dans la config d'un agent.")
    p.add_argument("--agent", required=True)
    p.add_argument("--target", required=True)
    mode = p.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="vérifie sans écrire (défaut)")
    mode.add_argument("--fix", action="store_true", help="installe et répare")
    mode.add_argument("--list", action="store_true", help="liste les liens attendus")
    p.add_argument("--repo", help="racine des sources de liens, par défaut le repo du script")
    args = p.parse_args(argv)

    manifeste = charger_manifeste(args.agent)
    cible = os.path.abspath(os.path.expanduser(args.target))
    repo_liens = os.path.abspath(os.path.expanduser(args.repo)) if args.repo else REPO
    attendus = liens_attendus(manifeste, repo_liens)

    if args.list:
        for rel, source in attendus.items():
            print(f"{rel} -> {source}")
        return 0

    ecarts, faits = verifier_liens(cible, manifeste, attendus, repo_liens, args.fix)
    e_settings, f_settings = verifier_settings(cible, manifeste, args.agent, repo_liens, args.fix)
    ecarts += e_settings
    faits += f_settings
    # Après la fusion : l'installateur écrit aussi dans settings.json.
    if "mcp" in manifeste and args.agent == "claude":
        e_mcp, f_mcp = verifier_mcp_claude(cible, charger_mcp(os.path.join(REPO, manifeste["mcp"])), args.fix)
        ecarts += e_mcp
        faits += f_mcp

    for f in faits:
        print(f"  {f}")
    if not ecarts:
        quoi = f" et {os.path.basename(manifeste['settings'])}" if "settings" in manifeste else ""
        print(f"✓ {cible} : {len(attendus)} liens{quoi}, aucun écart.")
        return 0
    for e in ecarts:
        print(f"  {e}", file=sys.stderr)
    print(f"✗ {len(ecarts)} écart(s). Relancer avec --fix répare ; un INTRUS ou un PAS UN LIEN se traite à la main.",
          file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
