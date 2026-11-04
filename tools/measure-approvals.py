#!/usr/bin/env python3
"""measure-approvals.py — which approval questions get a bare "yes".

Why this tool exists (issue #90): the agent ends its turns with "je pousse ?",
"je pars sur ça ?". A question that always gets "oui" costs a round trip and brings
nothing. This script counts, per action pattern, the share of bare yeses.

What it counts: the last line of the agent's last text before a user message, when it
ends with "?", plus the answers to AskUserQuestion. Each answer gets one of three classes:
  - "bare yes": oui, ok, vas-y..., a yes that only repeats the question's words
    ("oui commit" after "je commite ?"), or the recommended option;
  - "yes + correction": a yes followed by something else;
  - "redirect": anything else, most often another question.

What it misses: a question asked in the middle of a turn. A bare yes does not prove the
question was useless; the rate is a hint, reading the sessions decides.

Calibration (2026-11-03): on the #73 session, 18 questions found, 11 bare yeses, matching
the hand count. Recalibrate before reading a zero.

Usage:
    python3 tools/measure-approvals.py SESSION.jsonl...       Claude Code transcripts
    python3 tools/measure-approvals.py EXPORT.json...         OpenCode exports made by
                                                                tools/session-export.py
    python3 tools/measure-approvals.py --days 30              all of ~/.claude/projects
    python3 tools/measure-approvals.py --detail FILES...      each question and its answer
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

YES = re.compile(
    r"^(oui|ouais|yes|ok|okay|go|vas-y|vas y|d'accord|daccord|enchaine|enchaîne|"
    r"parfait|top|valide|validé|let's go|fais-le|fais le|continue|c'est bon|[a-d](?=[\s,.!]|$))",
    re.I,
)
FILLER = re.compile(
    r"^(oui|ouais|ok|okay|go|vas-y|vas|y|fais|le|la|ça|ca|c'est|bon|parfait|top|enchaine|"
    r"enchaîne|lance|continue|d'accord|yes|let's|on|va|tout|occupe|toi|de|merci|super|nickel)$",
    re.I,
)

BARE, CORRECTED, REDIRECT = "bare yes", "yes + correction", "redirect"

PATTERNS = [
    ("je pars sur ça", r"^(je pars sur|on part sur) (ça|cette|ce|le|la|les)"),
    ("push to default branch", r"(pousse|push)[^?]*\b(main|master|develop)\b"),
    ("branch push or draft PR", r"(pousse|push)[^?]*(branche|pr draft)|pr draft"),
    ("commit", r"commit"),
    ("merge", r"\bmerg|fusionne"),
    ("bascule", r"bascule"),
    ("cleanup after merge", r"supprim[^?]*(worktree|branche)|worktree[^?]*supprim"),
    ("next step of a plan", r"(phase|étape|tâche|lot|changement) (\d|suivant|deux|trois)"),
    ("read only", r"(surveille|regarde|vérifie|je lis|je relis|je mesure|je compte)"),
    ("issue creation", r"(crée|ouvre|j'ouvre|je crée)[^?]*issue"),
]


def text_of(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(
            x.get("text", "") for x in content if isinstance(x, dict) and x.get("type") == "text"
        )
    return ""


def last_question(text: str) -> str | None:
    lines = [l.strip() for l in text.strip().splitlines() if l.strip()]
    if not lines:
        return None
    return lines[-1] if lines[-1].rstrip("*_ `").endswith("?") else None


def is_human(text: str) -> bool:
    return bool(text) and not text.startswith(
        ("<", "/", "This session is being continued", "[Request interrupted")
    )


def classify(answer: str, question: str = "") -> str:
    answer = answer.strip()
    if "(Recommand" in answer:
        return BARE
    if not YES.match(answer):
        return REDIRECT
    words = [w.strip("!.,;:'") for w in re.findall(r"[\w'-]+", answer.lower())]
    words = [w for w in words if w]
    asked = {w[:4] for w in re.findall(r"\w+", question.lower()) if len(w) > 2}
    rest = [w for w in words if not FILLER.match(w)]
    if len(words) <= 8 and all(len(w) <= 2 or w[:4] in asked for w in rest):
        return BARE
    return CORRECTED


def patterns(question: str) -> list[str]:
    q = question.lower()
    return [name for name, rx in PATTERNS if re.search(rx, q)] or ["other"]


def claude_pairs(path: str):
    """(question, answer) pairs of a Claude Code transcript."""
    last = ""
    with open(path, errors="ignore") as f:
        for line in f:
            try:
                d = json.loads(line)
            except json.JSONDecodeError:
                continue
            if d.get("type") == "assistant":
                t = text_of(d.get("message", {}).get("content"))
                if t.strip():
                    last = t
                continue
            if d.get("type") != "user" or d.get("isMeta"):
                continue
            result = d.get("toolUseResult")
            if isinstance(result, dict) and isinstance(result.get("answers"), dict):
                for q, a in result["answers"].items():
                    yield q, str(a)
                continue
            c = d.get("message", {}).get("content")
            if isinstance(c, list) and any(isinstance(x, dict) and x.get("type") == "tool_result" for x in c):
                continue
            t = text_of(c).strip()
            if not is_human(t):
                continue
            q = last_question(last)
            if q:
                yield q, t
            last = ""


def opencode_pairs(path: str):
    """(question, answer) pairs of a JSON export made by tools/session-export.py."""
    with open(path, errors="ignore") as f:
        d = json.load(f)
    last = ""
    for m in d.get("messages", []):
        if m.get("type") == "assistant":
            t = text_of(m.get("content"))
            if t.strip():
                last = t
        elif m.get("type") == "user":
            t = (m.get("text") or "").strip()
            if not is_human(t):
                continue
            q = last_question(last)
            if q:
                yield q, t
            last = ""


def pairs(path: str):
    return opencode_pairs(path) if path.endswith(".json") else claude_pairs(path)


def recent(days: int) -> list[str]:
    limit = time.time() - days * 86400
    base = os.path.expanduser("~/.claude/projects")
    return [p for p in glob.glob(os.path.join(base, "*", "*.jsonl")) if os.path.getmtime(p) >= limit]


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("files", nargs="*")
    p.add_argument("--days", type=int, help="every Claude Code transcript of the last N days")
    p.add_argument("--detail", action="store_true")
    a = p.parse_args(argv)
    files = list(a.files) + (recent(a.days) if a.days else [])
    if not files:
        p.error("no file")

    table = defaultdict(Counter)
    per_session = Counter()
    total = 0
    for f in files:
        for q, ans in pairs(f):
            cls = classify(ans, q)
            total += 1
            if cls == BARE:
                per_session[f] += 1
            for name in patterns(q):
                table[name][cls] += 1
            if a.detail:
                print(f"[{'|'.join(patterns(q))}] {cls}\n  Q: {q[:160]}\n  A: {ans[:120]!r}")

    print(f"\n{len(files)} sessions, {total} questions")
    print(f"{'pattern':32}{'total':>6}{'bare':>7}{'+corr':>7}{'redir':>7}  bare share")
    for name, c in sorted(table.items(), key=lambda kv: -sum(kv[1].values())):
        t = sum(c.values())
        print(f"{name:32}{t:6}{c[BARE]:7}{c[CORRECTED]:7}{c[REDIRECT]:7}  {100 * c[BARE] // t:3d} %")
    if len(files) > 1 and per_session:
        print("\nsessions with the most bare yeses:")
        for f, n in per_session.most_common(5):
            print(f"  {n:3}  {f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
