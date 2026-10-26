#!/usr/bin/env bash
# bascule.sh — fait avancer le checkout principal sur origin/main et réinstalle les deux
# agents dans le même processus. Une sauvegarde est prise avant, `--retour` la restaure.
#
# POURQUOI UNE SEULE COMMANDE
#   Les liens de ~/.claude visent le checkout principal. Dès que `main` avance, ceux dont la
#   source a bougé pendent, et un garde introuvable bloque tous les appels Bash
#   (rules/workspaces.md, cadrage Q0). L'avance et `install.py --fix` tournent donc ici l'un
#   après l'autre, sans rendre la main.
#
# POURQUOI DEPUIS LE WORKTREE
#   Avant l'avance, le checkout principal ne contient pas encore ce script. On le lance
#   depuis `agent-config-v2`, et il exige que origin/main contienne le commit d'où il vient.
#
# CE QUI EST SAUVEGARDÉ, dans ETAT/<horodatage>/
#   liens-claude.txt, liens-opencode.txt   les liens vers REPO, `chemin -> cible`
#   dossiers-absents.txt                   les dossiers gérés qui n'existaient pas
#   settings.json, opencode.json, zshrc    les fichiers que le harnais écrit
#   opencode.json.absent                   marqueur, quand il n'existait pas
#   sha                                    le commit de main avant l'avance
#   Aucune archive de ~/.config/opencode : elle lirait service.json.
#
# ÉCHOUE FERMÉ
#   1  une précondition refusée (rien n'est écrit), une étape en échec (la commande de
#      retour est imprimée), ou un retour qui ne rend pas l'état sauvegardé
#
# Usage
#   bash tools/bascule.sh [--repo DIR] [--claude DIR] [--opencode DIR] [--zshrc FILE] [--etat DIR]
#   bash tools/bascule.sh --retour --etat ETAT/<horodatage> [--repo DIR] [--claude DIR] [--opencode DIR] [--zshrc FILE]
set -uo pipefail

ICI="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO="$HOME/Developpement/Workspaces/agent-config"
CLAUDE="$HOME/.claude"
OPENCODE="$HOME/.config/opencode"
ZSHRC="$HOME/.zshrc"
ETAT="$HOME/.local/state/agent-config/bascule"
RETOUR=0
LIGNE="export OPENCODE_DISABLE_CLAUDE_CODE_SKILLS=1"

while [ $# -gt 0 ]; do
    case "$1" in
        --repo) REPO="$2"; shift 2 ;;
        --claude) CLAUDE="$2"; shift 2 ;;
        --opencode) OPENCODE="$2"; shift 2 ;;
        --zshrc) ZSHRC="$2"; shift 2 ;;
        --etat) ETAT="$2"; shift 2 ;;
        --retour) RETOUR=1; shift ;;
        *) echo "bascule — option inconnue : $1" >&2; exit 1 ;;
    esac
done

REPO="$(cd "$REPO" && pwd)" || exit 1
refus() { echo "bascule — refus : $*" >&2; exit 1; }

liens() {  # liens() CIBLE : les liens de CIBLE qui visent REPO, triés
    [ -d "$1" ] || return 0
    find "$1" -type l -printf '%p -> %l\n' 2>/dev/null | grep -F -- " -> $REPO/" | sort
}

dossiers_geres() {  # les dossiers que le manifeste de l'agent remplit, sans doublon
    python3 "$1/tools/install.py" --agent "$2" --target "$3" --repo "$REPO" --list \
        | sed 's/ -> .*//' | xargs -r -n1 dirname | sort -u
}

empreinte() {  # empreinte FICHIER : son sha256, ou « absent »
    if [ -e "$1" ]; then sha256sum < "$1" | cut -d' ' -f1; else echo absent; fi
}

# ---------------------------------------------------------------------------- retour
if [ "$RETOUR" -eq 1 ]; then
    S="$ETAT"
    [ -f "$S/sha" ] || refus "$S n'est pas une sauvegarde de bascule (pas de fichier sha)."
    sha="$(cat "$S/sha")"
    git -C "$REPO" switch -q -C main "$sha" || refus "git switch -C main $sha a échoué."

    for paire in "claude:$CLAUDE" "opencode:$OPENCODE"; do
        agent="${paire%%:*}"; cible="${paire#*:}"
        # Retirer d'abord les liens vers REPO que la sauvegarde ne porte pas.
        comm -23 <(liens "$cible") <(sort "$S/liens-$agent.txt") | while IFS= read -r l; do
            rm -f -- "${l%% -> *}"
        done
        while IFS= read -r l; do
            [ -n "$l" ] || continue
            mkdir -p "$(dirname "${l%% -> *}")"
            ln -sfn -- "${l#* -> }" "${l%% -> *}"
        done < "$S/liens-$agent.txt"
    done
    cp -p "$S/settings.json" "$CLAUDE/settings.json"
    if [ -f "$S/opencode.json.absent" ]; then rm -f "$OPENCODE/opencode.json"; else cp -p "$S/opencode.json" "$OPENCODE/opencode.json"; fi
    cp -p "$S/zshrc" "$ZSHRC"
    # Les dossiers créés par la bascule, s'ils sont redevenus vides.
    tac "$S/dossiers-absents.txt" | while IFS= read -r d; do
        [ -n "$d" ] && rmdir --ignore-fail-on-non-empty -- "$d" 2>/dev/null
    done

    rc=0
    for paire in "claude:$CLAUDE" "opencode:$OPENCODE"; do
        agent="${paire%%:*}"; cible="${paire#*:}"
        if ! diff <(sort "$S/liens-$agent.txt") <(liens "$cible") >&2; then
            echo "✗ liens de $cible différents de la sauvegarde." >&2; rc=1
        fi
    done
    for f in "$CLAUDE/settings.json:settings.json" "$ZSHRC:zshrc"; do
        [ "$(empreinte "${f%%:*}")" = "$(empreinte "$S/${f#*:}")" ] || { echo "✗ ${f%%:*} différent de la sauvegarde." >&2; rc=1; }
    done
    [ "$(git -C "$REPO" rev-parse HEAD)" = "$sha" ] || { echo "✗ $REPO n'est pas sur $sha." >&2; rc=1; }
    [ "$rc" -eq 0 ] && echo "✓ retour fait : $REPO sur ${sha:0:7}, liens et fichiers restaurés depuis $S."
    exit "$rc"
fi

# ------------------------------------------------------------------- préconditions
[ -z "$(git -C "$REPO" status --porcelain)" ] || refus "$REPO n'est pas propre."
[ "$(git -C "$REPO" branch --show-current)" = "main" ] || refus "$REPO n'est pas sur main."
git -C "$REPO" fetch -q origin || refus "git fetch origin a échoué dans $REPO."
source_sha="$(git -C "$ICI" rev-parse HEAD)"
git -C "$REPO" merge-base --is-ancestor "$source_sha" origin/main \
    || refus "origin/main ne contient pas ${source_sha:0:7}, le commit de ce script. La PR vers main est-elle mergée ?"
git -C "$REPO" merge-base --is-ancestor HEAD origin/main || refus "main ne peut pas avancer en avance rapide sur origin/main."
for paire in "claude:$CLAUDE" "opencode:$OPENCODE"; do
    agent="${paire%%:*}"; cible="${paire#*:}"
    bloquants="$(python3 "$ICI/tools/install.py" --agent "$agent" --target "$cible" --repo "$REPO" --check 2>&1 \
        | grep -E '^  (PAS UN LIEN|INTRUS) ')"
    [ -z "$bloquants" ] || refus "écarts à traiter à la main dans $cible :
$bloquants"
done

# ---------------------------------------------------------------------- sauvegarde
S="$ETAT/$(date +%Y%m%d-%H%M%S)"
mkdir -p "$S" || exit 1
git -C "$REPO" rev-parse HEAD > "$S/sha"
liens "$CLAUDE" > "$S/liens-claude.txt"
liens "$OPENCODE" > "$S/liens-opencode.txt"
{ dossiers_geres "$ICI" claude "$CLAUDE" | sed "s|^|$CLAUDE/|"
  dossiers_geres "$ICI" opencode "$OPENCODE" | sed "s|^|$OPENCODE/|"
  echo "$OPENCODE"; } | sort -u | while IFS= read -r d; do [ -d "$d" ] || echo "$d"; done > "$S/dossiers-absents.txt"
cp -p "$CLAUDE/settings.json" "$S/settings.json" || refus "pas de $CLAUDE/settings.json à sauvegarder."
if [ -f "$OPENCODE/opencode.json" ]; then cp -p "$OPENCODE/opencode.json" "$S/opencode.json"; else : > "$S/opencode.json.absent"; fi
cp -p "$ZSHRC" "$S/zshrc" || refus "pas de $ZSHRC à sauvegarder."
echo "bascule — sauvegarde : $S"
RETOUR_CMD="bash $ICI/tools/bascule.sh --retour --etat $S --repo $REPO --claude $CLAUDE --opencode $OPENCODE --zshrc $ZSHRC"

# ------------------------------------------------------------------------ bascule
echec() {
    echo "✗ bascule arrêtée : $*" >&2
    echo "  Retour : $RETOUR_CMD" >&2
    exit 1
}
git -C "$REPO" merge -q --ff-only origin/main || echec "git merge --ff-only origin/main."
python3 "$REPO/tools/install.py" --agent claude --target "$CLAUDE" --fix || echec "install.py claude --fix."
python3 "$REPO/tools/install.py" --agent opencode --target "$OPENCODE" --fix || echec "install.py opencode --fix."
if ! grep -qxF "$LIGNE" "$ZSHRC"; then
    printf '\n# opencode : les skills du repo passent par ~/.config/opencode/skills, pas par ~/.claude/skills (tâche 7)\n%s\n' \
        "$LIGNE" >> "$ZSHRC" || echec "écriture de $ZSHRC."
fi
python3 "$REPO/tools/install.py" --agent claude --target "$CLAUDE" --check >/dev/null || echec "écarts restants sur $CLAUDE."
python3 "$REPO/tools/install.py" --agent opencode --target "$OPENCODE" --check >/dev/null || echec "écarts restants sur $OPENCODE."
pendants="$(find "$CLAUDE" "$OPENCODE" -xtype l -lname "$REPO/*" 2>/dev/null)"
[ -z "$pendants" ] || echec "liens pendants :
$pendants"

echo "✓ bascule faite : $REPO sur $(git -C "$REPO" rev-parse --short HEAD), 0 écart sur $CLAUDE et $OPENCODE."
echo "  Retour : $RETOUR_CMD"
