#!/usr/bin/env python3
"""Batterie du cœur des gardes, sur l'entrée normalisée de `hooks/check.py`.

Pourquoi cette batterie existe : les batteries de `wrappers/claude/hooks/tests/`
passent par l'adaptateur Claude. Un second agent n'aura que ce contrat-ci, donc le
cœur doit être prouvé sans aucun JSON de Claude. Elle couvre aussi
`no_remote_write`, qui n'avait aucune batterie.

Ce qui est vérifié : la DÉCISION (passe, refus, illisible), pas le libellé du refus.
Chaque garde a au moins un refus et un passage, sinon un garde muet passerait
pour un garde juste.

Sortie : 0 si tous les cas passent, 1 si un cas échoue.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
CHECK = os.path.join(REPO, "hooks", "check.py")

PASSE, REFUS, ILLISIBLE = 0, 2, 1
NOMS = {PASSE: "PASSE", REFUS: "REFUS", ILLISIBLE: "ILLISIBLE"}
echecs = 0


def lancer(entree: str, *argv) -> int:
    r = subprocess.run([sys.executable, CHECK, *argv], input=entree,
                       capture_output=True, text=True)
    return r.returncode


def verifier(nom, attendu, garde, action="shell", command="", paths=(), cwd="/tmp",
             skills_used=None):
    global echecs
    evenement = {"event": "pre_tool", "action": action, "command": command,
                 "paths": list(paths), "cwd": cwd, "session": "test",
                 "skills_used": skills_used}
    obtenu = lancer(json.dumps(evenement), "--guard", garde)
    if obtenu == attendu:
        print(f"  OK    {nom:<58} {NOMS[obtenu]}")
    else:
        print(f"  ECHEC {nom:<58} attendu={NOMS[attendu]} obtenu={NOMS.get(obtenu, obtenu)}")
        echecs += 1


print("=== no_ai_in_commit ===")
verifier("signature Co-Authored-By", REFUS, "no_ai_in_commit",
         command='git commit -m "fix: x\n\nCo-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>"')
verifier("nommer Claude n'est pas signer", PASSE, "no_ai_in_commit",
         command='git commit -m "fix: Claude"')
verifier("format non conventionnel", REFUS, "no_ai_in_commit", command='git commit -m "wip"')
verifier("format conventionnel", PASSE, "no_ai_in_commit",
         command='git commit -m "feat(hooks): add the core"')
verifier("PR signée", REFUS, "no_ai_in_commit",
         command='gh pr create --title "x" --body "Generated with [Claude Code]"')
verifier("fichier de message par variable", REFUS, "no_ai_in_commit",
         command='git commit -F "$S/msg.txt"')
verifier("action edit, hors périmètre", PASSE, "no_ai_in_commit", action="edit",
         paths=["/tmp/x"])

print("=== bash_tooling ===")
verifier("./mvnw direct", REFUS, "bash_tooling", command="./mvnw test")
verifier("forme prescrite", PASSE, "bash_tooling", command="bash -lc 'sh ./mvnw test'")
verifier("heredoc imbriqué", REFUS, "bash_tooling",
         command="bash -lc 'cat >> f << EOF\ncontenu\nEOF'")

print("=== no_remote_write ===")
verifier("écriture via ssh sur prod", REFUS, "no_remote_write",
         command="ssh winggyprod docker compose down")
verifier("lecture via ssh sur prod", PASSE, "no_remote_write",
         command="ssh winggyprod docker ps")
verifier("session ssh interactive sur prod", REFUS, "no_remote_write",
         command="ssh winggyprod")
verifier("upload scp vers preprod", REFUS, "no_remote_write",
         command="scp f.txt winggypreprod:/tmp/")
verifier("edit d'un chemin local", PASSE, "no_remote_write", action="edit",
         paths=["/tmp/x.txt"])

print("=== aidd_skill_lookup ===")
with tempfile.TemporaryDirectory() as aidd:
    os.mkdir(os.path.join(aidd, "aidd_docs"))
    verifier("geste sans skill aidd", REFUS, "aidd_skill_lookup",
             command='gh issue create --title x', cwd=aidd, skills_used=[])
    verifier("geste après un skill aidd", PASSE, "aidd_skill_lookup",
             command='gh issue create --title x', cwd=aidd,
             skills_used=["aidd-vcs:04-issue-create"])
    verifier("skills inconnus : échoue ouvert", PASSE, "aidd_skill_lookup",
             command='gh issue create --title x', cwd=aidd, skills_used=None)
    verifier("sortie aidd-skip", PASSE, "aidd_skill_lookup",
             command='gh issue create --title x # aidd-skip: test', cwd=aidd, skills_used=[])
verifier("hors repo AIDD", PASSE, "aidd_skill_lookup",
         command='gh issue create --title x', cwd="/tmp", skills_used=[])

print("=== contrat de check.py ===")
for nom, entree, attendu in [
    ("entrée non JSON", "pas du json", ILLISIBLE),
    ("entrée JSON qui n'est pas un objet", "[1]", ILLISIBLE),
    ("tous les gardes, commande anodine", json.dumps({"action": "shell", "command": "ls"}), PASSE),
    ("tous les gardes, commit signé",
     json.dumps({"action": "shell", "cwd": "/tmp",
                 "command": 'git commit -m "fix: x\n\nCo-Authored-By: Claude"'}), REFUS),
]:
    obtenu = lancer(entree)
    if obtenu == attendu:
        print(f"  OK    {nom:<58} {NOMS[obtenu]}")
    else:
        print(f"  ECHEC {nom:<58} attendu={NOMS[attendu]} obtenu={NOMS.get(obtenu, obtenu)}")
        echecs += 1

print("=== aucun format d'agent dans le cœur ===")
fuites = [
    f"{f}:{n}" for f in sorted(os.listdir(os.path.join(REPO, "hooks"))) if f.endswith(".py")
    for n, ligne in enumerate(open(os.path.join(REPO, "hooks", f), encoding="utf-8"), 1)
    if any(k in ligne for k in ("tool_input", "hookSpecificOutput", "tool_name"))
]
if fuites:
    print("  ECHEC champs Claude dans hooks/ : " + ", ".join(fuites))
    echecs += 1
else:
    print("  OK    aucun tool_input, tool_name ni hookSpecificOutput")

print(f"{'✓' if echecs == 0 else '✗'} {echecs} échec(s).")
sys.exit(1 if echecs else 0)
