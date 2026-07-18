## Commit Convention — Conventional Commits EN

All commit messages must follow the Conventional Commits specification in **English**.

### Format
```
<type>(<scope>): <subject>
```

- **type** (required): `feat`, `fix`, `refactor`, `docs`, `test`, `chore`, `perf`, `ci`
- **scope** (optional): affected module or layer, e.g. `auth`, `step1`, `db`
- **subject** (required): imperative, lowercase, no period at end

### Examples
```
feat(step2): add BM25 hybrid search fallback
fix(db): resolve PgVector connection pool exhaustion
refactor(eval): extract scoring logic into separate service
docs: update README with PostgreSQL migration steps
chore(deps): upgrade spring-boot to 3.4.2
```

### Rules
- Subject must be in English
- No capital first letter in subject
- No trailing period
- No mention of Claude, AI, or co-authorship in any field

### Why

**Structured format**: `<type>(<scope>)` is machine-readable. Changelog generation, semver bumps and release filtering all read the type — a free-form message is invisible to that tooling.

**English**: the history outlives the team that wrote it and travels with the repo. A mixed-language log is unsearchable.

**Imperative, lowercase, no period**: a subject completes the sentence "this commit will…". Lowercase and no period keep generated changelogs uniform without post-processing.

**No AI or co-authorship mention**: the history records *what changed and why*, not which tool typed it. Naming an assistant adds noise, dates badly, and blurs who is accountable for the decision.
