#!/usr/bin/env python3
"""guard-aidd-skill-lookup.py — PreToolUse hook for Claude Code: hand-typed delivery gesture in an AIDD repo (rules/aidd.md).

Shim. The decision lives in hooks/aidd_skill_lookup.py, the translation in claude_adapter.py.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))

import claude_adapter  # noqa: E402

if __name__ == "__main__":
    claude_adapter.run("aidd_skill_lookup")
