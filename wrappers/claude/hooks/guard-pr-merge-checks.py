#!/usr/bin/env python3
"""guard-pr-merge-checks.py — PreToolUse hook for Claude Code: `gh pr merge` while a check is not green.

Shim. The decision lives in hooks/pr_merge_checks.py, the translation in claude_adapter.py.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))

import claude_adapter  # noqa: E402

if __name__ == "__main__":
    claude_adapter.run("pr_merge_checks")
