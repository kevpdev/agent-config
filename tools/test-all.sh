#!/usr/bin/env bash
# test-all.sh — lance toutes les batteries du repo, une par une, et échoue si une seule échoue.
#
# POURQUOI CE SCRIPT
#   Les batteries vivent à trois endroits (tools/tests, wrappers/claude/hooks/tests,
#   wrappers/claude/scripts/tests). Lancées à la main, une batterie oubliée passe pour verte.
#   Ici, elles sont découvertes par leur nom `test-*`, et le nombre trouvé est affiché :
#   une batterie qui disparaît se voit au compte.
#
# Usage
#   bash tools/test-all.sh
set -uo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SORTIE="$(mktemp)"
trap 'rm -f "$SORTIE"' EXIT

total=0
echecs=0
while IFS= read -r t; do
    case "$t" in
        *.py) python3 "$t" > "$SORTIE" 2>&1 ;;
        *.sh) bash "$t" > "$SORTIE" 2>&1 ;;
        *) continue ;;
    esac
    rc=$?
    total=$((total + 1))
    if [ "$rc" -eq 0 ]; then
        echo "  ok    ${t#"$REPO"/}"
    else
        echecs=$((echecs + 1))
        echo "  FAIL  ${t#"$REPO"/} (code $rc)"
        tail -15 "$SORTIE" | sed 's/^/        /'
    fi
done < <(find "$REPO/tools/tests" "$REPO/wrappers/claude/hooks/tests" "$REPO/wrappers/claude/scripts/tests" \
    -maxdepth 1 -type f -name 'test-*' | sort)

if [ "$total" -eq 0 ]; then
    echo "✗ aucune batterie trouvée : l'instrument est cassé, pas le harnais." >&2
    exit 1
fi
echo "$([ "$echecs" -eq 0 ] && echo ✓ || echo ✗) $total batteries, $echecs en échec."
[ "$echecs" -eq 0 ]
