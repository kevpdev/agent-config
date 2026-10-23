# Suivi — refonte agnostique du harnais

Fichier de reprise du chantier. Le cadrage, qui fait foi, est dans `audits/2026-10-22-cadrage-harnais-agnostique.md`, avec le découpage en 13 tâches dans sa dernière section. Ce fichier ne porte que l'état. Il se met à jour à la fin de chaque tâche.

## Où vit le travail

- Le worktree `~/Developpement/Workspaces/agent-config-v2` est sur la branche `harness-v2`. Le checkout principal `agent-config` reste sur `main`, et c'est lui que vise `~/.claude`.
- Le tag `pre-v2` sur `d284502` est le point de retour arrière. La liste des 68 liens de `~/.claude` à cette date est dans `audits/2026-10-22-liens-pre-v2.txt`.
- Le banc isolé est `~/.claude-bench`, connecté une fois par `/login`. Il sert à prouver ce que le worktree charge sans toucher `~/.claude`.

## Le flux d'une tâche

1. Cadrer la tâche, dire la recommandation, puis attendre l'accord. Ensuite, plan mode.
2. Ouvrir l'issue par `aidd-vcs:04-issue-create`, avec un titre, un corps et un label validés avant création.
3. Créer une branche depuis `harness-v2`, puis ouvrir une PR draft vers `harness-v2` par `aidd-vcs:02-pull-request`.
4. Après le merge, fermer l'issue à la main. `Closes #` n'agit que sur la branche par défaut.

Commits et PR suivent les Conventional Commits, sujet en anglais, sans aucune mention d'IA, PR comprise.

## État au 2026-10-23

| Tâche | Issue | PR | Merge dans `harness-v2` |
|---|---|---|---|
| 1. Worktree, tag, sauvegarde des liens | #15 | — | `7ab852b` |
| 2. `tools/install.py` et manifeste Claude | #16 | #17 | `69b4751` |
| 3. Banc isolé Claude | #18 | #19 | `8f1ee6a` |
| 4. Rangement : `wrappers/claude/hooks/`, `tools/` | #21 | #22 | `1b1265b` |
| 5. Cœur des gardes dans `hooks/`, adaptateur Claude | #23 | #24 | `73cab94` |
| 6. Plugin OpenCode `harness-guards`, banc OpenCode | #25 | #26 | `170bec3` |
| 7. Skills du repo servis à OpenCode par liens | #27 | branche `feat/opencode-skills` | à merger |

**Prochaine étape** : cadrer la tâche 8, l'`AGENTS.md` global généré depuis `rules/`.

## La référence de parité

Après chaque tâche, ces commandes doivent rendre ce qui suit :

```bash
cd ~/Developpement/Workspaces/agent-config-v2
bash tools/test-all.sh          # 15 batteries, 0 en échec
bash tools/bench.sh claude      # 17 rules d'origine worktree, 26 skills du repo, 6 plugins, 7 hooks résolus, aucune fuite
bash tools/bench.sh opencode    # commit signé refusé en permission.rejected, ls passe, 12 skills auto exposés, 0 des 14 manuels, ~/.config/opencode inchangé
```

- Le banc rend 100 skills au total : 26 du repo, 17 intégrés, 47 des plugins AIDD et 10 `anthropic-skills:*` du compte. À la tâche 3, il en rendait 43, parce que `init` ne listait pas encore les skills préfixés. Relancé sur `8f1ee6a`, il rend aussi 100, donc l'écart ne vient pas du repo.
- Les 4 rules qui portent un `paths:` (`back-spring`, `front-react`, `backend-api`, `frontend-design`) ne se chargent pas dans une session vide. C'est attendu.
- Tant que la bascule (tâche 13) n'a pas eu lieu, `install.py --check` sur `~/.claude` rend 13 écarts avec le manifeste de `harness-v2`. Ce sont les liens dont la source a bougé à la tâche 4. Le vivant se contrôle en comparant ses liens à `audits/2026-10-22-liens-pre-v2.txt`.

## Décisions prises en route

- La disposition installée sous `~/.claude/scripts/` ne change pas avant la bascule. Ce sont les `source` du manifeste qui ont bougé, pas les cibles.
- `sync-rules.sh` et `sync-settings.py` restent jusqu'à la tâche 13, parce que `install.py` importe `sync-settings.py`.
- `wrappers/claude/settings.json` porte `model: "opus"`.
- Tâche 6 : le plugin écoute deux hooks. `permission.evaluate` refuse, et `tool.execute.before` lui fournit la commande entière et son `workdir`, que l'évaluation du shell ne porte pas. L'ordre et l'identifiant commun sont lus dans le source d'OpenCode (`packages/core/src/tool.ts`, l. 272, et `tool/plugin/shell.ts`, l. 118-140). Le banc les a confirmés au premier lancement.
- Tâche 6 : `python3` sort en code 2 sur un script qu'il ne peut pas ouvrir, le même code que le refus de `check.py`. Le plugin vérifie donc que le script existe avant de le lancer. C'est la batterie du plugin qui l'a montré.
- Tâche 7 : les skills passent à OpenCode par des liens sous `skills/` du dossier de config, pas par `skills: [...]` dans un `opencode.jsonc` comme le prévoyait le cadrage. Mesuré le 2026-10-23 : un skill lié dans `~/.opencode-bench/skills/` apparaît dans `core/skill-guidance`. La génération d'`opencode.jsonc` attend les tâches 9 et 10, qui en ont besoin.
- Tâche 7, décision pour la bascule (tâche 13) : poser `OPENCODE_DISABLE_CLAUDE_CODE_SKILLS=1` dans `~/.zshrc`. Sans elle, OpenCode verrait les skills du repo deux fois, par `~/.claude/skills` et par ses liens (dédoublonnage supposé, pas mesuré). La coupure retire aussi les 10 skills claude.ai de `~/.claude/skills/synced/`, faits pour l'environnement de claude.ai.
- Tâche 6 : `install.py --check` sur `~/.claude` rend les mêmes 14 écarts avant et après la tâche, donc la branche `settings` de Claude n'a pas bougé.
- Tâche 5 : le contrat du cœur est dans `hooks/check.py`. `exit 1` veut dire « entrée illisible », et chaque adaptateur décide quoi en faire. `skills_used: null` veut dire « inconnu », et le garde AIDD laisse alors passer.
- Tâche 5 : la parité de l'adaptateur Claude a été mesurée sur 963 commandes réelles tirées des transcripts, rejouées contre l'ancien et le nouveau garde. Résultat : 0 écart, et 35 refus identiques des deux côtés. Pour rejouer, il faut reprendre les anciens gardes par `git show 5af25cd:wrappers/claude/hooks/<garde>`.
- `git commit -m "fix: Claude"` **passe**, avant comme après la tâche 5 : nommer Claude n'est pas signer. Le critère de la tâche 6 dans le cadrage et la QA de l'issue #23 se testent donc avec `Co-Authored-By: Claude`.

## Fils ouverts, hors du chemin critique

- #20 : ranger `skills/_shared/` en `scripts/` et `references/`, avec un README. À faire entre deux tâches.
- Les plugins AIDD du banc sont plus récents que ceux du vivant, par exemple `aidd-vcs` 2.5.0 contre 2.4.0. C'est noté, pas corrigé.
- Le garde de mention d'IA ne couvre ni `gh api …/pulls`, ni `gh pr comment`, ni le format du titre de PR.
- Les branches mergées (`refactor/repo-layout`, `feat/claude-bench`, etc.) existent encore sur le dépôt distant.
- `skills_used` sous OpenCode : l'outil `skill` laisse `input.id` dans `opencode.db`, donc le plugin pourrait suivre les skills lancés. Tant que ce n'est pas fait, le garde AIDD ne refuse jamais sous OpenCode.
