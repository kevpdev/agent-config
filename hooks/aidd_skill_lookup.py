"""aidd_skill_lookup — guard core, agent-neutral (contract in hooks/check.py).

Refuses a delivery gesture typed by hand in an AIDD repo when the session has
not invoked any AIDD skill. It reminds, it does not choose the skill: the
refusal names the intention, never a skill, because skill names drift
(rules/aidd.md is the rule, this is its deterministic half).

Perimeter, all three needed to refuse:
  1. the command runs `gh issue create`, `gh pr create`, `gh release create`
     or `git tag -a`. Each has a dedicated skill. `git commit` is left out on
     purpose: frequent, already guarded, and a guard that refuses valid work
     gets disabled.
  2. the event `cwd` holds an `aidd_docs/` (same signal as rules/aidd.md).
  3. `skills_used` holds no skill whose name starts with `aidd-`.

Way out: end the command with `# aidd-skip: <reason>`, which leaves the
justification in the transcript.

FAILS OPEN, and says so: this is a reminder, not a protection. `skills_used`
set to null means the adapter could not tell, and lets the command through.
Knowing which skills ran is the agent's business: the Claude adapter reads the
session transcript (wrappers/claude/hooks/claude_adapter.py).
"""

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




def decide(event: dict):
    """Reason to refuse this delivery gesture, or None to let it through."""
    command = event.get("command") or ""
    if event.get("action") != "shell":
        return None
    intention = gesture(command)
    if not intention or SKIP.search(command):
        return None
    cwd = event.get("cwd") or ""
    if not cwd or not os.path.isdir(os.path.join(cwd, "aidd_docs")):
        return None

    used = event.get("skills_used")
    if used is None:
        print("guard-aidd-skill-lookup: skills de la session inconnus, pas de verdict rendu.",
              file=sys.stderr)
        return None
    if any(str(name).startswith("aidd-") for name in used):
        return None
    return (
        "Repo AIDD, geste « %s » tapé à la main sans skill AIDD invoqué dans "
        "cette session (rules/aidd.md). Parcourir le catalogue de skills pour "
        "cette intention et invoquer celui dont le « Use when » couvre le "
        "geste. Si aucun ne convient, rejouer la commande terminée par "
        "`# aidd-skip: <raison>`." % intention
    )
