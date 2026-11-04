#!/usr/bin/env python3
"""Test suite of tools/measure-approvals.py, on hand-made transcripts.

Why this suite exists: the answer classifier is a set of regexes, and its calibration
errors were real ("oui, go" filed as a correction because of the comma, "c'est l'outil
phare" read as option C). Each case here pins one of them.

Exit: 0 when every case passes, 1 otherwise.
"""

from __future__ import annotations

import importlib.util
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location(
    "approvals", os.path.join(os.path.dirname(HERE), "measure-approvals.py")
)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
failures = 0


def check(name, got, expected):
    global failures
    if got == expected:
        print(f"ok    {name}")
    else:
        failures += 1
        print(f"FAIL  {name}: {got!r} instead of {expected!r}")


CASES = [
    ("oui", "Je pousse ?", m.BARE),
    ("oui, go", "Je pousse ?", m.BARE),
    ("oui commit", "Je commite ces deux fichiers ?", m.BARE),
    ("oui occupe toi de tout", "Je merge ?", m.BARE),
    ("Abandonner (Recommandé)", "Changement 4 ?", m.BARE),
    ("A, vas-y", "A ou B ?", m.BARE),
    ("oui ferme l'issue #12", "Je pousse ?", m.CORRECTED),
    ("c'est l'outil phare ?", "Je pousse ?", m.REDIRECT),
    ("tu preconise quoi ?", "Je pousse ou tu merges ?", m.REDIRECT),
]
for answer, question, expected in CASES:
    check(f"classify {answer!r}", m.classify(answer, question), expected)

check("push to default branch", "push to default branch" in m.patterns("je pousse sur main ?"), True)
check("draft PR pattern", m.patterns("j'ouvre la PR draft ?"), ["branch push or draft PR"])
check("question on the last line only", m.last_question("Fait ?\n\nVoilà."), None)

with tempfile.TemporaryDirectory() as tmp:
    claude = os.path.join(tmp, "s.jsonl")
    lines = [
        {"type": "assistant", "message": {"content": [{"type": "text", "text": "Fait.\n\nJe pousse ?"}]}},
        {"type": "user", "message": {"content": "oui"}},
        {"type": "assistant", "message": {"content": [{"type": "text", "text": "Je merge ?"}]}},
        {"type": "user", "message": {"content": [{"type": "tool_result", "content": "x"}]}},
        {"type": "user", "isMeta": True, "message": {"content": "meta"}},
        {"type": "user", "message": {"content": "<command-name>/compact</command-name>"}},
        {
            "type": "user",
            "toolUseResult": {"answers": {"Quelle option ?": "B (Recommandé)"}},
            "message": {"content": [{"type": "tool_result", "content": "x"}]},
        },
        {"type": "user", "message": {"content": "non, attends"}},
    ]
    with open(claude, "w") as f:
        f.write("\n".join(json.dumps(x) for x in lines))
    check(
        "Claude pairs",
        list(m.pairs(claude)),
        [("Je pousse ?", "oui"), ("Quelle option ?", "B (Recommandé)"), ("Je merge ?", "non, attends")],
    )

    opencode = os.path.join(tmp, "e.json")
    with open(opencode, "w") as f:
        json.dump(
            {
                "info": {},
                "messages": [
                    {"type": "assistant", "content": [{"type": "reasoning", "text": "?"}, {"type": "text", "text": "Je commite ?"}]},
                    {"type": "user", "text": "ok"},
                ],
            },
            f,
        )
    check("OpenCode pairs", list(m.pairs(opencode)), [("Je commite ?", "ok")])

sys.exit(1 if failures else 0)
