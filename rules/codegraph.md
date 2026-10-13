# CodeGraph — le rayon d'impact avant de changer une fonction appelée

**DÉCLENCHEUR** : je m'apprête à changer la signature, le type de retour ou un champ d'une fonction, d'une classe ou d'une dataclass que d'autre code appelle, dans un repo qui porte un `.codegraph/`. Sous-agent compris.

**À LA PLACE de** lire les fichiers entiers et de deviner les appelants, lancer `codegraph_explore` sur le symbole avant d'éditer. Puis lire son rayon d'impact (*blast radius*, la liste de ce qui dépend du symbole), et planifier dans le même geste les appelants, les faux et les tests qui devront suivre. Sans le serveur MCP, la commande `codegraph explore "<symbole>"` rend la même sortie.

**CE QU'ELLE NE DEMANDE PAS** : passer par CodeGraph pour une chaîne de config, de doc ou de `aidd_docs/`, qu'il n'indexe pas. Là, `grep` reste le bon outil.

**Le contexte injecté ne vaut pas appel.** Le hook `UserPromptSubmit` (`codegraph prompt-hook`) cherche les mots du prompt, pas les symboles que je vais modifier. Son bloc ne dispense donc pas de l'appel.

**Un même fichier sous deux chemins signale un index pollué.** Quand CodeGraph rend une copie sous `.claude/worktrees/`, ne pas choisir entre les copies. Vérifier que `git check-ignore .claude/worktrees/x` répond. Sinon, ajouter `**/.claude/worktrees/` à `~/.config/git/ignore`, puis lancer `codegraph index`. CodeGraph saute tout ce que git ignore (son README, section des exclusions), et rien d'autre ne retire les worktrees des sous-agents.

**POURQUOI, constaté le 2026-10-13 sur `yt-transcriber`** : le hook a injecté trois copies de `app/runs.py`, dont deux venaient de worktrees de sous-agents. `~/.config/git/ignore` n'est versionné nulle part, donc cette page est ce qui survit à une nouvelle machine.

**POURQUOI, constaté le 2026-10-12 sur `yt-transcriber`, issue #8** : la session principale n'a jamais appelé CodeGraph, alors que la consigne générale de `~/.claude/CLAUDE.md` était chargée. Pour le sous-agent exécutant, ce n'est pas vérifié. `download_audio` et `Transcriber.run` ont changé de type de retour, et leurs trois dépendants (`app/fake.py`, `tests/test_jobs.py`, `tests/test_fake.py`) ont été trouvés en lisant le code, pas avant d'éditer. Sur un repo de 550 lignes, lire coûte autant de tokens. Ce qui se perd, c'est la vue des dépendances.

**POURQUOI ici et pas dans `~/.claude/CLAUDE.md`** : cette section est balisée (`CODEGRAPH_START`) et appartient à `codegraph install`, hors du repo. Une page de `rules/` est versionnée et injectée aux sous-agents, alors que l'auto-memory ne l'est pas (cf. `memory-policy.md`).
