#!/usr/bin/env bash
# Calibre `tools/apply-ci-ruleset.sh` sans réseau : --dry-run, et --check par --live.
#
# La fixture est le ruleset vivant d'agent-config, capturé le 2026-11-03 par `gh api`. Elle
# garde les champs que GitHub ajoute au payload (`required_reviewers`,
# `do_not_enforce_on_create`…), qui ne doivent pas compter comme des écarts.
#
# Sortie : 0 si tout passe, 1 si un cas échoue.
set -uo pipefail

ICI="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SCRIPT="$ICI/tools/apply-ci-ruleset.sh"
FIXTURE="$ICI/tools/tests/fixtures/ruleset-agent-config.json"
echecs=0

cas() {  # cas NOM OBTENU ATTENDU
    if [ "$2" = "$3" ]; then
        echo "  ok    $1"
    else
        echecs=$((echecs + 1))
        echo "  FAIL  $1"
        echo "        obtenu  : $2"
        echo "        attendu : $3"
    fi
}

T="$(mktemp -d)"
trap 'rm -rf "$T"' EXIT

# check NOM_DU_FICHIER FILTRE_JQ [OPTIONS...] : écrit la fixture modifiée, lance --check, rend « code|sortie ».
check() {
    local f="$T/$1" filtre="$2"
    shift 2
    jq "$filtre" "$FIXTURE" > "$f"
    local sortie rc
    sortie=$(bash "$SCRIPT" o/r --live "$f" "$@" 2>&1)
    rc=$?
    echo "$rc|$sortie"
}

strict=$(bash "$SCRIPT" o/r --dry-run | jq '.rules[] | select(.type == "required_status_checks") | .parameters.strict_required_status_checks_policy')
cas "--dry-run pose strict à true" "$strict" "true"

cas "le vivant conforme passe, champs GitHub en plus compris" \
    "$(check conforme.json '.')" "0|o/r : conforme au contrat"

cas "strict à false échoue en nommant le champ" \
    "$(check strict-false.json '(.rules[] | select(.type == "required_status_checks") | .parameters.strict_required_status_checks_policy) = false')" \
    "1|o/r : rule required_status_checks : strict_required_status_checks_policy attendu true, vivant false"

sortie=$(check contexte.json '(.rules[] | select(.type == "required_status_checks") | .parameters.required_status_checks) = [{"context": "build"}]')
cas "un autre contexte que ci échoue" "${sortie%%|*}" "1"

sortie=$(check sans-develop.json '.' --branch develop)
cas "une branche du contrat absente du vivant échoue" "${sortie%%|*}" "1"

cas "l'ordre des branches ne compte pas" \
    "$(check ordre.json '.conditions.ref_name.include = ["refs/heads/develop", "~DEFAULT_BRANCH"]' --branch develop)" \
    "0|o/r : conforme au contrat"

sortie=$(check sans-regle.json 'del(.rules[] | select(.type == "deletion"))')
cas "une règle absente du vivant échoue" "${sortie#*|}" "o/r : rule deletion : absente du vivant"

cas "un exclude non vide échoue" \
    "$(check exclude.json '.conditions.ref_name.exclude = ["refs/heads/main"]')" \
    "1|o/r : conditions.ref_name.exclude : attendu [], vivant [\"refs/heads/main\"]"

sortie=$(check target.json '.target = "tag"')
cas "une autre cible que branch échoue" "${sortie%%|*}" "1"

rc=0; bash "$SCRIPT" o/r --live "$T/absent.json" >/dev/null 2>&1 || rc=$?
cas "un fichier vivant absent ne conclut pas" "$rc" "2"

echo 'pas du json' > "$T/illisible.json"
rc=0; bash "$SCRIPT" o/r --live "$T/illisible.json" >/dev/null 2>&1 || rc=$?
cas "un JSON illisible ne conclut pas" "$rc" "2"

rc=0; bash "$SCRIPT" o/r --dry-run --check >/dev/null 2>&1 || rc=$?
cas "--dry-run et --check s'excluent" "$rc" "2"

[ "$echecs" -eq 0 ] || { echo "$echecs cas en échec"; exit 1; }
echo "tous les cas passent"
