#!/usr/bin/env bash
# worktree.sh — creates, then removes, the worktree of a piece of work through the richest
# tool available, Orca else git, with the same path and the same branch at every rank.
#
# WHY THIS SCRIPT
#   The choice between Orca and git used to live in the text of rules/worktrees.md, so in
#   the agent's judgement, and its commands aged with each Orca release. Here the choice is
#   tested, and Claude and OpenCode both call it the same way (issue #76, framing note
#   audits/2026-11-02-cadrage-workflow-coeur.md, Q3).
#
# CREATE RANKS, tried in order
#   1  ORCA_WORKTREE_ID is set and `orca-ide status` answers within the timeout: Orca
#      creates the worktree, with its metadata (linked issue, visibility in the UI). The
#      path is read from result.worktree.path in the JSON of
#      `orca-ide worktree create --json`, shape recorded on 2026-11-02 on Orca 1.4.243.
#   2  orca-ide is installed but unreachable: git creates the worktree at the path and on
#      the branch Orca would have used, with a warning.
#   3  no Orca: git, same path, same branch.
#
# THE BASE is origin/<default branch>, after a fetch. The local `main` of the agent-config
# checkout is never updated (rules/worktrees.md), it would be stale. Without origin/HEAD,
# the script tries `git remote set-head origin --auto`. If that fails, the base is
# origin/main and stderr says so.
#
# THE NAME becomes the branch <user.name>/<name>. It is refused before anything is created
# if it starts with `-`, contains a `/`, or if `git check-ref-format --branch` rejects the
# branch.
#
# REMOVE, `remove <name>`, cleans up after the merge, in this order
#   1  Path and branch are computed as for create: <root>/<repo>/<name> and
#      <user.name>/<name>, with the same name validation.
#   2  Refused, with nothing removed, when the resolved path is the main checkout, when a
#      directory exists at the path without being a worktree of the repo, when that
#      worktree holds another branch, when it has uncommitted changes (tracked or not), or
#      when `git ls-remote origin` fails.
#   3  Also refused when the local branch or the remote branch is not contained in
#      origin/<default branch> (after a fetch, same resolution as create). --abandon lifts
#      this refusal only, for abandoned work. A PR merged by squash is not seen as
#      contained, so it needs --abandon too.
#   4  The worktree goes through Orca when Orca is reachable (same test as create rank 1)
#      AND its path is listed by
#      `orca-ide worktree list --repo path:<repo> --limit 1000 --json`
#      (result.worktrees[].path and result.truncated, shape recorded on 2026-11-02 on Orca
#      1.4.243): `orca-ide worktree rm --worktree path:<path> --json`. A truncated list
#      that does not show the path is refused, since Orca may know the worktree. Otherwise
#      `git worktree remove`. A failed worktree removal stops the script with code 1, and
#      no branch is deleted.
#   5  Orca deletes the local branch on its own, after returning. The script waits up to
#      WORKTREE_BRANCHE_DELAI seconds for the branch to disappear, then deletes it with
#      `git branch -D` if it is still there. The dated why is in
#      rules/references/ref-worktrees.md.
#   6  The remote branch goes through `git push origin --delete` if `git ls-remote` sees it.
#   Each item is reported on stderr as removed (« retiré ») or already absent
#   (« déjà absent »). Exit 0 when everything is removed or absent, 1 on a refusal or a
#   failure. Never `git worktree prune`.
#
# On Linux, `orca-ide` and never `orca`. Outside an Orca terminal, `orca` starts the GNOME
# screen reader.
#
# Variables
#   ORCA_WORKSPACES     worktree root, ~/orca/workspaces by default (Orca's default)
#   WORKTREE_ORCA_CLI   the Orca CLI, orca-ide by default (tests replace it)
#   WORKTREE_ORCA_TIMEOUT  timeout of `orca-ide status` and `worktree list`, in whole
#                       seconds, 5 by default. Beyond it, Orca counts as unreachable
#                       (tests shorten it)
#   WORKTREE_BRANCHE_DELAI  maximum wait, in whole seconds, for Orca to delete the local
#                       branch after `worktree rm`, 5 by default
#   Both delays must be positive integers, checked before anything else.
#
# Output of create: the worktree path on the last line of stdout, the rank on stderr.
# Exit 1 on a refusal (invalid or taken name, outside a git repo) or a failed creation. A
# refusal leaves no directory behind.
#
# Usage: bash tools/worktree.sh create <name> [--issue N]
#        bash tools/worktree.sh remove <name> [--abandon]
set -uo pipefail

CLI="${WORKTREE_ORCA_CLI:-orca-ide}"
RACINE="${ORCA_WORKSPACES:-$HOME/orca/workspaces}"
DELAI="${WORKTREE_ORCA_TIMEOUT:-5}"
DELAI_BRANCHE="${WORKTREE_BRANCHE_DELAI:-5}"
ORCA_LIMITE=1000

usage() {
    echo "Usage : worktree.sh create <nom> [--issue N]" >&2
    echo "        worktree.sh remove <nom> [--abandon]" >&2
    exit 1
}
refus() { echo "worktree — $1" >&2; exit 1; }
dire() { echo "worktree — $1" >&2; }

# Reads a dotted key (a.b.c) from the JSON on stdin. Prints the value, empty if missing.
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

# Refuses unless the delay variable $1 holds a positive integer ($2 is its value).
entier_positif() {
    case "$2" in
        ''|*[!0-9]*|0*) refus "$1 doit être un entier positif de secondes, reçu « $2 »." ;;
    esac
}

# Sets PRINCIPAL, DEPOT and BRANCHE from $NOM, or refuses. Shared by create and remove.
contexte_depot() {
    case "$NOM" in */*) refus "nom invalide : « $NOM » contient un /." ;; esac
    # The main checkout, even when run from another worktree.
    local commun
    commun="$(git rev-parse --path-format=absolute --git-common-dir 2>/dev/null)" || refus "pas dans un dépôt git."
    PRINCIPAL="$(dirname "$commun")"
    DEPOT="$(basename "$PRINCIPAL")"
    local user_git
    user_git="$(git -C "$PRINCIPAL" config user.name)"
    [ -n "$user_git" ] || refus "git config user.name est vide, la branche ne peut pas suivre la forme <user>/<nom>."
    BRANCHE="$user_git/$NOM"
    git check-ref-format --branch "$BRANCHE" >/dev/null 2>&1 \
        || refus "nom invalide : « $BRANCHE » est refusé par git check-ref-format."
}

# The path Orca gives the worktree, which git reuses at ranks 2 and 3.
chemin_attendu() { echo "$RACINE/$DEPOT/$NOM"; }

branche_locale_existe() { git -C "$PRINCIPAL" rev-parse -q --verify "refs/heads/$BRANCHE" >/dev/null; }

# Fetches origin, then sets DEFAUT to origin/<default branch>, or refuses.
resoudre_defaut() {
    git -C "$PRINCIPAL" fetch -q origin 2>/dev/null \
        || dire "fetch d'origin en échec, base prise sur la dernière copie connue."
    defaut() { git -C "$PRINCIPAL" symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null; }
    DEFAUT="$(defaut)"
    if [ -z "$DEFAUT" ]; then
        git -C "$PRINCIPAL" remote set-head origin --auto >/dev/null 2>&1
        DEFAUT="$(defaut)"
    fi
    if [ -z "$DEFAUT" ]; then
        DEFAUT="origin/main"
        dire "origin/HEAD introuvable, base prise sur origin/main."
    fi
    git -C "$PRINCIPAL" rev-parse -q --verify "$DEFAUT^{commit}" >/dev/null || refus "base introuvable : $DEFAUT."
}

orca_joignable() {
    [ -n "${ORCA_WORKTREE_ID:-}" ] || return 1
    command -v "$CLI" >/dev/null 2>&1 || return 1
    local etat
    etat="$(timeout "$DELAI" "$CLI" status --json 2>/dev/null)" || return 1
    [ "$(printf '%s' "$etat" | json_cle result.runtime.reachable)" = "true" ]
}

# Announces rank 2 or rank 3, the ranks where git does the work. $1 says why Orca is out
# and what git does instead.
annoncer_rang_git() {
    if command -v "$CLI" >/dev/null 2>&1; then
        dire "rang 2 : $CLI est installé mais $1"
    else
        dire "rang 3 : git seul."
    fi
}

# ---------------------------------------------------------------------------- create

cmd_create() {
    local ISSUE=""
    while [ $# -gt 0 ]; do
        case "$1" in
            --issue) [ -n "${2:-}" ] || refus "--issue attend un numéro."
                     ISSUE="$2"; shift 2 ;;
            *) refus "option inconnue : $1" ;;
        esac
    done
    contexte_depot
    resoudre_defaut

    if orca_joignable; then
        dire "rang 1 : Orca."
        local ARGS=(worktree create --repo "path:$PRINCIPAL" --name "$NOM" --base-branch "$DEFAUT" --no-parent --setup skip --json)
        [ -n "$ISSUE" ] && ARGS+=(--issue "$ISSUE")
        local SORTIE CHEMIN
        SORTIE="$("$CLI" "${ARGS[@]}")" || refus "$CLI worktree create en échec."
        CHEMIN="$(printf '%s' "$SORTIE" | json_cle result.worktree.path)"
        [ -n "$CHEMIN" ] || refus "Orca n'a pas rendu result.worktree.path : $SORTIE"
        echo "$CHEMIN"
        exit 0
    fi

    annoncer_rang_git "Orca est injoignable. Worktree créé par git, sans les métadonnées d'Orca."

    local CHEMIN
    CHEMIN="$(chemin_attendu)"
    [ -e "$CHEMIN" ] && refus "le dossier existe déjà : $CHEMIN."
    branche_locale_existe && refus "la branche existe déjà : $BRANCHE."

    # The topmost directory the script creates, removed again if the creation fails.
    local CREE="" d="$RACINE/$DEPOT"
    while [ ! -e "$d" ]; do CREE="$d"; d="$(dirname "$d")"; done
    mkdir -p "$RACINE/$DEPOT" || refus "impossible de créer $RACINE/$DEPOT."
    if ! git -C "$PRINCIPAL" worktree add -q --no-track -b "$BRANCHE" "$CHEMIN" "$DEFAUT" >&2; then
        [ -n "$CREE" ] && rm -rf -- "$CREE"
        refus "git worktree add en échec."
    fi
    [ -n "$ISSUE" ] && dire "issue #$ISSUE non rattachée : seul Orca garde ce lien."
    echo "$CHEMIN"
}

# ---------------------------------------------------------------------------- remove

# The branch git ties to the worktree registered at path $1: "refs/heads/x", "detached",
# or nothing when no worktree of the repo sits at that path.
worktree_enregistre() {
    local cible ligne chemin="" trouve=""
    cible="$(realpath -m -- "$1")"
    while IFS= read -r ligne; do
        case "$ligne" in
            "worktree "*) chemin="$(realpath -m -- "${ligne#worktree }")" ;;
            "branch "*) [ "$chemin" = "$cible" ] && trouve="${ligne#branch }" ;;
            detached) [ "$chemin" = "$cible" ] && trouve="detached" ;;
        esac
    done < <(git -C "$PRINCIPAL" worktree list --porcelain)
    printf '%s' "$trouve"
}

# Whether Orca lists a worktree at path $1 for this repo. Exit 0: known. Exit 1: unknown,
# or Orca's answer is unreadable. Exit 2: the list is truncated and does not show the path,
# so nothing can be concluded.
orca_connait() {
    local liste
    liste="$(timeout "$DELAI" "$CLI" worktree list --repo "path:$PRINCIPAL" --limit "$ORCA_LIMITE" --json 2>/dev/null)" || return 1
    printf '%s' "$liste" | python3 -c 'import json, os, sys
try:
    resultat = json.loads(sys.stdin.read())["result"]
    rangs = resultat["worktrees"]
except (ValueError, KeyError, TypeError):
    sys.exit(1)
cible = os.path.realpath(sys.argv[1])
if any(os.path.realpath(r.get("path") or "") == cible for r in rangs):
    sys.exit(0)
sys.exit(2 if resultat.get("truncated") else 1)' "$1"
}

# Refuses, unless --abandon was given, when the tip $2 (named $1) is not contained in
# $DEFAUT.
verifier_contenue() {
    git -C "$PRINCIPAL" merge-base --is-ancestor "$2" "$DEFAUT" 2>/dev/null && return 0
    if [ "$ABANDON" = 1 ]; then
        dire "$1 n'est pas contenue dans $DEFAUT, retrait forcé par --abandon."
    else
        refus "refus : $1 n'est pas contenue dans $DEFAUT. Rien retiré. Une PR mergée par squash n'est pas vue comme contenue. Pour elle, ou pour un travail abandonné, relancer avec --abandon."
    fi
}

cmd_remove() {
    ABANDON=0
    while [ $# -gt 0 ]; do
        case "$1" in
            --abandon) ABANDON=1; shift ;;
            *) refus "option inconnue : $1" ;;
        esac
    done
    contexte_depot

    local CHEMIN
    CHEMIN="$(chemin_attendu)"
    [ "$(realpath -m -- "$CHEMIN")" = "$(realpath -m -- "$PRINCIPAL")" ] \
        && refus "refus : $CHEMIN est le checkout principal du dépôt, il ne se retire pas."

    # Every refusal comes before the first removal.
    local ENREGISTRE
    ENREGISTRE="$(worktree_enregistre "$CHEMIN")"
    if [ -z "$ENREGISTRE" ] && [ -e "$CHEMIN" ]; then
        refus "refus : $CHEMIN existe mais n'est pas un worktree de $PRINCIPAL. Rien retiré."
    fi
    if [ -n "$ENREGISTRE" ] && [ "$ENREGISTRE" != "refs/heads/$BRANCHE" ]; then
        refus "refus : le worktree $CHEMIN porte ${ENREGISTRE#refs/heads/}, pas $BRANCHE. Rien retiré."
    fi
    if [ -n "$ENREGISTRE" ] && [ -d "$CHEMIN" ]; then
        local SALE
        SALE="$(git -C "$CHEMIN" status --porcelain --untracked-files=all)" \
            || refus "refus : git status en échec dans $CHEMIN. Rien retiré."
        [ -z "$SALE" ] || refus "refus : changements non commités dans $CHEMIN. Rien retiré.
$SALE"
    fi

    resoudre_defaut
    local DISTANTE rc
    DISTANTE="$(git -C "$PRINCIPAL" ls-remote --exit-code --heads origin "refs/heads/$BRANCHE" 2>/dev/null)"
    rc=$?
    case "$rc" in
        0) DISTANTE="${DISTANTE%%[[:space:]]*}" ;;
        2) DISTANTE="" ;;
        *) refus "refus : git ls-remote origin en échec, la branche distante ne peut pas être constatée. Rien retiré." ;;
    esac

    # Both tips must be contained: the local branch, and the remote one, which may carry
    # commits the local branch lacks.
    local AVANT=0
    if branche_locale_existe; then
        AVANT=1
        verifier_contenue "$BRANCHE" "refs/heads/$BRANCHE"
    fi
    [ -n "$DISTANTE" ] && verifier_contenue "origin/$BRANCHE" "$DISTANTE"

    # 1. The worktree. A failure stops here, before any branch is deleted.
    local PAR_ORCA=0 connu=1
    if [ -z "$ENREGISTRE" ]; then
        dire "worktree $CHEMIN : déjà absent."
    else
        if orca_joignable; then
            orca_connait "$CHEMIN"
            connu=$?
            [ "$connu" = 2 ] && refus "refus : la liste d'Orca est tronquée à $ORCA_LIMITE worktrees et ne montre pas $CHEMIN. Orca le connaît peut-être, il n'est pas retiré par git. Rien retiré."
        fi
        if [ "$connu" = 0 ]; then
            dire "rang 1 : Orca."
            "$CLI" worktree rm --worktree "path:$CHEMIN" --json >/dev/null \
                || refus "worktree $CHEMIN : échec de $CLI worktree rm. Branches laissées en place."
            PAR_ORCA=1
        else
            annoncer_rang_git "Orca est injoignable ou ne connaît pas ce worktree. Retrait par git."
            git -C "$PRINCIPAL" worktree remove "$CHEMIN" >&2 \
                || refus "worktree $CHEMIN : échec de git worktree remove. Branches laissées en place."
        fi
        dire "worktree $CHEMIN : retiré."
    fi

    local ECHECS=0
    # 2. The local branch. Orca deletes it after returning, so wait for it to finish.
    if [ "$PAR_ORCA" = 1 ] && [ "$AVANT" = 1 ]; then
        local tours=$((DELAI_BRANCHE * 5))
        while branche_locale_existe && [ "$tours" -gt 0 ]; do
            sleep 0.2
            tours=$((tours - 1))
        done
    fi
    if branche_locale_existe; then
        if git -C "$PRINCIPAL" branch -q -D "$BRANCHE" >&2; then
            dire "branche locale $BRANCHE : retirée."
        else
            ECHECS=$((ECHECS + 1))
            dire "branche locale $BRANCHE : échec de git branch -D."
        fi
    elif [ "$PAR_ORCA" = 1 ] && [ "$AVANT" = 1 ]; then
        dire "branche locale $BRANCHE : déjà absente, supprimée par Orca."
    else
        dire "branche locale $BRANCHE : déjà absente."
    fi

    # 3. The remote branch.
    if [ -n "$DISTANTE" ]; then
        if git -C "$PRINCIPAL" push -q origin --delete "$BRANCHE" >&2; then
            dire "branche distante origin/$BRANCHE : retirée."
        else
            ECHECS=$((ECHECS + 1))
            dire "branche distante origin/$BRANCHE : échec de git push --delete."
        fi
    else
        dire "branche distante origin/$BRANCHE : déjà absente."
    fi

    [ "$ECHECS" -eq 0 ]
}

# ---------------------------------------------------------------------------- dispatch

COMMANDE="${1:-}"
case "$COMMANDE" in create|remove) ;; *) usage ;; esac
shift
NOM="${1:-}"
[ -n "$NOM" ] || usage
case "$NOM" in -*) usage ;; esac
shift
entier_positif WORKTREE_ORCA_TIMEOUT "$DELAI"
entier_positif WORKTREE_BRANCHE_DELAI "$DELAI_BRANCHE"
case "$COMMANDE" in
    create) cmd_create "$@" ;;
    remove) cmd_remove "$@" ;;
esac
