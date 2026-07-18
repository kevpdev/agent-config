#!/usr/bin/env bash
# regen-active-context.sh — Auto-update activeContext.md from sources of truth.
# Called by global SessionEnd hook. Silent when:
#   - memory-bank opted out (_claudeTeam.memoryBank="off" in settings.local.json)
#   - no memory-bank found in CWD
#   - CWD is inside the configured vault dir (_claudeTeam.vaultRoot, verbatim); the vault handles its own regen
# Also archives captures older than 7 days (short-term memory expiration).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/lib/common.sh"

# ── Guards ────────────────────────────────────────────────────────────────────

[ "$(claudeteam_config memoryBank)" = "off" ] && exit 0

MEMORY_DIR=$(find_memory_dir)
[ -z "$MEMORY_DIR" ] && exit 0

VAULT_ROOT=$(claudeteam_config vaultRoot)
VAULT_DIR="$VAULT_ROOT"
[ -n "$VAULT_ROOT" ] && [[ "$PWD" == "$VAULT_DIR"* ]] && exit 0   # vault handles it (only inside the vault dir)

ACTIVE="$MEMORY_DIR/activeContext.md"
[ -f "$ACTIVE" ] || exit 0

NOW=$(date +"%Y-%m-%d %H:%M")
TODAY=$(date +%Y-%m-%d)

# ── Collect Recent Changes from sources of truth ──────────────────────────────

recent=""

# From git log (level 2 → 3 promotion: commits from last 24h)
if git rev-parse --is-inside-work-tree &>/dev/null 2>&1; then
  git_log=$(git log --since=24h --oneline 2>/dev/null | head -5 || true)
  [ -n "$git_log" ] && recent+="$git_log"$'\n'
fi

# From today's captures (level 2)
CAPTURES_FILE="$MEMORY_DIR/captures/$TODAY.md"
if [ -f "$CAPTURES_FILE" ]; then
  captures=$(grep -v "^#" "$CAPTURES_FILE" 2>/dev/null | grep -v "^[[:space:]]*$" | head -5 || true)
  [ -n "$captures" ] && recent+="$captures"$'\n'
fi

# ── Archive captures > 7 days (short-term expiration) ────────────────────────

CAPTURES_DIR="$MEMORY_DIR/captures"
if [ -d "$CAPTURES_DIR" ]; then
  ARCHIVE_DIR="$CAPTURES_DIR/archived"
  while IFS= read -r -d '' capture_file; do
    fname=$(basename "$capture_file" .md)
    [[ "$fname" == "$TODAY" ]] && continue          # keep today
    [[ "$fname" == "archived" ]] && continue        # skip subdir

    # Check age (Linux/WSL2)
    file_epoch=$(date -d "$fname" +%s 2>/dev/null || echo "0")
    cutoff_epoch=$(date -d "7 days ago" +%s 2>/dev/null || echo "0")

    if [[ "$file_epoch" -gt 0 && "$file_epoch" -lt "$cutoff_epoch" ]]; then
      mkdir -p "$ARCHIVE_DIR"
      mv "$capture_file" "$ARCHIVE_DIR/"
    fi
  done < <(find "$CAPTURES_DIR" -maxdepth 1 -name "*.md" -print0 2>/dev/null)
fi

# ── Update activeContext.md (atomic write) ────────────────────────────────────

python3 - "$ACTIVE" "$NOW" "$recent" <<'PYEOF'
import sys, re, os, tempfile

path   = sys.argv[1]
now    = sys.argv[2]
recent = sys.argv[3].strip()

content = open(path, encoding='utf-8').read()

# Update timestamp
content = re.sub(r'^Last update:.*', f'Last update: {now}', content, flags=re.MULTILINE)

# Prepend to Recent Changes if anything to add
if recent:
    entry = '\n'.join(f'- {line}' for line in recent.splitlines() if line.strip())
    content = re.sub(
        r'(## Recent Changes\n)',
        lambda m: m.group(1) + entry + '\n',
        content
    )

with tempfile.NamedTemporaryFile('w', encoding='utf-8',
     dir=os.path.dirname(os.path.abspath(path)), delete=False, suffix='.tmp') as f:
    f.write(content)
    tmp = f.name
os.replace(tmp, path)
PYEOF

echo "✓ activeContext.md mis à jour ($ACTIVE)"
