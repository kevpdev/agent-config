#!/usr/bin/env python3
"""Rend ce qu'une session du banc a chargé, et échoue sur une fuite d'isolation.

POURQUOI CE SCRIPT
    Le banc (`tools/bench.sh`) doit prouver ce que Claude charge du worktree, sans
    regarder `~/.claude`. Les skills se lisent dans l'événement `system/init` du flux
    `stream-json`, comme le fait `run-skill-evals.py`. Les rules se lisent dans le
    journal du hook `InstructionsLoaded` (`tools/bench/log-instructions.sh`).

ORIGINE D'UNE RULE, par son chemin résolu
    worktree   le fichier vit dans le repo de ce script
    banc       le fichier vit dans le dossier du banc, sans lien vers ailleurs
    HORS BANC  tout le reste, `~/.claude` compris : l'isolation a fui

ÉCHOUE FERMÉ : code 1 si le flux n'a pas d'`init`, si le journal est vide ou porte
une LOG-ERREUR, ou si une rule est HORS BANC. Un journal vide veut dire « le journal
est cassé », jamais « aucune rule chargée ».

Usage
    python3 tools/bench-report.py --stream run.jsonl --log instructions.log --bench DIR [--repo DIR]
"""

from __future__ import annotations

import argparse
import json
import os
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def lire_init(chemin: str) -> dict | None:
    with open(chemin, encoding="utf-8") as f:
        for ligne in f:
            ligne = ligne.strip()
            if not ligne.startswith("{"):
                continue
            try:
                evt = json.loads(ligne)
            except json.JSONDecodeError:
                continue
            if evt.get("type") == "system" and evt.get("subtype") == "init":
                return evt
    return None


def lister(init: dict, cle: str) -> list:
    valeur = init.get(cle)
    return valeur if isinstance(valeur, list) else []


def skills_de_plugins(init: dict) -> dict[str, list[str]]:
    """Les skills d'un plugin ne sont pas dans `skills` : ils sortent dans
    `slash_commands`, préfixés par le nom du plugin (constaté en 2.1.308)."""
    noms = [p.get("name") for p in lister(init, "plugins") if isinstance(p, dict) and p.get("path") != "builtin"]
    commandes = [str(c) for c in lister(init, "slash_commands")]
    return {n: sorted(c for c in commandes if c.startswith(f"{n}:")) for n in noms}


def lire_journal(chemin: str) -> tuple[list[tuple[str, str]], list[str]]:
    """Rend [(raison, chemin)] et les lignes LOG-ERREUR."""
    entrees, erreurs = [], []
    if not os.path.exists(chemin):
        return entrees, erreurs
    with open(chemin, encoding="utf-8") as f:
        for ligne in f:
            champs = ligne.rstrip("\n").split("\t")
            if len(champs) < 3:
                continue
            if champs[1] == "LOG-ERREUR":
                erreurs.append(ligne.strip())
            else:
                entrees.append((champs[1], champs[2]))
    return entrees, erreurs


def sous(chemin: str, racine: str) -> bool:
    return chemin == racine or chemin.startswith(racine.rstrip(os.sep) + os.sep)


def origine(chemin: str, banc: str, repo: str) -> str:
    reel = os.path.realpath(chemin)
    if sous(reel, os.path.realpath(repo)):
        return "worktree"
    if sous(os.path.abspath(chemin), banc) and sous(reel, os.path.realpath(banc)):
        return "banc"
    return "HORS BANC"


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description="Rapport de chargement d'une session du banc.")
    p.add_argument("--stream", required=True)
    p.add_argument("--log", required=True)
    p.add_argument("--bench", required=True)
    p.add_argument("--repo", default=REPO)
    args = p.parse_args(argv)
    banc = os.path.abspath(os.path.expanduser(args.bench))

    problemes: list[str] = []

    init = lire_init(args.stream)
    if init is None:
        problemes.append(f"aucun événement system/init dans {args.stream}")
        init = {}
    skills = sorted(str(s) for s in lister(init, "skills"))
    print(f"Skills ({len(skills)})")
    for s in skills:
        print(f"  {s}")

    versions = {p.get("name"): p.get("version", "?") for p in lister(init, "plugins") if isinstance(p, dict)}
    par_plugin = skills_de_plugins(init)
    print(f"Plugins ({len(par_plugin)})")
    for nom, liste in par_plugin.items():
        print(f"  {nom}@{versions.get(nom)}  {len(liste)} skills")

    entrees, erreurs = lire_journal(args.log)
    if not entrees and not erreurs:
        problemes.append(f"journal vide ou absent : {args.log}. Le hook InstructionsLoaded ne s'est pas déclenché.")
    problemes += erreurs

    vus: dict[str, tuple[str, str]] = {}
    for raison, chemin in entrees:
        vus.setdefault(chemin, (raison, origine(chemin, banc, args.repo)))
    print(f"Rules et instructions ({len(vus)})")
    for chemin, (raison, orig) in sorted(vus.items(), key=lambda kv: (kv[1][1], kv[0])):
        print(f"  {orig:<9}  {raison:<14}  {chemin}")
        if orig == "HORS BANC":
            problemes.append(f"HORS BANC  {chemin} → {os.path.realpath(chemin)}")

    if problemes:
        for pb in problemes:
            print(f"  ✗ {pb}", file=sys.stderr)
        print(f"✗ {len(problemes)} problème(s).", file=sys.stderr)
        return 1
    n_plugins = sum(len(v) for v in par_plugin.values())
    print(f"✓ {len(skills)} skills, {n_plugins} skills de plugins, {len(vus)} fichiers d'instructions, aucune fuite.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
