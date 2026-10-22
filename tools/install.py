#!/usr/bin/env python3
"""Vérifie, ou installe, le harnais dans la config d'un agent.

POURQUOI CE SCRIPT
    L'installation tenait en deux scripts (`sync-rules.sh`, `sync-settings.py`) et
    47 liens posés à la main, que rien ne vérifiait. Les commandes de hooks de
    `wrappers/claude/settings.json` écrivent `~/.claude/scripts/…` en dur : un banc
    relocalisé par `CLAUDE_CONFIG_DIR` exécuterait donc les gardes du checkout
    principal (audits/2026-10-22-cadrage-harnais-agnostique.md, Q0).

    Ce script lit le manifeste de l'agent (`tools/manifests/<agent>.json`), pose un
    lien par entrée, et fusionne `settings.json` après avoir réécrit le préfixe
    `~/.claude/` des commandes vers la cible.

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

--repo remplace la racine des sources de liens, et seulement elle. Le manifeste et
settings.json se lisent toujours dans le repo du script. Sert à vérifier depuis un
worktree une config qui vise le checkout principal.
"""

from __future__ import annotations

import argparse
import glob
import importlib.util
import json
import os
import sys

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


def charger_sync_settings():
    spec = importlib.util.spec_from_file_location("sync_settings", SYNC_SETTINGS)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def verifier_settings(cible: str, manifeste: dict, fix: bool):
    sync = charger_sync_settings()
    repo = sync.charger(os.path.join(REPO, manifeste["settings"]))
    repo = reecrire_chemins(repo, rendre_cible(cible) + "/")
    fichier = os.path.join(cible, "settings.json")
    machine = sync.charger(fichier, absent_ok=True)
    resultat, ecarts = sync.fusionner(repo, machine)
    if fix and ecarts:
        os.makedirs(cible, exist_ok=True)
        sync.ecrire(fichier, resultat)
        return [], [f"appliqué   settings.json {e}" for e in ecarts]
    return [f"ÉCART  settings.json {e}" for e in ecarts], []


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
    e_settings, f_settings = verifier_settings(cible, manifeste, args.fix)
    ecarts += e_settings
    faits += f_settings

    for f in faits:
        print(f"  {f}")
    if not ecarts:
        print(f"✓ {cible} : {len(attendus)} liens et settings.json, aucun écart.")
        return 0
    for e in ecarts:
        print(f"  {e}", file=sys.stderr)
    print(f"✗ {len(ecarts)} écart(s). Relancer avec --fix répare ; un INTRUS ou un PAS UN LIEN se traite à la main.",
          file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
