#!/usr/bin/env python3
"""Batterie du rapport du banc OpenCode, sur une base jetable.

Pourquoi cette batterie existe : le banc réel passe par un modèle, donc il ne montre
jamais un échec à volonté. Un rapport qui dirait toujours « ✓ » passerait pour juste.
Ici, chaque défaut est fabriqué dans une base au schéma mesuré de `opencode.db`, réduit
aux colonnes que le rapport lit, et le rapport doit le signaler.

Sortie : 0 si tous les cas passent, 1 si un cas échoue.
"""

from __future__ import annotations

import json
import os
import sqlite3
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
RAPPORT = os.path.join(os.path.dirname(HERE), "bench", "opencode-report.py")
DOSSIER = "/tmp/depot-du-banc"
echecs = 0


def cas(nom: str, ok: bool, sortie: str = ""):
    global echecs
    print(f"  {'ok  ' if ok else 'FAIL'}  {nom}")
    if not ok:
        echecs += 1
        print("        " + sortie.replace("\n", "\n        "))


def appel(commande: str, status: str, erreur: str | None = None) -> dict:
    state = {"status": status, "input": {"command": commande}}
    if erreur:
        state["error"] = {"type": erreur, "message": "refusé par le garde"}
    return {"type": "tool", "name": "shell", "state": state}


def lecture(chemin: str, status: str, sortie: str = "") -> dict:
    state = {"status": status, "input": {"path": chemin}, "output": sortie}
    if status == "error":
        state["error"] = {"type": "permission.rejected", "message": "Blocked by configuration policy"}
    return {"type": "tool", "name": "read", "state": state}


def base(tmp: str, appels: list[dict], skills: list[str], dossier: str = DOSSIER,
         regles: list[str] | None = None) -> str:
    db = os.path.join(tmp, "opencode.db")
    con = sqlite3.connect(db)
    con.executescript("""
        create table session_v2 (id text primary key, directory text not null);
        create table session_message (id text primary key, session_id text, type text, seq integer, data text);
        create table instruction_state (session_id text primary key, initial_values text);
        create table instruction_blob (hash text primary key, value text);
    """)
    con.execute("insert into session_v2 values ('s1', ?)", (dossier,))
    con.execute("insert into session_message values ('m1', 's1', 'assistant', 1, ?)",
                (json.dumps({"content": appels}),))
    con.execute("insert into instruction_state values ('s1', ?)",
                (json.dumps({"core/skill-guidance": "h1", "core/instructions": "h2"}),))
    con.execute("insert into instruction_blob values ('h1', ?)",
                (json.dumps([{"id": s, "name": s, "description": ""} for s in skills]),))
    con.execute("insert into instruction_blob values ('h2', ?)",
                (json.dumps([{"path": p, "content": "x"} for p in regles or []]),))
    con.commit()
    con.close()
    return db


def skills_du_repo(tmp: str) -> str:
    racine = os.path.join(tmp, "skills")
    for nom, manuel in (("auto-a", False), ("auto-b", False), ("manuel-c", True)):
        os.makedirs(os.path.join(racine, nom))
        entete = "disable-model-invocation: true\n" if manuel else ""
        with open(os.path.join(racine, nom, "SKILL.md"), "w", encoding="utf-8") as f:
            f.write(f"---\nname: {nom}\ndescription: x\n{entete}---\n\ncorps\n")
    os.makedirs(os.path.join(racine, "_shared"))  # sans SKILL.md : pas un skill
    return racine


def regles_du_repo(tmp: str) -> str:
    racine = os.path.join(tmp, "rules")
    os.makedirs(os.path.join(racine, "references"))  # un dossier, pas une règle
    for nom in ("style.md", "tooling.md"):
        with open(os.path.join(racine, nom), "w", encoding="utf-8") as f:
            f.write("# règle\n")
    return racine


def lancer(db: str, skills: str | None, rules: str | None = None, leurre: bool = False) -> tuple[int, str]:
    argv = [sys.executable, RAPPORT, "--db", db, "--dir", DOSSIER] + (["--skills", skills] if skills else [])
    argv += ["--rules", rules] if rules else []
    argv += ["--leurre", LEURRE, "--temoin", TEMOIN] if leurre else []
    r = subprocess.run(argv, capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


LEURRE, TEMOIN = "/tmp/leurre/.config/opencode/service.json", "temoin-0123"
BONS = [appel("git commit --allow-empty -F msg.txt", "error", "permission.rejected"), appel("ls", "completed")]

with tempfile.TemporaryDirectory() as tmp:
    racine = skills_du_repo(tmp)

    def rapport(appels, skills, avec_skills=True, dossier=DOSSIER):
        sous = tempfile.mkdtemp(dir=tmp)
        return lancer(base(sous, appels, skills, dossier), racine if avec_skills else None)

    code, sortie = rapport(BONS, ["auto-a", "auto-b", "opencode"])
    cas("tout vu : code 0", code == 0, sortie)

    code, sortie = rapport([appel("git commit -F msg.txt", "completed"), appel("ls", "completed")], ["auto-a", "auto-b"])
    cas("commit passé : signalé", code == 1 and "aucun commit refusé" in sortie, sortie)

    code, sortie = rapport([BONS[0]], ["auto-a", "auto-b"])
    cas("ls absent : signalé", code == 1 and "ls n'a pas abouti" in sortie, sortie)

    code, sortie = rapport(BONS, ["auto-a"])
    cas("skill auto manquant : nommé", code == 1 and "auto-b" in sortie, sortie)

    code, sortie = rapport(BONS, ["auto-a", "auto-b", "manuel-c"])
    cas("skill manuel exposé : nommé", code == 1 and "manuel-c" in sortie, sortie)

    code, sortie = rapport(BONS, ["opencode"], avec_skills=False)
    cas("sans --skills : les skills ne sont pas jugés", code == 0, sortie)

    code, sortie = rapport(BONS, ["auto-a", "auto-b"], dossier="/ailleurs")
    cas("aucune session pour le dossier : code 1", code == 1 and "aucune session" in sortie, sortie)

    regles = regles_du_repo(tmp)
    auto = ["auto-a", "auto-b"]

    def avec_regles(chargees):
        sous = tempfile.mkdtemp(dir=tmp)
        return lancer(base(sous, BONS, auto, regles=chargees), racine, regles)

    code, sortie = avec_regles([os.path.join(regles, "style.md"), os.path.join(regles, "tooling.md")])
    cas("toutes les règles chargées : code 0", code == 0 and "2 règles" in sortie, sortie)

    code, sortie = avec_regles([os.path.join(regles, "style.md")])
    cas("règle manquante : nommée", code == 1 and "tooling.md" in sortie, sortie)

    def avec_leurre(appels):
        sous = tempfile.mkdtemp(dir=tmp)
        return lancer(base(sous, BONS + appels, auto), racine, leurre=True)

    cat = appel(f"cat {LEURRE}", "completed")
    cat["state"]["output"] = TEMOIN
    code, sortie = avec_leurre([lecture(LEURRE, "error"), cat])
    cas("read du leurre refusé, cat consigné : code 0",
        code == 0 and "read du leurre refusé" in sortie and "le témoin sort" in sortie, sortie)

    code, sortie = avec_leurre([lecture(LEURRE, "completed", TEMOIN)])
    cas("read du leurre abouti avec le témoin : code 1",
        code == 1 and "témoin du leurre est sorti" in sortie, sortie)

    code, sortie = avec_leurre([])
    cas("read du leurre absent : code 1", code == 1 and "aucun read sur le leurre" in sortie, sortie)

print(f"{'✓' if not echecs else '✗'} {echecs} échec(s).")
sys.exit(1 if echecs else 0)
