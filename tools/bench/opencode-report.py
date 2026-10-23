#!/usr/bin/env python3
"""Rapport du banc OpenCode : le garde a-t-il refusé le commit signé, et laissé passer `ls` ?

POURQUOI LIRE LA BASE
    `opencode run` n'écrit pas l'état des outils sur sa sortie de façon stable. La base
    `opencode.db` le garde : chaque message assistant de `session_message` porte ses
    appels d'outil, et un refus de `permission.evaluate` y apparaît comme
    `state.status: "error"` avec `error.type: "permission.rejected"`. Constaté le
    2026-10-21 sur une session du `garden-guard` du vault.

La base est ouverte en lecture seule. La session est celle dont `directory` est le dépôt
jetable du banc, qui n'existe que le temps d'un lancement.

Sortie : 0 si les deux attendus sont vus, 1 sinon.
"""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys


def appels(db: str, dossier: str):
    """Les appels shell des sessions ouvertes dans `dossier`, dans l'ordre."""
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    sessions = [r[0] for r in con.execute("select id from session_v2 where directory = ?", (dossier,))]
    out = []
    for sid in sessions:
        for (data,) in con.execute(
                "select data from session_message where session_id = ? and type = 'assistant' order by seq",
                (sid,)):
            for item in json.loads(data).get("content", []):
                if item.get("type") == "tool" and item.get("name") == "shell":
                    out.append(item.get("state", {}))
    return sessions, out


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--db", default=os.path.expanduser("~/.local/share/opencode/opencode.db"))
    p.add_argument("--dir", required=True, help="dossier de travail de la session du banc")
    args = p.parse_args(argv)

    sessions, etats = appels(args.db, args.dir)
    if not sessions:
        print(f"✗ aucune session dans {args.db} pour {args.dir} : la session n'a pas démarré.")
        return 1

    commande = lambda e: str(e.get("input", {}).get("command", ""))
    commits = [e for e in etats if "git commit" in commande(e)]
    ls = [e for e in etats if commande(e).strip() == "ls"]
    for e in etats:
        erreur = e.get("error") or {}
        print(f"  {e.get('status', '?'):<10} {commande(e)[:60]:<60} {erreur.get('type', '')}")

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
    return 1 if echecs else 0


if __name__ == "__main__":
    sys.exit(main())
