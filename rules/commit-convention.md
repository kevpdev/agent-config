# Commits — Conventional Commits, sujet anglais

Format `<type>(<scope>): <subject>`, zéro mention de Claude, d'IA ou de co-auteur, exception vault comprise : **tenus par** `wrappers/claude/scripts/hooks/guard-no-claude-in-commit.sh`, qui refuse à l'appel et donne la liste des types dans son message. Ne pas recopier ses critères ici, cette liste a déjà divergé une fois (`aidd_docs/memory/vcs.md` chez Winggy documente `style` et `revert`, que le garde refuse).

**Ce qu'il ne vérifie pas, donc du jugement** : sujet en **anglais**, à l'impératif, initiale minuscule, sans point final. Pour le vault, seul le `<subject>` peut être français, par exemple `docs(2026-07-23): import refs RAG`.

**POURQUOI** : le type est lu par l'outillage (changelog, semver) et l'anglais survit à l'équipe qui a écrit l'historique. Un historique enregistre ce qui a changé, pas quel outil a tapé, et nommer un assistant brouille qui répond de la décision.
