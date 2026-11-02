#!/usr/bin/env bash
# worktree.sh — crée le worktree d'un travail par l'outil le plus riche disponible, Orca
# sinon git, avec le même chemin et la même branche à chaque rang.
#
# POURQUOI CE SCRIPT
#   Le choix entre Orca et git vivait dans le texte de rules/worktrees.md, donc dans le
#   jugement de l'agent, et ses commandes vieillissaient avec les versions d'Orca. Ici le
#   choix se teste, et Claude comme OpenCode l'appellent de la même façon (issue #76,
#   cadrage audits/2026-11-02-cadrage-workflow-coeur.md, Q3).
#
# LES RANGS, testés dans l'ordre
#   1  ORCA_WORKTREE_ID défini et `orca-ide status` joignable en 5 s : Orca crée le
#      worktree, avec ses métadonnées (issue liée, visibilité dans l'interface). Le chemin
#      se lit dans result.worktree.path du JSON de `orca-ide worktree create --json`,
#      forme relevée le 2026-11-02 sur Orca 1.4.243.
#   2  orca-ide installé mais injoignable : git crée le worktree au chemin et sous la
#      branche qu'Orca aurait pris, avec un avertissement.
#   3  pas d'Orca : git, même chemin, même branche.
#
# LA BASE est origin/<branche par défaut>, après un fetch. Le `main` local du checkout
# d'agent-config n'est jamais mis à jour (rules/worktrees.md), il serait périmé. Sans
# origin/HEAD, le script tente `git remote set-head origin --auto`. S'il échoue, la base
# est origin/main et stderr le dit.
#
# LE NOM devient la branche <user.name>/<nom>. Il est refusé avant toute création s'il
# contient un `/` ou si `git check-ref-format --branch` rejette la branche.
#
# RETRAIT, en attendant une sous-commande remove
#   Après le merge, retirer le worktree et sa branche, locale et distante.
#   Créé par Orca : `orca-ide worktree rm --worktree path:<chemin>`. Orca supprime aussi
#   la branche locale. Créé par git : `git worktree remove <chemin>`, puis
#   `git branch -D <branche>`. Dans les deux cas, la distante part par
#   `git push origin --delete <branche>`.
#   Sous Linux, `orca-ide` et jamais `orca`. Hors d'un terminal Orca, `orca` lance le
#   lecteur d'écran GNOME.
#
# Variables
#   ORCA_WORKSPACES     racine des worktrees, ~/orca/workspaces par défaut (défaut d'Orca)
#   WORKTREE_ORCA_CLI   la CLI Orca, orca-ide par défaut (les tests la remplacent)
#
# Sortie : le chemin du worktree en dernière ligne de stdout, le rang sur stderr.
# Code 1 sur un refus (nom invalide ou déjà pris, hors d'un dépôt git) ou un échec de
# création. Un refus ne laisse aucun dossier derrière lui.
#
# Usage : bash tools/worktree.sh create <nom> [--issue N]
set -uo pipefail

CLI="${WORKTREE_ORCA_CLI:-orca-ide}"
RACINE="${ORCA_WORKSPACES:-$HOME/orca/workspaces}"

usage() { echo "Usage : worktree.sh create <nom> [--issue N]" >&2; exit 1; }
refus() { echo "worktree — $1" >&2; exit 1; }

# Lit une clé pointée (a.b.c) dans le JSON reçu sur stdin. Rend la valeur, vide si absente.
json_cle() {
    python3 -c 'import json, sys
try:
    v = json.loads(sys.stdin.read())
except ValueError:
    sys.exit(0)
for k in sys.argv[1].split("."):
    v = v.get(k) if isinstance(v, dict) else None
if isinstance(v, bool):
    print("true" if v else "false")
elif v is not None:
    print(v)' "$1"
}

[ "${1:-}" = "create" ] || usage
shift
NOM="${1:-}"
[ -n "$NOM" ] || usage
shift
ISSUE=""
while [ $# -gt 0 ]; do
    case "$1" in
        --issue) [ -n "${2:-}" ] || refus "--issue attend un numéro."
                 ISSUE="$2"; shift 2 ;;
        *) refus "option inconnue : $1" ;;
    esac
done
case "$NOM" in */*) refus "nom invalide : « $NOM » contient un /." ;; esac

# Le checkout principal, même lancé depuis un autre worktree.
COMMUN="$(git rev-parse --path-format=absolute --git-common-dir 2>/dev/null)" || refus "pas dans un dépôt git."
PRINCIPAL="$(dirname "$COMMUN")"
DEPOT="$(basename "$PRINCIPAL")"

USER_GIT="$(git -C "$PRINCIPAL" config user.name)"
[ -n "$USER_GIT" ] || refus "git config user.name est vide, la branche ne peut pas suivre la forme <user>/<nom>."
BRANCHE="$USER_GIT/$NOM"
git check-ref-format --branch "$BRANCHE" >/dev/null 2>&1 \
    || refus "nom invalide : « $BRANCHE » est refusé par git check-ref-format."

git -C "$PRINCIPAL" fetch -q origin 2>/dev/null \
    || echo "worktree — fetch d'origin en échec, base prise sur la dernière copie connue." >&2
defaut() { git -C "$PRINCIPAL" symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null; }
DEFAUT="$(defaut)"
if [ -z "$DEFAUT" ]; then
    git -C "$PRINCIPAL" remote set-head origin --auto >/dev/null 2>&1
    DEFAUT="$(defaut)"
fi
if [ -z "$DEFAUT" ]; then
    DEFAUT="origin/main"
    echo "worktree — origin/HEAD introuvable, base prise sur origin/main." >&2
fi
git -C "$PRINCIPAL" rev-parse -q --verify "$DEFAUT^{commit}" >/dev/null || refus "base introuvable : $DEFAUT."

orca_joignable() {
    [ -n "${ORCA_WORKTREE_ID:-}" ] || return 1
    command -v "$CLI" >/dev/null 2>&1 || return 1
    local etat
    etat="$(timeout 5 "$CLI" status --json 2>/dev/null)" || return 1
    [ "$(printf '%s' "$etat" | json_cle result.runtime.reachable)" = "true" ]
}

if orca_joignable; then
    echo "worktree — rang 1 : Orca." >&2
    ARGS=(worktree create --repo "path:$PRINCIPAL" --name "$NOM" --base-branch "$DEFAUT" --no-parent --setup skip --json)
    [ -n "$ISSUE" ] && ARGS+=(--issue "$ISSUE")
    SORTIE="$("$CLI" "${ARGS[@]}")" || refus "$CLI worktree create en échec."
    CHEMIN="$(printf '%s' "$SORTIE" | json_cle result.worktree.path)"
    [ -n "$CHEMIN" ] || refus "Orca n'a pas rendu result.worktree.path : $SORTIE"
    echo "$CHEMIN"
    exit 0
fi

if command -v "$CLI" >/dev/null 2>&1; then
    echo "worktree — rang 2 : $CLI est installé mais Orca est injoignable. Worktree créé par git, sans les métadonnées d'Orca." >&2
else
    echo "worktree — rang 3 : git seul." >&2
fi

CHEMIN="$RACINE/$DEPOT/$NOM"
[ -e "$CHEMIN" ] && refus "le dossier existe déjà : $CHEMIN."
git -C "$PRINCIPAL" rev-parse -q --verify "refs/heads/$BRANCHE" >/dev/null && refus "la branche existe déjà : $BRANCHE."

# Le plus haut dossier que le script crée, à retirer si la création échoue.
CREE=""
d="$RACINE/$DEPOT"
while [ ! -e "$d" ]; do CREE="$d"; d="$(dirname "$d")"; done
mkdir -p "$RACINE/$DEPOT" || refus "impossible de créer $RACINE/$DEPOT."
if ! git -C "$PRINCIPAL" worktree add -q --no-track -b "$BRANCHE" "$CHEMIN" "$DEFAUT" >&2; then
    [ -n "$CREE" ] && rm -rf -- "$CREE"
    refus "git worktree add en échec."
fi
[ -n "$ISSUE" ] && echo "worktree — issue #$ISSUE non rattachée : seul Orca garde ce lien." >&2
echo "$CHEMIN"
