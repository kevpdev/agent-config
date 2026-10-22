#!/usr/bin/env python3
"""init-codegraph.py — SessionStart(startup) hook for Claude Code.

Indexes an AIDD repo with CodeGraph the first time a session opens in it, so
every new project gets the graph without a manual `codegraph init`.

Fires only when all three hold:
  1. the payload `cwd` holds an `aidd_docs/` (same signal as rules/aidd.md),
  2. it holds no `.codegraph/` yet (an indexed repo is left alone),
  3. `codegraph` is on PATH.

It then makes sure the root `.gitignore` lists `.codegraph/`, and starts
`codegraph init` detached so a large repo never delays the session.

Existing repos are not covered on purpose: they get one explicit pass, not a
surprise index on their next session.

FAILS OPEN: a bad payload, a missing binary or a write error ends the hook
silently with exit 0, because a hook that breaks session start gets disabled.
"""

import json
import os
import shutil
import subprocess
import sys

IGNORE_LINE = ".codegraph/"


def ensure_ignored(cwd):
    path = os.path.join(cwd, ".gitignore")
    try:
        with open(path, encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        text = ""
    if IGNORE_LINE in (line.strip() for line in text.splitlines()):
        return
    sep = "" if text == "" or text.endswith("\n") else "\n"
    with open(path, "a", encoding="utf-8") as f:
        f.write(f"{sep}{IGNORE_LINE}\n")


def main():
    try:
        cwd = json.load(sys.stdin).get("cwd") or os.getcwd()
    except (ValueError, OSError):
        return 0
    if not os.path.isdir(os.path.join(cwd, "aidd_docs")):
        return 0
    if os.path.exists(os.path.join(cwd, ".codegraph")):
        return 0
    binary = shutil.which("codegraph")
    if not binary:
        return 0
    try:
        ensure_ignored(cwd)
        subprocess.Popen(
            [binary, "init"],
            cwd=cwd,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
    except OSError:
        return 0
    print("CodeGraph: première session dans ce repo AIDD, `codegraph init` lancé en arrière-plan.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
