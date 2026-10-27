#!/usr/bin/env python3
"""speak-on-stop.py — Stop hook for Claude Code: hands the final reply to hooks/speak.py.

Shim. The cleaning, the voice and the playback live in hooks/speak.py, shared
with OpenCode's voice plugin. speak.py keeps the reply for `lis`, and plays it
at once only in `auto` mode.

The final reply is `last_assistant_message` when the payload carries it. Else it
is read from `transcript_path`: the text blocks written after the last tool call
or the last user prompt, so the narration between tool calls is not spoken.

Always exits 0 and prints nothing: a Stop hook that fails or writes a decision
would keep Claude from stopping.
"""

import json
import os
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
SPEAK = os.path.join(REPO, "hooks", "speak.py")


def final_reply(path):
    texts = []
    try:
        with open(path, encoding="utf-8", errors="ignore") as fh:
            for line in fh:
                try:
                    entry = json.loads(line)
                except ValueError:
                    continue
                content = (entry.get("message") or {}).get("content")
                if entry.get("type") == "user":
                    # A tool result comes back as a user entry: it is not a new prompt.
                    if isinstance(content, str) or not all(
                            isinstance(b, dict) and b.get("type") == "tool_result" for b in content or []):
                        texts = []
                elif entry.get("type") == "assistant" and isinstance(content, list):
                    for block in content:
                        if not isinstance(block, dict):
                            continue
                        if block.get("type") == "tool_use":
                            texts = []
                        elif block.get("type") == "text":
                            texts.append(block.get("text", ""))
    except OSError:
        return ""
    return "\n\n".join(texts)


def main():
    try:
        payload = json.loads(sys.stdin.read())
    except ValueError:
        return
    if not isinstance(payload, dict):
        return
    reply = payload.get("last_assistant_message")
    if not isinstance(reply, str) or not reply.strip():
        reply = final_reply(payload.get("transcript_path") or "")
    if reply.strip():
        subprocess.run([sys.executable, SPEAK], input=reply, text=True,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


if __name__ == "__main__":
    main()
    sys.exit(0)
