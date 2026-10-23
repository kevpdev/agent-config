#!/usr/bin/env bash
# bench.sh — installe le worktree dans un dossier de config à part, y lance une session
# courte, et rend ce qu'elle a chargé. `~/.claude` n'est jamais touché.
#
# POURQUOI CE SCRIPT
#   Tester le harnais dans `~/.claude` change les gardes de la session en cours, et un
#   garde introuvable bloque tous les appels Bash (rules/workspaces.md). Le banc est un
#   second dossier de config, visé par CLAUDE_CONFIG_DIR, rempli par tools/install.py.
#
#   Sous CLAUDE_CONFIG_DIR, `.credentials.json` vit dans ce dossier (doc d'authentification
#   de Claude Code). Le banc se connecte donc une fois par /login, puis le garde.
#
# ÉCHOUE FERMÉ
#   1  une fuite d'isolation, un journal vide, ou une empreinte de ~/.claude qui a changé
#   2  le banc n'est pas encore connecté : la commande de connexion est affichée
#
# Usage
#   bash tools/bench.sh claude                 banc ~/.claude-bench
#   bash tools/bench.sh claude --dir DIR       autre dossier
#   bash tools/bench.sh opencode [--dir DIR]   banc ~/.opencode-bench, cf. tools/bench/opencode.sh
set -uo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
AGENT="${1:-}"
shift || true
[ "$AGENT" = "opencode" ] && exec bash "$REPO/tools/bench/opencode.sh" "$@"
BANC="$HOME/.claude-bench"
while [ $# -gt 0 ]; do
    case "$1" in
        --dir) BANC="$2"; shift 2 ;;
        *) echo "bench — option inconnue : $1" >&2; exit 1 ;;
    esac
done

if [ "$AGENT" != "claude" ]; then
    echo "bench — agent non pris en charge : « $AGENT ». Connus : claude, opencode." >&2
    exit 1
fi

BANC="$(mkdir -p "$BANC" && cd "$BANC" && pwd)"
if [ "$BANC" = "$(cd "$HOME/.claude" 2>/dev/null && pwd)" ]; then
    echo "bench — refus : le banc ne peut pas être ~/.claude." >&2
    exit 1
fi

empreinte() {
    (cd "$HOME" && find .claude -type l -printf '%p -> %l\n' 2>/dev/null | sort)
    sha256sum "$HOME/.claude/settings.json" 2>/dev/null
}

AVANT="$(empreinte)"

# 1. Installer le worktree dans le banc.
if ! python3 "$REPO/tools/install.py" --agent claude --target "$BANC" --fix >/dev/null; then
    python3 "$REPO/tools/install.py" --agent claude --target "$BANC" --check >&2
    echo "bench — l'installation dans le banc a laissé des écarts." >&2
    exit 1
fi

# 2. Poser le hook de journal, clé propre au banc qu'install.py ne retire jamais. Un hook
#    de journal laissé par un autre worktree est remplacé, pas empilé : sa cible peut
#    avoir disparu, et bench-report.py le compterait comme un hook introuvable.
HOOK="bash $REPO/tools/bench/log-instructions.sh"
python3 - "$BANC/settings.json" "$HOOK" <<'PY'
import json, sys
chemin, commande = sys.argv[1], sys.argv[2]
with open(chemin, encoding="utf-8") as f:
    s = json.load(f)
hooks = s.setdefault("hooks", {})
groupes = [g for g in hooks.get("InstructionsLoaded", [])
           if not any(str(h.get("command", "")).endswith("/tools/bench/log-instructions.sh") for h in g.get("hooks", []))]
groupes.append({"matcher": "*", "hooks": [{"type": "command", "command": commande}]})
if groupes != hooks.get("InstructionsLoaded"):
    hooks["InstructionsLoaded"] = groupes
    with open(chemin, "w", encoding="utf-8") as f:
        json.dump(s, f, indent=2, ensure_ascii=False)
        f.write("\n")
PY

# 3. Connexion, une fois pour toutes.
if [ ! -f "$BANC/.credentials.json" ]; then
    echo "bench — le banc n'est pas connecté. Dans un autre terminal :" >&2
    echo "    CLAUDE_CONFIG_DIR=$BANC claude" >&2
    echo "puis /login, et relancer ce script." >&2
    exit 2
fi

# 4. Une session courte, depuis un dossier vide hors du home : aucun CLAUDE.md de projet
#    ne s'y charge. Lancée depuis un dossier sous $HOME, la remontée des dossiers parents
#    chargeait ~/.claude/CLAUDE.md comme mémoire de projet (constaté le 2026-10-22).
#    Le flux et le journal restent dans le banc, pour relire un rapport surprenant.
RUN="$BANC/last-run"
rm -rf "$RUN"
mkdir -p "$RUN"
VIDE="$(mktemp -d)"
trap 'rm -rf "$VIDE"' EXIT
case "$VIDE" in "$HOME"/*) echo "bench — refus : le dossier temporaire $VIDE est sous le home." >&2; exit 1 ;; esac
(cd "$VIDE" && CLAUDE_CONFIG_DIR="$BANC" BENCH_LOG="$RUN/instructions.log" \
    timeout 180 claude -p "Réponds ok." --output-format stream-json --verbose \
    --no-session-persistence --max-turns 1 --model haiku \
    < /dev/null > "$RUN/run.jsonl" 2> "$RUN/run.err")
rc_session=$?
[ "$rc_session" -ne 0 ] && { echo "bench — session en code $rc_session :" >&2; tail -5 "$RUN/run.err" >&2; }

# 5. Le rapport.
python3 "$REPO/tools/bench-report.py" --stream "$RUN/run.jsonl" --log "$RUN/instructions.log" --bench "$BANC" \
    --settings "$BANC/settings.json"
rc=$?

# 6. ~/.claude n'a pas bougé.
if [ "$(empreinte)" != "$AVANT" ]; then
    echo "✗ l'empreinte de ~/.claude a changé pendant le banc :" >&2
    diff <(echo "$AVANT") <(empreinte) >&2
    exit 1
fi
echo "✓ ~/.claude inchangé (liens et settings.json)."
exit "$rc"
