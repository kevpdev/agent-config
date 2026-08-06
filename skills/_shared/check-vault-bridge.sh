#!/usr/bin/env bash
# Vérifie qu'un skill-pont vault résout réellement les cibles canoniques qu'il annonce.
#
# POURQUOI : un pont ne casse pas bruyamment. Le vault déménage, le skill canonique est
# renommé, et le pont continue d'exister en pointant dans le vide — l'échec n'apparaît qu'au
# moment où on l'invoque, en pleine tâche. Ce script rend l'écart mesurable hors invocation.
#
# ÉCHOUE FERMÉ : toute impossibilité de conclure (racine douteuse, SKILL.md illisible, vault
# absent, aucune cible trouvée) rend un code non nul. Un pont sans cible détectable est un
# échec, pas un succès — sinon le contrôle ne surveillerait que les ponts déjà bien écrits.
#
# Usage : check-vault-bridge.sh <nom-du-skill>   (ex. vault-load)

set -uo pipefail

SKILLS_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
if [ ! -d "$SKILLS_DIR/_shared" ]; then
  echo "FAIL racine dérivée invalide : $SKILLS_DIR ne porte pas _shared/"
  exit 2
fi

if [ $# -ne 1 ]; then
  echo "usage: check-vault-bridge.sh <nom-du-skill>"
  exit 2
fi

skill=$1
md="$SKILLS_DIR/$skill/SKILL.md"
if [ ! -r "$md" ]; then
  echo "FAIL $skill : SKILL.md illisible ($md)"
  exit 2
fi

if [ -z "${OBSIDIAN_VAULT_PRO:-}" ] || [ ! -d "${OBSIDIAN_VAULT_PRO:-}" ]; then
  echo "FAIL $skill : vault absent, \$OBSIDIAN_VAULT_PRO=${OBSIDIAN_VAULT_PRO:-<vide>}"
  exit 2
fi

# Les chemins porteurs d'un placeholder (<date>, <sujet>, <PROJET>) sont des gabarits, pas des
# cibles. On les écarte du contrôle, sans les compter comme cible trouvée.
mapfile -t refs < <(grep -oE '\$OBSIDIAN_VAULT_[A-Z]+/[^`" )]*' "$md" \
  | grep -v '<' | sed 's:/*$::' | sort -u)

if [ ${#refs[@]} -eq 0 ]; then
  echo "FAIL $skill : aucune cible canonique détectable dans SKILL.md"
  exit 1
fi

fail=0
for ref in "${refs[@]}"; do
  real=$(eval "echo $ref")
  if [ -e "$real" ]; then
    echo "PASS $skill : $ref"
  else
    echo "FAIL $skill : $ref ne résout pas ($real)"
    fail=1
  fi
done

exit $fail
