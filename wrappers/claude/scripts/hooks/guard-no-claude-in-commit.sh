#!/usr/bin/env bash
# guard-no-claude-in-commit.sh — PreToolUse(Bash) hook for Claude Code
# Blocks git commit commands that:
#   1. include "Claude" or co-authorship mentions
#   2. do not follow Conventional Commits EN format
set -euo pipefail

payload=$(cat)

tool=$(printf "%s" "$payload" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('tool_name',''))" 2>/dev/null || echo "")
[ "$tool" != "Bash" ] && exit 0

cmd=$(printf "%s" "$payload" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('tool_input',{}).get('command',''))" 2>/dev/null || echo "")
cwd=$(printf "%s" "$payload" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('cwd',''))" 2>/dev/null || echo "")

# Detect a real `git ... commit` invocation, tolerating global options between
# `git` and the subcommand (e.g. `git -C <path> commit`, `git -c k=v commit`).
# A plain grep for "git commit" missed those forms and let them bypass the guard.
is_commit=$(printf "%s" "$cmd" | python3 -c "
import sys, shlex
cmd = sys.stdin.read()
try:
    toks = shlex.split(cmd)
except ValueError:
    toks = cmd.split()
TWO_ARG = {'-C','-c','--git-dir','--work-tree','--namespace','--exec-path'}
def is_git_commit(t):
    i, n = 0, len(t)
    while i < n:
        if t[i] == 'git':
            j = i + 1
            while j < n:
                if t[j] in TWO_ARG:
                    j += 2; continue
                if t[j].startswith('-'):
                    j += 1; continue
                break
            if j < n and t[j] == 'commit':
                return True
        i += 1
    return False
print('yes' if is_git_commit(toks) else 'no')
" 2>/dev/null || echo "no")
[ "$is_commit" != "yes" ] && exit 0

# Block staging the personal bypass risk-ack into the tracked team settings.json.
# Claude Code re-injects "skipDangerousModePermissionPrompt": true into
# ~/.claude/settings.json on bypass launch; it belongs in settings.local.json,
# never in the team file. Only acts when the commit targets the ~/.claude repo.
#
# Resolve the repo ACTUALLY targeted — independent of command shape or where
# git is run from: honor an explicit `-C <path>`, else a leading `cd <path>`,
# else the session CWD from the hook payload. Expand ~ and $HOME by substitution
# (never eval — the command is untrusted input).
target="$cwd"
if [[ "$cmd" =~ git[[:space:]]+-C[[:space:]]+([^[:space:]\;\&\|]+) ]]; then
  target="${BASH_REMATCH[1]}"
elif [[ "$cmd" =~ (^|[[:space:]\;\&\|])cd[[:space:]]+([^[:space:]\;\&\|]+) ]]; then
  target="${BASH_REMATCH[2]}"
fi
target="${target//\"/}"; target="${target//\'/}"
target="${target/#\~/$HOME}"
target="${target//\$\{HOME\}/$HOME}"
target="${target//\$HOME/$HOME}"
case "$target" in /*) ;; *) target="$cwd/$target" ;; esac

# Matched by FILENAME in the targeted repo, not by repo path. The file used to
# live in ~/.claude and now lives in agent-config (wrappers/claude/settings.json,
# reached by symlink); gating on "$HOME/.claude" meant the guard silently stopped
# covering it the day it moved. Same failure mode as listing hosts instead of
# resolving them: an enumeration of homes drifts, a property does not.
offender=""
while IFS= read -r f; do
  [ -z "$f" ] && continue
  if git -C "$target" diff --cached -- "$f" 2>/dev/null \
       | grep -qE "^\+.*skipDangerousModePermissionPrompt"; then
    offender="$f"
    break
  fi
done < <(git -C "$target" diff --cached --name-only 2>/dev/null \
           | grep -E '(^|/)settings\.json$' || true)

if [ -n "$offender" ]; then
  python3 -c "
import json, sys
p = sys.argv[1]
print(json.dumps({
    'decision': 'block',
    'reason': 'Staged file ' + p + ' adds skipDangerousModePermissionPrompt (a personal bypass risk-ack). It must never land in a tracked settings file. Unstage it with: git restore --staged ' + p + '  — keep your worktree copy, this key belongs in settings.local.json.'
}))
" "$offender"
  exit 0
fi

# Block Claude co-authorship mentions
if printf "%s" "$cmd" | grep -qiE "Co-Authored-By: Claude|claude sonnet|claude opus|claude haiku|noreply@anthropic"; then
  python3 -c "
import json
print(json.dumps({
    'decision': 'block',
    'reason': 'Claude mention detected in commit message. Convention: no Claude or Co-Authored-By references in commits. Remove and retry.'
}))
"
  exit 0
fi

# Extract the subject of the message THIS `git commit` will actually use.
#
# A bare search for `-m` over the whole command is wrong: the first `-m` does not
# necessarily belong to the commit. Measured 2026-07-30 — `git commit -F - <<'EOF'
# … EOF` followed by `git tag -m 'point de depart'` in the same command validated
# the TAG's message and blocked a perfectly conformant commit. A guard that
# refuses valid work is the kind that gets switched off.
#
# So: set heredoc bodies aside, isolate the shell segment carrying `git commit`,
# and read only that invocation's own arguments. Every ambiguity resolves to "no
# subject extracted" — fail-open, matching the intent stated below: this validates
# what it can read, it is not a gate that must have the last word.
msg=$(CMD="$cmd" python3 - <<'PY' 2>/dev/null || echo ""
import os, re, shlex

cmd = os.environ.get("CMD", "")

# 1. Lift heredoc bodies out. They hold free text, and a "&&" or ";" inside a
#    sentence would otherwise cut the command into bogus segments.
heredocs = {}
lines = cmd.split("\n")
kept, i = [], 0
while i < len(lines):
    kept.append(lines[i])
    # <<EOF, <<'EOF', <<"EOF", <<-MSG … first marker on the line only: two
    # heredocs opened by one line is exotic, and guessing there would cost more
    # than the fail-open it replaces.
    m = re.search(r"<<-?\s*(['\"]?)([A-Za-z_][A-Za-z0-9_]*)\1", lines[i])
    i += 1
    if m:
        delim, body = m.group(2), []
        while i < len(lines) and lines[i].strip() != delim:
            body.append(lines[i])
            i += 1
        i += 1  # skip the terminator line itself
        heredocs.setdefault(delim, "\n".join(body))
flat = "\n".join(kept)

# 2. Keep only the segment that carries the commit. Same token walk as the
#    detection above, so `git -C <path> commit` is recognized here too.
TWO_ARG = {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--exec-path"}

def commit_args(tokens):
    """Arguments of the `git … commit` invocation, or None if there is none."""
    for i, t in enumerate(tokens):
        if t != "git":
            continue
        j = i + 1
        while j < len(tokens):
            if tokens[j] in TWO_ARG:
                j += 2
            elif tokens[j].startswith("-"):
                j += 1
            else:
                break
        if j < len(tokens) and tokens[j] == "commit":
            return tokens[j + 1:]
    return None

args = None
for segment in re.split(r"&&|\|\||;|\||\n", flat):
    try:
        tokens = shlex.split(segment)
    except ValueError:
        tokens = segment.split()
    found = commit_args(tokens)
    if found is not None:
        args = found
        break

if args is None:
    print("")
    raise SystemExit(0)

# 3. Read the message from those arguments only.
subject, reads_stdin, k = "", False, 0
while k < len(args):
    a = args[k]
    if a in ("-m", "--message"):
        subject = args[k + 1] if k + 1 < len(args) else ""
        break
    if a.startswith("--message="):
        subject = a.split("=", 1)[1]
        break
    # Bundled short flags: `git commit -am "msg"` used to slip through entirely,
    # because the old regex required a standalone `-m`.
    if re.fullmatch(r"-[A-Za-z]*m", a):
        subject = args[k + 1] if k + 1 < len(args) else ""
        break
    if a in ("-F", "--file") and k + 1 < len(args) and args[k + 1] == "-":
        reads_stdin = True
    if a == "--file=-":
        reads_stdin = True
    k += 1

# A commit reading stdin takes the heredoc — but only when there is exactly one.
# With several, which one feeds the commit is a guess, and guessing here risks
# blocking on text that is not the commit message at all.
if not subject and reads_stdin and len(heredocs) == 1:
    subject = next(iter(heredocs.values()))

first = subject.strip().splitlines()
print(first[0].strip() if first else "")
PY
)

# Validate Conventional Commits EN format when extractable (fail-open if not).
# Applies to every repo, vault included: a vault commit is `<type>(<date>): <subject>`
# (e.g. docs(2026-07-23): import refs RAG). Only the <subject> may be French for the vault
# (personal FR notes) — the type/scope grammar is enforced identically everywhere.
if [ -n "$msg" ]; then
  if ! printf "%s" "$msg" | grep -qE "^(feat|fix|refactor|docs|test|chore|perf|ci)(\(.+\))?: .+"; then
    python3 -c "
import json
print(json.dumps({
    'decision': 'block',
    'reason': 'Commit message does not follow Conventional Commits EN format. Expected: <type>(<scope>): <subject>  — types: feat, fix, refactor, docs, test, chore, perf, ci. Example: feat(auth): add JWT refresh token support'
}))
"
    exit 0
  fi
fi

exit 0
