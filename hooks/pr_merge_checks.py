"""pr_merge_checks — guard core, agent-neutral (contract in hooks/check.py).

Refuses `gh pr merge` (`--auto` included) unless every check GitHub reports on
the pull request is green. Green means `pass` or `skipping`, as printed in the
second column of `gh pr checks`. Everything else refuses: `fail`, `pending`, an
unknown state, no check at all, or checks that cannot be read (gh missing, API
unreachable, output without columns). `--disable-auto` merges nothing and passes.

Why: a private repository on a free account has no ruleset, so nothing requires
the `ci` gate and a red pull request stays mergeable (measured 2026-11-05 on
kevpdev/hypomnesis, the rulesets API answers HTTP 403). This guard puts the
gate back in front of the agent. It fails closed everywhere, because a false
green is exactly what it exists to prevent, and a merge needs the network anyway.

The pull request read is the one the merge targets. `gh pr checks` gets the
merge's selector and repository: `-R`/`--repo` placed after `gh`, after `pr` or
after `merge`, else a `GH_REPO=` prefix. It runs in the directory of a `cd`
placed before the merge (no_ai_in_commit.resolve_target), else the session cwd.
A digit glued to `<` or `>` is a file descriptor, any other digit is an argument.

A command that names `gh pr merge` but cannot be read is refused, since letting
it through would be a false green: broken quoting, a selector or repository
built from a variable or a substitution, gh started by `xargs` or `parallel`,
or a heredoc fed to a shell (`bash <<EOF`) whose body names `gh pr merge`. Other
heredoc bodies are prose and are set aside, so a commit message that quotes
`gh pr merge` is not a merge.

`gh pr checks N --watch && gh pr merge N` is judged before it runs, checks still
pending, so it is refused: the wait goes in a separate call.

Threat model is "the agent makes a mistake", NOT "the agent evades the guard".

Not seen: a merge through `gh api` on the merge endpoint, a click in the web UI,
a merge nested in a quoted string (`bash -c 'gh pr merge 5'`), a heredoc piped
into a shell (`cat <<'EOT' | bash`), a line continuation (`\` then newline) on
the line that opens a heredoc or inside the body of a heredoc fed to a shell, an
`export GH_REPO=...` placed before the merge in the same command, and the `cd`
lost by OpenCode when no call is retained.
"""

import os
import re
import subprocess

from hooks import bash_tooling, no_ai_in_commit

# Loose prefilter: the token pass below decides. Options may sit between the words.
MERGE = re.compile(r"\bgh\b[^\n;&|]*?\bpr\b[^\n;&|]*?\bmerge\b")
GREEN = {"pass", "skipping"}
TIMEOUT = 20

# `gh pr merge --help`, gh 2.45.0: the flags that take a value.
VALUE_FLAGS = {"-t", "--subject", "-b", "--body", "-F", "--body-file", "-A", "--author-email",
               "--match-head-commit"}
REPO_FLAGS = {"-R", "--repo"}
LAUNCHERS = {"xargs", "parallel"}
REDIRECTION = re.compile(r"^(?:[<>]+&?|&>>?|<&|>&)$")
SHELL_HEREDOC = re.compile(r"(?:^|[\s;&|(])(?:\S*/)?(?:bash|sh|zsh|dash)(?:\s+-\S+)*\s*<<")

HOW = ("Attendre les checks par `gh pr checks <N> --watch` dans un appel séparé, puis relancer "
       "le merge, ou laisser l'humain merger.")
REASON_UNREADABLE_COMMAND = (
    "Merge refusé : la commande contient `gh pr merge` mais le garde ne peut pas la lire "
    "(guillemet non fermé, sélecteur ou dépôt construit par une variable ou une substitution, "
    "gh lancé par xargs ou parallel, ou heredoc passé à un shell). Il ne peut donc pas "
    "vérifier les checks de la PR visée. Écrire le numéro, l'URL ou la branche en clair, une "
    "PR par appel."
)


class Unreadable(Exception):
    """The command names a merge that the guard cannot pin down."""


def shell_heredoc_merges(command):
    """True when a heredoc fed to a shell carries `gh pr merge` in its body."""
    lines, i = command.split("\n"), 0
    while i < len(lines):
        opener = bash_tooling.HEREDOC.search(lines[i])
        runs_shell = opener and SHELL_HEREDOC.search(lines[i])
        i += 1
        if not opener:
            continue
        body = []
        while i < len(lines) and lines[i].strip() != opener.group(2):
            body.append(lines[i])
            i += 1
        i += 1
        if runs_shell and MERGE.search("\n".join(body)):
            return True
    return False


def drop_glued_descriptors(command):
    """Same text without the digits glued to `<` or `>` outside quotes (`2>&1` -> `>&1`).

    Tokens lose the spacing, so `gh pr merge 2 >x` and `gh pr merge 2>x` would read
    alike. Only the glued form names a descriptor, and `&>` never takes one.
    """
    out, quote, i = [], None, 0
    while i < len(command):
        ch = command[i]
        if quote:
            out.append(ch)
            if ch == quote:
                quote = None
            elif ch == "\\" and quote == '"' and i + 1 < len(command):
                i += 1
                out.append(command[i])
        elif ch in "\"'":
            quote = ch
            out.append(ch)
        elif ch == "\\" and i + 1 < len(command):
            out.append(ch + command[i + 1])
            i += 1
        elif ch.isdigit() and (i == 0 or command[i - 1].isspace()):
            j = i
            while j < len(command) and command[j].isdigit():
                j += 1
            if j < len(command) and command[j] in "<>":
                i = j
                continue
            out.append(command[i:j])
            i = j
            continue
        else:
            out.append(ch)
        i += 1
    return "".join(out)


def skip_options(tokens, k, repo):
    """Skip the options before a subcommand word, keeping a `-R`/`--repo` value."""
    while k < len(tokens) and tokens[k].startswith("-"):
        if tokens[k] in REPO_FLAGS:
            repo = tokens[k + 1] if k + 1 < len(tokens) else ""
            k += 2
            continue
        if tokens[k].startswith("--repo="):
            repo = tokens[k].split("=", 1)[1]
        k += 1
    return k, repo


def merge_calls(tokens):
    """(position, selector or None, repo or None, disable_auto) per merge in a simple command."""
    calls = []
    for i, token in enumerate(tokens):
        if os.path.basename(token) != "gh":
            continue
        repo = next((t.split("=", 1)[1] for t in tokens[:i] if t.startswith("GH_REPO=")), None)
        k, repo = skip_options(tokens, i + 1, repo)
        if k >= len(tokens) or tokens[k] != "pr":
            continue
        k, repo = skip_options(tokens, k + 1, repo)
        if k >= len(tokens) or tokens[k] != "merge":
            continue
        if any(os.path.basename(t) in LAUNCHERS for t in tokens[:i]):
            raise Unreadable()
        args = tokens[k + 1:]
        selector, disable_auto, k = None, False, 0
        while k < len(args):
            arg = args[k]
            nxt = args[k + 1] if k + 1 < len(args) else ""
            if REDIRECTION.match(arg):
                k += 2
                continue
            if arg == "--disable-auto":
                disable_auto = True
            elif arg in REPO_FLAGS:
                repo = nxt
                k += 1
            elif arg.startswith("--repo="):
                repo = arg.split("=", 1)[1]
            elif arg in VALUE_FLAGS:
                k += 1
            elif arg.startswith("-"):
                pass  # boolean flag, `--opt=value` or short flag with its value glued
            elif selector is None:
                selector = arg
            k += 1
        calls.append((i, selector, repo, disable_auto))
    return calls


def read_checks(selector, repo, directory):
    """(lines, error): the tab-separated rows of `gh pr checks`, or why they could not be read."""
    cmd = ["gh", "pr", "checks"] + ([selector] if selector else []) + (["-R", repo] if repo else [])
    try:
        result = subprocess.run(cmd, cwd=directory, capture_output=True, text=True,
                                timeout=TIMEOUT)
    except (OSError, subprocess.SubprocessError) as error:
        return None, str(error)
    rows = [line.split("\t") for line in result.stdout.splitlines() if line.strip()]
    if any(len(row) < 2 for row in rows):
        return None, "sortie sans colonnes : " + result.stdout.strip()[:200]
    if not rows and result.returncode != 0:
        return None, (result.stderr.strip() or "code %d" % result.returncode)[:200]
    return rows, None


def judge(selector, repo, directory, watch_in_command):
    """Refusal reason for one merge, or None when every check is green."""
    target = selector or "la branche courante"
    rows, error = read_checks(selector, repo, directory)
    if error is not None:
        return ("Merge refusé : les checks de %s n'ont pas pu être lus (%s). Sans eux, le "
                "garde ne peut pas dire que la PR est verte. %s" % (target, error, HOW))
    if not rows:
        return ("Merge refusé : aucun check rapporté sur %s. Juste après un push, les checks "
                "ne sont pas encore enregistrés, et chaque dépôt a une porte `ci`. %s"
                % (target, HOW))
    red = ["%s (%s)" % (row[0].strip(), row[1].strip()) for row in rows
           if row[1].strip() not in GREEN]
    if not red:
        return None
    reason = "Merge refusé : des checks de %s ne sont pas verts : %s. %s" % (
        target, ", ".join(red), HOW)
    if watch_in_command:
        reason += (" Un `--watch` enchaîné dans la même commande ne suffit pas : le garde juge "
                   "la commande avant qu'elle tourne, checks encore en attente.")
    return reason


def decide(event: dict):
    """Reason to refuse this merge, or None to let it through."""
    if event.get("action") != "shell":
        return None
    raw = event.get("command") or ""
    if shell_heredoc_merges(raw):
        return REASON_UNREADABLE_COMMAND
    # Bash deletes a backslash-newline, but not inside a quoted heredoc: join the
    # lines only once the heredoc bodies are gone.
    command = bash_tooling.without_heredoc_bodies(raw).replace("\\\n", "")
    if not MERGE.search(command):
        return None
    try:
        commands = bash_tooling.simple_commands(
            bash_tooling.tokenize(drop_glued_descriptors(command)))
        calls = []
        for n, tokens in enumerate(commands):
            for i, selector, repo, disable_auto in merge_calls(tokens):
                # Only a `cd` placed before the merge decides where it runs.
                before = " ; ".join(" ".join(t) for t in commands[:n] + [tokens[:i]])
                calls.append((before, selector, repo, disable_auto))
    except (ValueError, Unreadable):
        return REASON_UNREADABLE_COMMAND
    watch = "--watch" in command
    for before, selector, repo, disable_auto in calls:
        if disable_auto:
            continue
        if any(c in (selector or "") + (repo or "") for c in "$`"):
            return REASON_UNREADABLE_COMMAND
        directory = no_ai_in_commit.resolve_target(before, event.get("cwd") or "")
        reason = judge(selector, repo, directory, watch)
        if reason:
            return reason
    return None
