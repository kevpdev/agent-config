#!/usr/bin/env python3
"""Batterie du hook Stop de lecture vocale, `speak-on-stop.py`.

Pourquoi cette batterie existe : le hook choisit quoi lire dans le transcript.
S'il se trompe, il lit la narration entre deux appels d'outil au lieu de la
réponse finale, et rien ne le signale sauf l'oreille.

Ce qui est vérifié : le texte extrait d'un transcript jetable, et la sortie 0
sans rien sur stdout, puisqu'un hook Stop qui écrit une décision empêche Claude
de s'arrêter.

Sortie : 0 si tous les cas passent, 1 si un cas échoue.
"""

import importlib.util
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.realpath(__file__))
HOOK = os.path.join(os.path.dirname(HERE), "speak-on-stop.py")
spec = importlib.util.spec_from_file_location("speak_on_stop", HOOK)
hook = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hook)

echecs = 0


def egal(nom, obtenu, attendu):
    global echecs
    ok = obtenu == attendu
    print("  %s %s" % ("OK   " if ok else "ECHEC", nom))
    if not ok:
        print("        attendu=%r obtenu=%r" % (attendu, obtenu))
        echecs += 1


def transcript(*entrees):
    fh = tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False)
    for e in entrees:
        fh.write(json.dumps(e) + "\n")
    fh.close()
    return fh.name


def user(content):
    return {"type": "user", "message": {"content": content}}


def assistant(*blocks):
    return {"type": "assistant", "message": {"content": list(blocks)}}


def text(t):
    return {"type": "text", "text": t}


TOOL = {"type": "tool_use", "name": "Bash", "input": {}}
RESULT = [{"type": "tool_result", "content": "ok"}]

t = transcript(user("question 1"), assistant(text("réponse 1")),
               user("question 2"), assistant(text("je regarde"), TOOL), user(RESULT),
               assistant(text("voici la réponse 2")))
egal("narration avant l'outil ignorée", hook.final_reply(t), "voici la réponse 2")

t = transcript(user("q"), assistant(text("partie A")), assistant(text("partie B")))
egal("plusieurs blocs finaux joints", hook.final_reply(t), "partie A\n\npartie B")

t = transcript(user("q"), assistant(text("réponse")), user([{"type": "text", "text": "nouvelle"}]))
egal("nouveau prompt sans réponse : rien", hook.final_reply(t), "")

egal("transcript absent : rien", hook.final_reply("/nonexistent.jsonl"), "")

for nom, entree in (("payload vide", ""), ("payload illisible", "{pas du json"),
                    ("payload coupé par AGENT_VOICE", json.dumps({"last_assistant_message": "Bonjour."}))):
    r = subprocess.run([sys.executable, HOOK], input=entree, capture_output=True, text=True,
                       env={**os.environ, "AGENT_VOICE": "0", "XDG_RUNTIME_DIR": tempfile.mkdtemp()})
    egal(nom + " : sortie 0, stdout vide", (r.returncode, r.stdout), (0, ""))

print("%d échec(s)" % echecs)
sys.exit(1 if echecs else 0)
