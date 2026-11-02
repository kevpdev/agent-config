#!/usr/bin/env bash
# Replays `tools/worktree.sh create` and `remove` at their three ranks, on a throwaway repo
# and a fake orca-ide.
#
# Aucun accès réseau ni au vrai Orca : l'`origin` du dépôt est un dépôt nu local, la CLI
# Orca est un script posé dans un PATH temporaire (WORKTREE_ORCA_CLI), et la racine des
# worktrees est un dossier temporaire (ORCA_WORKSPACES).
#
# Sortie : 0 si tout passe, 1 si un cas échoue.
set -uo pipefail

ICI="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SCRIPT="$ICI/tools/worktree.sh"
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
case "$T" in "$HOME"/*) echo "refus : $T est sous le home." >&2; exit 1 ;; esac

# Le dépôt : origin/main a un commit d'avance sur le main local, comme le checkout
# d'agent-config qu'on ne met jamais à jour.
git init -q --bare -b main "$T/origin.git"
REPO="$T/Workspaces/projet"
git clone -q "$T/origin.git" "$REPO" 2>/dev/null
git -C "$REPO" config user.name testeur
git -C "$REPO" config user.email testeur@localhost
git -C "$REPO" commit -q --allow-empty -m "chore: init"
git -C "$REPO" push -q origin main
git -C "$REPO" remote set-head origin main
AUTRE="$T/autre"
git clone -q "$T/origin.git" "$AUTRE"
git -C "$AUTRE" -c user.name=x -c user.email=x@localhost commit -q --allow-empty -m "feat: en avance"
git -C "$AUTRE" push -q origin main
EN_AVANCE="$(git -C "$AUTRE" rev-parse HEAD)"

# The fake orca-ide: `status` is reachable per FAUX_JOIGNABLE, and slow by FAUX_DORT seconds.
# Every `worktree` call is logged.
# `worktree list` returns the single path FAUX_CONNU, and `truncated` per FAUX_TRONQUE.
# `worktree rm` fails when FAUX_RM_ECHEC=1. Otherwise it removes the worktree through git
# and, when FAUX_SUPPRIME_BRANCHE=1, deletes its branch FAUX_RETARD seconds later in the
# background, like the real one, which deletes it after returning.
BIN="$T/bin"
mkdir -p "$BIN"
cat > "$BIN/faux-orca" <<'EOF'
#!/usr/bin/env bash
case "$1" in
    status) sleep "${FAUX_DORT:-0}"
            [ "${FAUX_JOIGNABLE:-0}" = 1 ] && r=true || r=false
            printf '{"result": {"runtime": {"reachable": %s}}}\n' "$r" ;;
    worktree) echo "$*" >> "$FAUX_JOURNAL"
              case "$2" in
                  list) [ "${FAUX_TRONQUE:-0}" = 1 ] && t=true || t=false
                        printf '{"result": {"worktrees": [{"path": "%s"}], "truncated": %s}}\n' "${FAUX_CONNU:-/nulle/part}" "$t" ;;
                  rm) [ "${FAUX_RM_ECHEC:-0}" = 1 ] && exit 1
                      p="${4#path:}"
                      principal="$(dirname "$(git -C "$p" rev-parse --path-format=absolute --git-common-dir)")"
                      br="$(git -C "$p" branch --show-current)"
                      git -C "$principal" worktree remove "$p" || exit 1
                      if [ "${FAUX_SUPPRIME_BRANCHE:-0}" = 1 ]; then
                          (sleep "${FAUX_RETARD:-0}"; git -C "$principal" branch -q -D "$br") >/dev/null 2>&1 &
                      fi
                      printf '{"result": {"removed": true}}\n' ;;
                  # Like the real one, another `path` (here the repo's) comes before the worktree's.
                  *) printf '{"result": {"repo": {"path": "/depot/principal"}, "worktree": {"path": "/orca/chemin/rendu"}}}\n' ;;
              esac ;;
esac
EOF
chmod +x "$BIN/faux-orca"
export FAUX_JOURNAL="$T/journal"
RACINE="$T/workspaces"

lancer() {  # lancer AVEC_CLI ORCA_ID JOIGNABLE ARGS... ; stdout dans $T/out, stderr dans $T/err
    # Le dépôt courant est $ICI_DEPOT, $REPO par défaut.
    local avec="$1" id="$2" joignable="$3"
    shift 3
    local chemin="/usr/bin:/bin"
    [ "$avec" = 1 ] && chemin="$BIN:$chemin"
    (cd "${ICI_DEPOT:-$REPO}" && env -u ORCA_WORKTREE_ID PATH="$chemin" ORCA_WORKSPACES="$RACINE" \
        WORKTREE_ORCA_CLI=faux-orca FAUX_JOIGNABLE="$joignable" ${id:+ORCA_WORKTREE_ID="$id"} \
        bash "$SCRIPT" "$@" > "$T/out" 2> "$T/err")
}

# Rang 1 : Orca joignable, la création passe par lui.
lancer 1 x 1 create un --issue 7
cas "rang 1 : code 0" "$?" "0"
cas "rang 1 : chemin rendu par Orca" "$(tail -1 "$T/out")" "/orca/chemin/rendu"
cas "rang 1 : base origin/main et issue passées à Orca" \
    "$(grep -c -- '--name un --base-branch origin/main --no-parent --setup skip --json --issue 7' "$FAUX_JOURNAL")" "1"
cas "rang 1 : annoncé" "$(grep -c 'rang 1' "$T/err")" "1"

# Rang 2 : terminal Orca mais runtime injoignable.
lancer 1 x 0 create deux
cas "rang 2 : code 0" "$?" "0"
cas "rang 2 : chemin au format d'Orca" "$(tail -1 "$T/out")" "$RACINE/projet/deux"
cas "rang 2 : branche <user>/<nom>" "$(git -C "$RACINE/projet/deux" branch --show-current)" "testeur/deux"
cas "rang 2 : avertissement" "$(grep -c 'rang 2' "$T/err")" "1"
cas "rang 2 : Orca n'a rien créé" "$(wc -l < "$FAUX_JOURNAL" | tr -d ' ')" "1"

# Rang 2 aussi : `status` dépasse le délai, Orca compte comme injoignable.
FAUX_DORT=3 WORKTREE_ORCA_TIMEOUT=1 lancer 1 x 1 create deux-lent
cas "rang 2 sur délai dépassé : code 0" "$?" "0"
cas "rang 2 sur délai dépassé : annoncé" "$(grep -c 'rang 2' "$T/err")" "1"
cas "rang 2 sur délai dépassé : Orca n'a rien créé" "$(wc -l < "$FAUX_JOURNAL" | tr -d ' ')" "1"

# Rang 2 : l'issue ne se rattache pas, et le script le dit.
lancer 1 x 0 create deux-issue --issue 9
cas "rang 2 : issue non rattachée annoncée" "$(grep -c 'issue #9 non rattachée' "$T/err")" "1"

# Rang 2 aussi : orca-ide installé, hors terminal Orca.
lancer 1 "" 1 create deux-bis
cas "rang 2 hors terminal Orca" "$(grep -c 'rang 2' "$T/err")" "1"

# Rang 3 : pas d'Orca du tout.
lancer 0 x 1 create trois
cas "rang 3 : code 0" "$?" "0"
cas "rang 3 : chemin au format d'Orca" "$(tail -1 "$T/out")" "$RACINE/projet/trois"
cas "rang 3 : branche <user>/<nom>" "$(git -C "$RACINE/projet/trois" branch --show-current)" "testeur/trois"
cas "rang 3 : annoncé" "$(grep -c 'rang 3' "$T/err")" "1"

lancer 0 x 1 create trois-issue --issue 9
cas "rang 3 : issue non rattachée annoncée" "$(grep -c 'issue #9 non rattachée' "$T/err")" "1"

# La base est origin/main, pas le main local en retard.
cas "base : le commit en avance d'origin" "$(git -C "$RACINE/projet/trois" rev-parse HEAD)" "$EN_AVANCE"
cas "base : main local resté en retard" "$(git -C "$REPO" rev-parse main)" "$(git -C "$REPO" rev-parse "$EN_AVANCE^")"
cas "base : branche sans suivi d'origin/main" "$(git -C "$REPO" config branch.testeur/trois.merge || echo aucun)" "aucun"

# Lancé depuis un worktree, il remonte au dépôt principal.
(cd "$RACINE/projet/trois" && env -u ORCA_WORKTREE_ID PATH=/usr/bin:/bin ORCA_WORKSPACES="$RACINE" \
    bash "$SCRIPT" create quatre > "$T/out" 2> "$T/err")
cas "depuis un worktree : chemin sous le dépôt principal" "$(tail -1 "$T/out")" "$RACINE/projet/quatre"

# Refus, avec leur message.
lancer 0 "" 0 create trois
cas "refus : nom déjà pris, code 1" "$?" "1"
cas "refus : nom déjà pris, message" "$(grep -c 'le dossier existe déjà' "$T/err")" "1"
lancer 0 "" 0 create a/b
cas "refus : nom avec /, code 1" "$?" "1"
cas "refus : nom avec /, message" "$(grep -c 'contient un /' "$T/err")" "1"
lancer 0 "" 0 create
cas "refus : nom absent, code 1" "$?" "1"
cas "refus : nom absent, usage" "$(grep -c '^Usage' "$T/err")" "1"
lancer 0 "" 0 create cinq --force
cas "refus : option inconnue, code 1" "$?" "1"
cas "refus : option inconnue, message" "$(grep -c 'option inconnue : --force' "$T/err")" "1"
lancer 0 "" 0 create cinq --issue
cas "refus : --issue sans valeur, code 1" "$?" "1"
cas "refus : --issue sans valeur, message" "$(grep -c -- '--issue attend un numéro' "$T/err")" "1"

# Branche déjà là sans son dossier : refus, et aucun dossier créé.
git -C "$REPO" branch testeur/six main
lancer 0 "" 0 create six
cas "refus : branche existante, code 1" "$?" "1"
cas "refus : branche existante, message" "$(grep -c 'la branche existe déjà : testeur/six' "$T/err")" "1"
cas "refus : branche existante, aucun dossier" "$([ -e "$RACINE/projet/six" ] && echo present || echo absent)" "absent"

# git worktree add en échec : testeur/dix/x empêche de créer testeur/dix.
# Une racine créée par le script est retirée, une racine qui existait reste.
git -C "$REPO" branch testeur/dix/x main
RACINE_DIX="$T/racine-dix"
(cd "$REPO" && env -u ORCA_WORKTREE_ID PATH=/usr/bin:/bin ORCA_WORKSPACES="$RACINE_DIX" \
    bash "$SCRIPT" create dix > "$T/out" 2> "$T/err")
cas "add en échec, racine neuve : code 1" "$?" "1"
cas "add en échec, racine neuve : message" "$(grep -c 'git worktree add en échec' "$T/err")" "1"
cas "add en échec, racine neuve : racine retirée" "$([ -e "$RACINE_DIX" ] && echo present || echo absent)" "absent"
RACINE_PRE="$T/racine-pre"
mkdir -p "$RACINE_PRE"
(cd "$REPO" && env -u ORCA_WORKTREE_ID PATH=/usr/bin:/bin ORCA_WORKSPACES="$RACINE_PRE" \
    bash "$SCRIPT" create dix > "$T/out" 2> "$T/err")
cas "add en échec, racine préexistante : code 1" "$?" "1"
cas "add en échec, racine préexistante : racine gardée" "$([ -d "$RACINE_PRE" ] && echo present || echo absent)" "present"
cas "add en échec, racine préexistante : dossier du dépôt retiré" \
    "$([ -e "$RACINE_PRE/projet" ] && echo present || echo absent)" "absent"

# user.name vide : refus, sans dossier. La config globale de la machine est masquée.
SANS_USER="$T/Workspaces/sans-user"
git clone -q "$T/origin.git" "$SANS_USER"
RACINE_USER="$T/racine-user"
(cd "$SANS_USER" && env -u ORCA_WORKTREE_ID PATH=/usr/bin:/bin ORCA_WORKSPACES="$RACINE_USER" \
    GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1 bash "$SCRIPT" create onze > "$T/out" 2> "$T/err")
cas "refus : user.name vide, code 1" "$?" "1"
cas "refus : user.name vide, message" "$(grep -c 'user.name est vide' "$T/err")" "1"
cas "refus : user.name vide, aucun dossier" "$([ -e "$RACINE_USER" ] && echo present || echo absent)" "absent"

# Nom refusé par git check-ref-format : refus avant Orca et avant tout dossier.
RACINE_NEUVE="$T/racine-neuve"
: > "$FAUX_JOURNAL"
(cd "$REPO" && env PATH="$BIN:/usr/bin:/bin" ORCA_WORKSPACES="$RACINE_NEUVE" WORKTREE_ORCA_CLI=faux-orca \
    FAUX_JOIGNABLE=1 ORCA_WORKTREE_ID=x bash "$SCRIPT" create 'mauvais..nom' > "$T/out" 2> "$T/err")
cas "refus : check-ref-format, code 1" "$?" "1"
cas "refus : check-ref-format, message" "$(grep -c 'refusé par git check-ref-format' "$T/err")" "1"
cas "refus : check-ref-format, Orca pas appelé" "$(wc -l < "$FAUX_JOURNAL" | tr -d ' ')" "0"
cas "refus : check-ref-format, aucun dossier" "$([ -e "$RACINE_NEUVE" ] && echo present || echo absent)" "absent"

# origin/HEAD absent, origin joignable : set-head --auto le retrouve, sans avertissement.
SANS_HEAD="$T/Workspaces/sans-head"
git clone -q "$T/origin.git" "$SANS_HEAD"
git -C "$SANS_HEAD" config user.name testeur
git -C "$SANS_HEAD" remote set-head origin -d
ICI_DEPOT="$SANS_HEAD" lancer 0 "" 0 create sept
cas "origin/HEAD absent : code 0" "$?" "0"
cas "origin/HEAD absent : retrouvé par set-head" "$(git -C "$SANS_HEAD" symbolic-ref --short refs/remotes/origin/HEAD)" "origin/main"
cas "origin/HEAD absent : aucun repli annoncé" "$(grep -c 'origin/HEAD introuvable' "$T/err")" "0"

# Hors ligne : origin injoignable, base prise sur la dernière copie connue d'origin/main.
HORS_LIGNE="$T/Workspaces/hors-ligne"
git clone -q "$T/origin.git" "$HORS_LIGNE"
git -C "$HORS_LIGNE" config user.name testeur
CONNU="$(git -C "$HORS_LIGNE" rev-parse origin/main)"
git -C "$HORS_LIGNE" remote set-url origin "$T/injoignable.git"
ICI_DEPOT="$HORS_LIGNE" lancer 0 "" 0 create huit
cas "hors ligne : code 0" "$?" "0"
cas "hors ligne : fetch en échec annoncé" "$(grep -c "fetch d'origin en échec" "$T/err")" "1"
cas "hors ligne : base sur la dernière copie connue" "$(git -C "$RACINE/hors-ligne/huit" rev-parse HEAD)" "$CONNU"

# Hors ligne et sans origin/HEAD : repli sur origin/main, annoncé.
git -C "$HORS_LIGNE" remote set-head origin -d
ICI_DEPOT="$HORS_LIGNE" lancer 0 "" 0 create neuf
cas "repli origin/main : code 0" "$?" "0"
cas "repli origin/main : annoncé" "$(grep -c 'origin/HEAD introuvable, base prise sur origin/main' "$T/err")" "1"
cas "repli origin/main : base" "$(git -C "$RACINE/hors-ligne/neuf" rev-parse HEAD)" "$CONNU"

# ---------------------------------------------------------------------------- remove

present() { [ -e "$1" ] && echo present || echo absent; }
locale() { git -C "$REPO" rev-parse -q --verify "refs/heads/testeur/$1" >/dev/null && echo present || echo absent; }
distante() { git -C "$REPO" ls-remote --exit-code --heads origin "refs/heads/testeur/$1" >/dev/null && echo present || echo absent; }
enregistre() { git -C "$REPO" worktree list --porcelain | grep -c "^worktree $RACINE/projet/$1\$"; }
# Worktree registered, local branch, remote branch, in that order: "1/present/present".
etat() { echo "$(enregistre "$1")/$(locale "$1")/$(distante "$1")"; }

# preparer NAME [MERGED]: creates the worktree through git, commits in it, pushes the
# branch and, when MERGED is 1 (default), fast-forwards origin/main onto it.
preparer() {
    local nom="$1" mergee="${2:-1}" wt="$RACINE/projet/$1"
    lancer 0 "" 0 create "$nom"
    git -C "$wt" commit -q --allow-empty -m "feat: $nom"
    git -C "$wt" push -q origin "testeur/$nom" 2>/dev/null
    [ "$mergee" = 1 ] && git -C "$wt" push -q origin "HEAD:main" 2>/dev/null
    return 0
}
: > "$FAUX_JOURNAL"

# Rank 1: Orca is reachable and knows the worktree. It removes it, then deletes the local
# branch a second later. The script waits, finds it gone, and removes the remote one.
preparer r-orca
FAUX_CONNU="$RACINE/projet/r-orca" FAUX_SUPPRIME_BRANCHE=1 FAUX_RETARD=1 WORKTREE_BRANCHE_DELAI=4 \
    lancer 1 x 1 remove r-orca
cas "remove rank 1: exit 0" "$?" "0"
cas "remove rank 1: announced" "$(grep -c 'rang 1' "$T/err")" "1"
cas "remove rank 1: list asked with an explicit limit" \
    "$(grep -c -- "worktree list --repo path:$REPO --limit 1000 --json" "$FAUX_JOURNAL")" "1"
cas "remove rank 1: worktree rm handed to Orca" \
    "$(grep -c -- "worktree rm --worktree path:$RACINE/projet/r-orca --json" "$FAUX_JOURNAL")" "1"
cas "remove rank 1: worktree removed" "$(enregistre r-orca)/$(present "$RACINE/projet/r-orca")" "0/absent"
cas "remove rank 1: local branch deleted by Orca, reported already absent" \
    "$(grep -c 'branche locale testeur/r-orca : déjà absente, supprimée par Orca' "$T/err")/$(locale r-orca)" "1/absent"
cas "remove rank 1: remote branch removed" \
    "$(grep -c 'branche distante origin/testeur/r-orca : retirée' "$T/err")/$(distante r-orca)" "1/absent"

# Rank 1: Orca keeps the local branch, the script deletes it.
preparer r-orca-garde
FAUX_CONNU="$RACINE/projet/r-orca-garde" FAUX_SUPPRIME_BRANCHE=0 WORKTREE_BRANCHE_DELAI=1 \
    lancer 1 x 1 remove r-orca-garde
cas "remove rank 1, branch kept by Orca: exit 0" "$?" "0"
cas "remove rank 1, branch kept by Orca: deleted by the script" \
    "$(grep -c 'branche locale testeur/r-orca-garde : retirée' "$T/err")/$(locale r-orca-garde)" "1/absent"

# Rank 1: Orca fails to remove the worktree. Stop, exit 1, both branches left in place.
preparer r-orca-echec
FAUX_CONNU="$RACINE/projet/r-orca-echec" FAUX_RM_ECHEC=1 lancer 1 x 1 remove r-orca-echec
cas "remove rank 1, rm fails: exit 1" "$?" "1"
cas "remove rank 1, rm fails: message" "$(grep -c 'échec de faux-orca worktree rm. Branches laissées en place' "$T/err")" "1"
cas "remove rank 1, rm fails: nothing removed" "$(etat r-orca-echec)" "1/present/present"

# Truncated Orca list that does not show the path: refused, not removed through git.
FAUX_TRONQUE=1 lancer 1 x 1 remove r-orca-echec
cas "remove refused, truncated Orca list: exit 1" "$?" "1"
cas "remove refused, truncated Orca list: message" "$(grep -c 'liste d.Orca est tronquée' "$T/err")" "1"
cas "remove refused, truncated Orca list: nothing removed" "$(etat r-orca-echec)" "1/present/present"

# Rank 2: Orca is reachable but does not know this worktree, git removes it.
preparer r-inconnu
: > "$FAUX_JOURNAL"
lancer 1 x 1 remove r-inconnu
cas "remove rank 2, unknown to Orca: exit 0" "$?" "0"
cas "remove rank 2, unknown to Orca: announced" "$(grep -c 'rang 2' "$T/err")" "1"
cas "remove rank 2, unknown to Orca: no worktree rm" "$(grep -c 'worktree rm' "$FAUX_JOURNAL")" "0"
cas "remove rank 2, unknown to Orca: all removed" \
    "$(etat r-inconnu)/$(present "$RACINE/projet/r-inconnu")" "0/absent/absent/absent"

# Rank 2: Orca unreachable, git removes.
preparer r-deux
: > "$FAUX_JOURNAL"
FAUX_CONNU="$RACINE/projet/r-deux" lancer 1 x 0 remove r-deux
cas "remove rank 2, unreachable: exit 0" "$?" "0"
cas "remove rank 2, unreachable: announced" "$(grep -c 'rang 2' "$T/err")" "1"
cas "remove rank 2, unreachable: Orca not called" "$(wc -l < "$FAUX_JOURNAL" | tr -d ' ')" "0"
cas "remove rank 2, unreachable: all removed" "$(etat r-deux)" "0/absent/absent"

# Rank 3: no Orca, git removes.
preparer r-trois
lancer 0 x 1 remove r-trois
cas "remove rank 3: exit 0" "$?" "0"
cas "remove rank 3: announced" "$(grep -c 'rang 3' "$T/err")" "1"
cas "remove rank 3: three items removed" "$(grep -c ': retiré' "$T/err")" "3"
cas "remove rank 3: all removed" \
    "$(etat r-trois)/$(present "$RACINE/projet/r-trois")" "0/absent/absent/absent"

# Rank 3: git fails to remove a locked worktree. Stop, exit 1, branches left in place.
preparer r-verrou
git -C "$REPO" worktree lock "$RACINE/projet/r-verrou"
lancer 0 "" 0 remove r-verrou
cas "remove rank 3, git fails: exit 1" "$?" "1"
cas "remove rank 3, git fails: message" "$(grep -c 'échec de git worktree remove. Branches laissées en place' "$T/err")" "1"
cas "remove rank 3, git fails: nothing removed" "$(etat r-verrou)" "1/present/present"

# Refused on a modified tracked file, then on an untracked file: nothing removed.
preparer r-sale
echo x > "$RACINE/projet/r-sale/suivi"
git -C "$RACINE/projet/r-sale" add suivi
git -C "$RACINE/projet/r-sale" commit -q -m "feat: suivi"
git -C "$RACINE/projet/r-sale" push -q origin "HEAD:main" "testeur/r-sale" 2>/dev/null
echo y > "$RACINE/projet/r-sale/suivi"
lancer 0 "" 0 remove r-sale
cas "remove refused, tracked change: exit 1" "$?" "1"
cas "remove refused, tracked change: message" "$(grep -c 'changements non commités' "$T/err")" "1"
cas "remove refused, tracked change: nothing removed" "$(etat r-sale)" "1/present/present"
git -C "$RACINE/projet/r-sale" checkout -q -- suivi
echo z > "$RACINE/projet/r-sale/non-suivi"
lancer 0 "" 0 remove r-sale --abandon
cas "remove refused, untracked file, --abandon does not lift it: exit 1" "$?" "1"
cas "remove refused, untracked file: message" "$(grep -c 'changements non commités' "$T/err")" "1"
cas "remove refused, untracked file: nothing removed" "$(etat r-sale)" "1/present/present"

# Refused on an unmerged branch, then --abandon removes it.
preparer r-non-mergee 0
lancer 0 "" 0 remove r-non-mergee
cas "remove refused, unmerged: exit 1" "$?" "1"
cas "remove refused, unmerged: message" "$(grep -c "n'est pas contenue dans origin/main" "$T/err")" "1"
cas "remove refused, unmerged: squash hint" "$(grep -c 'mergée par squash' "$T/err")" "1"
cas "remove refused, unmerged: nothing removed" "$(etat r-non-mergee)" "1/present/present"
lancer 0 "" 0 remove r-non-mergee --abandon
cas "remove --abandon, unmerged: exit 0" "$?" "0"
cas "remove --abandon: announced" "$(grep -c 'retrait forcé par --abandon' "$T/err")" "2"
cas "remove --abandon: all removed" "$(etat r-non-mergee)" "0/absent/absent"

# Local branch merged, remote branch one commit ahead: refused, nothing removed.
preparer r-dist-avance
EN_PLUS="$(git -C "$REPO" commit-tree "testeur/r-dist-avance^{tree}" -p testeur/r-dist-avance -m "feat: en plus")"
git -C "$REPO" push -q origin "$EN_PLUS:refs/heads/testeur/r-dist-avance"
lancer 0 "" 0 remove r-dist-avance
cas "remove refused, remote ahead of a merged local: exit 1" "$?" "1"
cas "remove refused, remote ahead: message names the remote" \
    "$(grep -c "origin/testeur/r-dist-avance n'est pas contenue" "$T/err")" "1"
cas "remove refused, remote ahead: nothing removed" "$(etat r-dist-avance)" "1/present/present"

# Worktree already removed by hand, branches left: not an error, they go.
preparer r-orphelin
git -C "$REPO" worktree remove "$RACINE/projet/r-orphelin"
lancer 0 "" 0 remove r-orphelin
cas "remove, worktree already absent: exit 0" "$?" "0"
cas "remove, worktree already absent: reported" "$(grep -c "worktree $RACINE/projet/r-orphelin : déjà absent" "$T/err")" "1"
cas "remove, worktree already absent: branches removed" "$(locale r-orphelin)/$(distante r-orphelin)" "absent/absent"

# Lone local branch, unmerged and without worktree: refused like the others.
HORS_MAIN="$(git -C "$REPO" commit-tree "origin/main^{tree}" -p origin/main -m "feat: hors main")"
git -C "$REPO" branch testeur/r-seule "$HORS_MAIN"
lancer 0 "" 0 remove r-seule
cas "remove refused, lone unmerged branch: exit 1" "$?" "1"
cas "remove refused, lone unmerged branch: kept" "$(locale r-seule)" "present"

# Everything already absent: exit 0, three "already absent".
lancer 0 "" 0 remove jamais-cree
cas "remove, all absent: exit 0" "$?" "0"
cas "remove, all absent: three already absent" "$(grep -c 'déjà absent' "$T/err")" "3"

# A directory at the path that is not a worktree of the repo: refused, untouched.
mkdir -p "$RACINE/projet/r-etranger"
lancer 0 "" 0 remove r-etranger
cas "remove refused, foreign directory: exit 1" "$?" "1"
cas "remove refused, foreign directory: message" "$(grep -c "n'est pas un worktree de" "$T/err")" "1"
cas "remove refused, foreign directory: kept" "$(present "$RACINE/projet/r-etranger")" "present"

# The worktree at the path holds another branch: refused, nothing removed.
preparer r-autre
git -C "$RACINE/projet/r-autre" switch -q -c testeur/ailleurs
lancer 0 "" 0 remove r-autre
cas "remove refused, other branch: exit 1" "$?" "1"
cas "remove refused, other branch: message" "$(grep -c 'porte testeur/ailleurs, pas testeur/r-autre' "$T/err")" "1"
cas "remove refused, other branch: nothing removed" \
    "$(enregistre r-autre)/$(locale r-autre)/$(distante r-autre)/$(locale ailleurs)" "1/present/present/present"

# git ls-remote fails (origin unreachable): refused, nothing removed.
ICI_DEPOT="$HORS_LIGNE" lancer 0 "" 0 remove huit
cas "remove refused, ls-remote fails: exit 1" "$?" "1"
cas "remove refused, ls-remote fails: message" "$(grep -c 'git ls-remote origin en échec' "$T/err")" "1"
cas "remove refused, ls-remote fails: worktree kept" "$(present "$RACINE/hors-ligne/huit")" "present"
cas "remove refused, ls-remote fails: local branch kept" \
    "$(git -C "$HORS_LIGNE" rev-parse -q --verify refs/heads/testeur/huit >/dev/null && echo present)" "present"

# The computed path lands on the main checkout: refused.
PIEGE="$T/piege/boucle/boucle"
git clone -q "$T/origin.git" "$PIEGE"
git -C "$PIEGE" config user.name testeur
(cd "$PIEGE" && env -u ORCA_WORKTREE_ID PATH=/usr/bin:/bin ORCA_WORKSPACES="$T/piege" \
    bash "$SCRIPT" remove boucle > "$T/out" 2> "$T/err")
cas "remove refused, main checkout: exit 1" "$?" "1"
cas "remove refused, main checkout: message" "$(grep -c 'checkout principal' "$T/err")" "1"
cas "remove refused, main checkout: kept" "$(present "$PIEGE/.git")" "present"

# Delay variables must be positive integers, checked before any removal.
preparer r-delai
for v in 2.5 abc; do
    WORKTREE_BRANCHE_DELAI="$v" lancer 0 "" 0 remove r-delai
    cas "remove refused, WORKTREE_BRANCHE_DELAI=$v: exit and message" \
        "$?/$(grep -c "WORKTREE_BRANCHE_DELAI doit être un entier positif de secondes, reçu « $v »" "$T/err")" "1/1"
    WORKTREE_ORCA_TIMEOUT="$v" lancer 0 "" 0 remove r-delai
    cas "remove refused, WORKTREE_ORCA_TIMEOUT=$v: exit and message" \
        "$?/$(grep -c "WORKTREE_ORCA_TIMEOUT doit être un entier positif de secondes, reçu « $v »" "$T/err")" "1/1"
done
cas "remove refused, invalid delays: nothing removed" "$(etat r-delai)" "1/present/present"
WORKTREE_ORCA_TIMEOUT=abc lancer 0 "" 0 create r-delai-create
cas "create refused, invalid timeout: exit 1, no directory" \
    "$?/$(present "$RACINE/projet/r-delai-create")" "1/absent"

# Arguments.
lancer 0 "" 0 remove
cas "remove refused, missing name: usage" "$?/$(grep -c '^Usage' "$T/err")" "1/1"
lancer 0 "" 0 remove --abandon
cas "remove refused, option in place of the name: usage" "$?/$(grep -c '^Usage' "$T/err")" "1/1"
lancer 0 "" 0 create -x
cas "create refused, name starting with -: usage, no directory" \
    "$?/$(grep -c '^Usage' "$T/err")/$(present "$RACINE/projet/-x")" "1/1/absent"
lancer 0 "" 0 remove x --force
cas "remove refused, unknown option" "$?/$(grep -c 'option inconnue : --force' "$T/err")" "1/1"
lancer 0 "" 0 remove a/b
cas "remove refused, name with /" "$?/$(grep -c 'contient un /' "$T/err")" "1/1"

[ "$echecs" -eq 0 ] && { echo "✓ 0 cas en échec."; exit 0; }
echo "✗ $echecs cas en échec."
exit 1
