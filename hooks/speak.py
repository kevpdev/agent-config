#!/usr/bin/env python3
"""speak.py — read an agent's reply aloud with Piper, for every agent.

Input: the reply as markdown on stdin, from an agent's end-of-turn hook. The
text is cleaned for the ear (code blocks, tables and URLs dropped, markdown
markers removed, units and anglicisms respelled), cut at `max_chars` on a
sentence end, and kept as the last reply in $XDG_RUNTIME_DIR/agent-voice/.

It is played only in `auto` mode. In `on-demand` mode, the default, the human
asks for it with `lis` (tools/lis), which runs `--last`. Playback is
`piper --output_raw | aplay` in a detached session, so the caller returns at
once, and a new reading stops the one still playing.

Settings live in speak.json next to this file, or in the file AGENT_VOICE_CONFIG
names. AGENT_VOICE=0 turns `auto` playback off.

Never fails the caller: a missing Piper or voice prints one line on stderr and
exits 0. A broken voice must not block an agent.

Usage:
    python3 hooks/speak.py [--dry-run]     # from a hook; --dry-run prints the cleaned text
    python3 hooks/speak.py --last          # play the last reply
    python3 hooks/speak.py --stop          # stop the current reading
"""

import argparse
import json
import os
import re
import signal
import subprocess
import sys

HERE = os.path.dirname(os.path.realpath(__file__))
CONFIG = os.environ.get("AGENT_VOICE_CONFIG") or os.path.join(HERE, "speak.json")
STATE = os.path.join(os.environ.get("XDG_RUNTIME_DIR") or "/tmp", "agent-voice")
PIDFILE = os.path.join(STATE, "player.pid")
LAST = os.path.join(STATE, "last.txt")

FENCE = re.compile(r"^\s*(```|~~~).*?^\s*\1[^\n]*$", re.S | re.M)
LINK = re.compile(r"\[([^\]]*)\]\([^)]*\)")
URL = re.compile(r"https?://\S+")
INLINE_CODE = re.compile(r"`([^`]*)`")
EMPHASIS = re.compile(r"(\*\*|__|\*)(\S(?:.*?\S)?)\1")
SKIPPED_LINE = re.compile(r"^\s*(\||@\{view:|-{3,}\s*$|\[!\w+\]\s*$)")
LINE_PREFIX = re.compile(r"^\s*(#{1,6}\s+|>\s?(\[!\w+\]\s*)?|[-*+]\s+|\d+[.)]\s+)+")
SENTENCE_END = re.compile(r"[.!?…:;]$")


def load_config():
    with open(CONFIG, encoding="utf-8") as fh:
        config = json.load(fh)
    for key in ("piper", "voices_dir"):
        config[key] = os.path.expanduser(config[key])
    return config


def enabled(config):
    flag = os.environ.get("AGENT_VOICE")
    if flag is not None:
        return flag.strip().lower() not in ("0", "off", "false", "no", "")
    return bool(config.get("enabled", True))


def clean(text):
    """Markdown reply → plain sentences fit to be spoken."""
    text = FENCE.sub("", text)
    sentences = []
    for line in text.splitlines():
        if SKIPPED_LINE.match(line):
            continue
        line = LINE_PREFIX.sub("", line)
        line = LINK.sub(r"\1", line)
        line = URL.sub("", line)
        line = INLINE_CODE.sub(r"\1", line)
        line = EMPHASIS.sub(r"\2", line)
        line = " ".join(line.split())
        if not line:
            continue
        sentences.append(line if SENTENCE_END.search(line) else line + ".")
    return " ".join(sentences)


def pronounce(text, config):
    """Spell units and anglicisms the way espeak-ng's French rules will say them right.

    Piper's network only voices the phonemes espeak-ng hands it, and espeak-ng
    reads every word as French: `ms` letter by letter, `pipeline` as French.
    """
    units = config.get("units") or {}
    if units:
        alternation = "|".join(re.escape(u) for u in sorted(units, key=len, reverse=True))
        text = re.sub(r"(\d+(?:[.,]\d+)?)\s*(%s)(?=[^\w]|$)" % alternation,
                      lambda m: "%s %s" % (m.group(1), units[m.group(2)]), text)
    lexicon = {k.lower(): v for k, v in (config.get("lexicon") or {}).items()}
    if lexicon:
        alternation = "|".join(re.escape(w) for w in sorted(lexicon, key=len, reverse=True))
        text = re.sub(r"(?<!\w)(%s)(?!\w)" % alternation,
                      lambda m: lexicon[m.group(1).lower()], text, flags=re.I)
    return text


def truncate(text, max_chars):
    """Cut at the last sentence end before max_chars, or hard at max_chars."""
    if len(text) <= max_chars:
        return text
    head = text[:max_chars]
    ends = [m.end() for m in re.finditer(r"[.!?…](\s|$)", head)]
    return head[:ends[-1]].strip() if ends else head.strip()


def stop_current():
    try:
        with open(PIDFILE) as fh:
            pgid = int(fh.read().strip())
        os.killpg(pgid, signal.SIGTERM)
    except (OSError, ValueError):
        pass


def play(text, config):
    model = os.path.join(config["voices_dir"], config["voice"] + ".onnx")
    for path in (config["piper"], model):
        if not os.path.exists(path):
            print("speak.py: %s introuvable, lecture ignorée." % path, file=sys.stderr)
            return
    with open(model + ".json", encoding="utf-8") as fh:
        rate = json.load(fh)["audio"]["sample_rate"]
    pipeline = "%s -q -m %s --length_scale %s --output_raw | aplay -q -r %d -f S16_LE -t raw -" % (
        _quote(config["piper"]), _quote(model), float(config.get("length_scale", 1.0)), rate)
    stop_current()
    os.makedirs(STATE, exist_ok=True)
    proc = subprocess.Popen(["sh", "-c", pipeline], stdin=subprocess.PIPE,
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                            start_new_session=True)
    with open(PIDFILE, "w") as fh:
        fh.write(str(proc.pid))
    proc.stdin.write(text.encode("utf-8"))
    proc.stdin.close()


def _quote(value):
    return "'" + str(value).replace("'", "'\\''") + "'"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    action = parser.add_mutually_exclusive_group()
    action.add_argument("--dry-run", action="store_true", help="print the cleaned text, play nothing")
    action.add_argument("--last", action="store_true", help="play the last reply")
    action.add_argument("--stop", action="store_true", help="stop the current reading")
    args = parser.parse_args(argv)
    if args.stop:
        stop_current()
        return 0
    try:
        config = load_config()
    except (OSError, ValueError) as exc:
        print("speak.py: config illisible (%s), lecture ignorée." % exc, file=sys.stderr)
        return 0
    try:
        if args.last:
            try:
                with open(LAST, encoding="utf-8") as fh:
                    text = fh.read()
            except OSError:
                print("speak.py: aucune réponse mémorisée.", file=sys.stderr)
                return 0
            if text:
                play(text, config)
            return 0
        text = truncate(pronounce(clean(sys.stdin.read()), config), int(config.get("max_chars", 800)))
        if args.dry_run:
            print(text)
            return 0
        if not text:
            return 0
        os.makedirs(STATE, exist_ok=True)
        with open(LAST, "w", encoding="utf-8") as fh:
            fh.write(text)
        if config.get("mode") == "auto" and enabled(config):
            play(text, config)
    except (OSError, ValueError, KeyError) as exc:
        print("speak.py: lecture impossible (%s)." % exc, file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
