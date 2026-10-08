#!/usr/bin/env bash
# apply-ci-ruleset.sh — pose, sur un dépôt GitHub, le ruleset du contrat CI.
#
# Le ruleset protège la branche par défaut et n'exige que les contextes du contrat
# (`rules/references/ref-ci-github.md`) : `check`, `security`, et `e2e` avec --e2e.
# Il reprend les règles du ruleset de yt-transcriber : suppression et réécriture
# d'historique interdites, pull request obligatoire sans relecteur imposé.
#
# Usage
#   bash apply-ci-ruleset.sh OWNER/REPO [--e2e] [--dry-run]
#
# --dry-run affiche le JSON qui serait envoyé et n'écrit rien. Sans lui, le script
# met à jour le ruleset du même nom s'il existe, sinon le crée.
#
# ATTENTION : appliquer ce ruleset avant que les jobs aient rapporté leur nouveau nom
# sur une pull request bloque sa fusion. Voir « L'ordre pour changer des noms de job »
# dans la fiche.
set -euo pipefail

NAME="Protection de la branche par défaut"
REPO=""
E2E=0
DRY=0
for arg in "$@"; do
  case "$arg" in
    --e2e) E2E=1 ;;
    --dry-run) DRY=1 ;;
    -*) echo "option inconnue : $arg" >&2; exit 2 ;;
    *) REPO="$arg" ;;
  esac
done
[ -n "$REPO" ] || { echo "usage : $0 OWNER/REPO [--e2e] [--dry-run]" >&2; exit 2; }
command -v jq >/dev/null || { echo "jq manquant" >&2; exit 2; }

CONTEXTS='["check","security"]'
[ "$E2E" = 1 ] && CONTEXTS='["check","security","e2e"]'

PAYLOAD=$(jq -n --arg name "$NAME" --argjson contexts "$CONTEXTS" '{
  name: $name,
  target: "branch",
  enforcement: "active",
  conditions: {ref_name: {include: ["~DEFAULT_BRANCH"], exclude: []}},
  rules: [
    {type: "deletion"},
    {type: "non_fast_forward"},
    {type: "pull_request", parameters: {
      required_approving_review_count: 0,
      dismiss_stale_reviews_on_push: false,
      require_code_owner_review: false,
      require_last_push_approval: false,
      required_review_thread_resolution: false,
      allowed_merge_methods: ["merge", "squash", "rebase"]
    }},
    {type: "required_status_checks", parameters: {
      strict_required_status_checks_policy: false,
      required_status_checks: ($contexts | map({context: .}))
    }}
  ]
}')

if [ "$DRY" = 1 ]; then
  echo "$PAYLOAD"
  exit 0
fi

# Un ruleset existant est repéré par son nom. Celui de yt-transcriber, créé à la main
# avant ce script, s'appelle « Protection de la branche main » : on le met à jour sans le
# renommer.
EXISTING=$(gh api "repos/$REPO/rulesets" --jq \
  "[.[] | select(.name == \"$NAME\" or .name == \"Protection de la branche main\")][0] // empty | [.id, .name] | @tsv")

if [ -n "$EXISTING" ]; then
  ID=${EXISTING%%$'\t'*}
  KEPT=${EXISTING#*$'\t'}
  echo "$PAYLOAD" | jq --arg name "$KEPT" '.name = $name' \
    | gh api -X PUT "repos/$REPO/rulesets/$ID" --input - --jq '"mis à jour : \(.name) (\(.id))"'
else
  echo "$PAYLOAD" | gh api -X POST "repos/$REPO/rulesets" --input - --jq '"créé : \(.name) (\(.id))"'
fi
