#!/usr/bin/env bash
# apply-ci-ruleset.sh — pose, sur un dépôt GitHub, le ruleset du contrat CI, ou vérifie celui qui y est.
#
# Le ruleset protège la branche par défaut, plus chaque branche passée par --branch, et n'exige qu'un contexte, la porte `ci`
# (`rules/references/ref-ci-github.md`), qui attend tous les autres jobs de son workflow.
# Il exige aussi une PR à jour de sa branche cible (`strict`) : deux PR mergées en parallèle
# peuvent casser la branche sans conflit textuel, chacune ayant un `ci` vert calculé sans l'autre.
# Il reprend les règles du ruleset de yt-transcriber : suppression et réécriture
# d'historique interdites, pull request obligatoire sans relecteur imposé.
#
# Usage
#   bash apply-ci-ruleset.sh OWNER/REPO [--branch NOM]... [--dry-run | --check [--live FICHIER]]
#
# --branch protège aussi une branche d'intégration, par exemple `develop` quand les pull
# requests la visent au lieu de la branche par défaut. Répétable.
# --dry-run affiche le JSON qui serait envoyé et n'écrit rien. Sans lui, le script
# met à jour le ruleset du même nom s'il existe, sinon le crée.
# --check compare le ruleset vivant au contrat et n'écrit rien. Seuls les champs que le
# contrat pose sont comparés : ceux que GitHub ajoute ne sont pas des écarts. Une ligne par
# écart. Code 0 si conforme, 1 si un écart est mesuré ou si aucun ruleset n'est trouvé,
# 2 si le ruleset vivant ne peut pas être lu (API injoignable, fichier absent, JSON illisible).
# --live FICHIER lit le ruleset vivant dans FICHIER au lieu de l'API. Implique --check.
# Un dépôt privé d'un compte gratuit n'a pas de ruleset : l'API répond « Upgrade to GitHub
# Pro or make this repository public ». --check le rend en écart « ruleset indisponible »,
# code 1, parce que rien n'exige alors la porte `ci`. Toute autre erreur de l'API rend 2.
#
# ATTENTION : appliquer ce ruleset avant que les jobs aient rapporté leur nouveau nom
# sur une pull request bloque sa fusion. Voir « L'ordre pour changer des noms de job »
# dans la fiche.
set -euo pipefail

NAME="Protection de la branche par défaut"
# Celui de yt-transcriber, créé à la main avant ce script, porte ce nom : on le met à jour
# sans le renommer.
LEGACY_NAME="Protection de la branche main"
REPO=""
DRY=0
CHECK=0
LIVE=""
INCLUDE='["~DEFAULT_BRANCH"]'
while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run) DRY=1 ;;
    --check) CHECK=1 ;;
    --live)
      [ -n "${2:-}" ] || { echo "--live demande un fichier" >&2; exit 2; }
      LIVE="$2"; CHECK=1
      shift ;;
    --branch)
      [ -n "${2:-}" ] || { echo "--branch demande un nom de branche" >&2; exit 2; }
      INCLUDE=$(jq -c --arg ref "refs/heads/$2" '. + [$ref]' <<<"$INCLUDE")
      shift ;;
    -*) echo "option inconnue : $1" >&2; exit 2 ;;
    *) REPO="$1" ;;
  esac
  shift
done
[ -n "$REPO" ] || { echo "usage : $0 OWNER/REPO [--branch NOM]... [--dry-run | --check [--live FICHIER]]" >&2; exit 2; }
[ "$DRY" = 1 ] && [ "$CHECK" = 1 ] && { echo "--dry-run et --check s'excluent" >&2; exit 2; }
command -v jq >/dev/null || { echo "jq manquant" >&2; exit 2; }

CONTEXTS='["ci"]'

PAYLOAD=$(jq -n --arg name "$NAME" --argjson contexts "$CONTEXTS" --argjson include "$INCLUDE" '{
  name: $name,
  target: "branch",
  enforcement: "active",
  conditions: {ref_name: {include: $include, exclude: []}},
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
      strict_required_status_checks_policy: true,
      required_status_checks: ($contexts | map({context: .}))
    }}
  ]
}')

if [ "$DRY" = 1 ]; then
  echo "$PAYLOAD"
  exit 0
fi

# Le ruleset du contrat, repéré par son nom : « id<TAB>nom », vide s'il n'existe pas.
find_existing() {
  gh api "repos/$REPO/rulesets" --jq \
    "[.[] | select(.name == \"$NAME\" or .name == \"$LEGACY_NAME\")][0] // empty | [.id, .name] | @tsv"
}

if [ "$CHECK" = 1 ]; then
  # Ne pas pouvoir lire le vivant rend 2 : un appelant distingue ainsi une API injoignable
  # d'un ruleset non conforme.
  if [ -n "$LIVE" ]; then
    LIVE_JSON=$(cat "$LIVE") || { echo "$REPO : impossible de lire $LIVE" >&2; exit 2; }
  else
    ERR=$(mktemp); trap 'rm -f "$ERR"' EXIT
    if EXISTING=$(find_existing 2>"$ERR"); then
      [ -n "$EXISTING" ] || { echo "$REPO : aucun ruleset du contrat"; exit 1; }
      LIVE_JSON=$(gh api "repos/$REPO/rulesets/${EXISTING%%$'\t'*}") \
        || { echo "$REPO : lecture du ruleset impossible" >&2; exit 2; }
    elif grep -qiE 'upgrade to github pro|make this repository public' "$ERR"; then
      # Un dépôt privé d'un compte gratuit n'a pas de ruleset : rien n'exige la porte `ci`
      # (mesuré le 2026-11-05 sur hypomnesis). C'est un écart, pas une API injoignable.
      LIVE_JSON='{"rules": []}'
      NO_RULESET="ruleset indisponible : dépôt privé sur un compte gratuit, la porte ci n'est exigée par rien"
    else
      cat "$ERR" >&2; echo "$REPO : lecture des rulesets impossible" >&2; exit 2
    fi
  fi
  jq -e 'type == "object"' >/dev/null 2>&1 <<<"$LIVE_JSON" \
    || { echo "$REPO : le ruleset vivant n'est pas un objet JSON" >&2; exit 2; }
  # Le contrat est un sous-ensemble du vivant. Les tableaux se comparent triés : l'ordre
  # des contextes ou des branches ne porte pas de sens.
  GAPS=$(jq -r --argjson want "$PAYLOAD" '
    def canon: walk(if type == "array" then sort else . end);
    def show: tojson;
    . as $live
    | ([["target"], ["enforcement"], ["conditions", "ref_name", "include"], ["conditions", "ref_name", "exclude"]][]
       | . as $p
       | ($want | getpath($p) | canon) as $w
       | ($live | getpath($p) | canon) as $l
       | if $w != $l then "\($p | join(".")) : attendu \($w | show), vivant \($l | show)" else empty end),
      ($want.rules[] as $r
       | ([$live.rules[]? | select(.type == $r.type)][0]) as $l
       | if $l == null then "rule \($r.type) : absente du vivant"
         else ($r.parameters // {} | to_entries[]) as $e
           | ($l.parameters[$e.key]) as $v
           | if ($e.value | canon) != ($v | canon)
               then "rule \($r.type) : \($e.key) attendu \($e.value | show), vivant \($v | show)"
               else empty end
         end)
  ' <<<"$LIVE_JSON")
  [ -z "${NO_RULESET:-}" ] || GAPS="$NO_RULESET"
  if [ -n "$GAPS" ]; then
    sed "s|^|$REPO : |" <<<"$GAPS"
    exit 1
  fi
  echo "$REPO : conforme au contrat"
  exit 0
fi

EXISTING=$(find_existing)

if [ -n "$EXISTING" ]; then
  ID=${EXISTING%%$'\t'*}
  KEPT=${EXISTING#*$'\t'}
  echo "$PAYLOAD" | jq --arg name "$KEPT" '.name = $name' \
    | gh api -X PUT "repos/$REPO/rulesets/$ID" --input - --jq '"mis à jour : \(.name) (\(.id))"'
else
  echo "$PAYLOAD" | gh api -X POST "repos/$REPO/rulesets" --input - --jq '"créé : \(.name) (\(.id))"'
fi
