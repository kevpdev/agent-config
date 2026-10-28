"""no_sensitive_write — guard core, agent-neutral (contract in hooks/check.py).

Refuses writing or deleting a file policy/deny.yaml denies with `action: write`:
the git history, the shell start-up files, SSH access, the system. Issue #47.

Two actions are judged:
  - edit: every path of the event. The declarative rules (Claude permissions.deny,
    OpenCode policies) already cover the edit tools, this is the net under them.
  - shell: the operands a command writes or deletes. `rm -rf .git`,
    `echo x >> ~/.zshrc`, `sed -i … ~/.ssh/config`, `sudo tee /etc/hosts`.

What stays allowed, on purpose:
  - `git` itself: `git commit` writes .git/ without naming it, so nothing here sees it.
  - reads: `cat ~/.zshrc`, `cp ~/.zshrc /tmp/b`. Reading secrets is no_secret_read's job.
  - a file of the same name elsewhere: `~/.zshrc` is anchored at the home, so a
    `.zshrc` versioned in a dotfiles repo stays writable.

Threat model = "the model makes a mistake", NOT "the model evades the guard", as in
no_secret_read. `bash -c "rm .git/HEAD"`, `find .git -delete` or a script pass.
"""

import os

from hooks.bash_tooling import ENV_ASSIGN, PREFIX_WRAPPERS, simple_commands, tokenize
from hooks.deny_policy import denied, load_entries, matching, resolve, strip_heredocs

# Every operand is written or deleted.
ALL_OPERANDS = {"rm", "rmdir", "unlink", "shred", "truncate", "tee"}
# The source disappears and the destination is written.
MOVING = {"mv"}
# Only the destination is written: the last operand, or the directory of `-t`.
TO_LAST = {"cp", "install", "ln"}
# Edit in place with -i, and only then.
IN_PLACE = {"sed", "perl"}
REDIRECTS = {">", ">>", ">|", "&>", "&>>"}


def write_operands(tokens):
    """(program, operands it writes or deletes) for one simple command."""
    while tokens and (ENV_ASSIGN.match(tokens[0]) or os.path.basename(tokens[0]) in PREFIX_WRAPPERS):
        tokens = tokens[1:]
    if not tokens:
        return None, []
    program = os.path.basename(tokens[0])
    args, written, skip = [], [], False
    for i, t in enumerate(tokens[1:], 1):
        if skip:
            skip = False
            continue
        following = tokens[i + 1] if i + 1 < len(tokens) else ""
        if t.isdigit() and following in REDIRECTS | {">&", "<"}:
            continue  # the descriptor of `2>`, not an operand
        if t == ">&":
            skip = True  # `2>&1` duplicates a descriptor, it names no file
            continue
        if t in REDIRECTS or t == "<":
            if t != "<" and i + 1 < len(tokens):
                written.append(tokens[i + 1])
            skip = True
            continue
        args.append(t)
    operands = [a for a in args if not a.startswith("-")]
    if program in ALL_OPERANDS or program in MOVING:
        written += operands
    elif program in TO_LAST:
        target = [args[i + 1] for i, a in enumerate(args[:-1]) if a == "-t"]
        written += target or operands[-1:]
    elif program in IN_PLACE and any(a.startswith(("-i", "--in-place")) for a in args):
        written += operands
    elif program == "dd":
        written += [a[3:] for a in args if a.startswith("of=")]
    return program, written


def refusal(e, what):
    return (
        f"Écriture interdite (policy/deny.yaml, entrée {e['id']}) : {what} modifierait ou "
        f"supprimerait {e['fin']}, {e['raison']} Si le changement est voulu, demande à "
        "l'humain de le lancer lui-même avec `! <commande>`."
    )


def decide(event: dict):
    """Reason to refuse this action, or None to let it through."""
    action = event.get("action")
    if action not in {"shell", "edit"}:
        return None
    command = event.get("command") or ""
    if action == "shell" and not command.strip():
        return None
    entries = load_entries("write", "no_sensitive_write")
    if not entries:
        return None
    cwd = event.get("cwd") or os.getcwd()
    if action == "edit":
        for path in event.get("paths") or []:
            e = matching(resolve(path, cwd), entries)
            if e:
                return refusal(e, f"l'édition de {path}")
        return None
    try:
        commands = simple_commands(tokenize(strip_heredocs(command)))
    except ValueError:
        return None
    for tokens in commands:
        program, operands = write_operands(tokens)
        for token in operands:
            # A variable the guard cannot expand hides where the path leads: the replay
            # of real commands refused `rm -rf $S/t/base/.git`, a throwaway copy.
            if "$" in os.path.expandvars(token):
                continue
            e = denied(token, cwd, entries)
            if e:
                return refusal(e, f"`{program} {token}`")
    return None
