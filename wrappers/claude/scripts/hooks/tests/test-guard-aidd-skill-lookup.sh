#!/usr/bin/env bash
# Batterie de cas pour ../guard-aidd-skill-lookup.py
#
# Usage : bash wrappers/claude/scripts/hooks/tests/test-guard-aidd-skill-lookup.sh
# Sortie 0 si tous les cas passent, 1 sinon. Tout vit dans un dossier temporaire.
#
# Les cas POSITIFS sont fabriques : `gh issue create` n'apparait que dans 1 session
# sur 36 du corpus (mesure du 2026-10-07), aucun trafic reel ne calibre le garde.
# Les cas NEGATIFS pesent autant : un garde qui refuse un travail valide est desactive.
# Seule la DECISION est verifiee (bloque / passe), pas le libelle.

set -uo pipefail

ICI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK="$ICI/../guard-aidd-skill-lookup.py"
ECHECS=0
[ -f "$HOOK" ] || { echo "garde introuvable : $HOOK" >&2; exit 1; }

T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT
mkdir -p "$T/aidd/aidd_docs" "$T/plain"
SANS="$T/sans-skill.jsonl"; AVEC="$T/avec-skill.jsonl"; AUTRE="$T/autre-skill.jsonl"
echo '{"message":{"content":[{"type":"text","text":"hello"}]}}' > "$SANS"
echo '{"message":{"content":[{"type":"tool_use","name":"Skill","input":{"skill":"aidd-vcs:04-issue-create"}}]}}' > "$AVEC"
echo '{"message":{"content":[{"type":"tool_use","name":"Skill","input":{"skill":"mermaid-craft"}}]}}' > "$AUTRE"

verifier() {
  local nom="$1" attendu="$2" commande="$3" cwd="${4:-$T/aidd}" transcript="${5:-$SANS}"
  local sortie obtenu
  sortie=$(python3 -c "
import json, sys
print(json.dumps({'tool_name':'Bash','cwd':sys.argv[2],'transcript_path':sys.argv[3],
                  'tool_input':{'command':sys.argv[1]}}))
" "$commande" "$cwd" "$transcript" | python3 "$HOOK" 2>/dev/null)
  obtenu="PASSE"
  printf '%s' "$sortie" | grep -q '"permissionDecision": "deny"' && obtenu="BLOQUE"
  if [ "$obtenu" = "$attendu" ]; then
    printf '  OK    %-52s %s\n' "$nom" "$obtenu"
  else
    printf '  ECHEC %-52s attendu=%s obtenu=%s\n' "$nom" "$attendu" "$obtenu"
    ECHECS=$((ECHECS + 1))
  fi
}

echo "=== Gestes sans skill, repo AIDD : refus ==="
verifier "gh issue create"            BLOQUE 'gh issue create --title "x" --body-file b.md'
verifier "gh pr create"               BLOQUE 'gh pr create --fill'
verifier "gh release create"          BLOQUE 'gh release create v1.0.0'
verifier "git tag -a"                 BLOQUE 'git tag -a v1.0.0 -m "release"'
verifier "git -C ... tag -a"          BLOQUE 'git -C /tmp/x tag -a v1 -m r'
verifier "enchaine apres &&"          BLOQUE 'cd /tmp && gh issue create --title x'
verifier "skill non AIDD invoque"     BLOQUE 'gh issue create --title x' "$T/aidd" "$AUTRE"

echo
echo "=== Les sorties de secours : passe ==="
verifier "skill aidd- dans le transcript" PASSE 'gh issue create --title x' "$T/aidd" "$AVEC"
verifier "# aidd-skip: raison"            PASSE 'gh issue create --title x # aidd-skip: aucun skill ne couvre ce cas'
verifier "repo sans aidd_docs"            PASSE 'gh issue create --title x' "$T/plain"

echo
echo "=== Hors perimetre : passe, sinon le garde sera desactive ==="
verifier "gh issue list"              PASSE 'gh issue list'
verifier "gh pr view"                 PASSE 'gh pr view 3'
verifier "gh issue edit"              PASSE 'gh issue edit 4 --body-file b.md'
verifier "git commit"                 PASSE 'git commit -m "feat(x): y"'
verifier "git tag -l"                 PASSE 'git tag -l'
verifier "gesture citee dans un message" PASSE 'git commit -m "docs: mention gh issue create"'
verifier "gesture dans un corps heredoc" PASSE "$(printf "git commit -F - <<'EOF'\ndocs(x): y\n\nne plus lancer gh issue create a la main\nEOF")"

echo
echo "=== Echec ouvert : passe ==="
verifier "transcript absent"          PASSE 'gh issue create --title x' "$T/aidd" "$T/nexiste-pas.jsonl"
out=$(printf 'pas du json' | python3 "$HOOK" 2>/dev/null); rc=$?
if [ $rc -eq 0 ] && [ -z "$out" ]; then echo "  OK    payload casse                                        PASSE"
else echo "  ECHEC payload casse"; ECHECS=$((ECHECS + 1)); fi

echo
[ "$ECHECS" -eq 0 ] && echo "Tous les cas passent." || echo "$ECHECS cas en echec."
[ "$ECHECS" -eq 0 ]
