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

# Les vaults se lisent comme `resolve-vault.sh` les lit : OBSIDIAN_VAULT_PRO ou OBSIDIAN_VAULT_PERSO, si elle
# pointe un dossier. Un pont écrit avec `<vault>/` est contrôlé contre chacun d'eux.
mapfile -t vaults < <(env | grep -E '^OBSIDIAN_VAULT_(PRO|PERSO)=' | cut -d= -f2- | while read -r v; do [ -d "$v" ] && echo "$v"; done)
if [ ${#vaults[@]} -eq 0 ]; then
  echo "FAIL $skill : vault absent, ni \$OBSIDIAN_VAULT_PRO ni \$OBSIDIAN_VAULT_PERSO ne pointe un dossier"
  exit 2
fi

# Les chemins porteurs d'un placeholder (<date>, <sujet>, <PROJET>) sont des gabarits, pas des
# cibles. On les écarte du contrôle, sans les compter comme cible trouvée. `<vault>/` est le
# seul placeholder accepté, en tête de chemin.
mapfile -t refs < <(grep -oE '(\$OBSIDIAN_VAULT_[A-Z]+|<vault>)/[^`" )]*' "$md" \
  | grep -vE '/.*<' | sed 's:/*$::' | sort -u)

if [ ${#refs[@]} -eq 0 ]; then
  echo "FAIL $skill : aucune cible canonique détectable dans SKILL.md"
  exit 1
fi

fail=0
for ref in "${refs[@]}"; do
  if [[ "$ref" == "<vault>/"* ]]; then
    for v in "${vaults[@]}"; do
      real="$v/${ref#<vault>/}"
      if [ -e "$real" ]; then
        echo "PASS $skill : $ref ($v)"
      else
        echo "FAIL $skill : $ref ne résout pas ($real)"
        fail=1
      fi
    done
  else
    var=${ref%%/*}
    var=${var#\$}
    if [ -z "${!var:-}" ] || [ ! -d "${!var:-}" ]; then
      echo "FAIL $skill : vault absent, \$$var=${!var:-<vide>}"
      exit 2
    fi
    real=$(eval "echo $ref")
    if [ -e "$real" ]; then
      echo "PASS $skill : $ref"
    else
      echo "FAIL $skill : $ref ne résout pas ($real)"
      fail=1
    fi
  fi
done

exit $fail
