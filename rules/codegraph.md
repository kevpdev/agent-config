# CodeGraph — le rayon d'impact avant de changer une fonction appelée

**DÉCLENCHEUR** : je m'apprête à changer la signature, le type de retour ou un champ d'une fonction, d'une classe ou d'une dataclass que d'autre code appelle, dans un repo qui porte un `.codegraph/`. Sous-agent compris.

**À LA PLACE de** lire les fichiers entiers et de deviner les appelants, lancer `codegraph_explore` sur le symbole avant d'éditer. Puis lire son rayon d'impact (*blast radius*, la liste de ce qui dépend du symbole), et planifier dans le même geste les appelants, les faux et les tests qui devront suivre. Sans le serveur MCP, la commande `codegraph explore "<symbole>"` rend la même sortie.

**POURQUOI** : en lisant le code, on trouve les dépendants après l'édition, pas avant. Ce qui se perd, c'est la vue des dépendances.

**CE QU'ELLE NE DEMANDE PAS** : passer par CodeGraph pour une chaîne de config, de doc ou de `aidd_docs/`, qu'il n'indexe pas. Là, `grep` reste le bon outil.

**Le contexte injecté ne vaut pas appel.** Le hook `UserPromptSubmit` (`codegraph prompt-hook`) cherche les mots du prompt, pas les symboles que je vais modifier. Son bloc ne dispense donc pas de l'appel.

## Index pollué par les worktrees

**DÉCLENCHEUR** : CodeGraph rend un même fichier sous deux chemins, dont une copie sous `.claude/worktrees/`.

**À LA PLACE de** choisir entre les copies, vérifier que `git check-ignore .claude/worktrees/x` répond. Sinon, ajouter `**/.claude/worktrees/` à `~/.config/git/ignore`, puis lancer `codegraph index`.

**POURQUOI** : CodeGraph saute tout ce que git ignore (son README, section des exclusions), et rien d'autre ne retire les worktrees des sous-agents.

Récits datés et raisons de rangement de cette page → `rules/references/ref-codegraph.md`.
