#!/usr/bin/env python3
"""claude_adapter.py — Claude Code side of the guard core (hooks/).

The guard files next to this one are shims over `run(<guard>)`. This file
does the translation, and nothing in hooks/ knows Claude's payload:

  in   PreToolUse payload (`tool_name`, `tool_input`, `cwd`, `session_id`,
       `transcript_path`) → normalized event (contract in hooks/check.py)
  out  refusal reason → JSON on stdout, both decision shapes (see deny())

It also keeps what only exists under Claude Code:
  - `skills_used`, read from the session transcript, and only when the command
    is a delivery gesture: a transcript read on every Bash call costs for nothing.
  - the `skipDangerousModePermissionPrompt` check on the user-level settings.

Not linked by the manifest: a shim reached through ~/.claude/scripts/hooks/
resolves its own link, and finds this file and the repo from there.

Usage (by the shims): claude_adapter.py <guard>
"""

import json
import os
import re
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
sys.path.insert(0, REPO)

from hooks import GUARDS, aidd_skill_lookup, no_ai_in_commit  # noqa: E402

EDIT_TOOLS = {"Write": "file_path", "Edit": "file_path", "MultiEdit": "file_path",
              "NotebookEdit": "notebook_path"}

# Shown on stderr when the payload is unreadable. bash_tooling exits 2 there, so
# stderr reaches the agent: refusing would deny every tool call in the session,
# including the reads needed to diagnose it. The other guards stay silent and
# let the call through, as they did before the core existed.
LOUD_ON_BROKEN_PAYLOAD = {"bash_tooling"}


def normalize(payload):
    """PreToolUse payload → normalized event."""
    tool = payload.get("tool_name", "")
    ti = payload.get("tool_input") or {}
    event = {"event": "pre_tool", "action": "read", "command": "", "paths": [],
             "cwd": payload.get("cwd") or "", "session": payload.get("session_id") or "",
             "skills_used": None}
    if tool == "Bash":
        event["action"] = "shell"
        event["command"] = ti.get("command", "") or ""
    elif tool in EDIT_TOOLS:
        event["action"] = "edit"
        path = ti.get(EDIT_TOOLS[tool], "") or ""
        event["paths"] = [path] if path else []
    return event


def skills_used(path):
    """Names of the skills called in the transcript, or None if unreadable.

    Verified 2026-10-07: the PreToolUse payload carries `transcript_path`, and a
    skill call is a `tool_use` block named `Skill` with `input.skill` (e.g.
    `aidd-dev:01-plan`).
    """
    names = []
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
                    if (isinstance(block, dict) and block.get("type") == "tool_use"
                            and block.get("name") == "Skill"):
                        names.append(str((block.get("input") or {}).get("skill", "")))
        return names
    except OSError:
        return None


def git(target, *args):
    r = subprocess.run(["git", "-C", target, *args], capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def settings_ack_reason(event):
    """Refuse staging the personal bypass risk-ack into the TRACKED USER-LEVEL settings.

    Claude Code re-injects "skipDangerousModePermissionPrompt": true into
    ~/.claude/settings.json on bypass launch, and that file is a symlink into this
    repo, so the ack lands in a commit unless something stops it.

    WHAT PASSES, AND WHY IT MUST — measured in the binary on 2026-09-01:
      function lA(){return!!(_e("userSettings")?.skipDangerousModePermissionPrompt
        ||_e("localSettings")?....||_e("flagSettings")?....||_e("policySettings")?....)}
      Two facts follow. projectSettings is ABSENT, so the key is inert in a
      .claude/settings.json and only works from .claude/settings.local.json. And it
      is an OR, not a precedence chain, so a `false` cannot turn anything off — it
      is a sentinel that makes the tool's re-injection visible in `git diff`.
      Blocking `false`, or blocking a per-project opt-in, would therefore refuse
      valid work. A guard that refuses valid work gets switched off.

    Only acts when the commit targets the repo holding the user-level file.

    The user-level file is identified by RESOLVING ~/.claude/settings.json, not by
    listing paths. The file used to live in ~/.claude and now lives in agent-config
    (wrappers/claude/settings.json, reached by symlink); an enumeration of homes
    drifts, a property does not. The suffix test is the fallback for a machine
    where the symlink is not deployed yet — there the repo path is all there is.
    """
    cmd = event["command"]
    if event["action"] != "shell" or no_ai_in_commit.kind_of(cmd) != "commit":
        return None
    target = no_ai_in_commit.resolve_target(cmd, event["cwd"])
    user_settings = os.path.realpath(os.path.expanduser("~/.claude/settings.json"))
    toplevel = git(target, "rev-parse", "--show-toplevel").strip()
    if not toplevel:
        return None
    for f in git(target, "diff", "--cached", "--name-only").splitlines():
        if not re.search(r"(^|/)settings\.json$", f):
            continue
        real = os.path.realpath(os.path.join(toplevel, f))
        # Not the user-level file → a per-project setting, which is the owner's call.
        if real != user_settings and not real.endswith("/wrappers/claude/settings.json"):
            continue
        diff = git(target, "diff", "--cached", "--", f)
        if re.search(r'^\+.*"skipDangerousModePermissionPrompt"\s*:\s*true', diff, re.M):
            return (
                "Staged file " + f + " sets skipDangerousModePermissionPrompt to true in "
                "the user-level settings (the target of ~/.claude/settings.json). That is "
                "a personal bypass risk-ack the tool re-injects on every bypass launch; it "
                "must never land in a tracked user-level file. Unstage it with: git restore "
                "--staged " + f + "  — keep your worktree copy. To opt a project in, put "
                "the key in that project's .claude/settings.local.json instead: the key is "
                "read from localSettings, and is inert in a .claude/settings.json."
            )
    return None


def deny(reason):
    """Refuse the call.

    Emits BOTH decision shapes on purpose. `decision: "block"` is the older
    shape, and the installed version honours it — measured 2026-08-11 on the live
    session: a non-conformant `git commit` was refused and the reason came back to
    the agent. But it no longer appears in the published hooks reference, which
    documents hookSpecificOutput.permissionDecision instead. A guard whose refusal
    channel quietly stops being read fails OPEN — so carry both keys and let
    whichever the runtime reads do the refusing.
    """
    print(json.dumps({
        "decision": "block",
        "reason": reason,
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        },
    }))
    sys.exit(0)


def run(guard):
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw)
        if not isinstance(payload, dict):
            raise ValueError("not a JSON object")
    except ValueError as exc:
        if guard in LOUD_ON_BROKEN_PAYLOAD and raw.strip():
            print("%s: payload PreToolUse illisible (%s). Le garde ne peut rien juger : "
                  "vérifier le contrat de hook avant de continuer." % (guard, exc),
                  file=sys.stderr)
            sys.exit(2)
        print("%s: payload illisible, commande laissée passer." % guard, file=sys.stderr)
        sys.exit(0)

    event = normalize(payload)

    if guard == "aidd_skill_lookup" and aidd_skill_lookup.gesture(event["command"]):
        transcript = payload.get("transcript_path") or ""
        event["skills_used"] = skills_used(transcript) if transcript else None

    reason = settings_ack_reason(event) if guard == "no_ai_in_commit" else None
    reason = reason or GUARDS[guard].decide(event)
    if reason:
        deny(reason)
    sys.exit(0)


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in GUARDS:
        print("usage: claude_adapter.py {%s}" % ",".join(sorted(GUARDS)), file=sys.stderr)
        sys.exit(0)
    run(sys.argv[1])
