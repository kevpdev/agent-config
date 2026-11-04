#!/usr/bin/env python3
"""measure-reference-loads.py — how often each on-demand reference gets read.

Why this tool exists (issue #90, proposal 5): a reference under rules/references/ is
loaded on demand. Its revision signal ("three sessions loading it in a month promote it to a
permanent rule") is dead without a counter, and a dead signal reads like a live one.

What it counts: every Read tool call whose file_path ends with rules/references/<name>.md,
in the main session transcripts and their subagent transcripts. One count per call, plus
the number of distinct sessions that made at least one. A subagent belongs to its parent
session.

What it drops: for a given reference, every session that also edits it (Edit or Write).
Those reads are maintenance, not use, and would push the promotion signal by themselves.

What it misses: a reference read through Bash (cat, sed) and OpenCode sessions.
Recalibrate on a reference known to be read before reading a zero.

Usage:
    python3 tools/measure-reference-loads.py SESSION.jsonl...
    python3 tools/measure-reference-loads.py --days 31
    python3 tools/measure-reference-loads.py --days 31 --ref ref-portes.md
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys
import time
from collections import Counter, defaultdict

REF = re.compile(r"rules/references/([^/]+\.md)$")


def reference_of(path: str) -> str | None:
    match = REF.search(path or "")
    return match.group(1) if match else None


def tool_calls(path: str):
    """Yield (tool name, reference name) for each tool call on a reference in one transcript."""
    with open(path, encoding="utf-8", errors="replace") as handle:
        for line in handle:
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue
            if entry.get("type") != "assistant":
                continue
            content = entry.get("message", {}).get("content")
            if not isinstance(content, list):
                continue
            for part in content:
                if not isinstance(part, dict) or part.get("type") != "tool_use":
                    continue
                name = reference_of(part.get("input", {}).get("file_path", ""))
                if name:
                    yield part.get("name"), name


def session_of(path: str) -> str:
    """A subagent transcript (<project>/<sid>/subagents/x.jsonl) belongs to <project>/<sid>."""
    parts = path.split(os.sep)
    if len(parts) >= 3 and parts[-2] == "subagents":
        return os.sep.join(parts[:-2])
    return path[: -len(".jsonl")] if path.endswith(".jsonl") else path


def recent(days: int) -> list[str]:
    cutoff = time.time() - days * 86400
    root = os.path.expanduser("~/.claude/projects")
    files = glob.glob(f"{root}/*/*.jsonl") + glob.glob(f"{root}/*/*/subagents/*.jsonl")
    return [f for f in files if os.path.getmtime(f) >= cutoff]


def count(files: list[str]) -> tuple[Counter, dict]:
    reads: dict = defaultdict(Counter)
    edited: dict = defaultdict(set)
    for path in files:
        session = session_of(path)
        for tool, name in tool_calls(path):
            if tool == "Read":
                reads[name][session] += 1
            elif tool in ("Edit", "Write"):
                edited[name].add(session)
    calls: Counter = Counter()
    sessions: dict = defaultdict(set)
    for name, per_session in reads.items():
        for session, n in per_session.items():
            if session in edited[name]:
                continue
            calls[name] += n
            sessions[name].add(session)
    return calls, sessions


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("files", nargs="*")
    parser.add_argument("--days", type=int)
    parser.add_argument("--ref", help="only this reference, e.g. ref-portes.md")
    args = parser.parse_args(argv)
    files = args.files or (recent(args.days) if args.days else [])
    if not files:
        parser.error("give transcripts or --days")
    calls, sessions = count(files)
    names = [args.ref] if args.ref else sorted(calls, key=lambda n: (-calls[n], n))
    print(f"{len({session_of(f) for f in files})} sessions read ({len(files)} transcripts)")
    if not names:
        print("no reference read outside the sessions that edit it")
    for name in names:
        print(f"{name}: {calls.get(name, 0)} loads in {len(sessions.get(name, ()))} sessions")
    return 0


if __name__ == "__main__":
    sys.exit(main())
