#!/usr/bin/env python3
"""guard-aidd-skill-lookup.py — PreToolUse(Bash) hook for Claude Code.

Refuses a delivery gesture typed by hand in an AIDD repo when the session has
not invoked any AIDD skill. It reminds, it does not choose the skill: the
refusal names the intention, never a skill, because skill names drift
(rules/aidd.md is the rule, this is its deterministic half).

Perimeter, all three needed to refuse:
  1. the command runs `gh issue create`, `gh pr create`, `gh release create`
     or `git tag -a`. Each has a dedicated skill. `git commit` is left out on
     purpose: frequent, already guarded, and a guard that refuses valid work
     gets disabled.
  2. the payload `cwd` holds an `aidd_docs/` (same signal as rules/aidd.md).
  3. the session transcript holds no `Skill` call whose name starts with `aidd-`.

Way out: end the command with `# aidd-skip: <reason>`, which leaves the
justification in the transcript.

FAILS OPEN, and says so: this is a reminder, not a protection. An unreadable
payload or transcript lets the command through.

Verified 2026-10-07: the PreToolUse payload carries `transcript_path`, `cwd`
and `session_id` (probe with `claude -p --settings`), and a skill call is a
`tool_use` block named `Skill` with `input.skill` (e.g. `aidd-dev:01-plan`).
"""

import json
import os
import re
import shlex
import sys

SKIP = re.compile(r"#\s*aidd-skip:\s*\S")
HEREDOC = re.compile(r"<<-?\s*(['\"]?)(\w+)\1")
GIT_TWO_ARG = {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--exec-path"}

# (gesture, intention) — the intention is what the refusal names.
GH_GESTURES = {
    ("issue", "create"): "produit et backlog",
    ("pr", "create"): "versionner et livrer",
    ("release", "create"): "versionner et livrer",
}


def strip_heredocs(command):
    """Drop heredoc bodies: they are prose, never a command."""
    out, end = [], None
    for line in command.split("\n"):
        if end is not None:
            if line.strip() == end:
                end = None
            continue
        out.append(line)
        m = HEREDOC.search(line)
        if m:
            end = m.group(2)
    return "\n".join(out)


def gesture(command):
    """Return the intention of a delivery gesture in `command`, else None."""
    text = strip_heredocs(command)
    try:
        toks = shlex.split(text)
    except ValueError:
        toks = text.split()
    for i, t in enumerate(toks):
        if t == "gh" and i + 2 < len(toks):
            key = (toks[i + 1], toks[i + 2])
            if key in GH_GESTURES:
                return GH_GESTURES[key]
        if t == "git":
            j = i + 1
            while j < len(toks):
                if toks[j] in GIT_TWO_ARG:
                    j += 2
                elif toks[j].startswith("-"):
                    j += 1
                else:
                    break
            if j < len(toks) and toks[j] == "tag" and "-a" in toks[j + 1:]:
                return "versionner et livrer"
    return None


def used_aidd_skill(path):
    """True if the transcript holds a Skill call named aidd-*. None if unreadable."""
    try:
        with open(path, encoding="utf-8", errors="ignore") as fh:
            for line in fh:
                if '"Skill"' not in line:
                    continue
                try:
                    content = (json.loads(line).get("message") or {}).get("content")
                except ValueError:
                    continue
                if not isinstance(content, list):
                    continue
                for block in content:
                    if (
                        isinstance(block, dict)
                        and block.get("type") == "tool_use"
                        and block.get("name") == "Skill"
                        and str((block.get("input") or {}).get("skill", "")).startswith("aidd-")
                    ):
                        return True
        return False
    except OSError:
        return None


def deny(intention):
    reason = (
        "Repo AIDD, geste « %s » tapé à la main sans skill AIDD invoqué dans "
        "cette session (rules/aidd.md). Parcourir le catalogue de skills pour "
        "cette intention et invoquer celui dont le « Use when » couvre le "
        "geste. Si aucun ne convient, rejouer la commande terminée par "
        "`# aidd-skip: <raison>`." % intention
    )
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        },
    }))
    sys.exit(0)


def main():
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw)
        if payload.get("tool_name") != "Bash":
            sys.exit(0)
        command = (payload.get("tool_input") or {}).get("command", "") or ""
        cwd = payload.get("cwd") or ""
        transcript = payload.get("transcript_path") or ""
    except (ValueError, AttributeError):
        print("guard-aidd-skill-lookup: payload illisible, commande laissée passer.",
              file=sys.stderr)
        sys.exit(0)

    intention = gesture(command)
    if not intention or SKIP.search(command):
        sys.exit(0)
    if not cwd or not os.path.isdir(os.path.join(cwd, "aidd_docs")):
        sys.exit(0)

    used = used_aidd_skill(transcript) if transcript else None
    if used is None:
        print("guard-aidd-skill-lookup: transcript illisible, pas de verdict rendu.",
              file=sys.stderr)
        sys.exit(0)
    if not used:
        deny(intention)
    sys.exit(0)


if __name__ == "__main__":
    main()
