#!/usr/bin/env python3
"""Rapport du banc OpenCode : gardes et skills d'une session lancée dans le dépôt jetable.

POURQUOI LIRE LA BASE
    `opencode run` n'écrit pas l'état des outils sur sa sortie de façon stable. La base
    `opencode.db` le garde :
    - chaque message assistant de `session_message` porte ses appels d'outil, et un refus de
      `permission.evaluate` y apparaît comme `state.status: "error"` avec
      `error.type: "permission.rejected"`. Constaté le 2026-10-21 sur une session du
      `garden-guard` du vault ;
    - `instruction_state.initial_values` donne, par session, le hash de `core/skill-guidance`,
      et `instruction_blob` la liste `[{id, name, description}]` des skills exposés au modèle.
      L'id vaut le nom du dossier du skill, mesuré le 2026-10-23.

Ce qui est vérifié :
    1. le commit signé est refusé, et `ls` passe ;
    2. avec --skills : les skills auto-invocables du repo sont exposés, et aucun de ceux qui
       portent `disable-model-invocation: true` ;
    3. avec --rules : chaque `rules/*.md` est dans `core/instructions`, chargé par le
       tableau `instructions` d'opencode.json. Cette liste porte `[{path, content}]`.

La base est ouverte en lecture seule. La session est celle dont `directory` est le dépôt
jetable du banc, qui n'existe que le temps d'un lancement.

Sortie : 0 si tout est vu, 1 sinon.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3
import sys

MANUEL = re.compile(r"^disable-model-invocation:\s*true\s*$", re.M)


def ouvrir(db: str):
    return sqlite3.connect(f"file:{db}?mode=ro", uri=True)


def sessions_de(con, dossier: str) -> list[str]:
    return [r[0] for r in con.execute("select id from session_v2 where directory = ?", (dossier,))]


def appels_shell(con, sessions: list[str]) -> list[dict]:
    """Les états des appels shell des sessions, dans l'ordre."""
    out = []
    for sid in sessions:
        for (data,) in con.execute(
                "select data from session_message where session_id = ? and type = 'assistant' order by seq",
                (sid,)):
            for item in json.loads(data).get("content", []):
                if item.get("type") == "tool" and item.get("name") == "shell":
                    out.append(item.get("state", {}))
    return out


def skills_vus(con, sessions: list[str]) -> set[str]:
    """Les ids de `core/skill-guidance`, toutes sessions confondues."""
    vus: set[str] = set()
    for sid in sessions:
        r = con.execute("select initial_values from instruction_state where session_id = ?", (sid,)).fetchone()
        h = json.loads(r[0]).get("core/skill-guidance") if r else None
        blob = con.execute("select value from instruction_blob where hash = ?", (h,)).fetchone() if h else None
        if blob:
            vus |= {s["id"] for s in json.loads(blob[0])}
    return vus


def instructions_vues(con, sessions: list[str]) -> set[str]:
    """Les chemins de `core/instructions`, en realpath, toutes sessions confondues."""
    vues: set[str] = set()
    for sid in sessions:
        r = con.execute("select initial_values from instruction_state where session_id = ?", (sid,)).fetchone()
        h = json.loads(r[0]).get("core/instructions") if r else None
        blob = con.execute("select value from instruction_blob where hash = ?", (h,)).fetchone() if h else None
        if blob:
            vues |= {os.path.realpath(i["path"]) for i in json.loads(blob[0])}
    return vues


def verifier_rules(vues: set[str], dossier: str) -> int:
    attendues = {os.path.realpath(os.path.join(dossier, f)) for f in os.listdir(dossier) if f.endswith(".md")}
    manquantes = sorted(os.path.basename(f) for f in attendues - vues)
    if manquantes:
        print(f"✗ {len(manquantes)} règle(s) absente(s) de core/instructions : {', '.join(manquantes)}")
        return 1
    print(f"✓ {len(attendues)} règles chargées par instructions.")
    return 0


def skills_attendus(dossier: str) -> tuple[set[str], set[str]]:
    """(auto-invocables, manuels) du repo. Un dossier sans SKILL.md n'est pas un skill."""
    auto, manuels = set(), set()
    for nom in sorted(os.listdir(dossier)):
        chemin = os.path.join(dossier, nom, "SKILL.md")
        if not os.path.isfile(chemin):
            continue
        with open(chemin, encoding="utf-8") as f:
            texte = f.read()
        entete = texte.split("---", 2)[1] if texte.startswith("---") else ""
        (manuels if MANUEL.search(entete) else auto).add(nom)
    return auto, manuels


def verifier_gardes(etats: list[dict]) -> int:
    commande = lambda e: str(e.get("input", {}).get("command", ""))
    for e in etats:
        erreur = e.get("error") or {}
        print(f"  {e.get('status', '?'):<10} {commande(e)[:60]:<60} {erreur.get('type', '')}")
    commits = [e for e in etats if "git commit" in commande(e)]
    ls = [e for e in etats if commande(e).strip() == "ls"]
    echecs = 0
    refus = [e for e in commits if e.get("status") == "error"
             and (e.get("error") or {}).get("type") == "permission.rejected"]
    if refus:
        print("✓ commit signé refusé par le garde :", (refus[0]["error"].get("message") or "")[:160])
    else:
        echecs += 1
        print("✗ aucun commit refusé par permission.rejected" + ("" if commits else " (le modèle n'a pas lancé de commit)"))
    if any(e.get("status") == "completed" for e in ls):
        print("✓ ls passe.")
    else:
        echecs += 1
        print("✗ ls n'a pas abouti" + ("" if ls else " (le modèle ne l'a pas lancé)"))
    return echecs


def verifier_skills(vus: set[str], auto: set[str], manuels: set[str]) -> int:
    manquants, intrus = sorted(auto - vus), sorted(manuels & vus)
    if not manquants:
        print(f"✓ {len(auto)} skills auto-invocables exposés.")
    else:
        print(f"✗ {len(manquants)} skill(s) auto-invocable(s) absent(s) : {', '.join(manquants)}")
    if not intrus:
        print(f"✓ aucun des {len(manuels)} skills manuels exposé.")
    else:
        print(f"✗ skill(s) manuel(s) exposé(s) au modèle : {', '.join(intrus)}")
    return (1 if manquants else 0) + (1 if intrus else 0)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--db", default=os.path.expanduser("~/.local/share/opencode/opencode.db"))
    p.add_argument("--dir", required=True, help="dossier de travail de la session du banc")
    p.add_argument("--skills", help="dossier skills/ du repo, pour vérifier les skills exposés")
    p.add_argument("--rules", help="dossier rules/ du repo, pour vérifier les règles chargées")
    args = p.parse_args(argv)

    con = ouvrir(args.db)
    sessions = sessions_de(con, args.dir)
    if not sessions:
        print(f"✗ aucune session dans {args.db} pour {args.dir} : la session n'a pas démarré.")
        return 1

    echecs = verifier_gardes(appels_shell(con, sessions))
    if args.skills:
        echecs += verifier_skills(skills_vus(con, sessions), *skills_attendus(args.skills))
    if args.rules:
        echecs += verifier_rules(instructions_vues(con, sessions), args.rules)
    return 1 if echecs else 0


if __name__ == "__main__":
    sys.exit(main())
