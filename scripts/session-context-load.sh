#!/usr/bin/env bash
# session-context-load.sh — SessionStart hook for Claude Code
# Two-branch context injection, both driven by local config (settings.local.json):
#   - vault   : opt-in. Set _claudeTeam.vaultRoot to the vault dir itself. Fires ONLY when CWD
#               is inside that dir → reads its HOME.md. The path is taken verbatim from config,
#               no folder name is appended. Scope: outside the vault dir, NO vault injection.
#   - memory-bank : ON by default. Set _claudeTeam.memoryBank="off" to opt out
#                   (for devs with their own memory system). Reads .ai-local/memory-bank/.
# Silent (exit 0) when no context source applies — safe on any project, any OS.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib/common.sh"

VAULT_ROOT=$(claudeteam_config vaultRoot)
VAULT_DIR="$VAULT_ROOT"
VAULT_HOME="$VAULT_DIR/HOME.md"

inject_context() {
  python3 -c "
import sys, json
ctx = sys.stdin.read()
print(json.dumps({
    'hookSpecificOutput': {
        'hookEventName': 'SessionStart',
        'additionalContext': ctx.strip()
    }
}))
" <<< "$1"
}

# ── Branch vault (opt-in via _claudeTeam.vaultRoot) ────────────────────────────

if [ -n "$VAULT_ROOT" ] && [[ "$PWD" == "$VAULT_DIR"* ]]; then
  [ -f "$VAULT_HOME" ] || exit 0

  sprint=$(awk '/^## Sprint actif/{found=1; next} found && /^## /{exit} found && /\[\[/{
    line=$0; gsub(/.*\[\[[^|]*\|/, "", line); gsub(/\]\].*/, "", line); print line; exit
  }' "$VAULT_HOME" 2>/dev/null || true)

  projects=$(awk '/^## Projets actifs/{found=1; next} found && /^## /{exit} found && /\[\[/{
    line=$0; gsub(/.*\[\[[^|]*\\\|/, "", line); gsub(/\]\].*/, "", line); names[++n]=line
  } END {
    for(i=1;i<=n;i++) printf "%s%s", names[i], (i<n?", ":"")
  }' "$VAULT_HOME" 2>/dev/null || true)

  blocker_count=$(awk '/^## Blockers/{found=1; next} found && /^## /{exit} found && /\[\[/{c++} END{print c+0}' "$VAULT_HOME" 2>/dev/null || echo "0")

  inbox_line=$(awk '/^## INBOX/{found=1; next} found && /^## /{exit} found && /[^[:space:]]/{print; exit}' "$VAULT_HOME" 2>/dev/null || true)

  [ -z "$sprint" ] && [ -z "$projects" ] && exit 0

  context="[Vault — HOME.md]"$'\n'
  [ -n "$sprint" ]        && context+="Sprint : $sprint"$'\n'
  [ -n "$projects" ]      && context+="Projets actifs : $projects"$'\n'
  context+="Blockers : $blocker_count"$'\n'
  [ -n "$inbox_line" ]    && context+="INBOX : $inbox_line"$'\n'

  # Dernier recap de session (continuité inter-sessions)
  # Extrait le dernier bloc "## HH:MM — Session" du fichier le plus récent.
  SESSIONS_DIR="$VAULT_DIR/scripts/logs/sessions"
  TODAY_D=$(date +%Y-%m-%d)
  recent_recap=""
  [ -f "$SESSIONS_DIR/$TODAY_D.md" ] && recent_recap="$SESSIONS_DIR/$TODAY_D.md"
  if [ -z "$recent_recap" ] && [ -d "$SESSIONS_DIR" ]; then
    recent_recap=$(find "$SESSIONS_DIR" -maxdepth 1 -name "*.md" -type f 2>/dev/null | sort -r | head -1 || true)
  fi
  if [ -n "$recent_recap" ]; then
    recap_date=$(basename "$recent_recap" .md)
    # Garde uniquement le dernier bloc "## HH:MM" jusqu'à EOF
    recap_content=$(awk '
      /^## [0-9]{2}:[0-9]{2}/ { buf = ""; in_block = 1 }
      in_block { buf = buf $0 "\n" }
      END { printf "%s", buf }
    ' "$recent_recap" 2>/dev/null || true)
    if [ -n "$recap_content" ]; then
      context+="---"$'\n'
      context+="[Dernier recap — $recap_date]"$'\n'
      context+="$recap_content"
    fi
  fi

  inject_context "$context"
  exit 0
fi

# ── Branch memory bank (ON par défaut, opt-out _claudeTeam.memoryBank="off") ───

[ "$(claudeteam_config memoryBank)" = "off" ] && exit 0

MEMORY_DIR=$(find_memory_dir)
[ -z "$MEMORY_DIR" ] && exit 0

ACTIVE="$MEMORY_DIR/activeContext.md"
[ -f "$ACTIVE" ] || exit 0

focus=$(awk '/^## Current Focus/{found=1; next} found && /^## /{exit} found && /[^[:space:]]/{print; exit}' "$ACTIVE" 2>/dev/null || true)
next=$(awk '/^## Next Steps/{found=1; next} found && /^## /{exit} found && /[^[:space:]]/{print}' "$ACTIVE" 2>/dev/null | head -5 || true)

[ -z "$focus" ] && [ -z "$next" ] && exit 0

context="[Contexte de session chargé depuis $ACTIVE]"$'\n'
[ -n "$focus" ] && context+="Focus actuel : $focus"$'\n'
if [ -n "$next" ]; then
  context+="Prochaines étapes :"$'\n'
  while IFS= read -r line; do
    context+="  $line"$'\n'
  done <<< "$next"
fi

# Append today's captures (short-term memory — level 2)
TODAY=$(date +%Y-%m-%d)
CAPTURES_FILE="$MEMORY_DIR/captures/$TODAY.md"
if [ -f "$CAPTURES_FILE" ]; then
  context+="Captures du jour :"$'\n'
  while IFS= read -r line; do
    [[ "$line" =~ ^# ]]      && continue
    [[ -z "${line// }" ]]    && continue
    context+="  $line"$'\n'
  done < "$CAPTURES_FILE"
fi

inject_context "$context"
