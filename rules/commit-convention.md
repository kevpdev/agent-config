## Commit Convention — Conventional Commits EN

### Format

```
<type>(<scope>): <subject>
```

- **type** (required): `feat`, `fix`, `refactor`, `docs`, `test`, `chore`, `perf`, `ci`
- **scope** (optional): affected module or layer (`auth`, `db`, `step1`)
- **subject** (required): English, imperative, lowercase, no trailing period

```
feat(step2): add BM25 hybrid search fallback
fix(db): resolve PgVector connection pool exhaustion
```

**No mention of Claude, AI, or co-authorship in any field.** The history records what changed and why, not which tool typed it. Naming an assistant dates badly and blurs who is accountable for the decision.

**Exception — Obsidian vault**: a vault commit puts the date in the scope (`docs(2026-07-23): import refs RAG`), and only its `<subject>` may be French. The English rule buys searchability for a shared, long-lived history, and a personal vault has neither the audience nor the tooling that pays for it. The subject bends, the machine-readable structure does not.

**WHY**: the type is read by tooling (changelog, semver, release filtering), and English outlives the team that wrote the history. A free-form or mixed-language log is invisible to both.

### What is enforced, and what is not

`guard-no-claude-in-commit.sh` refuses an AI mention, and a subject that fails the `<type>(<scope>): <subject>` grammar. It carries the same type list as this file, so a new type has to be added in both places.

It does **not** check English, imperative mood, the lowercase initial, the trailing period, or the date-as-scope form for a vault. Those five stay on judgment. Its subject extractor also fails open whenever it cannot read the message, which is deliberate: a guard that refuses a valid commit is the kind that gets switched off.

**And it is a Claude Code hook, not a git hook.** No repo carries a `commit-msg` hook and `core.hooksPath` is unset (measured 2026-08-05), so a commit typed by hand in a terminal passes unchecked. This convention is deterministic for the agent and advisory for the human.
