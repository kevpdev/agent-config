#!/usr/bin/env bash
# guard-no-claude-in-commit.sh — PreToolUse hook for Claude Code: AI attribution
# in commits and PRs, Conventional Commits format (rules/commit-convention.md).
#
# Shim. The decision lives in hooks/no_ai_in_commit.py, the translation and the
# Claude-only settings check in claude_adapter.py. The file keeps its name and
# its .sh: renaming it would move settings.json, the ~/.claude/scripts link and
# every README mention.
exec python3 "$(dirname "$(readlink -f "$0")")/claude_adapter.py" no_ai_in_commit
