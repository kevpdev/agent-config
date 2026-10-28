# Worktrees — un par issue, partis de `main`

**DÉCLENCHEUR** : je commence une issue, ou un travail qui n'a pas encore d'issue, dans un dépôt git.

**À LA PLACE de** changer de branche dans le checkout principal, créer un worktree par issue, parti de la branche par défaut. Sans issue, un nom parlant suffit, l'issue se rattache après.

- **Pas de la branche en cours**, même depuis un autre worktree. Seule exception, le travail empilé que l'utilisateur demande.
- **Après le merge**, supprimer le worktree et sa branche, locale et distante.
- **Un worktree n'est pas un projet** : `workspaces.md` ne s'applique pas à son dossier.
- **Projet lourd à installer** (plusieurs minutes de dépendances ou de build, une base à lui) : un worktree seulement pour le parallèle.
- **Harnais dont `~/.claude` pointe vers le checkout** : jamais de `git switch` ni de `git pull` dans ce checkout, voir le README d'`agent-config`.

**POURQUOI** : un `git switch` dans le checkout d'`agent-config` change les règles et les gardes de toutes les sessions ouvertes. Ailleurs, le worktree évite le `stash` et le fichier oublié au changement de branche.

## Dans Orca

**DÉCLENCHEUR** : la même chose, et `ORCA_WORKTREE_ID` est défini dans l'environnement du shell.

**À LA PLACE de** `git worktree add`, créer le worktree par Orca, sans demander : décidé par l'utilisateur le 2026-10-28. Charger le skill `orca-cli` avant la première commande, il charge le guide qui correspond à la version installée. S'il manque, `orca-ide --help`.

- **Sous Linux, `orca-ide`, jamais `orca`** : hors d'un terminal Orca, `orca` lance le lecteur d'écran GNOME.
- **Les commandes ne sont pas recopiées ici** : le CLI change avec les versions d'Orca, le guide du skill suit la version.

**POURQUOI, mesuré le 2026-10-28** : 2 dépôts sur 3 enregistrés dans Orca cachent les worktrees créés hors d'Orca (`externalWorktreeVisibility: hide`). Un worktree Orca rattache aussi l'issue et lance un agent avec son brief en une seule commande.
