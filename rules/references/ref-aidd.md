# Références — `rules/aidd.md`

Les décisions datées et l'historique de deux sections de la règle, « Chercher un skill avant d'agir » et « CI GitHub ». Jamais chargé automatiquement : la règle garde le déclencheur et un fait par pourquoi. Sortis de la règle le 2026-10-28 (issue #66), texte d'origine. Le contrat CI lui-même vit dans `ref-ci-github.md`.

---

## Chercher un skill — le pourquoi complet (2026-10-07)

**POURQUOI**, mesuré le 2026-10-07 : 9 issues écrites à la main alors qu'un skill existait, vu seulement quand l'utilisateur a posé la question. Aucun nom de skill ici, parce qu'ils dérivent, et `aidd_docs/` est le même signal que `memory-policy.md`.

## Chercher un skill — l'état du garde (2026-10-07)

**ÉTAT DU GARDE, décidé le 2026-10-07** : `guard-aidd-skill-lookup.py` rappelle et ne bloque pas, la sortie `# aidd-skip: <raison>` reste libre. On ne le durcit que si on constate que les skills AIDD sont ignorés malgré leur présence.

## CI GitHub — l'historique du contrat (2026-10-08)

**POURQUOI**, constaté le 2026-10-08 : la CI de `yt-transcriber` nommait ses jobs d'après ses outils (`check (ruff, pyright, pytest)`), donc le ruleset aurait changé avec chaque stack. Le contrat fixe les noms, et le script le mesure au lieu de laisser la relecture le deviner. Les trois noms fixes ont ensuite laissé place à une porte unique (issue `agent-config#8`) : `check` ne disait pas ce qu'il vérifiait et imposait le même découpage à toutes les stacks. Le README de `swapi` avait aussi été oublié dans la PR #1, relevé par l'utilisateur.
