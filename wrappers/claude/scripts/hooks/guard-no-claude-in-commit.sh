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

toplevel=$(git -C "$target" rev-parse --show-toplevel 2>/dev/null || true)

if [ "$toplevel" = "$HOME/.claude" ]; then
  if git -C "$HOME/.claude" diff --cached -- settings.json 2>/dev/null \
       | grep -qE "^\+.*skipDangerousModePermissionPrompt"; then
    python3 -c "
import json
print(json.dumps({
    'decision': 'block',
    'reason': 'settings.json is staged with skipDangerousModePermissionPrompt (a personal bypass risk-ack). It must never land in the tracked team file. Run: git restore --staged --worktree settings.json  — this key lives in settings.local.json.'
}))
"
    exit 0
  fi
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

# Extract first line of commit message (handles -m "msg" and heredoc patterns)
msg=$(printf "%s" "$cmd" | python3 -c "
import sys, re
cmd = sys.stdin.read()
# Match: -m \"message\" or -m 'message'
m = re.search(r\"-m\s+[\\\"'](.*?)[\\\"|']\", cmd)
if m:
    print(m.group(1).splitlines()[0].strip())
    sys.exit(0)
# Match heredoc: <<'EOF' ... EOF
m = re.search(r\"<<'?EOF'?\s*\n(.*?)\nEOF\", cmd, re.DOTALL)
if m:
    print(m.group(1).strip().splitlines()[0])
    sys.exit(0)
print('')
" 2>/dev/null || echo "")

# Validate Conventional Commits EN format when extractable (fail-open if not)
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
