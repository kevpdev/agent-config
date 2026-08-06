#!/usr/bin/env bash
# Détection des projets enfants d'un dossier parent — implémentation unique.
#
# Référence partagée. Citée par `aidd-pilot` (périmètre de planification),
# `doc-sync` (homes de doc à synchroniser) et `memory-bootstrap` (enfants sans
# porte). R6 : un fait, un seul home — trois copies de cette règle dériveraient.
#
# Usage :
#   bash "$SKILLS_ROOT/_shared/detect-children.sh"          # liste les enfants
#   bash "$SKILLS_ROOT/_shared/detect-children.sh" --long   # + attributs vcs/build
# S'exécute depuis le dossier parent (le CWD). Aucune écriture, aucun effet de bord.
#
# ── LA RÈGLE ────────────────────────────────────────────────────────────────
# Un enfant est le dossier le PLUS HAUT, hors racine, portant SOIT un `.git`,
# SOIT un manifeste de projet. On ne cherche pas d'enfant à l'intérieur d'un enfant.
#
# POURQUOI l'union des deux signaux, et pas `.git` seul :
#   un enfant n'est pas forcément versionné à part. Un monorepo a un seul `.git`
#   à la racine et n'en donne aucun à ses projets — chercher `.git` y conclut
#   « mono-projet » et le fan-out ne s'arme jamais. Mesuré le 2026-07-30 sur un
#   monorepo à deux projets : 0 enfant trouvé par `.git`, 2 par l'union.
#
# POURQUOI pas le manifeste seul :
#   un enfant peut n'avoir rien à compiler. Mesuré sur Winggy-v3 le 2026-07-30 :
#   le manifeste seul perd 6 dépôts réels (config, devops, docker, deux dépôts de
#   documentation, et un enfant multi-module dont le `pom.xml` vit un niveau plus bas).
#
# POURQUOI aucune limite de profondeur :
#   plafonner à deux niveaux prétendait éviter les doublons et tenir le coût.
#   Les doublons sont évités par le `-prune` sur la trouvaille — on ne descend pas
#   dans un enfant, donc le module interne d'un enfant n'est jamais listé. Le coût
#   est tenu par l'exclusion des dossiers d'artefacts : mesuré 0,16 s sur un
#   coordinateur de 20 dépôts. La limite, elle, ratait un enfant rangé à
#   `apps/backend/svc/` — un rangement banal. Vérifié : 0 trouvé avec, 1 sans.
#
# POURQUOI deux attributs et pas un seul verdict :
#   le manifeste répond « y a-t-il une porte de test à franchir ici ? », le `.git`
#   répond « ce dossier peut-il porter sa propre branche ? ». Un dépôt de
#   documentation a le second sans le premier, un projet de monorepo l'inverse.
#   Les confondre est ce qui a produit la règle trop étroite.

set -uo pipefail

# Dossiers jamais traversés : artefacts de build et dépendances. C'est ce qui tient
# le coût, et ça évite de prendre un `package.json` de dépendance pour un projet.
EXCLUS=(node_modules target dist build .venv vendor .git .idea .next .gradle)

# Fichiers qui identifient un projet. Liste fermée et volontairement courte :
# un fichier absent d'ici n'est pas « oublié », il est hors périmètre — à ajouter
# explicitement plutôt qu'à devenir une heuristique floue.
MANIFESTES=(pom.xml build.gradle build.gradle.kts package.json pyproject.toml
            Cargo.toml go.mod composer.json)

prune_expr=()
for d in "${EXCLUS[@]}"; do prune_expr+=(-name "$d" -o); done
unset 'prune_expr[${#prune_expr[@]}-1]'

test_expr=(-exec test -e '{}/.git' \;)
for m in "${MANIFESTES[@]}"; do test_expr+=(-o -exec test -e "{}/$m" \;); done

# `-print -prune` : on retient le dossier, puis on refuse d'y descendre.
# La racine est exclue par `-mindepth 1` — c'est le parent, pas un enfant.
enfants=$(find . -mindepth 1 -type d \
  \( "${prune_expr[@]}" \) -prune -o \
  -type d \( "${test_expr[@]}" \) -print -prune 2>/dev/null \
  | sed 's#^\./##' | sort)

if [ -z "$enfants" ]; then
  echo "aucun enfant : topologie mono-projet" >&2
  exit 0
fi

if [ "${1:-}" != "--long" ]; then
  printf '%s\n' "$enfants"
  exit 0
fi

# Forme longue : les deux attributs, plus le home memory.
# Le dossier memory d'un enfant groupé porte son nom SIMPLE (`backend/catalogue`
# → `aidd_docs/memory/catalogue/`), d'où le `basename` : sans lui on teste
# `aidd_docs/memory/backend/catalogue/`, qui n'existe pas, et chaque enfant est
# classé « sans memory » à tort.
printf '%-40s %-12s %-24s %s\n' CHEMIN VCS BUILD MEMORY
while IFS= read -r c; do
  [ -n "$c" ] || continue
  n=$(basename "$c")

  if [ -e "$c/.git" ]; then vcs="propre"; else vcs="parent"; fi

  build="aucun"
  for m in "${MANIFESTES[@]}"; do
    if [ -e "$c/$m" ]; then build="$m"; break; fi
  done

  if [ -d "$c/aidd_docs/memory" ]; then mem="distribué"
  elif [ -d "aidd_docs/memory/$n" ]; then mem="centralisé (memory/$n)"
  else mem="aucune"; fi

  printf '%-40s %-12s %-24s %s\n' "$c" "$vcs" "$build" "$mem"
done <<< "$enfants"
