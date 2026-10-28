"""deny_policy — reads policy/deny.yaml and says which entry a path falls under.

Shared by no_secret_read (action `read`) and no_sensitive_write (action `write`),
so both guards read the same file with the same matching.

A `fin` takes three shapes:
  - `~/.zshrc`    anchored at the home directory
  - `/etc/**`     anchored at the root
  - `.ssh/id_rsa` a suffix of components, at any depth
Each component is an fnmatch pattern, and `**` matches zero or more components:
`.git/**` designates `.git` itself and everything under it.
"""

import fnmatch
import os
import sys

from hooks.bash_tooling import HEREDOC

REPO = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
DENY = os.path.join(REPO, "policy", "deny.yaml")


def load_entries(action, guard, path=DENY):
    """Entries of deny.yaml for `action`, or None when it cannot be read (the guard fails open)."""
    try:
        import yaml
        with open(path, encoding="utf-8") as f:
            entries = yaml.safe_load(f) or []
        return [e for e in entries if e.get("action") == action and e.get("fin")]
    except Exception as exc:  # noqa: BLE001 — any failure means no verdict
        print(f"{guard}: {path} illisible ({exc}), pas de verdict rendu.", file=sys.stderr)
        return None


def _match(parts, pattern):
    """True when the components `parts` match `pattern` from start to end."""
    if not pattern:
        return not parts
    if pattern[0] == "**":
        return any(_match(parts[i:], pattern[1:]) for i in range(len(parts) + 1))
    return bool(parts) and fnmatch.fnmatchcase(parts[0], pattern[0]) and _match(parts[1:], pattern[1:])


def designates(path: str, fin: str) -> bool:
    """True when the absolute, normalized `path` falls under `fin`."""
    parts = [p for p in path.split("/") if p]
    if fin.startswith("~/"):
        fin = os.path.expanduser("~") + fin[1:]
    want = [p for p in fin.split("/") if p]
    if fin.startswith("/"):
        return _match(parts, want)
    return any(_match(parts[k:], want) for k in range(len(parts) + 1))


def resolve(token: str, cwd: str) -> str:
    """Absolute, normalized path a shell token names, `~` and `$HOME` expanded."""
    return os.path.normpath(os.path.join(cwd, os.path.expandvars(os.path.expanduser(token))))


def matching(path: str, entries):
    """The entry `path` falls under, `sauf` honoured, or None."""
    for e in entries:
        if designates(path, e["fin"]) and not any(designates(path, s) for s in e.get("sauf") or []):
            return e
    return None


def denied(token: str, cwd: str, entries):
    """The entry the shell token `token` designates, or None. `--opt=path` is followed."""
    if not token or token.startswith("-") and "=" not in token:
        return None
    if token.startswith("-"):
        token = token.split("=", 1)[1]
    return matching(resolve(token, cwd), entries)


def strip_heredocs(command: str) -> str:
    """`command` without its heredoc bodies: `cat >> f <<'EOF'` writes them, it does not run them."""
    kept, pending = [], []
    for line in command.split("\n"):
        if pending:
            if line.lstrip("\t") == pending[0]:
                pending.pop(0)
            continue
        kept.append(line)
        pending = [m.group(2) for m in HEREDOC.finditer(line)]
    return "\n".join(kept)
