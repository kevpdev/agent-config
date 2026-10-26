"""no_secret_read — guard core, agent-neutral (contract in hooks/check.py).

Refuses a shell command that PRINTS the content of a file policy/deny.yaml denies:
`cat .env`, `grep KEY .env`, `sqlite3 ~/.local/share/opencode/opencode.db`, the
source of a `cp`. Under OpenCode the declarative policy only sees the `read` tool,
and `cat` on the bench decoy let the witness out (measured 2026-10-26).

What stays allowed, on purpose:
  - writes: `>`, `>>`, `cp .env.example .env`, the agent's write tool. The agent
    lays out the skeleton, the human fills in the values.
  - a program loading the file itself: `docker compose --env-file .env up`,
    `source .env && pytest`. Its variables reach the program, not the model.
  - metadata: `ls`, `test -f`.

Threat model = "the model makes a mistake", NOT "the model evades the guard", as
in no_remote_write. `cat "$(echo .e)nv"` or a script that opens the file pass.
The printing commands are a denylist, open by construction: blocking every
command that names the file would refuse `--env-file .env`, which loads values
without printing them.

Claude does not run this guard: each Claude shim runs one named guard, and the
measurement tooling reads opencode.db through Bash (65 of 3,492 real commands).
"""

import fnmatch
import os
import sys

from hooks.bash_tooling import ENV_ASSIGN, PREFIX_WRAPPERS, simple_commands, tokenize

REPO = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
DENY = os.path.join(REPO, "policy", "deny.yaml")

# Commands whose operands end up on their output, whole or filtered.
PRINTING = {
    "cat", "tac", "head", "tail", "less", "more", "nl", "grep", "egrep", "fgrep",
    "rg", "ag", "awk", "sed", "cut", "sort", "uniq", "base64", "xxd", "od",
    "hexdump", "strings", "diff", "jq", "yq", "sqlite3",
}
# Commands that copy their sources elsewhere: every operand but the last is read.
COPYING = {"cp", "scp", "rsync"}


def load_entries(path=DENY):
    """Entries of deny.yaml, or None when it cannot be read (the guard fails open)."""
    try:
        import yaml
        with open(path, encoding="utf-8") as f:
            entries = yaml.safe_load(f) or []
        return [e for e in entries if e.get("action") == "read" and e.get("fin")]
    except Exception as exc:  # noqa: BLE001 — any failure means no verdict
        print(f"no_secret_read: {path} illisible ({exc}), pas de verdict rendu.", file=sys.stderr)
        return None


def ends_with(path: str, fin: str) -> bool:
    """True when the last components of `path` match `fin`, component by component."""
    parts = [p for p in path.split("/") if p]
    want = [p for p in fin.split("/") if p]
    if len(parts) < len(want):
        return False
    return all(fnmatch.fnmatchcase(a, b) for a, b in zip(parts[-len(want):], want))


def denied(token: str, cwd: str, entries):
    """The deny.yaml entry `token` designates, or None."""
    if not token or token.startswith("-") and "=" not in token:
        return None
    if token.startswith("-"):
        token = token.split("=", 1)[1]
    path = os.path.normpath(os.path.join(cwd, os.path.expanduser(token)))
    for e in entries:
        if ends_with(path, e["fin"]) and not any(ends_with(path, s) for s in e.get("sauf") or []):
            return e
    return None


def read_operands(tokens):
    """(program, operands it prints or copies) for one simple command."""
    while tokens and (ENV_ASSIGN.match(tokens[0]) or os.path.basename(tokens[0]) in PREFIX_WRAPPERS):
        tokens = tokens[1:]
    if not tokens:
        return None, []
    program = os.path.basename(tokens[0])
    args, redirected, skip = [], [], False
    for i, t in enumerate(tokens[1:], 1):
        if skip:
            skip = False
            continue
        if t in {">", ">>", ">|", "&>", "2>", "<"}:
            if t == "<" and i + 1 < len(tokens):
                redirected.append(tokens[i + 1])
            skip = True
            continue
        args.append(t)
    if program == "sed" and any(a == "-i" or a.startswith(("-i", "--in-place")) for a in args):
        return program, []  # edits the file in place, prints nothing
    if program in PRINTING:
        return program, args + redirected
    if program in COPYING:
        operands = [a for a in args if not a.startswith("-")]
        return program, operands[:-1]
    return program, []


def decide(event: dict):
    """Reason to refuse this shell command, or None to let it through."""
    command = event.get("command") or ""
    if event.get("action") != "shell" or not command.strip():
        return None
    entries = load_entries()
    if not entries:
        return None
    try:
        commands = simple_commands(tokenize(command))
    except ValueError:
        return None
    cwd = event.get("cwd") or os.getcwd()
    for tokens in commands:
        program, operands = read_operands(tokens)
        for token in operands:
            e = denied(token, cwd, entries)
            if e:
                return (
                    f"Lecture interdite (policy/deny.yaml, entrée {e['id']}) : `{program} {token}` "
                    f"sortirait le contenu de {e['fin']}, {e['raison']} "
                    "Pour un .env, pose le squelette sans valeurs (cp .env.example .env) et laisse "
                    "l'humain remplir. Pour vérifier, test -f, ou lance le programme qui le charge."
                )
    return None
