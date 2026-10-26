#!/usr/bin/env python3
"""Calibre `tools/bench/opencode-go.py` sur une base fabriquée.

Ne lance aucune session. Une somme qui rate ses lignes rend 0 $, et 0 $ se lit comme
« quota intact » : le défaut passerait pour un feu vert. Chaque cas montre donc une
consommation qui compte, et une qui doit être écartée.

Sortie : 0 si tout passe, 1 si un cas échoue.
"""

from __future__ import annotations

import importlib.util
import json
import os
import sqlite3
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
MODULE = os.path.join(os.path.dirname(HERE), "bench", "opencode-go.py")
spec = importlib.util.spec_from_file_location("opencode_go", MODULE)
go = importlib.util.module_from_spec(spec)
spec.loader.exec_module(go)
echecs = 0

H = 3600 * 1000
MAINTENANT = 1_000 * 24 * H
DS, MM = go.CHAINE


def cas(nom: str, obtenu, attendu):
    global echecs
    ok = obtenu == attendu
    print(f"  {'ok  ' if ok else 'FAIL'}  {nom}")
    if not ok:
        echecs += 1
        print(f"        obtenu  : {obtenu!r}\n        attendu : {attendu!r}")


def base(tmp: str, sessions: list[tuple[str, float, int]]) -> str:
    """sessions : (modèle complet, coût, âge en heures)."""
    db = os.path.join(tmp, f"oc-{len(os.listdir(tmp))}.db")
    con = sqlite3.connect(db)
    con.execute("create table session_v2 (id text, model text, cost real, time_created integer)")
    for i, (modele, cout, age) in enumerate(sessions):
        fournisseur, ident = modele.split("/", 1)
        con.execute("insert into session_v2 values (?, ?, ?, ?)",
                    (f"s{i}", json.dumps({"id": ident, "providerID": fournisseur}), cout, MAINTENANT - age * H))
    con.commit()
    con.close()
    return db


with tempfile.TemporaryDirectory() as tmp:
    con = go.ouvrir(base(tmp, [(DS, 1.0, 1), (DS, 2.0, 10), (DS, 4.0, 24 * 10), (DS, 8.0, 24 * 40),
                              (MM, 100.0, 1), ("opencode/deepseek-v4.1-flash", 50.0, 1)]))
    cas("5 h : seules les sessions récentes du modèle comptent", go.conso(con, DS, MAINTENANT - 5 * H), 1.0)
    cas("7 j et 30 j : la fenêtre glisse, la session de 40 j sort",
        [round(c, 2) for _, c, _ in go.etat(con, DS, MAINTENANT)][1:], [3.0, 7.0])
    cas("même id chez un autre fournisseur : écarté", go.conso(con, "opencode/deepseek-v4.1-flash", 0), 50.0)

    cas("sous le seuil : DeepSeek retenu", go.choisir(con, MAINTENANT)[0], DS)
    cas("--apres DeepSeek : MiniMax au-delà, aucun modèle", go.choisir(con, MAINTENANT, apres=DS)[0], None)

    seuil_5h = go.PLAFONDS[DS] * 0.2 * go.SEUIL
    pleine = go.ouvrir(base(tmp, [(DS, seuil_5h, 1)]))
    modele, motifs = go.choisir(pleine, MAINTENANT)
    cas("DeepSeek à 80 % des 5 h : repli sur MiniMax", modele, MM)
    cas("le motif chiffre la fenêtre dépassée", "5 h" in motifs[0] and DS in motifs[0], True)
    juste = go.ouvrir(base(tmp, [(DS, seuil_5h - 0.01, 1)]))
    cas("DeepSeek juste sous 80 % : retenu", go.choisir(juste, MAINTENANT)[0], DS)

    cas("modèle hors Go : refusé", "abonnement Go" in (go.controler(con, "opencode/x", MAINTENANT) or ""), True)
    cas("modèle Go sans plafond : refusé", "plafond" in (go.controler(con, "opencode-go/autre", MAINTENANT) or ""), True)

    cas("erreur de limite Go : reconnue, casse et séparateurs ignorés",
        [go.est_limite_go(e) for e in ("gousagelimiterror", "GoUsageLimitError : x", "go_usage_limit")],
        [True, True, True])
    cas("autre erreur : pas une limite Go",
        [go.est_limite_go(e) for e in ("provider.quota", "freeusagelimiterror", None)], [False, False, False])
    cas("suivant : MiniMax après DeepSeek, rien après MiniMax", (go.suivant(DS), go.suivant(MM)), (MM, None))

    sortie = os.path.join(tmp, "run.jsonl")
    with open(sortie, "w", encoding="utf-8") as f:
        f.write(json.dumps({"type": "error", "error": {"type": "GoUsageLimitError"}}) + "\n")
    propre = os.path.join(tmp, "run.err")
    open(propre, "w").close()
    cli = lambda *a: subprocess.run([sys.executable, MODULE, *a], capture_output=True, text=True)
    cas("CLI --limite : 0 sur une sortie qui porte la limite", cli("--limite", propre, sortie).returncode, 0)
    cas("CLI --limite : 1 sur une sortie propre", cli("--limite", propre).returncode, 1)
    r = cli("--db", base(tmp, []), "--modele", "opencode/deepseek-v4.1-flash-free")
    cas("CLI --modele hors Go : code 1, rien sur stdout", (r.returncode, r.stdout), (1, ""))

print(f"{'✓' if not echecs else '✗'} {echecs} échec(s).")
sys.exit(1 if echecs else 0)
