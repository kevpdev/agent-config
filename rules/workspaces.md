# Workspaces — un projet, un dossier, au premier niveau

**DÉCLENCHEUR** : je cherche, crée, clone ou déplace un projet sous `~/Developpement/Workspaces`.

**La règle** : chaque projet est un dossier directement sous `Workspaces/`, nommé comme son dépôt. Aucun dossier de catégorie (langage, techno, client).

- **Chercher** : `ls ~/Developpement/Workspaces`, puis un `grep` sur le nom. Ne jamais deviner un sous-dossier.
- **Cloner ou créer** : `ls` d'abord. Si `Workspaces/<nom>` existe, c'est le projet, il n'y a rien à cloner.
- **Un produit en plusieurs dépôts** : des dossiers frères au préfixe commun (`focusflow-back`, `focusflow-front`), jamais l'un dans l'autre.
- **Fichiers hors projet** : dans `_vrac/`, jamais à la racine de `Workspaces/`.
- **Dépôts imbriqués** : interdits. Un dossier de projet ne contient pas un autre dépôt.

**POURQUOI**, constaté le 2026-10-08 : un rangement par langage avait laissé trois dossiers vides et séparé `focusflow-back` de `focusflow-front`, deux moitiés d'un même produit. Il m'a aussi fait cloner `swapi` hors de `Workspaces/` : la bonne case ne se déduisait pas du nom. À plat, le nom du dépôt suffit à retrouver le dossier, et `ccp` (`~/.zshrc`) liste déjà les projets par `.git`, `package.json` ou `pom.xml` sans connaître de catégorie.

## Le vault perso : par sa variable, jamais par son nom

**DÉCLENCHEUR** : je cherche le vault, un de ses skills (`.agents/skills/`) ou une note.

**À LA PLACE de** deviner le dossier ou lancer un `find` sur `~`, lire `$OBSIDIAN_VAULT_PERSO`. Si l'environnement du shell est vide, `grep OBSIDIAN_VAULT_PERSO ~/.zshrc` donne le chemin (définie à la ligne `export`, utilisée par les alias `ccvault` et `ccovault`). Les skills du vault sont dans `$OBSIDIAN_VAULT_PERSO/.agents/skills/`.

**POURQUOI** : le nom du dossier se dérive et peut changer, la variable est la seule source qui suit un renommage.

## Déplacer un projet existant

Un dossier déplacé casse ce qui le vise par chemin absolu. Les liens de `~/.claude` (règles, skills, scripts, gardes de hooks) visent `agent-config`, et un garde cassé bloque **tous** les appels `Bash` et `Write`, donc on ne peut plus réparer depuis la session.

**À LA PLACE de** déplacer puis réparer, faire les deux dans **une seule commande** :

1. Lister d'abord, sans limite de profondeur : `find ~ -type l -lname '*<ancien chemin>*' -not -path "$HOME/.cache/*"`. Une limite de profondeur a manqué les gardes en profondeur 4 le 2026-10-08.
2. Déplacer, rebrancher les liens, corriger `~/.zshrc` et renommer le dossier d'historique `~/.claude/projects/<chemin-avec-tirets>` dans le même enchaînement.
3. Si la session est déjà bloquée, c'est à l'utilisateur de lancer la réparation avec `! <commande>`.

**TEST** : `ls -p ~/Developpement/Workspaces | grep -v /` ne renvoie aucun fichier, et chaque dossier de premier niveau est un projet, `VPS/` ou `_vrac/`.
