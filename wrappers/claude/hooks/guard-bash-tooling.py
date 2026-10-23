#!/usr/bin/env python3
"""guard-bash-tooling.py — PreToolUse hook for Claude Code: java/mvnw outside bash -lc 'sh ./mvnw', nested heredoc (rules/tooling.md).

Shim. The decision lives in hooks/bash_tooling.py, the translation in claude_adapter.py.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))

import claude_adapter  # noqa: E402

if __name__ == "__main__":
    claude_adapter.run("bash_tooling")
