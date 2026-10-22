#!/usr/bin/env python3
"""guard-no-remote-write.py — PreToolUse hook for Claude Code.

Blocks agent-initiated WRITES to the protected remote servers (preprod, prod).
Reads stay allowed: losing diagnosis ability would make the guard so annoying
it would get disabled, and a disabled guard protects less than a narrow one.

Threat model = "the agent makes a mistake", NOT "the agent evades the guard".
String inspection of a shell command can always be defeated (`bash -lc "$V"`,
base64, ...). This is a seatbelt against the accidental `docker compose down`
on prod, not a sandbox.

Two axes, because either one alone leaves a hole:

  1. COMMAND axis — ssh / scp / sftp / rsync / ansible / docker -H / DOCKER_HOST.
     Host tokens are resolved through `ssh -G`, so an alias added to
     ~/.ssh/config pointing at a protected IP is still caught: we compare the
     RESOLVED hostname, never the literal string typed.

  2. PATH axis — a gvfs or sshfs mount turns the remote host into an ordinary
     local path. Writing to
       /run/user/1000/gvfs/sftp:host=winggyprod/home/betterfly/docker-compose.yml
     mentions no ssh, no hostname, no IP. A command-only guard sees nothing.

Classification is an ALLOWLIST of read-only commands, not a denylist of
dangerous ones: a denylist is open by construction (every unlisted binary
passes), an allowlist is closed (every unlisted binary is refused).
"""

import json
import os
import re
import shlex
import subprocess
import sys

# Aliases whose write access is denied to the agent. labs/dev stay writable on
# purpose — that is the sandbox, and blocking it would create the friction that
# gets guards switched off.
PROTECTED_ALIASES = ["winggypreprod", "winggyprod"]

# Commands that only read. Anything absent from this list is treated as a write.
READONLY = {
    "cat", "ls", "pwd", "whoami", "id", "df", "du", "free", "uptime", "uname",
    "hostname", "stat", "head", "tail", "grep", "egrep", "fgrep", "rg", "find",
    "wc", "file", "readlink", "realpath", "tree", "date", "env", "printenv",
    "ps", "netstat", "ss", "ip", "lsof", "dmesg", "journalctl", "which",
    "type", "echo", "true", "test", "getent", "nproc", "lscpu", "lsblk",
    "vmstat", "iostat", "sha256sum", "md5sum", "diff", "cmp", "jq", "awk",
    "sed", "cut", "sort", "uniq", "tr", "column", "less", "more", "zcat",
}

# Subcommand-scoped allowlists: the binary alone says nothing about intent.
READONLY_SUB = {
    "systemctl": {"status", "show", "is-active", "is-enabled", "list-units",
                  "list-unit-files", "cat"},
    "docker": {"ps", "images", "logs", "inspect", "version", "info", "stats",
               "top", "port", "diff", "events", "history", "image", "context"},
    "docker-compose": {"ps", "logs", "config", "version", "top", "images"},
    "git": {"status", "log", "diff", "show", "branch", "remote", "rev-parse",
            "describe", "ls-files", "config"},
    "apachectl": {"configtest", "status"},
    "nginx": set(),  # only `nginx -t` — flag-based, handled below
}

# `docker compose <sub>` (space form) reuses the docker-compose allowlist.
COMPOSE_READONLY = READONLY_SUB["docker-compose"]

# curl mutates as soon as it carries a body or a non-GET verb.
CURL_WRITE_FLAGS = re.compile(
    r"(^|\s)(-X|--request|-d|--data\b|--data-\S+|-T|--upload-file|-F|--form)(\s|=|$)"
)

# Redirections and stream writers, whatever the binary in front of them.
WRITE_SHELL = re.compile(r"(>>?|\btee\b|\bdd\b)")


def hostpart(token: str) -> str:
    """Extract the bare host from any target form.

    Handles alias, user@host, host:/path, and URL forms such as
    ssh://betterfly@winggyprod — DOCKER_HOST uses the last one, and a naive
    split on ':' would return "ssh" and silently miss the protected server.
    """
    t = re.sub(r"^[A-Za-z][A-Za-z0-9+.-]*://", "", token.strip())
    t = t.split("@")[-1]
    t = t.split("/")[0]
    t = t.split(":")[0]
    return t.strip("[]")


def resolve(token: str) -> str:
    """Resolve an ssh target (alias, user@host, host) to its real hostname.

    Uses `ssh -G`, so ~/.ssh/config aliases are honoured — that is what closes
    the "add a new alias for the same IP" bypass.
    """
    host = hostpart(token)
    if not host:
        return ""
    try:
        out = subprocess.run(
            ["ssh", "-G", host], capture_output=True, text=True, timeout=5
        ).stdout
    except (OSError, subprocess.SubprocessError):
        return host
    for line in out.splitlines():
        if line.startswith("hostname "):
            return line.split(None, 1)[1].strip()
    return host


def protected_targets():
    """Resolved hostnames/IPs of the protected servers, plus their alias names."""
    names = set(PROTECTED_ALIASES)
    for alias in PROTECTED_ALIASES:
        r = resolve(alias)
        if r:
            names.add(r)
    return names


PROTECTED = protected_targets()


def is_protected(token: str) -> bool:
    if not token:
        return False
    host = hostpart(token)
    if host in PROTECTED:
        return True
    return resolve(host) in PROTECTED


def protected_mount_prefixes():
    """Local paths that are really the protected remote filesystems.

    gvfs names its mount dirs sftp:host=<host>[,user=<u>]; sshfs mounts are read
    from /proc/mounts. Both make a remote write look like a local file write.
    """
    prefixes = []

    gvfs_root = "/run/user/%d/gvfs" % os.getuid()
    try:
        for entry in os.listdir(gvfs_root):
            m = re.match(r"sftp:host=([^,]+)", entry)
            if m and is_protected(m.group(1)):
                prefixes.append(os.path.join(gvfs_root, entry))
    except OSError:
        pass

    try:
        with open("/proc/mounts", "r") as fh:
            for line in fh:
                parts = line.split()
                if len(parts) < 3 or not parts[2].startswith("fuse.sshfs"):
                    continue
                src, mnt = parts[0], parts[1].replace("\\040", " ")
                if is_protected(src):
                    prefixes.append(mnt)
    except OSError:
        pass

    return prefixes


def split_pipeline(cmd: str):
    """Split a shell string into individual simple commands."""
    return [c for c in re.split(r"(?:&&|\|\||[;|\n])", cmd) if c.strip()]


def classify(cmd: str):
    """Return None if the whole shell string only reads, else the offending part.

    Unknown binary -> treated as a write. Unparseable -> treated as a write.
    Fail-closed here is deliberate: we already know a protected host is involved,
    so "I cannot tell" must not mean "go ahead".
    """
    if WRITE_SHELL.search(cmd):
        return "shell redirection or stream write"

    for part in split_pipeline(cmd):
        try:
            toks = shlex.split(part)
        except ValueError:
            return part.strip()
        # Drop env-var prefixes (FOO=bar cmd) and sudo/nice wrappers.
        while toks and ("=" in toks[0].split(" ")[0] and not toks[0].startswith("-")
                        and re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", toks[0])):
            toks.pop(0)
        while toks and toks[0] in ("sudo", "nice", "nohup", "time", "env"):
            toks.pop(0)
            if toks and toks[0] == "-u":
                toks = toks[2:]
        if not toks:
            continue

        binary = os.path.basename(toks[0])
        args = [t for t in toks[1:] if t]
        sub = next((a for a in args if not a.startswith("-")), None)

        if binary == "curl":
            if CURL_WRITE_FLAGS.search(part):
                return part.strip()
            continue
        if binary == "nginx":
            if "-t" not in args and "-T" not in args:
                return part.strip()
            continue
        if binary == "docker" and sub == "compose":
            rest = [a for a in args if not a.startswith("-")][1:]
            nxt = rest[0] if rest else None
            if nxt not in COMPOSE_READONLY:
                return part.strip()
            continue
        if binary in READONLY_SUB:
            if sub not in READONLY_SUB[binary]:
                return part.strip()
            continue
        if binary in READONLY:
            continue
        return part.strip()

    return None


def block(reason: str):
    print(json.dumps({"decision": "block", "reason": reason}))
    sys.exit(0)


def check_bash(cmd: str):
    # --- PATH axis: a mounted remote is just a local path ---
    for prefix in protected_mount_prefixes():
        if prefix in cmd:
            offending = classify(cmd)
            if offending:
                block(
                    "Blocked: this writes to a PROTECTED remote server through the "
                    "mount %s (gvfs/sshfs makes a remote write look local). "
                    "Offending part: %s. Reads are allowed; a write to preprod/prod "
                    "must be done by the human." % (prefix, offending)
                )

    # --- COMMAND axis ---
    try:
        toks = shlex.split(cmd)
    except ValueError:
        toks = cmd.split()

    for i, tok in enumerate(toks):
        binary = os.path.basename(tok)

        if binary == "ssh":
            rest = toks[i + 1:]
            host = None
            j = 0
            while j < len(rest):
                a = rest[j]
                if a in ("-o", "-i", "-p", "-l", "-F", "-J", "-L", "-R", "-D",
                         "-b", "-c", "-E", "-e", "-I", "-m", "-O", "-Q", "-S",
                         "-W", "-w"):
                    j += 2
                    continue
                if a.startswith("-"):
                    j += 1
                    continue
                host = a
                break
            if host and is_protected(host):
                remote = " ".join(rest[j + 1:])
                if not remote.strip():
                    block(
                        "Blocked: interactive ssh session to PROTECTED server %s. "
                        "An interactive shell cannot be classified read-only. Run it "
                        "yourself, or pass an explicit read-only command." % host
                    )
                offending = classify(remote)
                if offending:
                    block(
                        "Blocked: write command on PROTECTED server %s. Offending "
                        "part: %s. Reads (cat, ls, docker ps, docker compose "
                        "config, journalctl, git log...) are allowed; writes to "
                        "preprod/prod must be done by the human." % (host, offending)
                    )

        elif binary in ("scp", "rsync"):
            positional = [a for a in toks[i + 1:] if not a.startswith("-")]
            if positional:
                dest = positional[-1]
                if ":" in dest and is_protected(dest):
                    block(
                        "Blocked: %s uploads to PROTECTED server %s. Downloading "
                        "FROM it is allowed (read); pushing TO it is not."
                        % (binary, dest.split(":")[0])
                    )

        elif binary == "sftp":
            for a in toks[i + 1:]:
                if not a.startswith("-") and is_protected(a):
                    block(
                        "Blocked: sftp session to PROTECTED server %s. It can `put`, "
                        "and an interactive session cannot be classified read-only." % a
                    )

        elif binary in ("ansible", "ansible-playbook", "ansible-pull"):
            for a in toks[i + 1:]:
                if is_protected(a):
                    block(
                        "Blocked: %s targets PROTECTED server %s. Ansible mutates by "
                        "design." % (binary, a)
                    )

        elif binary in ("docker", "docker-compose") and "-H" in toks[i + 1:]:
            k = toks.index("-H", i)
            if k + 1 < len(toks) and is_protected(toks[k + 1]):
                offending = classify(cmd)
                if offending:
                    block(
                        "Blocked: docker command against the PROTECTED daemon %s. "
                        "Offending part: %s." % (toks[k + 1], offending)
                    )

    m = re.search(r"DOCKER_HOST=([^\s;|&]+)", cmd)
    if m and is_protected(m.group(1)):
        offending = classify(cmd)
        if offending:
            block(
                "Blocked: DOCKER_HOST points at the PROTECTED daemon %s. Offending "
                "part: %s." % (m.group(1), offending)
            )


def check_path(path: str, tool: str):
    if not path:
        return
    real = os.path.abspath(path)
    for prefix in protected_mount_prefixes():
        if real.startswith(prefix):
            block(
                "Blocked: %s targets %s, which is the PROTECTED remote server mounted "
                "at %s. Editing a mounted path writes straight to preprod/prod — that "
                "is the human's call, not the agent's." % (tool, real, prefix)
            )


def main():
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        sys.exit(0)  # nothing to judge -> stay out of the way

    tool = payload.get("tool_name", "")
    ti = payload.get("tool_input", {}) or {}

    if tool == "Bash":
        check_bash(ti.get("command", "") or "")
    elif tool in ("Write", "Edit", "MultiEdit"):
        check_path(ti.get("file_path", "") or "", tool)
    elif tool == "NotebookEdit":
        check_path(ti.get("notebook_path", "") or "", tool)

    sys.exit(0)


if __name__ == "__main__":
    main()
