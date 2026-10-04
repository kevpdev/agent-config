#!/usr/bin/env bash
# Résout le vault Obsidian à utiliser, parmi OBSIDIAN_VAULT_PRO et OBSIDIAN_VAULT_PERSO, exportées
# par le profil du shell de lancement (le .zshrc). Liste fermée : une variable OBSIDIAN_VAULT_*
# étrangère ne devient jamais un candidat, donc le comportement ne dépend que de ces deux noms.
#
# POURQUOI : un skill qui câble `$OBSIDIAN_VAULT_PRO` casse sur un poste qui n'a qu'un vault
# perso, et inversement. La liste des vaults se lit au lieu de se supposer.
#
# Sortie et codes :
#   0  un seul vault (ou un choix valide en argument) : son chemin absolu, seul, sur stdout
#   3  plusieurs vaults : une ligne `<n> <NOM>=<chemin>` par vault, à faire choisir à l'utilisateur
#   1  aucun vault exploitable : le message dit quoi exporter
#   2  argument de choix inconnu
#
# Usage : resolve-vault.sh            liste et décide
#         resolve-vault.sh <n|NOM>    rend le chemin du vault choisi (numéro de liste, ou suffixe
#                                     de la variable, ex. PERSO)

set -uo pipefail

names=()
paths=()
while IFS='=' read -r name value; do
  [ -n "$value" ] && [ -d "$value" ] || continue
  names+=("${name#OBSIDIAN_VAULT_}")
  paths+=("$value")
done < <(env | grep -E '^OBSIDIAN_VAULT_(PRO|PERSO)=' | sort)

if [ ${#paths[@]} -eq 0 ]; then
  echo "AUCUN vault : exporter OBSIDIAN_VAULT_PRO ou OBSIDIAN_VAULT_PERSO (\"/chemin/absolu\") depuis le .zshrc."
  exit 1
fi

if [ $# -ge 1 ]; then
  choix=$1
  for i in "${!paths[@]}"; do
    if [ "$choix" = "$((i + 1))" ] || [ "$choix" = "${names[$i]}" ]; then
      echo "${paths[$i]}"
      exit 0
    fi
  done
  echo "choix inconnu : $choix"
  exit 2
fi

if [ ${#paths[@]} -eq 1 ]; then
  echo "${paths[0]}"
  exit 0
fi

for i in "${!paths[@]}"; do
  echo "$((i + 1)) ${names[$i]}=${paths[$i]}"
done
exit 3
