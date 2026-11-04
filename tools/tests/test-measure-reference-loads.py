#!/usr/bin/env python3
"""Test suite of tools/measure-reference-loads.py, on hand-made transcripts.

Why this suite exists: the counter is the revision signal of ref-portes.md. A counter
that silently returns zero would make the signal look alive while it is dead.

Exit: 0 when every case passes, 1 otherwise.
"""

from __future__ import annotations

import importlib.util
import io
import json
import os
import shutil
import sys
import tempfile
from contextlib import redirect_stdout

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location(
    "loads", os.path.join(os.path.dirname(HERE), "measure-reference-loads.py")
)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
failures = 0


def check(name, got, expected):
    global failures
    if got == expected:
        print(f"  ok    {name}")
    else:
        failures += 1
        print(f"  FAIL  {name}: got {got!r}, expected {expected!r}")


def tool_use(name, **inputs):
    return {"type": "assistant", "message": {"content": [
        {"type": "tool_use", "name": name, "input": inputs}]}}


def transcript(path, entries):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        for entry in entries:
            handle.write(json.dumps(entry) + "\n")
        handle.write("not json\n")
    return path


HOME = tempfile.mkdtemp()
PROJECTS = os.path.join(HOME, ".claude", "projects", "-repo")
REPO = "/home/u/agent-config"
PORTES = f"{REPO}/rules/references/ref-portes.md"

a = transcript(f"{PROJECTS}/sa.jsonl", [
    tool_use("Read", file_path=PORTES),
    tool_use("Read", file_path=PORTES, offset=10),
    tool_use("Read", file_path=f"{REPO}/rules/intention.md"),
    tool_use("Bash", command=f"cat {PORTES}"),
    {"type": "user", "message": {"content": "rules/references/ref-portes.md"}},
])
a_sub = transcript(f"{PROJECTS}/sa/subagents/agent-1.jsonl", [
    tool_use("Read", file_path=PORTES),
])
b = transcript(f"{PROJECTS}/sb.jsonl", [
    tool_use("Read", file_path="/other/worktree/rules/references/ref-portes.md"),
    tool_use("Read", file_path=f"{REPO}/rules/references/ref-aidd.md"),
])
c = transcript(f"{PROJECTS}/sc.jsonl", [
    tool_use("Read", file_path=PORTES),
])
c_sub = transcript(f"{PROJECTS}/sc/subagents/agent-2.jsonl", [
    tool_use("Edit", file_path=PORTES, old_string="x", new_string="y"),
])

calls, sessions = m.count([a, a_sub, b, c, c_sub])
check("Read calls are summed across sessions, subagents included", calls["ref-portes.md"], 4)
check("a subagent counts in its parent session", len(sessions["ref-portes.md"]), 2)
check("a session that edits the reference is dropped for it",
      m.session_of(c) in sessions["ref-portes.md"], False)
check("a loaded rule outside references is ignored", "intention.md" in calls, False)
check("another reference has its own count", calls["ref-aidd.md"], 1)
check("reference_of rejects a nested path", m.reference_of("rules/references/x/y.md"), None)

os.environ["HOME"] = HOME
check("recent finds main and subagent transcripts", sorted(m.recent(1)),
      sorted([a, a_sub, b, c, c_sub]))

out = io.StringIO()
with redirect_stdout(out):
    m.main(["--days", "1", "--ref", "ref-absent.md"])
lines = out.getvalue().splitlines()
check("--days reports sessions, not transcripts", lines[0], "3 sessions read (5 transcripts)")
check("an absent reference prints an explicit zero", lines[-1], "ref-absent.md: 0 loads in 0 sessions")

shutil.rmtree(HOME)
sys.exit(1 if failures else 0)
