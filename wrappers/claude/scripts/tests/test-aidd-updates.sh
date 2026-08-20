#!/usr/bin/env bash
# Batterie de cas pour ../aidd-updates.py
#
# Usage : bash wrappers/claude/scripts/tests/test-aidd-updates.sh
# Sortie 0 si tous les cas passent, 1 sinon.
# N'ecrit que dans un dossier jetable, ne touche ni ~/.local/state ni ~/.claude, et ne va pas sur le
# reseau (sauf le dernier cas, explicitement non bloquant).
#
# POURQUOI CE FICHIER EXISTE
#   Le script sort TOUJOURS en 0, par choix (cf. son en-tete). Son code de sortie ne dit donc rien,
#   et un detecteur casse se comporte exactement comme un detecteur qui n'a rien trouve : les deux
#   se taisent. Seule une batterie distingue les deux.
#
#   D'OU L'ORDRE DES CAS. Le premier est le CALIBRAGE : un retard fabrique a la main, que
#   l'instrument doit voir. S'il echoue, tous les « silences » verifies ensuite ne prouvent rien,
#   et la batterie s'arrete la plutot que de rendre un vert trompeur.
#
# CE QUI EST VERIFIE : la DECISION du script (notifie / se tait, plan garde / invalide), pas ses
#   libelles. La prose changera, le contrat non.

set -uo pipefail

ICI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT="$ICI/../aidd-updates.py"
ECHECS=0
CAS=0

if [ ! -f "$SCRIPT" ]; then
  echo "script introuvable : $SCRIPT" >&2
  exit 1
fi

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

export AIDD_UPDATES_STATE_DIR="$TMP/etat"
export AIDD_UPDATES_PLUGINS_JSON="$TMP/installed_plugins.json"
export AIDD_UPDATES_TAGS_FILE="$TMP/tags.txt"
export AIDD_UPDATES_NO_DETACH=1

PLAN="$TMP/etat/plan.md"

# --------------------------------------------------------------------------- utilitaires

lance() { python3 "$SCRIPT" "$@" 2>"$TMP/err.txt"; }

# Les versions installees, fabriquees a la main : c'est la reference dont depend tout le reste.
ecrire_installe() {
  cat > "$AIDD_UPDATES_PLUGINS_JSON" <<JSON
{
  "version": 2,
  "plugins": {
    "aidd-refine@aidd-framework": [{"scope": "user", "version": "$1"}],
    "aidd-dev@aidd-framework": [{"scope": "user", "version": "$2"}]
  }
}
JSON
}

ecrire_tags() {
  : > "$AIDD_UPDATES_TAGS_FILE"
  for couple in "$@"; do
    echo "0000000000000000000000000000000000000000	refs/tags/${couple}" >> "$AIDD_UPDATES_TAGS_FILE"
  done
}

verifie() {
  local intitule="$1" attendu="$2" obtenu="$3"
  CAS=$((CAS + 1))
  if [ "$attendu" = "$obtenu" ]; then
    printf '  ok   %s\n' "$intitule"
  else
    printf '  KO   %s\n       attendu « %s », obtenu « %s »\n' "$intitule" "$attendu" "$obtenu"
    ECHECS=$((ECHECS + 1))
  fi
}

champ() { grep -m1 "^$1:" "$PLAN" 2>/dev/null | sed "s/^$1: *//"; }

# --------------------------------------------------------- 1. CALIBRAGE — un retard doit etre vu

echo "1. calibrage — retard fabrique a la main"
ecrire_installe "2.2.1" "2.3.1"
ecrire_tags "aidd-refine-v2.2.4" "aidd-refine-v3.0.0" "aidd-dev-v2.4.1" "aidd-orchestrator-v9.9.9"
lance --refresh > /dev/null
SORTIE="$(lance --notify)"

verifie "notifie sur un retard" "oui" "$([ -n "$SORTIE" ] && echo oui || echo non)"
verifie "le majeur est signale cassant" "[aidd-refine]" "$(champ cassant)"
verifie "le message porte CASSANT" "oui" "$(echo "$SORTIE" | grep -q 'CASSANT' && echo oui || echo non)"
verifie "sortie JSON parsable" "oui" \
  "$(echo "$SORTIE" | python3 -c 'import json,sys; json.load(sys.stdin); print("oui")' 2>/dev/null || echo non)"
verifie "le hook nomme bien SessionStart" "SessionStart" \
  "$(echo "$SORTIE" | python3 -c 'import json,sys; print(json.load(sys.stdin)["hookSpecificOutput"]["hookEventName"])' 2>/dev/null)"
verifie "un plugin non installe n'est pas un retard" "non" \
  "$(echo "$SORTIE" | grep -q 'orchestrator' && echo oui || echo non)"

if [ "$ECHECS" -ne 0 ]; then
  echo
  echo "CALIBRAGE ECHOUE — l'instrument ne voit pas un retard fabrique a la main." >&2
  echo "Les cas suivants verifient des silences : ils passeraient sans rien mesurer. Arret ici." >&2
  exit 1
fi

# --------------------------------------------------------- 2. un seul rappel par jour

echo "2. le rappel est plafonne a une fois par jour"
verifie "le second --notify du jour se tait" "" "$(lance --notify)"

# --------------------------------------------------------- 3. plan garde tant que rien ne bouge

echo "3. le plan survit a un refresh sans changement"
printf '# Plan fabrique\n\nPatcher 01-intake.md ligne 45.\n' | lance --marquer-planifie > /dev/null
PLANIFIE_AVANT="$(champ planifie_le)"
lance --refresh > /dev/null
verifie "planifie_le preserve" "$PLANIFIE_AVANT" "$(champ planifie_le)"
verifie "statut preserve" "planifie" "$(champ statut)"
verifie "corps du plan preserve" "oui" "$(grep -q 'Patcher 01-intake' "$PLAN" && echo oui || echo non)"
verifie "--etat dit que le plan tient" "false" \
  "$(lance --etat | python3 -c 'import json,sys; print(str(json.load(sys.stdin)["plan_a_refaire"]).lower())')"

# --------------------------------------------------------- 4. plan invalide quand une version bouge

echo "4. une nouvelle version upstream invalide le plan"
ecrire_tags "aidd-refine-v3.1.0" "aidd-dev-v2.4.1"
lance --refresh > /dev/null
verifie "planifie_le remis a null" "null" "$(champ planifie_le)"
verifie "statut revenu a detecte" "detecte" "$(champ statut)"
verifie "corps du plan efface" "non" "$(grep -q 'Patcher 01-intake' "$PLAN" && echo oui || echo non)"
verifie "--etat demande une replanification" "true" \
  "$(lance --etat | python3 -c 'import json,sys; print(str(json.load(sys.stdin)["plan_a_refaire"]).lower())')"

# --------------------------------------------------------- 5. plus de retard, plus de bruit

echo "5. a jour"
ecrire_installe "3.1.0" "2.4.1"
lance --refresh > /dev/null
verifie "statut a-jour" "a-jour" "$(champ statut)"
verifie "aucune notification" "" "$(lance --notify)"

# --------------------------------------------------------- 6. statut applique fait taire le hook

echo "6. une fois applique, le hook se tait"
ecrire_installe "2.2.1" "2.3.1"
lance --refresh > /dev/null
lance --marquer-applique > /dev/null
verifie "aucune notification malgre le retard" "" "$(lance --notify)"

# --------------------------------------------------------- 7. panne de source

echo "7. source des tags injoignable"
# La panne est simulee par un fichier de tags absent, PAS par une vraie coupure reseau : c'est le
# meme chemin de code (exception Panne), et une batterie ne doit pas dependre du reseau.
rm -f "$PLAN"
ecrire_installe "2.2.1" "2.3.1"
ecrire_tags "aidd-refine-v3.0.0" "aidd-dev-v2.4.1"
lance --refresh > /dev/null
printf '# Plan a proteger\n' | lance --marquer-planifie > /dev/null
AIDD_UPDATES_TAGS_FILE="$TMP/absent.txt" lance --refresh > /dev/null
CODE=$?
verifie "sortie 0 malgre la panne" "0" "$CODE"
verifie "derniere_erreur renseignee" "oui" \
  "$([ -n "$(champ derniere_erreur)" ] && [ "$(champ derniere_erreur)" != "null" ] && echo oui || echo non)"
verifie "le plan existant survit a la panne" "oui" "$(grep -q 'Plan a proteger' "$PLAN" && echo oui || echo non)"
verifie "aucune trace Python" "non" "$(grep -q 'Traceback' "$TMP/err.txt" && echo oui || echo non)"

# --------------------------------------------------------- 8. etat corrompu

echo "8. front-matter tronque"
printf -- '---\nstatut: detecte\ncle_installe: {aidd-refine: 2.2.1\n' > "$PLAN"
SORTIE="$(lance --notify)"
verifie "sortie 0" "0" "$?"
verifie "se tait au lieu de deviner" "" "$SORTIE"
verifie "aucune trace Python" "non" "$(grep -q 'Traceback' "$TMP/err.txt" && echo oui || echo non)"

echo "8b. fichier d'etat absent"
rm -f "$PLAN"
verifie "se tait" "" "$(lance --notify)"
verifie "aucune trace Python" "non" "$(grep -q 'Traceback' "$TMP/err.txt" && echo oui || echo non)"

# --------------------------------------------------------- 9. appel fautif

echo "9. mode inconnu"
lance --nawak > /dev/null
verifie "sortie 2 sur un mode inconnu" "2" "$?"

# --------------------------------------------------------- 10. le vrai reseau, non bloquant

echo "10. reseau reel (informatif, n'echoue pas hors ligne)"
unset AIDD_UPDATES_TAGS_FILE
rm -f "$PLAN"
ecrire_installe "2.2.1" "2.3.1"
lance --refresh > /dev/null
REEL="$(champ cle_upstream)"
if [ -n "$REEL" ] && [ "$REEL" != "null" ]; then
  echo "  ok   ls-remote a repondu : $REEL"
else
  echo "  --   pas de reseau, ou tags absents : $(champ derniere_erreur)"
fi

# --------------------------------------------------------------------------- verdict

echo
if [ "$ECHECS" -eq 0 ]; then
  echo "$CAS cas, tous passent."
  exit 0
fi
echo "$CAS cas, $ECHECS echec(s)." >&2
exit 1
