# Références — `rules/workspaces.md`

La procédure de déplacement d'un projet. Jamais chargé automatiquement : la règle garde le déclencheur et la raison. Sortie de la règle le 2026-11-03 (issue #73), parce que le geste est rare et que la règle la chargeait à chaque session. Texte d'origine.

---

## Déplacer un projet existant

Un dossier déplacé casse ce qui le vise par chemin absolu. Les liens de `~/.claude` (règles, skills, scripts, gardes de hooks) visent `agent-config`, et un garde cassé bloque **tous** les appels `Bash` et `Write`, donc on ne peut plus réparer depuis la session.

**À LA PLACE de** déplacer puis réparer, faire les deux dans **une seule commande** :

1. Lister d'abord, sans limite de profondeur : `find ~ -type l -lname '*<ancien chemin>*' -not -path "$HOME/.cache/*"`. Une limite de profondeur a manqué les gardes en profondeur 4 le 2026-10-08.
2. Déplacer, rebrancher les liens, corriger `~/.zshrc` et renommer le dossier d'historique `~/.claude/projects/<chemin-avec-tirets>` dans le même enchaînement. `policy/deny.yaml` interdit à l'agent d'écrire `~/.zshrc` (issue #47) : j'écris la commande, l'utilisateur la lance avec `! <commande>`.
3. Si la session est déjà bloquée, c'est à l'utilisateur de lancer la réparation avec `! <commande>`.
