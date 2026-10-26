#!/usr/bin/env python3
"""Batterie de tools/session-export.py, sur un export fabriqué.

Pourquoi cette batterie existe : une session réelle ne contient un secret que par
accident, donc elle ne montre jamais un masquage raté à volonté. Ici, l'export suit le
schéma mesuré de `opencode session export` le 2026-10-26 (`info`, `messages[]`, parts
`text`, `reasoning` et `tool`), et chaque secret y est posé exprès.

Sortie : 0 si tous les cas passent, 1 si un cas échoue.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
OUTIL = os.path.join(os.path.dirname(HERE), "session-export.py")
echecs = 0

VALEUR_ENV = "valeurdotenv8c2f41"
VALEUR_EXEMPLE = "valeurexemple5d7e90"
GHP = "ghp_" + "a1" * 18
SK = "sk-" + "b2" * 12
AKIA = "AKIA" + "C3D4" * 4
CLE = "-----BEGIN OPENSSH PRIVATE KEY-----\nb3BlbnNzaC1rZXk\n-----END OPENSSH PRIVATE KEY-----"
RAISONNEMENT = "je réfléchis à la consigne"


def cas(nom: str, ok: bool, detail: str = ""):
    global echecs
    print(f"  {'ok  ' if ok else 'FAIL'}  {nom}")
    if not ok:
        echecs += 1
        print("        " + detail.replace("\n", "\n        ")[:600])


def export(dossier: str) -> dict:
    sortie = (f"1: API_KEY=xyz123abc\n2: DEBUG=1\n3: {{\"password\": \"motdepasse42\"}}\n"
              f"4: {GHP}\n5: {SK}\n6: {AKIA}\n7: {CLE}")
    return {
        "info": {"id": "ses_test", "title": "lecture de notes", "cost": 0.001,
                 "model": {"id": "deepseek-v4.1-flash"}, "location": {"directory": dossier}},
        "messages": [
            {"type": "user", "text": f"retrouve {VALEUR_ENV} et {VALEUR_EXEMPLE} dans le projet", "files": []},
            {"type": "assistant", "content": [
                {"type": "reasoning", "text": RAISONNEMENT},
                {"type": "tool", "name": "read", "state": {
                    "status": "completed", "input": {"path": "notes.txt"},
                    "content": [{"type": "text", "text": sortie}]}},
                {"type": "text", "text": "le fichier contient une liste de réglages"},
            ]},
            {"type": "idle", "outcome": "succeeded"},
        ],
    }


def lancer(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, OUTIL, *args], capture_output=True, text=True)


with tempfile.TemporaryDirectory() as tmp:
    projet = os.path.join(tmp, "projet")
    os.makedirs(os.path.join(projet, "sub"))
    with open(os.path.join(projet, "sub", ".env"), "w") as f:
        f.write(f"export SERVICE_URL=\"{VALEUR_ENV}\"\nDEBUG=1\n")
    with open(os.path.join(projet, ".env.example"), "w") as f:
        f.write(f"SERVICE_URL={VALEUR_EXEMPLE}\n")
    chemin = os.path.join(tmp, "export.json")
    with open(chemin, "w") as f:
        json.dump(export(projet), f)

    r = lancer("--depuis", chemin)
    out = r.stdout
    print("JSON")
    cas("sortie 0", r.returncode == 0, r.stderr)
    cas("valeur d'un .env en sous-dossier, citée en texte libre, masquée", VALEUR_ENV not in out, out)
    cas("valeur de .env.example intacte", VALEUR_EXEMPLE in out, out)
    for nom, jeton in [("ghp_", GHP), ("sk-", SK), ("AKIA", AKIA), ("bloc de clé privée", "b3BlbnNzaC1rZXk")]:
        cas(f"motif {nom} masqué", jeton not in out, out)
    cas("API_KEY=xyz123abc devient API_KEY=***", "API_KEY=***" in out and "xyz123abc" not in out, out)
    cas('"password": "…" devient "password": "***"', "motdepasse42" not in out and 'password\\": \\"***' in out, out)
    cas("DEBUG=1 intact", "DEBUG=1" in out, out)
    cas("texte ordinaire intact", "le fichier contient une liste de réglages" in out, out)
    try:
        json.loads(out)
        cas("la sortie reste du JSON", True)
    except ValueError as exc:
        cas("la sortie reste du JSON", False, str(exc))
    secrets_poses = [VALEUR_ENV, GHP, SK, AKIA, "xyz123abc", "motdepasse42"]
    cas("le bilan compte sans citer de valeur",
        "remplacement" in r.stderr and not any(s in r.stderr for s in secrets_poses), r.stderr)

    print("texte")
    r = lancer("--depuis", chemin, "--texte")
    out = r.stdout
    cas("## user et ## assistant", "## user" in out and "## assistant" in out, out)
    cas("l'outil en une ligne, → read notes.txt", "→ read notes.txt [completed]" in out, out)
    cas("le raisonnement omis", RAISONNEMENT not in out, out)
    cas("le masquage tient aussi en texte", not any(s in out for s in secrets_poses), out)

    print("--env")
    autre = os.path.join(tmp, "ailleurs.env")
    with open(autre, "w") as f:
        f.write(f"X={VALEUR_EXEMPLE}\n")
    r = lancer("--depuis", chemin, "--env", autre)
    cas("une source donnée par --env est masquée", VALEUR_EXEMPLE not in r.stdout, r.stdout)

    print("échec")
    casse = os.path.join(tmp, "casse.json")
    with open(casse, "w") as f:
        f.write("{pas du json")
    r = lancer("--depuis", casse)
    cas("export illisible : sortie 2, stdout vide", r.returncode == 2 and r.stdout == "", r.stdout + r.stderr)

print(f"\n✗ {echecs} cas en échec." if echecs else "\n✓ tous les cas passent.")
sys.exit(1 if echecs else 0)
