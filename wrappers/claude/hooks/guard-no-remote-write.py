#!/usr/bin/env python3
"""guard-no-remote-write.py — PreToolUse hook for Claude Code: agent writes to preprod and prod.

Shim. The decision lives in hooks/no_remote_write.py, the translation in claude_adapter.py.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))

import claude_adapter  # noqa: E402

if __name__ == "__main__":
    claude_adapter.run("no_remote_write")
