# Workspaces — un projet, un dossier, au premier niveau

**DÉCLENCHEUR** : je cherche, crée, clone ou déplace un projet sous `~/Developpement/Workspaces`.

**La règle** : chaque projet est un dossier directement sous `Workspaces/`, nommé comme son dépôt. Aucun dossier de catégorie (langage, techno, client).

- **Chercher** : `ls ~/Developpement/Workspaces`, puis un `grep` sur le nom. Ne jamais deviner un sous-dossier.
- **Cloner ou créer** : `ls` d'abord. Si `Workspaces/<nom>` existe, c'est le projet, il n'y a rien à cloner.
- **Un produit en plusieurs dépôts** : des dossiers frères au préfixe commun (`focusflow-back`, `focusflow-front`), jamais l'un dans l'autre.
- **Fichiers hors projet** : dans `_vrac/`, jamais à la racine de `Workspaces/`.
- **Dépôts imbriqués** : interdits. Un dossier de projet ne contient pas un autre dépôt.

**POURQUOI**, constaté le 2026-10-08 : un rangement par langage avait laissé trois dossiers vides et séparé `focusflow-back` de `focusflow-front`, deux moitiés d'un même produit. Il m'a aussi fait cloner `swapi` hors de `Workspaces/` : la bonne case ne se déduisait pas du nom. À plat, le nom du dépôt suffit à retrouver le dossier, et `ccp` (`~/.zshrc`) liste déjà les projets par `.git`, `package.json` ou `pom.xml` sans connaître de catégorie.

## Créer un projet : par le skill, jamais à la main

**DÉCLENCHEUR** : le dossier d'un projet neuf reste à créer sous `~/Developpement/Workspaces`.

**À LA PLACE d'** échafauder à la main, passer par le skill `dev-init-project`. Il pose les questions, scaffolde, écrit les conventions du projet dans son `AGENTS.md` et amorce sa mémoire AIDD.

**POURQUOI cette ligne existe** : un projet créé à la main n'emporte ni ses conventions ni sa mémoire, et rien ne le signale plus tard. Le skill écrit hors de tout dépôt git, donc son déclenchement au flair se paie au pire un dossier à supprimer.

## Le vault perso : par sa variable, jamais par son nom

**DÉCLENCHEUR** : je cherche le vault, un de ses skills (`.agents/skills/`) ou une note.

**À LA PLACE de** deviner le dossier ou lancer un `find` sur `~`, lire `$OBSIDIAN_VAULT_PERSO`. Si l'environnement du shell est vide, `grep OBSIDIAN_VAULT_PERSO ~/.zshrc` donne le chemin (définie à la ligne `export`, utilisée par les alias `ccvault` et `ccovault`). Les skills du vault sont dans `$OBSIDIAN_VAULT_PERSO/.agents/skills/`.

**POURQUOI** : le nom du dossier se dérive et peut changer, la variable est la seule source qui suit un renommage.

## Déplacer un projet existant

**DÉCLENCHEUR** : je m'apprête à déplacer ou renommer un dossier de projet, `agent-config` surtout.

**À LA PLACE de** déplacer d'abord, lire `rules/references/ref-workspaces.md` et suivre sa procédure. Un garde de hook introuvable (les liens de `~/.claude` visent `agent-config`) bloque tous les appels `Bash` et `Write`, et la session ne peut plus se réparer.

**TEST** : `ls -p ~/Developpement/Workspaces | grep -v /` ne renvoie aucun fichier, et chaque dossier de premier niveau est un projet, `VPS/` ou `_vrac/`.
