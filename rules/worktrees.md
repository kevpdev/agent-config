# Worktrees — un par issue, partis d'`origin`

**DÉCLENCHEUR** : je commence une issue, ou un travail qui n'a pas encore d'issue, dans un dépôt git.

**À LA PLACE de** changer de branche dans le checkout principal, créer un worktree par issue avec `bash <dossier de config de l'agent>/scripts/worktree.sh create <nom> [--issue N]`, sans demander. Sans issue, un nom parlant suffit, l'issue se rattache après.

Le script est `~/.claude/scripts/worktree.sh` sous Claude Code et `~/.config/opencode/scripts/worktree.sh` sous OpenCode.

Le script choisit seul entre Orca et git, part d'`origin/<branche par défaut>` et rend le chemin du worktree en dernière ligne. Ses rangs et leurs raisons sont dans son en-tête (`tools/worktree.sh`).

- **Pas de la branche en cours**, même depuis un autre worktree. Seule exception, le travail empilé que l'utilisateur demande.
- **Après le merge**, supprimer le worktree et sa branche, locale et distante, avec `bash <dossier de config de l'agent>/scripts/worktree.sh remove <nom>`.
- **La session principale orchestre** : rôles, borne et routage dans `rules/aidd.md`, section « Rôles et boucle de correction ».
- **Un worktree n'est pas un projet** : `workspaces.md` ne s'applique pas à son dossier.
- **Projet lourd à installer** (plusieurs minutes de dépendances ou de build, une base à lui) : un worktree seulement pour le parallèle.
- **Harnais dont `~/.claude` pointe vers le checkout** : jamais de `git switch` ni de `git pull` dans ce checkout, voir le README d'`agent-config`.

**POURQUOI** : un `git switch` dans le checkout d'`agent-config` change les règles et les gardes de toutes les sessions ouvertes.
