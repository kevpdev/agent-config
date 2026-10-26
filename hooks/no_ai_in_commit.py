"""no_ai_in_commit — guard core, agent-neutral (contract in hooks/check.py).

Refuses git commit commands that:
  1. include "Claude" or co-authorship mentions
  2. do not follow Conventional Commits EN format
Refuses `gh pr create` / `gh pr edit` commands whose title or body carries an AI
attribution (check 1 only).

Ported from wrappers/claude/hooks/guard-no-claude-in-commit.sh, which was 445
lines of bash around Python blocks; that file is now a shim over this module.

SCOPE: this is an agent hook, NOT a git hook. No repo carries a commit-msg
hook and core.hooksPath is unset (measured 2026-08-05), so a commit typed by
hand in a terminal passes unchecked. Deterministic for the agent, advisory for
the human. What it does NOT check, and what therefore stays on judgment, is in
rules/commit-convention.md — the only place that list lives.

The Claude-only check on `skipDangerousModePermissionPrompt` in the user-level
settings stays in the Claude adapter: no other agent writes that key.
"""

import os
import re
import shlex

UNREADABLE = "__GUARD_UNREADABLE_MESSAGE_FILE__"

TWO_ARG = {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--exec-path"}

# Naming the tool is not signing: "Claude Code" alone passes, this repo talks
# about it constantly. Only the attribution shapes block.
ATTRIBUTION = re.compile(
    r"Co-Authored-By: Claude|claude (sonnet|opus|haiku|fable)|noreply@anthropic"
    r"|Generated with \[?Claude Code|claude\.com/claude-code",
    re.IGNORECASE,
)

CONVENTIONAL = re.compile(r"^(feat|fix|refactor|docs|test|chore|perf|ci)(\(.+\))?: .+")

MESSAGE_FILE = re.compile(r"(?:--body-file|--file|-F)(?:=|\s+)(\"[^\"]*\"|'[^']*'|[^\s;&|]+)")

REASON_ATTRIBUTION = (
    "AI attribution detected in the commit message or pull request text "
    "(Co-Authored-By: Claude, Generated with Claude Code, noreply@anthropic…). "
    "Convention: no AI or co-author mention in commits or PRs. Naming Claude Code "
    "as a tool is fine; signing with it is not. Remove and retry."
)
REASON_PR_FILE = (
    "PR body file passed through a shell variable, which this guard cannot resolve "
    "without evaluating untrusted input, so the body would go unchecked. Use a literal "
    "path (--body-file /abs/path/body.md), a heredoc (--body-file - <<EOF), or --body."
)
REASON_COMMIT_FILE = (
    "Commit message file passed through a shell variable, which this guard cannot "
    "resolve without evaluating untrusted input — so the message would go unchecked. "
    "Use a literal path (git commit -F /abs/path/msg.txt), a heredoc "
    "(git commit -F - <<EOF), or -m."
)
REASON_FORMAT = (
    "Commit message does not follow Conventional Commits EN format. Expected: "
    "<type>(<scope>): <subject>  — types: feat, fix, refactor, docs, test, chore, "
    "perf, ci. Example: feat(auth): add JWT refresh token support"
)


def commit_args(tokens):
    """Arguments of the `git … commit` invocation, or None if there is none.

    Tolerates global options between `git` and the subcommand (e.g. `git -C <path>
    commit`, `git -c k=v commit`). A plain grep for "git commit" missed those forms
    and let them bypass the guard.
    """
    for i, t in enumerate(tokens):
        if t != "git":
            continue
        j = i + 1
        while j < len(tokens):
            if tokens[j] in TWO_ARG:
                j += 2
            elif tokens[j].startswith("-"):
                j += 1
            else:
                break
        if j < len(tokens) and tokens[j] == "commit":
            return tokens[j + 1:]
    return None


def kind_of(cmd):
    """'commit', 'pr' or None.

    `gh pr create` / `gh pr edit` are detected too. Measured 2026-10-22: PR #13 went
    out signed "Generated with [Claude Code]" because this guard exited on anything
    that was not a commit. Only the mention check applies to a PR, not the format
    check.
    """
    try:
        toks = shlex.split(cmd)
    except ValueError:
        toks = cmd.split()
    if commit_args(toks) is not None:
        return "commit"
    if any(toks[i] == "gh" and toks[i + 1] == "pr" and toks[i + 2] in ("create", "edit")
           for i in range(len(toks) - 2)):
        return "pr"
    return None


def resolve_target(cmd, cwd):
    """The repo ACTUALLY targeted, independent of command shape or where git runs.

    Honors an explicit `-C <path>`, else a leading `cd <path>`, else the session
    cwd. Expands ~ and $HOME by substitution (never eval — the command is
    untrusted input).
    """
    home = os.path.expanduser("~")
    target = cwd
    m = re.search(r"git\s+-C\s+([^\s;&|]+)", cmd)
    if m:
        target = m.group(1)
    else:
        m = re.search(r"(?:^|[\s;&|])cd\s+([^\s;&|]+)", cmd)
        if m:
            target = m.group(1)
    target = target.replace('"', "").replace("'", "")
    if target.startswith("~"):
        target = home + target[1:]
    target = target.replace("${HOME}", home).replace("$HOME", home)
    if not target.startswith("/"):
        target = cwd + "/" + target
    return target


def mention_text(cmd, target):
    """The command text plus the content of any message file it names.

    The command text alone is not the message: `git commit -F msg.txt` and
    `gh pr create --body-file body.md` carry only a file name. Measured 2026-10-22,
    PR #13 went out through `--body-file`, so the signature never reached the grep.
    Paths resolve against `target`, like the subject extractor below. A path built
    from a shell variable cannot be resolved without evaluating untrusted input:
    for a PR that fails closed, for a commit the extractor refuses it.
    """
    out = [cmd]
    for m in MESSAGE_FILE.finditer(cmd):
        path = m.group(1).strip("\"'")
        if path == "-":
            continue  # stdin: the heredoc body is already in the command text
        if not os.path.isabs(path):
            path = os.path.join(target, path)
        if "$" in path or "`" in path:
            out.append(UNREADABLE)
            continue
        try:
            with open(path, encoding="utf-8", errors="replace") as fh:
                out.append(fh.read(65536))
        except OSError:
            pass  # absent file: the command itself will fail on it
    return "\n".join(out)


def split_top_level(text):
    """Split on shell separators, but never inside a quoted string.

    Splitting on a bare regex cut inline multi-line messages in half: the message
    of `git commit -m "subject … body"` legitimately holds newlines, so the segment
    ended on an unterminated quote, shlex gave up, and the naive fallback below
    yielded `"docs(x):` — a stump that fails the format check.

    Measured 2026-08-11 on real traffic: 46 commit segments were unsplittable and
    21 VALID commits were refused out of 26 format refusals. A guard that refuses
    valid work gets switched off, so this is the same failure family as an open
    failure. Segment isolation itself stays — it was introduced because a
    neighbouring `git tag -m` had its message judged as the commit's.
    """
    segs, buf, quote, i = [], [], None, 0
    while i < len(text):
        ch = text[i]
        if quote:
            buf.append(ch)
            if ch == quote:
                quote = None
            elif ch == "\\" and quote == '"' and i + 1 < len(text):
                i += 1
                buf.append(text[i])
            i += 1
            continue
        if ch in "\"'":
            quote = ch
            buf.append(ch)
            i += 1
            continue
        if text.startswith("&&", i) or text.startswith("||", i):
            segs.append("".join(buf)); buf = []; i += 2
            continue
        if ch in ";|\n":
            segs.append("".join(buf)); buf = []; i += 1
            continue
        buf.append(ch)
        i += 1
    segs.append("".join(buf))
    return segs


def commit_subject(cmd, target):
    """Subject of the message THIS `git commit` will actually use, "" if unknown,
    or UNREADABLE when the message file goes through a shell variable.

    A bare search for `-m` over the whole command is wrong: the first `-m` does not
    necessarily belong to the commit. Measured 2026-07-30 — `git commit -F - <<'EOF'
    … EOF` followed by `git tag -m 'point de depart'` in the same command validated
    the TAG's message and blocked a perfectly conformant commit. A guard that
    refuses valid work is the kind that gets switched off.

    So: set heredoc bodies aside, isolate the shell segment carrying `git commit`,
    and read only that invocation's own arguments. Every ambiguity resolves to "no
    subject extracted" — fail-open, matching the intent: this validates what it can
    read, it is not a gate that must have the last word.
    """
    # 1. Lift heredoc bodies out. They hold free text, and a "&&" or ";" inside a
    #    sentence would otherwise cut the command into bogus segments.
    heredocs = {}
    lines = cmd.split("\n")
    kept, i = [], 0
    while i < len(lines):
        kept.append(lines[i])
        # <<EOF, <<'EOF', <<"EOF", <<-MSG … first marker on the line only: two
        # heredocs opened by one line is exotic, and guessing there would cost more
        # than the fail-open it replaces.
        m = re.search(r"<<-?\s*(['\"]?)([A-Za-z_][A-Za-z0-9_]*)\1", lines[i])
        i += 1
        if m:
            delim, body = m.group(2), []
            while i < len(lines) and lines[i].strip() != delim:
                body.append(lines[i])
                i += 1
            i += 1  # skip the terminator line itself
            heredocs.setdefault(delim, "\n".join(body))
    flat = "\n".join(kept)

    # 2. Keep only the segment that carries the commit.
    args = None
    for segment in split_top_level(flat):
        try:
            tokens = shlex.split(segment)
        except ValueError:
            tokens = segment.split()
        found = commit_args(tokens)
        if found is not None:
            args = found
            break
    if args is None:
        return ""

    # 3. Read the message from those arguments only.
    subject, reads_stdin, file_path, k = "", False, "", 0
    while k < len(args):
        a = args[k]
        if a in ("-m", "--message"):
            subject = args[k + 1] if k + 1 < len(args) else ""
            break
        if a.startswith("--message="):
            subject = a.split("=", 1)[1]
            break
        # Bundled short flags: `git commit -am "msg"` used to slip through entirely,
        # because the old regex required a standalone `-m`.
        if re.fullmatch(r"-[A-Za-z]*m", a):
            subject = args[k + 1] if k + 1 < len(args) else ""
            break
        if a in ("-F", "--file") and k + 1 < len(args):
            if args[k + 1] == "-":
                reads_stdin = True
            else:
                file_path = args[k + 1]
        if a == "--file=-":
            reads_stdin = True
        elif a.startswith("--file="):
            file_path = a.split("=", 1)[1]
        k += 1

    # `-m "$(cat <<'EOF' … EOF)"` — the argument is a command substitution, not a
    # message. Measured 2026-07-31: the unbalanced quote makes shlex give up, the
    # fallback split yields the token `"$(cat`, and a conformant commit was blocked
    # on it. Failing open here would be worse than elsewhere: this is the standard
    # shape for a multi-line message, so the most common commit of all would go
    # unvalidated. With exactly one heredoc, its body IS the message; with several,
    # which one feeds the commit is a guess — renounce, as everywhere else here.
    #
    # Not the mere presence of `$(`: a closed `$(pwd)` INSIDE a subject is a
    # subject, and must keep being validated. Two shapes say "this argument is a
    # substitution, not a message" — it is unterminated, or the argument BEGINS
    # with it, which no real subject ever does.
    #
    # The second test was added the day the quote-aware splitter landed: keeping
    # the quoted argument whole made shlex succeed, so the substitution came back
    # balanced and the unterminated test stopped firing. The battery caught it
    # immediately — which is what a battery is for, once the wiring is proven
    # elsewhere.
    if subject.count("$(") > subject.count(")") or subject.strip().startswith("$("):
        subject = next(iter(heredocs.values())) if len(heredocs) == 1 else ""

    # A commit reading stdin takes the heredoc — but only when there is exactly one.
    # With several, which one feeds the commit is a guess, and guessing here risks
    # blocking on text that is not the commit message at all.
    if not subject and reads_stdin and len(heredocs) == 1:
        subject = next(iter(heredocs.values()))

    # `-F <path>` / `--file=<path>` — the message lives in a file, so the command
    # carries only its name and the extractor saw nothing. Measured 2026-08-11 in a
    # sandbox: `git commit -F badmsg.txt` whose subject was "wip stuff" landed
    # unvalidated, and the four commits of that same day had all taken this path.
    #
    # This is NOT an ambiguity to renounce on, unlike the heredoc cases above: the
    # source is single, named and readable. Opening it turns an unknown into a
    # known, so no valid work can be refused by it. Any read error falls back to ""
    # — the same fail-open as everywhere else in this extractor.
    #
    # The path is almost always RELATIVE, and the hook does not run from the
    # commit's directory. Measured the same day: the first version of this read
    # opened the path as given, the battery passed on absolute paths, and the live
    # commit went through untouched. So resolve against `target` — the directory
    # the commit actually runs in.
    #
    # A path built from a shell variable — `-F "$S/msg.txt"` — is the one form that
    # CANNOT be resolved here: expanding it would mean evaluating untrusted input,
    # which this guard never does. And it is the dangerous form, because the shell
    # resolves it perfectly well, so the commit succeeds while the guard saw
    # nothing. Measured 2026-08-11: two successive fixes went green on the battery
    # and the live commit still landed, both times because the real command carried
    # `-F "$G/badmsg.txt"`.
    #
    # So discriminate on the consequence, not on the shape:
    #   - unresolvable (holds `$` or a backtick) → git WILL commit → renounce is a
    #     silent hole → refuse, and say which forms are readable.
    #   - plain path that simply does not exist → `git commit` fails on it too, so
    #     no unvalidated commit can land → fail-open, harmless.
    #
    # Test the RESOLVED path, not the argument: the variable is as often in the
    # target directory (`cd "$G" && git commit -F msg.txt`) as in the argument
    # itself. The third failed fix of that day checked only the argument, which was
    # a clean relative path, and let the bogus target through.
    if not subject and file_path:
        if not os.path.isabs(file_path):
            file_path = os.path.join(target, file_path)
        if "$" in file_path or "`" in file_path:
            return UNREADABLE
        try:
            with open(file_path, encoding="utf-8", errors="replace") as fh:
                subject = fh.read(4096)
        except OSError:
            subject = ""

    first = subject.strip().splitlines()
    return first[0].strip() if first else ""


def decide(event: dict):
    """Reason to refuse this commit or PR command, or None to let it through."""
    cmd = event.get("command") or ""
    if event.get("action") != "shell":
        return None
    kind = kind_of(cmd)
    if kind is None:
        return None
    target = resolve_target(cmd, event.get("cwd") or "")

    text = mention_text(cmd, target)
    if ATTRIBUTION.search(text):
        return REASON_ATTRIBUTION

    if kind == "pr":
        # The format check below is for commit subjects only.
        return REASON_PR_FILE if UNREADABLE in text else None

    subject = commit_subject(cmd, target)
    # A message file the guard cannot read is the one case that fails CLOSED: the
    # shell would have resolved it, so letting it through means an unchecked
    # commit lands.
    if subject == UNREADABLE:
        return REASON_COMMIT_FILE

    # Validate Conventional Commits EN format when extractable (fail-open if not).
    # Applies to every repo, vault included: a vault commit is
    # `<type>(<date>): <subject>` (e.g. docs(2026-07-23): import refs RAG). Only
    # the <subject> may be French for the vault (personal FR notes) — the
    # type/scope grammar is enforced identically everywhere.
    if subject and not CONVENTIONAL.match(subject):
        return REASON_FORMAT
    return None
