#!/usr/bin/env bash
# sync-rules.sh — vérifie, ou répare, les symlinks de ~/.claude/rules.
#
# POURQUOI CE SCRIPT
#   `~/.claude/rules/` est le seul point de montage de la config qui ne peut pas
#   être un symlink de dossier : deux dossiers du repo (`rules/` et
#   `wrappers/claude/rules/`) se déversent au même endroit, et un lien de dossier
#   ne fusionne pas. Il faut donc un lien PAR FICHIER, créé à la main.
#
#   Les cinq autres cibles (`skills`, `agents`, `output-styles`, `scripts`,
#   `settings.json`) sont des liens de dossier ou de fichier uniques, donc elles
#   ne peuvent pas dériver — vérifié le 2026-08-05. Ce périmètre est complet.
#
#   Le geste manuel a échoué deux fois le 2026-08-05. Un fichier de règle
#   committé et relu ne se chargeait pas, faute de lien. Puis, en le supprimant,
#   un lien pendu aurait survécu. Aucun des deux cas ne donne de signal.
#
# ÉCHOUE FERMÉ : tout écart rend un code de sortie non nul (cf. rules/workflow.md).
#
# Usage
#   bash sync-rules.sh          vérifie, n'écrit rien
#   bash sync-rules.sh --fix    crée et répare les liens
#
# CLAUDE_RULES_DIR vise un dossier de test au lieu de ~/.claude/rules, pour que
# le script soit calibrable sans toucher la config vivante.
set -uo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
CIBLE="${CLAUDE_RULES_DIR:-$HOME/.claude/rules}"
FIX=0
[ "${1:-}" = "--fix" ] && FIX=1

# Racine dérivée, jamais en dur : elle doit porter les deux dossiers source.
for d in "$REPO/rules" "$REPO/wrappers/claude/rules"; do
    if [ ! -d "$d" ]; then
        echo "sync-rules — racine invalide : « $REPO » ne porte pas $d." >&2
        exit 1
    fi
done

mkdir -p "$CIBLE"
ecarts=0
declare -A source_de

# 1. Chaque fichier source doit avoir son lien, pointant vers lui.
for f in "$REPO"/rules/*.md "$REPO"/wrappers/claude/rules/*.md; do
    [ -e "$f" ] || continue
    nom="$(basename "$f")"

    # Collision de noms entre les deux dossiers source : le second lien
    # écraserait le premier, et lequel gagne dépendrait de l'ordre de la boucle.
    if [ -n "${source_de[$nom]:-}" ]; then
        echo "  COLLISION  $nom existe dans les deux dossiers source" >&2
        echo "             ${source_de[$nom]}" >&2
        echo "             $f" >&2
        ecarts=$((ecarts + 1))
        continue
    fi
    source_de[$nom]="$f"

    lien="$CIBLE/$nom"
    actuel="$(readlink "$lien" 2>/dev/null || true)"

    if [ "$actuel" = "$f" ]; then
        continue
    elif [ -z "$actuel" ] && [ ! -e "$lien" ]; then
        etat="ABSENT"
    elif [ -z "$actuel" ]; then
        etat="PAS UN LIEN"
    else
        etat="MAUVAISE CIBLE ($actuel)"
    fi

    if [ "$FIX" -eq 1 ] && [ "$etat" != "PAS UN LIEN" ]; then
        ln -sfn "$f" "$lien" && echo "  réparé     $nom"
    else
        echo "  $etat  $nom" >&2
        ecarts=$((ecarts + 1))
    fi
done

# 2. Aucun lien ne doit survivre à la disparition de son fichier source.
for lien in "$CIBLE"/*.md; do
    [ -L "$lien" ] || continue
    nom="$(basename "$lien")"
    [ -n "${source_de[$nom]:-}" ] && continue

    if [ "$FIX" -eq 1 ]; then
        rm "$lien" && echo "  retiré     $nom (plus de source)"
    else
        echo "  ORPHELIN   $nom pointe vers $(readlink "$lien"), qui n'est plus une source" >&2
        ecarts=$((ecarts + 1))
    fi
done

if [ "$ecarts" -eq 0 ]; then
    echo "✓ ${#source_de[@]} règles, ${#source_de[@]} liens, aucun écart."
    exit 0
fi

echo "✗ $ecarts écart(s). Relancer avec --fix pour réparer." >&2
exit 1
