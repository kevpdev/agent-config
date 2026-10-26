#!/usr/bin/env bash
# Répète `tools/bascule.sh` sur un clone et des cibles jetables, jamais sur le vivant.
#
# La cible Claude est refaite depuis la vraie liste de liens d'avant la refonte
# (audits/2026-10-22-liens-pre-v2.txt), réécrite vers le clone. Un `.claude.json` porte
# déjà codegraph, pour que `--fix` ne lance pas l'installateur. Aucun accès réseau :
# l'`origin` du clone est un dépôt nu local, dont `main` porte le commit testé.
#
# Sortie : 0 si tout passe, 1 si un cas échoue.
set -uo pipefail

ICI="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
BASCULE="$ICI/tools/bascule.sh"
LIGNE="export OPENCODE_DISABLE_CLAUDE_CODE_SKILLS=1"
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

# Le dépôt : origin/main porte le commit testé, main local reste sur pre-v2.
git clone -q --bare "$ICI" "$T/origin.git"
git -C "$T/origin.git" update-ref refs/heads/main "$(git -C "$ICI" rev-parse HEAD)"
REPO="$T/Workspaces/agent-config"
git clone -q "$T/origin.git" "$REPO"
PRE="$(git -C "$REPO" rev-parse "pre-v2^{commit}")"
git -C "$REPO" switch -q -C main "$PRE"

# Les cibles, dans l'état d'avant la refonte.
C="$T/claude"; O="$T/opencode"; Z="$T/zshrc"; E="$T/etat"
while IFS= read -r l; do
    rel="${l%% -> *}"; lien="$C/${rel#\~/.claude/}"
    source="${l#* -> }"; source="$REPO/${source#\~/Developpement/Workspaces/agent-config/}"
    mkdir -p "$(dirname "$lien")"
    ln -s "$source" "$lien"
done < "$ICI/audits/2026-10-22-liens-pre-v2.txt"
git -C "$REPO" show pre-v2:wrappers/claude/settings.json > "$C/settings.json"
echo '{"mcpServers": {"codegraph": {"type": "stdio", "command": "codegraph"}}}' > "$C/.claude.json"
mkdir -p "$O"
echo '{"plugin": []}' > "$O/tui.json"
printf '# opencode\nexport PATH=/opt/opencode/bin:$PATH\n' > "$Z"

liens() { find "$1" -type l -printf '%p -> %l\n' 2>/dev/null | grep -F -- " -> $REPO/" | sort; }
empreinte() { if [ -e "$1" ]; then sha256sum < "$1" | cut -d' ' -f1; else echo absent; fi; }
lancer() { bash "$BASCULE" --repo "$REPO" --claude "$C" --opencode "$O" --zshrc "$Z" --etat "$E" "$@" >"$T/sortie" 2>&1; }
check() { (cd "$REPO" && python3 tools/install.py --agent "$1" --target "$2" --check >/dev/null 2>&1); echo $?; }

AVANT_C="$(liens "$C")"; AVANT_S="$(empreinte "$C/settings.json")"; AVANT_Z="$(empreinte "$Z")"
TUI="$(empreinte "$O/tui.json")"
cas "la cible Claude jetable reprend les 68 liens d'avant" "$(echo "$AVANT_C" | wc -l)" 68

# Refus : rien ne doit être écrit.
git -C "$T/origin.git" update-ref refs/heads/main "$PRE"
lancer; rc=$?
cas "origin/main sans le commit du script : refus" "$rc $(ls "$E" 2>/dev/null | wc -l)" "1 0"
git -C "$T/origin.git" update-ref refs/heads/main "$(git -C "$ICI" rev-parse HEAD)"
touch "$REPO/sale"
lancer; rc=$?
cas "dépôt sale : refus, rien n'est écrit" "$rc $(ls "$E" 2>/dev/null | wc -l) $(git -C "$REPO" rev-parse HEAD)" "1 0 $PRE"
rm -f "$REPO/sale"

# Bascule.
lancer; rc=$?
[ "$rc" -eq 0 ] || sed 's/^/        /' "$T/sortie"
cas "bascule : code 0" "$rc" 0
cas "bascule : main a avancé sur le commit testé" "$(git -C "$REPO" rev-parse HEAD)" "$(git -C "$ICI" rev-parse HEAD)"
cas "bascule : 0 écart sur les deux cibles" "$(check claude "$C") $(check opencode "$O")" "0 0"
cas "bascule : aucun lien ne pend" "$(find "$C" "$O" -xtype l | wc -l)" 0
cas "bascule : tui.json non géré, intact" "$(empreinte "$O/tui.json")" "$TUI"
cas "bascule : la ligne du .zshrc posée une fois" "$(grep -cxF "$LIGNE" "$Z")" 1
S="$E/$(ls "$E" | head -1)"

# Retour.
bash "$BASCULE" --retour --etat "$S" --repo "$REPO" --claude "$C" --opencode "$O" --zshrc "$Z" >"$T/sortie" 2>&1; rc=$?
[ "$rc" -eq 0 ] || sed 's/^/        /' "$T/sortie"
cas "retour : code 0" "$rc" 0
cas "retour : main revenu sur pre-v2" "$(git -C "$REPO" rev-parse HEAD) $(git -C "$REPO" branch --show-current)" "$PRE main"
cas "retour : les liens d'avant, à l'identique" "$(liens "$C")" "$AVANT_C"
cas "retour : settings.json et .zshrc d'avant" "$(empreinte "$C/settings.json") $(empreinte "$Z")" "$AVANT_S $AVANT_Z"
cas "retour : opencode.json retiré, skills/ aussi" "$(empreinte "$O/opencode.json") $(ls -d "$O/skills" 2>/dev/null | wc -l)" "absent 0"
cas "retour : aucun lien vers le clone sous OpenCode" "$(liens "$O" | wc -l)" 0

# Seconde bascule, la ligne du .zshrc déjà là.
echo "$LIGNE" >> "$Z"
sleep 1  # l'horodatage de la sauvegarde est à la seconde
lancer; rc=$?
cas "seconde bascule : code 0, 0 écart" "$rc $(check claude "$C") $(check opencode "$O")" "0 0 0"
cas "seconde bascule : la ligne du .zshrc n'est pas doublée" "$(grep -cxF "$LIGNE" "$Z")" 1

echo "$([ "$echecs" -eq 0 ] && echo ✓ || echo ✗) $echecs échec(s)."
[ "$echecs" -eq 0 ]
