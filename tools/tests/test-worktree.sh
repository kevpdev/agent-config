#!/usr/bin/env bash
# Répète `tools/worktree.sh` dans ses trois rangs, sur un dépôt jetable et un faux orca-ide.
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

# Le faux orca-ide : `status` joignable selon FAUX_JOIGNABLE, `worktree create` journalisé.
BIN="$T/bin"
mkdir -p "$BIN"
cat > "$BIN/faux-orca" <<'EOF'
#!/usr/bin/env bash
case "$1" in
    status) [ "${FAUX_JOIGNABLE:-0}" = 1 ] && r=true || r=false
            printf '{"result": {"runtime": {"reachable": %s}}}\n' "$r" ;;
    worktree) echo "$*" >> "$FAUX_JOURNAL"
              # Comme le vrai, un autre `path` (ici celui du dépôt) précède celui du worktree.
              printf '{"result": {"repo": {"path": "/depot/principal"}, "worktree": {"path": "/orca/chemin/rendu"}}}\n' ;;
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

# Rang 2 aussi : orca-ide installé, hors terminal Orca.
lancer 1 "" 1 create deux-bis
cas "rang 2 hors terminal Orca" "$(grep -c 'rang 2' "$T/err")" "1"

# Rang 3 : pas d'Orca du tout.
lancer 0 x 1 create trois
cas "rang 3 : code 0" "$?" "0"
cas "rang 3 : chemin au format d'Orca" "$(tail -1 "$T/out")" "$RACINE/projet/trois"
cas "rang 3 : branche <user>/<nom>" "$(git -C "$RACINE/projet/trois" branch --show-current)" "testeur/trois"
cas "rang 3 : annoncé" "$(grep -c 'rang 3' "$T/err")" "1"

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

[ "$echecs" -eq 0 ] && { echo "✓ 0 cas en échec."; exit 0; }
echo "✗ $echecs cas en échec."
exit 1
