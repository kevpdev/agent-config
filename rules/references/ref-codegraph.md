# Références — `rules/codegraph.md`

Les récits datés et les raisons de rangement de la règle. Jamais chargé automatiquement : la règle garde le déclencheur et un fait par pourquoi. Sortis de la règle le 2026-10-28 (issue #66), texte d'origine.

---

## L'index pollué par les worktrees (2026-10-13)

**POURQUOI, constaté le 2026-10-13 sur `yt-transcriber`** : le hook a injecté trois copies de `app/runs.py`, dont deux venaient de worktrees de sous-agents. `~/.config/git/ignore` n'est versionné nulle part, donc cette page est ce qui survit à une nouvelle machine.

## La consigne chargée mais jamais suivie (2026-10-12)

**POURQUOI, constaté le 2026-10-12 sur `yt-transcriber`, issue #8** : la session principale n'a jamais appelé CodeGraph, alors que la consigne générale de `~/.claude/CLAUDE.md` était chargée. Pour le sous-agent exécutant, ce n'est pas vérifié. `download_audio` et `Transcriber.run` ont changé de type de retour, et leurs trois dépendants (`app/fake.py`, `tests/test_jobs.py`, `tests/test_fake.py`) ont été trouvés en lisant le code, pas avant d'éditer. Sur un repo de 550 lignes, lire coûte autant de tokens. Ce qui se perd, c'est la vue des dépendances.

## Pourquoi la règle vit dans `rules/` et pas dans `~/.claude/CLAUDE.md`

**POURQUOI ici et pas dans `~/.claude/CLAUDE.md`** : cette section est balisée (`CODEGRAPH_START`) et appartient à `codegraph install`, hors du repo. Une page de `rules/` est versionnée et injectée aux sous-agents, alors que l'auto-memory ne l'est pas (cf. `memory-policy.md`).
