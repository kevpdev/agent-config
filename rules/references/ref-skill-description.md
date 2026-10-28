# Références — `rules/skill-description.md`

La mesure, les sources et la raison de rangement de la règle. Jamais chargé automatiquement : la règle garde le déclencheur, les deux consignes et le test. Sortis de la règle le 2026-10-28 (issue #66), texte d'origine.

---

## Pourquoi la règle est globale et non scopée par `paths:`

**POURQUOI global et non scopé par `paths:`** : un `paths:` se déclenche à l'édition, et la planification vient avant. Constaté le 2026-10-15 : un plan d'extension de `video-brief` a été écrit sans que cette règle soit chargée, rattrapée seulement parce que l'utilisateur l'a citée. La règle est courte, la charger toujours coûte presque rien.

## Les chevrons échappés (2026-10-15)

**POURQUOI, mesuré le 2026-10-15** : `/capture-video <url>` dans une `description` sortait en `&lt;url&gt;` dans la liste des skills. La doc range les arguments dans `argument-hint`, qui s'affiche à l'autocomplétion. Je ne sais pas si cette autocomplétion montre aussi la `description` : non mesuré.

## Sources

**Sources** : `platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices` (section « Writing effective descriptions ») et `code.claude.com/docs/en/skills` (champs `description` et `argument-hint`).
