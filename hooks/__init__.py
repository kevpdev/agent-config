"""Guard core: the decisions, with no agent's payload format in them.

Each module exposes `decide(event) -> str | None`, the refusal reason or None.
The event shape and the command-line contract are in hooks/check.py. Each agent
reaches this package through its own adapter (wrappers/<agent>/hooks/).
"""

from hooks import aidd_skill_lookup, bash_tooling, no_ai_in_commit, no_remote_write, no_secret_read

# Run in this order by check.py; the first refusal wins.
GUARDS = {
    "no_ai_in_commit": no_ai_in_commit,
    "no_remote_write": no_remote_write,
    "no_secret_read": no_secret_read,
    "bash_tooling": bash_tooling,
    "aidd_skill_lookup": aidd_skill_lookup,
}


def first_refusal(event, names=None):
    """Reason of the first guard that refuses `event`, or None."""
    for name in names or GUARDS:
        reason = GUARDS[name].decide(event)
        if reason:
            return reason
    return None
