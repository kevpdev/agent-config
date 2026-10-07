#!/usr/bin/env bash
# Batterie de cas pour ../init-codegraph.py
#
# Usage : bash wrappers/claude/scripts/hooks/tests/test-init-codegraph.sh
# Sortie 0 si tous les cas passent, 1 sinon. Tout vit dans un dossier temporaire.
#
# Les cas tournent contre le vrai `codegraph` (pas un faux binaire) : le hook lance
# `codegraph init` detache, on attend donc l'apparition de `.codegraph/`.
# Les cas NEGATIFS pesent autant : un hook qui indexe un repo non voulu est desactive.

set -uo pipefail

ICI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK="$ICI/../init-codegraph.py"
ECHECS=0
[ -f "$HOOK" ] || { echo "hook introuvable : $HOOK" >&2; exit 1; }
command -v codegraph >/dev/null || { echo "codegraph absent du PATH" >&2; exit 1; }

T="$(mktemp -d)"; trap 'rm -rf "$T"' EXIT

lancer() { python3 -c "import json,sys; print(json.dumps({'cwd':sys.argv[1]}))" "$1" | python3 "$HOOK" >/dev/null 2>&1; }

attendre() { for _ in $(seq 1 50); do [ -f "$1/.codegraph/codegraph.db" ] && return 0; sleep 0.2; done; return 1; }

verifier() {
  local nom="$1" ok="$2"
  if [ "$ok" = "0" ]; then printf '  OK    %s\n' "$nom"; else printf '  ECHEC %s\n' "$nom"; ECHECS=$((ECHECS + 1)); fi
}

echo "=== Repo AIDD sans .codegraph : indexe ==="
mkdir -p "$T/neuf/aidd_docs"; echo 'print(1)' > "$T/neuf/a.py"
lancer "$T/neuf"
attendre "$T/neuf"; verifier "cree .codegraph/codegraph.db" $?
grep -qxF '.codegraph/' "$T/neuf/.gitignore"; verifier "cree .gitignore avec .codegraph/" $?

echo "=== .gitignore existant ==="
mkdir -p "$T/sansnl/aidd_docs"; printf 'dist/' > "$T/sansnl/.gitignore"
lancer "$T/sansnl"; attendre "$T/sansnl"
[ "$(cat "$T/sansnl/.gitignore")" = $'dist/\n.codegraph/' ]; verifier "ajoute apres une derniere ligne sans saut" $?

echo "=== Cas qui ne font rien ==="
mkdir -p "$T/sansaidd"; lancer "$T/sansaidd"; sleep 1
[ ! -e "$T/sansaidd/.codegraph" ] && [ ! -e "$T/sansaidd/.gitignore" ]; verifier "repo sans aidd_docs : intact" $?
mkdir -p "$T/deja/aidd_docs/../.codegraph"; lancer "$T/deja"; sleep 1
[ ! -e "$T/deja/.gitignore" ] && [ ! -e "$T/deja/.codegraph/codegraph.db" ]; verifier "deja indexe : intact" $?
echo 'pas du json' | python3 "$HOOK" >/dev/null 2>&1; verifier "payload illisible : sort 0" $?

echo
[ "$ECHECS" = "0" ] && echo "Tous les cas passent." || { echo "$ECHECS echec(s)."; exit 1; }
