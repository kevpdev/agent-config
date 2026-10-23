#!/usr/bin/env python3
"""check.py — run the guard core on one normalized event.

Input, one JSON object on stdin:

    {"event": "pre_tool", "action": "shell|edit|read", "command": "...",
     "paths": ["..."], "cwd": "...", "session": "...",
     "skills_used": ["aidd-dev:01-plan"] | null}

`skills_used` is null when the agent cannot tell which skills ran.

Exit codes:
    0  every guard lets the action through
    2  refused, the reason is on stderr
    1  unreadable input: no verdict. What to do with it is the adapter's call.

Usage:
    python3 hooks/check.py [--guard NAME ...]

One process runs every guard: an agent that spawns a process per evaluation
(OpenCode's plugin) pays one, not four.
"""

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from hooks import GUARDS, first_refusal  # noqa: E402


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--guard", action="append", choices=sorted(GUARDS),
                        help="run only this guard (repeatable)")
    args = parser.parse_args(argv)

    try:
        event = json.loads(sys.stdin.read())
        if not isinstance(event, dict):
            raise ValueError("not a JSON object")
    except ValueError as exc:
        print("check.py: entrée illisible (%s), pas de verdict rendu." % exc, file=sys.stderr)
        return 1

    reason = first_refusal(event, args.guard)
    if reason:
        print(reason, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
