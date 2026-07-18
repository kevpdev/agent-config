#!/usr/bin/env bash
# common.sh — shared helpers for the claude-team config scripts. Source, do not execute.

# Resolve memory-bank directory for the current project.
# Prints the path if found, empty string if not.
find_memory_dir() {
  if [ -d ".ai-local/memory-bank" ]; then
    echo ".ai-local/memory-bank"
  elif [ -d ".claude/memory-bank" ]; then
    echo ".claude/memory-bank"
  else
    echo ""
  fi
}

# Resolve captures directory. Returns empty string if no memory-bank exists.
find_captures_dir() {
  local mem
  mem=$(find_memory_dir)
  if [ -n "$mem" ]; then
    echo "$mem/captures"
  else
    echo ""
  fi
}

# Read a _claudeTeam.<key> string value from ~/.claude/settings.local.json.
# Prints the value, or empty string if unset / file missing / unparseable.
# Used for local opt-out / opt-in flags (never tracked by the team repo).
claudeteam_config() {
  local key="$1"
  local cfg="$HOME/.claude/settings.local.json"
  [ -f "$cfg" ] || { echo ""; return 0; }
  CFG_PATH="$cfg" CFG_KEY="$key" python3 -c "
import os, sys, json
try:
    d = json.load(open(os.environ['CFG_PATH']))
except Exception:
    print(''); sys.exit(0)
v = d.get('_claudeTeam', {}).get(os.environ['CFG_KEY'], '')
print(v if v is not None else '')
" 2>/dev/null || echo ""
}
