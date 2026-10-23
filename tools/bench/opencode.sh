#!/usr/bin/env bash
# opencode.sh — branche OpenCode de tools/bench.sh. Installe le worktree dans un dossier de
# config à part, lance une session qui tente un commit signé puis un `ls`, et lit dans
# opencode.db ce que le plugin harness-guards en a fait, et quels skills la session expose.
# `~/.config/opencode` n'est jamais touché.
#
# POURQUOI CES VARIABLES
#   OPENCODE_CONFIG_DIR           le banc, fouillé pour ses plugins comme un `.opencode`
#                                 (doc config.mdx). Le dossier global reste chargé avant lui.
#   OPENCODE_DISABLE_CLAUDE_CODE  sans elle, OpenCode charge aussi ~/.claude, donc les règles
#                                 et skills du vivant (cadrage, Q0).
#   --standalone                  un serveur privé : le service de fond garderait l'ancienne
#                                 config et ses plugins.
#   Les identifiants vivent dans opencode.db (table `credential`), pas dans le dossier de
#   config : le banc est connecté dès que le vivant l'est.
#
# CE QUE LE BANC LAISSE : sa session reste dans ~/.local/share/opencode/opencode.db.
# Relocaliser la base couperait aussi les identifiants.
#
# ÉCHOUE FERMÉ : 1 si l'installation, la session ou le rapport échoue, ou si l'empreinte de
# ~/.config/opencode a changé.
#
# Usage : bash tools/bench/opencode.sh [--dir DIR]       banc ~/.opencode-bench par défaut
set -uo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
BANC="$HOME/.opencode-bench"
while [ $# -gt 0 ]; do
    case "$1" in
        --dir) BANC="$2"; shift 2 ;;
        *) echo "bench — option inconnue : $1" >&2; exit 1 ;;
    esac
done

VIVANT="$HOME/.config/opencode"
BANC="$(mkdir -p "$BANC" && cd "$BANC" && pwd)"
if [ "$BANC" = "$(cd "$VIVANT" 2>/dev/null && pwd)" ]; then
    echo "bench — refus : le banc ne peut pas être $VIVANT." >&2
    exit 1
fi

# Taille et date, pas de contenu : service.json porte des secrets.
empreinte() {
    (cd "$HOME" && find .config/opencode -printf '%p %y %s %T@ %l\n' 2>/dev/null | sort)
}
AVANT="$(empreinte)"

# 1. Installer le worktree dans le banc.
if ! python3 "$REPO/tools/install.py" --agent opencode --target "$BANC" --fix >/dev/null; then
    python3 "$REPO/tools/install.py" --agent opencode --target "$BANC" --check >&2
    echo "bench — l'installation dans le banc a laissé des écarts." >&2
    exit 1
fi

# 2. Un dépôt jetable hors du home, avec un message de commit signé dans un fichier. La
#    chaîne est coupée en deux ici pour ne jamais apparaître entière dans le repo.
DEPOT="$(mktemp -d)"
trap 'rm -rf "$DEPOT"' EXIT
case "$DEPOT" in "$HOME"/*) echo "bench — refus : le dossier temporaire $DEPOT est sous le home." >&2; exit 1 ;; esac
git -C "$DEPOT" init -q
git -C "$DEPOT" -c user.name=bench -c user.email=bench@localhost commit -q --allow-empty -m "chore: init"
printf 'fix: x\n\n%s%s: Claude <noreply@anthropic.com>\n' "Co-Authored" "-By" > "$DEPOT/msg.txt"

# 3. La session. Le flux reste dans le banc, pour relire un rapport surprenant.
RUN="$BANC/last-run"
rm -rf "$RUN"
mkdir -p "$RUN"
CONSIGNE="Lance exactement ces deux commandes shell dans le dossier courant, chacune dans son propre appel d'outil, sans les modifier ni les réessayer, même si la première échoue : d'abord « git commit --allow-empty -F msg.txt », puis « ls ». Réponds ensuite « fini »."
(cd "$DEPOT" && OPENCODE_CONFIG_DIR="$BANC" OPENCODE_DISABLE_CLAUDE_CODE=1 \
    timeout 300 opencode run --standalone --auto --format json "$CONSIGNE" \
    < /dev/null > "$RUN/run.jsonl" 2> "$RUN/run.err")
rc_session=$?
[ "$rc_session" -ne 0 ] && { echo "bench — session en code $rc_session :" >&2; tail -5 "$RUN/run.err" >&2; }

# 4. Le rapport, lu dans la base.
python3 "$REPO/tools/bench/opencode-report.py" --dir "$DEPOT" --skills "$REPO/skills" --rules "$REPO/rules"
rc=$?

# 5. ~/.config/opencode n'a pas bougé.
if [ "$(empreinte)" != "$AVANT" ]; then
    echo "✗ l'empreinte de $VIVANT a changé pendant le banc :" >&2
    diff <(echo "$AVANT") <(empreinte) >&2
    exit 1
fi
echo "✓ $VIVANT inchangé."
exit "$rc"
