"""no_remote_write — guard core, agent-neutral (contract in hooks/check.py).

Blocks agent-initiated WRITES to the protected remote hosts.

Which hosts are protected is DECLARED, never guessed: one ssh alias per line in
~/.config/agent-config/protected-hosts (XDG_CONFIG_HOME honoured, overridden by
AGENT_CONFIG_PROTECTED_HOSTS). A host is protected because it is listed there,
never because it looks like a prod. No file or an empty one means nothing is
protected, and `python3 hooks/no_remote_write.py --status` says so. tools/bascule.sh
prints that status after every switch, because a dead list reads like a protection.
The signal shows at the next switch, not at the moment a list dies (an edit of
~/.ssh/config between two switches stays silent until then).
Reads stay allowed: losing diagnosis ability would make the guard so annoying
it would get disabled, and a disabled guard protects less than a narrow one.

Threat model = "the agent makes a mistake", NOT "the agent evades the guard".
String inspection of a shell command can always be defeated (`bash -lc "$V"`,
base64, ...). This is a seatbelt against the accidental `docker compose down`
on prod, not a sandbox.

Out of scope, on purpose: `git push` to a protected host (no deploy goes through
git today) and `gh repo create` (GitHub is not a protected host).

Three axes, because any one alone leaves a hole:

  1. COMMAND axis — ssh / scp / sftp / rsync / ansible / docker -H / DOCKER_HOST.
     Host tokens are resolved through `ssh -G`, so an alias added to
     ~/.ssh/config pointing at a protected IP is still caught: we compare the
     RESOLVED hostname, never the literal string typed.

  2. PATH axis — a gvfs or sshfs mount turns the remote host into an ordinary
     local path. Writing to
       /run/user/1000/gvfs/sftp:host=vps/home/deploy/docker-compose.yml
     mentions no ssh, no hostname, no IP. A command-only guard sees nothing.

  3. HTTP axis — a local `curl` or `wget` whose URL names a protected host and
     carries a body or a verb other than GET/HEAD/OPTIONS writes to that host's API
     without any ssh. The URL host is matched as typed: an API domain that differs
     from the ssh HostName must be listed in protected-hosts as well. Not seen:
     other HTTP clients (httpie, python requests) and a URL built in a variable.

Classification is an ALLOWLIST of read-only commands, not a denylist of
dangerous ones: a denylist is open by construction (every unlisted binary
passes), an allowlist is closed (every unlisted binary is refused).
"""

import functools
import os
import re
import shlex
import subprocess

# Hosts left out of the list stay writable on purpose: a sandbox server must stay
# usable, and blocking it would create the friction that gets guards switched off.


def hosts_file() -> str:
    explicit = os.environ.get("AGENT_CONFIG_PROTECTED_HOSTS")
    if explicit:
        return explicit
    base = os.environ.get("XDG_CONFIG_HOME") or os.path.expanduser("~/.config")
    return os.path.join(base, "agent-config", "protected-hosts")


@functools.cache
def protected_aliases() -> tuple:
    """Declared aliases, one per line, `#` starts a comment. Unreadable means none."""
    try:
        with open(hosts_file(), encoding="utf-8") as fh:
            lines = [line.split("#", 1)[0].strip() for line in fh]
    except OSError:
        return ()
    return tuple(line for line in lines if line)

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

# curl and wget mutate as soon as they carry a body or a verb other than GET/HEAD.
READ_VERBS = {"GET", "HEAD", "OPTIONS"}
CURL_BODY_LONG = ("--json", "--data", "--form", "--upload-file")
WGET_WRITE_LONG = ("--post-data", "--post-file", "--body-data", "--body-file")


def strip_wrappers(toks: list) -> list:
    """Drop env-var prefixes (FOO=bar cmd) and sudo/nice/... wrappers."""
    toks = list(toks)
    while toks and re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", toks[0]):
        toks.pop(0)
    while toks and toks[0] in ("sudo", "nice", "nohup", "time", "env"):
        toks.pop(0)
        if toks and toks[0] == "-u":
            toks = toks[2:]
    return toks


def http_writes(toks: list) -> bool:
    """True when a curl or wget invocation sends a body or a non-read verb."""
    binary = os.path.basename(toks[0]) if toks else ""
    args = toks[1:]
    if binary == "wget":
        for i, a in enumerate(args):
            if a.startswith(WGET_WRITE_LONG):
                return True
            if a.startswith("--method"):
                verb = a.split("=", 1)[1] if "=" in a else (args[i + 1] if i + 1 < len(args) else "")
                if verb.upper() not in READ_VERBS:
                    return True
        return False
    if binary != "curl":
        return False
    for i, a in enumerate(args):
        if a.startswith(CURL_BODY_LONG):
            return True
        if a.startswith("--request"):
            verb = a.split("=", 1)[1] if "=" in a else (args[i + 1] if i + 1 < len(args) else "")
            if verb.upper() not in READ_VERBS:
                return True
        elif a.startswith("-") and not a.startswith("--"):
            flags = a[1:]
            for k, c in enumerate(flags):
                if c in "dFT":
                    return True
                if c == "X":
                    verb = flags[k + 1:] or (args[i + 1] if i + 1 < len(args) else "")
                    if verb.upper() not in READ_VERBS:
                        return True
                    break
    return False


# Redirections and stream writers, whatever the binary in front of them.
WRITE_SHELL = re.compile(r"(>>?|\btee\b|\bdd\b)")


def hostpart(token: str) -> str:
    """Extract the bare host from any target form.

    Handles alias, user@host, host:/path, and URL forms such as
    ssh://deploy@vps — DOCKER_HOST uses the last one, and a naive
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
        cmd = ["ssh", "-G", host]
        ssh_config = os.environ.get("AGENT_CONFIG_SSH_CONFIG")
        if ssh_config:
            cmd[1:1] = ["-F", ssh_config]
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=5).stdout
    except (OSError, subprocess.SubprocessError):
        return host
    for line in out.splitlines():
        if line.startswith("hostname "):
            return line.split(None, 1)[1].strip()
    return host


@functools.cache
def protected_targets():
    """Resolved hostnames/IPs of the protected servers, plus their alias names.

    Computed on first need, not at import: hooks/check.py imports every guard
    for every call, and two `ssh -G` per shell command would be paid even by
    a command that names no host at all.
    """
    names = set(protected_aliases())
    for alias in protected_aliases():
        r = resolve(alias)
        if r:
            names.add(r)
    return frozenset(names)


def is_protected(token: str) -> bool:
    if not token:
        return False
    host = hostpart(token)
    if not protected_aliases():
        return False
    if host in protected_aliases():
        return True
    protected = protected_targets()
    if host in protected:
        return True
    return resolve(host) in protected


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
        toks = strip_wrappers(toks)
        if not toks:
            continue

        binary = os.path.basename(toks[0])
        args = [t for t in toks[1:] if t]
        sub = next((a for a in args if not a.startswith("-")), None)

        if binary in ("curl", "wget"):
            if http_writes(toks):
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


class Refused(Exception):
    """Carries the refusal reason out of the nested checks to decide()."""


def block(reason: str):
    raise Refused(reason)


def check_bash(cmd: str):
    # --- PATH axis: a mounted remote is just a local path ---
    for prefix in protected_mount_prefixes():
        if prefix in cmd:
            offending = classify(cmd)
            if offending:
                block(
                    "Blocked: this writes to a PROTECTED remote server through the "
                    "mount %s (gvfs/sshfs makes a remote write look local). "
                    "Offending part: %s. Reads are allowed; a write to a protected host "
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
                        "a protected host must be done by the human." % (host, offending)
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

    # --- HTTP axis: a local curl that writes to a protected host's API ---
    for part in split_pipeline(cmd):
        try:
            ptoks = shlex.split(part)
        except ValueError:
            continue
        ptoks = strip_wrappers(ptoks)
        if not http_writes(ptoks):
            continue
        for target in ptoks[1:]:
            if target.startswith("-") or not re.match(r"^(https?://)?[\w.-]+(:\d+)?(/|$)", target):
                continue
            if is_protected(target):
                block(
                    "Blocked: %s writes to the API of PROTECTED host %s (body or "
                    "non-read verb). Reads stay allowed, a write must be done by "
                    "the human." % (os.path.basename(ptoks[0]), hostpart(target))
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
                "at %s. Editing a mounted path writes straight to a protected host — that "
                "is the human's call, not the agent's." % (tool, real, prefix)
            )


def decide(event: dict):
    """Reason to refuse this action, or None to let it through."""
    action = event.get("action")
    try:
        if action == "shell":
            check_bash(event.get("command") or "")
        elif action == "edit":
            for path in event.get("paths") or []:
                check_path(path, "edit")
    except Refused as refusal:
        return str(refusal)
    return None


def status() -> str:
    """One line saying whether the declared list still protects a live host.

    An alias is live when ssh resolves it to something else than its own name,
    i.e. a Host entry gives it a HostName. An entry with a dot (IP or API domain)
    counts as live without any check.
    """
    aliases = protected_aliases()
    if not aliases:
        return ("no_remote_write : aucune cible déclarée dans %s, le garde ne protège rien."
                % hosts_file())
    dead = [a for a in aliases if "." not in a and resolve(a) == a]
    if dead:
        return ("no_remote_write : %d sur %d cibles ne résolvent vers aucun HostName ssh (%s), "
                "elles ne protègent rien." % (len(dead), len(aliases), ", ".join(dead)))
    return "no_remote_write : %d cible(s) vivante(s) (%s)." % (len(aliases), ", ".join(aliases))


if __name__ == "__main__":
    import sys

    if sys.argv[1:] != ["--status"]:
        print("usage: no_remote_write.py --status", file=sys.stderr)
        sys.exit(1)
    print(status())
