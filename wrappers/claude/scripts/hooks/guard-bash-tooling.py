#!/usr/bin/env python3
"""guard-bash-tooling.py — PreToolUse(Bash) hook for Claude Code.

Holds the two tooling invariants that used to live as 449 words of prose in
rules/tooling.md. The audit of 2026-08-10 sent both out of the permanent context
on criterion C2: each is a string pattern over an ephemeral action (a Bash
command), and a PreToolUse hook is the only mechanism that can hold one.

  T1  `java`, `javac` and the Maven wrapper go through `bash -lc '<cmd>'`, and
      the wrapper is invoked `sh ./mvnw`, never `./mvnw`.
        - without the login shell, JAVA_HOME is unset: the Bash tool starts a
          non-login shell, which never sources ~/.bashrc.
        - without `sh`, the kernel refuses a wrapper committed 100644 —
          "Permission non accordée". Nine of the eleven Winggy backend repos
          carry that mode (measured 2026-08-06 on origin/HEAD). Read via `sh`
          only the `r` bit is needed, and the shebang becomes a comment.

  T2  No heredoc nested inside `<shell> -c '…'`. The Bash tool runs zsh, and the
      quoted argument adds a second quoting pass: the heredoc never forms and zsh
      EVALUATES the body as code — backticks become substitutions, `**` a glob,
      an apostrophe closes the string. Technical markdown is the worst possible
      payload, being saturated with all three.
      And the failure is silent: it does not fail, it writes half the file.
      Measured 2026-08-06 on the vault's scripts/logs/decisions.md, which
      received one truncated line instead of the whole block.
      The way out is the Write tool, then `cat <source> >> <cible>`.

  What stays allowed, because the ban is on NESTING, not on heredocs: a
  first-level `git commit -F - <<'EOF'`, and heredocs inside a versioned .sh —
  bash runs those directly, with no extra pass.

WHERE IT FAILS CLOSED, AND WHERE IT RENOUNCES (cf. rules/workflow.md). The
perimeter is a raw substring test that cannot itself fail; a command outside it
exits 0 untouched. Inside it:

  - a broken payload contract exits 2, so stderr reaches the agent. Refusing
    there would deny every tool call in the session, including the reads needed
    to diagnose it — and what the rule forbids is an INVISIBLE failure, which
    this is not.
  - a command the shell lexer cannot tokenize falls back to evidence_only(),
    which refuses only on a pattern it can positively read. Blanket-refusing
    there was the first design, and the real corpus killed it: see the
    measurement in that function. A guard that blocks ordinary commits gets
    switched off, and then protects nothing.
"""

import json
import os
import re
import shlex
import sys

SHELLS = {"sh", "bash", "dash", "zsh", "ksh"}
JDK = {"java", "javac"}
WRAPPERS = {"mvnw"}

# Prefixes that carry a command without being one.
PREFIX_WRAPPERS = {"sudo", "env", "time", "nohup", "nice", "command", "exec"}
ENV_ASSIGN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")

# Token boundaries between two simple commands. Redirection tokens (`>`, `>>`,
# `>&`) are deliberately absent: they do not open a new command, and treating
# them as separators would put a filename in command position.
SEPARATORS = {"&&", "||", ";", "|", "&", "\n", "(", ")", "{", "}"}

# A heredoc opener: `<<EOF`, `<< 'EOF'`, `<<-MSG`. The delimiter must start with
# a letter or underscore, which is what keeps `$((1 << 2))` out — an arithmetic
# shift is not a heredoc, and blocking it would be a false positive on ordinary
# shell arithmetic.
HEREDOC = re.compile(r"<<-?\s*(['\"]?)([A-Za-z_][A-Za-z0-9_]*)\1")

# A shell invoked with a flag, i.e. the only shape that can nest a heredoc.
SHELL_WITH_FLAG = re.compile(r"(?:^|[\s;&|(])(?:bash|sh|zsh|dash|ksh)\s+-")

FORM = "bash -lc 'sh ./mvnw <goals>'"

# A wrapper run directly, readable without tokenizing: `./mvnw`, `path/to/mvnw`
# at the start of a command. Used only by the evidence-only fallback below.
RAW_WRAPPER = re.compile(r"(?:^|[\s;&|(])((?:\./|/)[\w./-]*mvnw)\b")


def in_perimeter(cmd: str) -> bool:
    """Does this command even fall under one of the two invariants?

    Cheap and parse-free ON PURPOSE: this is the one test that must not be able
    to fail, since everything below it is allowed to refuse. A T1 violation
    always names java/javac/mvnw textually; a T2 violation always carries both a
    flagged shell and a heredoc opener.
    """
    if "java" in cmd or "mvnw" in cmd:
        return True
    return "<<" in cmd and SHELL_WITH_FLAG.search(cmd) is not None


def tokenize(cmd: str):
    """Shell-aware tokens, quotes honoured, operators kept as their own tokens.

    Raises ValueError on broken quoting — the caller turns that into a refusal.
    """
    lexer = shlex.shlex(cmd, posix=True, punctuation_chars=True)
    lexer.whitespace_split = True
    return list(lexer)


def simple_commands(tokens):
    """Split a token stream into the simple commands it chains."""
    out, current = [], []
    for token in tokens:
        if token in SEPARATORS:
            if current:
                out.append(current)
                current = []
        else:
            current.append(token)
    if current:
        out.append(current)
    return out


def strip_prefixes(tokens):
    """Drop env assignments and wrappers; report whether JAVA_HOME was set.

    `JAVA_HOME=/opt/jdk java -version` supplies by hand exactly what the login
    shell was there to provide, so it must not be refused — a guard that blocks
    a correct command is the kind that gets switched off.
    """
    java_home = False
    while tokens:
        head = tokens[0]
        if ENV_ASSIGN.match(head):
            if head.startswith("JAVA_HOME="):
                java_home = True
            tokens = tokens[1:]
            continue
        if os.path.basename(head) in PREFIX_WRAPPERS:
            tokens = tokens[1:]
            continue
        break
    return tokens, java_home


def shell_flags(args):
    """(is_login, inner_command) for a shell invocation's arguments."""
    letters = ""
    inner = None
    for i, arg in enumerate(args):
        if not arg.startswith("-"):
            continue
        letters += arg.lstrip("-")
        if inner is None and "c" in arg.lstrip("-"):
            rest = args[i + 1:]
            inner = rest[0] if rest else None
    return ("l" in letters, inner)


def analyse(tokens, login, findings, depth=0):
    """Walk simple commands, collecting invariant violations."""
    if depth > 4:  # a shell inside a shell inside a shell: stop, and say so.
        findings.append(
            "commande imbriquée trop profondément pour être jugée — "
            "l'aplatir, ou passer par un script versionné."
        )
        return

    for raw in simple_commands(tokens):
        args, java_home = strip_prefixes(list(raw))
        if not args:
            continue
        here = login or java_home
        head = os.path.basename(args[0])
        rest = args[1:]

        if head in SHELLS:
            is_login, inner = shell_flags(rest)
            if inner is not None:
                if HEREDOC.search(inner):
                    findings.append(
                        "heredoc imbriqué dans « %s -c » : le heredoc ne se forme "
                        "pas et zsh évalue son corps comme du code — le fichier "
                        "s'écrit à moitié, sans erreur. À LA PLACE : écrire le "
                        "contenu avec le tool Write, puis « cat <source> >> "
                        "<cible> ». (Un heredoc de premier niveau, lui, reste "
                        "autorisé : l'interdit porte sur l'imbrication.)" % head
                    )
                    continue  # the inner string will not tokenize as intended
                try:
                    analyse(tokenize(inner), here or is_login, findings, depth + 1)
                except ValueError:
                    findings.extend(evidence_only(inner))
                continue

            script = next((a for a in rest if not a.startswith("-")), None)
            if script and os.path.basename(script) in WRAPPERS and not here:
                findings.append(
                    "« %s %s » sans shell de login : JAVA_HOME est absent, le "
                    "Bash tool ne source pas ~/.bashrc. Forme complète : %s"
                    % (head, script, FORM)
                )
            continue

        if head in WRAPPERS:
            findings.append(
                "« %s » exécuté directement : le wrapper est committé en 100644 "
                "dans neuf des onze repos backend, et le noyau refuse un fichier "
                "sans bit x (« Permission non accordée »). L'invoquer par « sh », "
                "qui le LIT au lieu de l'exécuter. Forme complète : %s"
                % (args[0], FORM)
            )
            continue

        if head in JDK and not here:
            findings.append(
                "« %s » sans shell de login : JAVA_HOME est absent, le Bash tool "
                "ne source pas ~/.bashrc. À LA PLACE : bash -lc '%s'"
                % (head, " ".join(args))
            )


def without_heredoc_bodies(text: str) -> str:
    """Same text, heredoc BODIES removed, opener lines kept.

    A heredoc body is prose, not commands: a commit message that merely mentions
    `./mvnw` must not read as an invocation of it. Measured 2026-08-11 — the very
    first commit of this guard was refused by it, because the French apostrophe in
    the message left an odd quote count, which sent the command down the
    evidence-only path where the body was still being scanned.
    """
    lines, kept, i = text.split("\n"), [], 0
    while i < len(lines):
        kept.append(lines[i])
        opener = HEREDOC.search(lines[i])
        i += 1
        if opener:
            delimiter = opener.group(2)
            while i < len(lines) and lines[i].strip() != delimiter:
                i += 1
            i += 1  # the terminator line itself
    return "\n".join(kept)


def evidence_only(text: str):
    """Findings readable WITHOUT tokenizing — for when the quoting defeats shlex.

    Deliberately narrow, and this is the one place the guard renounces instead of
    refusing. Measured 2026-08-11 over the 986 in-perimeter commands of the real
    session transcripts: refusing every command it could not tokenize produced 8
    refusals, 5 of them ordinary `git commit -F - <<'EOF'` whose only tie to the
    perimeter was a staged path containing `src/main/java`. Blocking routine
    commits is how a guard gets switched off, and a switched-off guard protects
    nothing — so "I cannot read this" is not evidence, and only evidence refuses.
    """
    findings = []

    # Prose first, commands after: everything below reads a heredoc-free view, so
    # a message that merely QUOTES a forbidden form is not mistaken for one. The
    # opener lines survive, and a genuine nested heredoc carries `<shell> -c` and
    # its opener on the same line, so nothing real is lost.
    text = without_heredoc_bodies(text)

    if SHELL_WITH_FLAG.search(text) and HEREDOC.search(text):
        findings.append(
            "heredoc et « shell -c » dans la même commande, dont le quoting ne "
            "se referme pas : c'est la signature du heredoc imbriqué, qui fait "
            "évaluer le corps au lieu de l'écrire. À LA PLACE : écrire le contenu "
            "avec le tool Write, puis « cat <source> >> <cible> »."
        )

    for match in RAW_WRAPPER.finditer(text):
        before = text[: match.start(1)].rstrip()
        if before.endswith("sh"):
            continue
        findings.append(
            "« %s » exécuté directement : le wrapper est committé en 100644 dans "
            "neuf des onze repos backend, et le noyau refuse un fichier sans bit "
            "x. L'invoquer par « sh », qui le LIT au lieu de l'exécuter. Forme "
            "complète : %s" % (match.group(1), FORM)
        )

    return findings


def deny(reason: str):
    """Refuse the call.

    Emits BOTH decision shapes on purpose. `decision: "block"` is what the two
    sibling guards use, and the installed version honours it — measured
    2026-08-11 on the live session: a non-conformant `git commit` was refused and
    the reason came back to the agent. But it no longer appears in the published
    hooks reference, which documents hookSpecificOutput.permissionDecision
    instead. A guard whose refusal channel quietly stops being read fails OPEN,
    the one mode rules/workflow.md forbids — so carry both keys and let whichever
    the runtime reads do the refusing.
    """
    payload = {
        "decision": "block",
        "reason": reason,
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        },
    }
    print(json.dumps(payload))
    sys.exit(0)


def main():
    raw = sys.stdin.read()
    if not raw.strip():
        # Run by hand with no payload: nothing to judge, and nothing to hide.
        print("guard-bash-tooling: aucun payload sur stdin.", file=sys.stderr)
        sys.exit(0)

    try:
        payload = json.loads(raw)
        tool = payload.get("tool_name", "")
        command = (payload.get("tool_input", {}) or {}).get("command", "") or ""
    except (ValueError, AttributeError) as exc:
        # The payload contract broke. Cannot know the perimeter, so cannot judge
        # anything — say it loudly instead of waving every command through.
        print(
            "guard-bash-tooling: payload PreToolUse illisible (%s). Le garde ne "
            "peut rien juger : vérifier le contrat de hook avant de continuer."
            % exc,
            file=sys.stderr,
        )
        sys.exit(2)

    if tool != "Bash" or not command.strip():
        sys.exit(0)

    if not in_perimeter(command):
        sys.exit(0)

    findings = []
    try:
        analyse(tokenize(command), login=False, findings=findings)
    except ValueError:
        findings = evidence_only(command)
        if not findings:
            # Renounced, and said so: a silent renunciation is the failure mode
            # rules/workflow.md forbids, whereas this one leaves a trace.
            print(
                "guard-bash-tooling: commande non analysable et aucune preuve de "
                "violation — pas de verdict rendu.",
                file=sys.stderr,
            )

    if findings:
        seen, unique = set(), []
        for f in findings:
            if f not in seen:
                seen.add(f)
                unique.append(f)
        deny("Règle outillage (rules/tooling.md) — " + " | ".join(unique))

    sys.exit(0)


if __name__ == "__main__":
    main()
