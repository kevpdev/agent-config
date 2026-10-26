#!/usr/bin/env python3
"""Calibre la lecture des drivers de `tools/drivers/` sur des sorties fabriquées.

Ne lance aucune session. Une lecture cassée rend une liste vide, et une liste vide se lit
comme « aucun skill ne s'est ouvert » : le défaut passerait pour un verdict. Chaque cas
montre donc une lecture qui trouve, et une qui doit écarter.

Sortie : 0 si tout passe, 1 si un cas échoue.
"""

from __future__ import annotations

import importlib.util
import json
import os
import sqlite3
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
DRIVERS = os.path.join(os.path.dirname(HERE), "drivers")
echecs = 0


def load(name: str):
    spec = importlib.util.spec_from_file_location(f"driver_{name}", os.path.join(DRIVERS, f"{name}.py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def cas(nom: str, obtenu, attendu):
    global echecs
    ok = obtenu == attendu
    print(f"  {'ok  ' if ok else 'FAIL'}  {nom}")
    if not ok:
        echecs += 1
        print(f"        obtenu  : {obtenu!r}\n        attendu : {attendu!r}")


def lignes(*events) -> str:
    return "\n".join(json.dumps(e) for e in events) + "\n"


def claude(driver):
    stream = lignes(
        {"type": "system", "subtype": "init", "skills": ["demo", "autre"]},
        {"type": "assistant", "message": {"content": [
            {"type": "tool_use", "name": "Skill", "input": {"skill": "demo"}},
            {"type": "tool_use", "name": "Read", "input": {"file_path": "x"}},
        ]}},
        {"type": "result", "result": "fini", "total_cost_usd": 0.5},
    )
    cas("claude — skill ouvert, listing, texte, coût", driver.parse_stream(stream),
        (["demo"], ["demo", "autre"], "fini", 0.5))
    cas("claude — un autre outil n'ouvre rien", driver.parse_stream(lignes(
        {"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "Read", "input": {}}]}},
    ))[0], [])


def opencode_stream(driver):
    stream = lignes(
        {"type": "step_start", "sessionID": "s1", "part": {}},
        {"type": "tool_use", "sessionID": "s1", "part": {"tool": "skill", "state": {"status": "completed", "input": {"id": "demo"}}}},
        {"type": "tool_use", "sessionID": "s1", "part": {"tool": "shell", "state": {"status": "error", "input": {"command": "ls"}}}},
        {"type": "step_finish", "sessionID": "s1", "part": {"cost": 0.25}},
        {"type": "text", "sessionID": "s1", "part": {"text": "fini"}},
    )
    cas("opencode — skill ouvert, session, texte, coût", driver.parse_stream(stream),
        (["demo"], "s1", "fini", 0.25, None))
    cas("opencode — une erreur de fournisseur remonte", driver.parse_stream(lignes(
        {"type": "error", "sessionID": "s1", "error": {"type": "provider.quota", "message": "limite"}},
    ))[2:], ("", 0.0, "provider.quota : limite"))


def opencode_rejeu(driver):
    """Sur une limite Go, la session est rejouée une fois avec le modèle suivant."""
    limite = lignes({"type": "error", "error": {"type": "GoUsageLimitError", "message": "limit"}})
    bonne = lignes({"type": "text", "part": {"text": "fini"}})
    joues = []

    def faux(ctx, case, workdir, model, timeout):
        joues.append(model)
        return (limite if len(joues) == 1 else bonne), 0

    vrai, driver._lancer = driver._lancer, faux
    try:
        with tempfile.TemporaryDirectory() as tmp:
            work = os.path.join(tmp, "work")
            os.makedirs(work)
            ctx = {"go": driver.GO, "db": os.path.join(tmp, "absente.db"), "rapport": None}
            res = driver.run_session(ctx, {"query": "q"}, work, driver.GO.CHAINE[0], 10)
    finally:
        driver._lancer = vrai
    cas("opencode — limite Go : rejeu sur le modèle suivant", (joues, res[2]), (driver.GO.CHAINE, "fini"))


def opencode_base(driver):
    with tempfile.TemporaryDirectory() as tmp:
        db = os.path.join(tmp, "opencode.db")
        con = sqlite3.connect(db)
        con.executescript("""
            create table session_v2 (id text primary key, directory text);
            create table session_message (id text primary key, session_id text, type text, seq integer, data text);
            create table instruction_state (session_id text primary key, initial_values text);
            create table instruction_blob (hash text primary key, value text);
        """)
        modele = {"providerID": "p", "id": "m"}
        reponse = lambda t: json.dumps({"model": modele, "content": [{"type": "text", "text": t}]})
        rows = [
            ("vivant", "/home/x/projet", [("user", json.dumps({"text": "explique plus simplement"})),
                                          ("assistant", reponse("une réponse ; deux"))]),
            ("regle", "/home/x/autre", [("assistant", reponse("avec la règle"))]),
            ("banc", os.path.join(tempfile.gettempdir(), "tmp.banc"), [("assistant", reponse("du banc"))]),
        ]
        for sid, directory, messages in rows:
            con.execute("insert into session_v2 values (?, ?)", (sid, directory))
            for seq, (kind, data) in enumerate(messages):
                con.execute("insert into session_message values (?, ?, ?, ?, ?)", (f"{sid}{seq}", sid, kind, seq, data))
        con.execute("insert into instruction_state values ('regle', ?)", (json.dumps({"core/instructions": "h"}),))
        con.execute("insert into instruction_blob values ('h', ?)",
                    (json.dumps([{"path": "/repo/rules/ponctuation.md", "content": ""}]),))
        con.commit()
        con.close()

        convs = driver.conversations(db)
        cas("opencode — les sessions du dossier temporaire sont écartées",
            sorted(r for c in convs for r in c["replies"]), ["avec la règle", "une réponse ; deux"])
        titres = sorted(c["titre"] for c in convs)
        cas("opencode — un groupe par modèle et par présence de ponctuation.md", titres, [
            "modèle p/m, ponctuation.md absente, 1 session(s)",
            "modèle p/m, ponctuation.md chargée, 1 session(s)",
        ])
        cas("opencode — le prompt suit le modèle de sa session",
            [c["prompts"] for c in convs if "absente" in c["titre"]], [["explique plus simplement"]])


def main() -> int:
    claude(load("claude"))
    oc = load("opencode")
    opencode_stream(oc)
    opencode_base(oc)
    opencode_rejeu(oc)
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "opencode.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"instructions": ["x"]}, f)
        oc.ajouter_agent(path)
        with open(path, encoding="utf-8") as f:
            config = json.load(f)
        cas("opencode — l'agent d'éval ne garde que skill",
            config["agent"][oc.AGENT]["permission"], {"*": "deny", "skill": "allow"})
        cas("opencode — le reste de la config est gardé", config["instructions"], ["x"])
    env = oc.environnement("/cfg")
    cas("opencode — aucune variable CLAUDE* ni ANTHROPIC* dans la session",
        [k for k in env if k.startswith(("CLAUDE", "ANTHROPIC"))], [])
    return 1 if echecs else 0


if __name__ == "__main__":
    sys.exit(main())
