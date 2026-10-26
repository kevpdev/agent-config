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

## État au 2026-10-26

| Tâche | Issue | PR | Merge dans `harness-v2` |
|---|---|---|---|
| 1. Worktree, tag, sauvegarde des liens | #15 | — | `7ab852b` |
| 2. `tools/install.py` et manifeste Claude | #16 | #17 | `69b4751` |
| 3. Banc isolé Claude | #18 | #19 | `8f1ee6a` |
| 4. Rangement : `wrappers/claude/hooks/`, `tools/` | #21 | #22 | `1b1265b` |
| 5. Cœur des gardes dans `hooks/`, adaptateur Claude | #23 | #24 | `73cab94` |
| 6. Plugin OpenCode `harness-guards`, banc OpenCode | #25 | #26 | `170bec3` |
| 7. Skills du repo servis à OpenCode par liens | #27 | #28 | `b693130` |
| 8. Rules du repo servies à OpenCode par `instructions` | #29 | #30 | `dd91ab4` |
| 9. Lectures interdites, `policy/deny.yaml` pour les deux agents | #31 | branche `feat/deny-policy` | à merger |

**Prochaine étape** : cadrer la tâche 10, `mcp/servers.yaml` et la délégation à `codegraph install`.

## La référence de parité

Après chaque tâche, ces commandes doivent rendre ce qui suit :

```bash
cd ~/Developpement/Workspaces/agent-config-v2
bash tools/test-all.sh          # 16 batteries, 0 en échec
bash tools/bench.sh claude      # 17 rules d'origine worktree, 26 skills du repo, 6 plugins, 7 hooks résolus, aucune fuite, Read du leurre refusé en bypass
bash tools/bench.sh opencode    # commit signé refusé en permission.rejected, ls passe, 12 skills auto exposés, 0 des 14 manuels, 19 règles chargées, read du leurre refusé, ~/.config/opencode inchangé
```

- Le banc rend 100 skills au total : 26 du repo, 17 intégrés, 47 des plugins AIDD et 10 `anthropic-skills:*` du compte. À la tâche 3, il en rendait 43, parce que `init` ne listait pas encore les skills préfixés. Relancé sur `8f1ee6a`, il rend aussi 100, donc l'écart ne vient pas du repo.
- Les 4 rules qui portent un `paths:` (`back-spring`, `front-react`, `backend-api`, `frontend-design`) ne se chargent pas dans une session vide. C'est attendu.
- Tant que la bascule (tâche 13) n'a pas eu lieu, `install.py --check` sur `~/.claude` rend 15 écarts avec le manifeste de `harness-v2`. Ce sont les 13 liens dont la source a bougé à la tâche 4, `model` et `permissions.deny` (tâche 9). Le vivant se contrôle en comparant ses liens à `audits/2026-10-22-liens-pre-v2.txt`.

## Décisions prises en route

- La disposition installée sous `~/.claude/scripts/` ne change pas avant la bascule. Ce sont les `source` du manifeste qui ont bougé, pas les cibles.
- `sync-rules.sh` et `sync-settings.py` restent jusqu'à la tâche 13, parce que `install.py` importe `sync-settings.py`.
- `wrappers/claude/settings.json` porte `model: "opus"`.
- Tâche 6 : le plugin écoute deux hooks. `permission.evaluate` refuse, et `tool.execute.before` lui fournit la commande entière et son `workdir`, que l'évaluation du shell ne porte pas. L'ordre et l'identifiant commun sont lus dans le source d'OpenCode (`packages/core/src/tool.ts`, l. 272, et `tool/plugin/shell.ts`, l. 118-140). Le banc les a confirmés au premier lancement.
- Tâche 6 : `python3` sort en code 2 sur un script qu'il ne peut pas ouvrir, le même code que le refus de `check.py`. Le plugin vérifie donc que le script existe avant de le lancer. C'est la batterie du plugin qui l'a montré.
- Tâche 7 : les skills passent à OpenCode par des liens sous `skills/` du dossier de config, pas par `skills: [...]` dans un `opencode.jsonc` comme le prévoyait le cadrage. Mesuré le 2026-10-23 : un skill lié dans `~/.opencode-bench/skills/` apparaît dans `core/skill-guidance`. La génération d'`opencode.jsonc` attend les tâches 9 et 10, qui en ont besoin.
- Tâche 7, décision pour la bascule (tâche 13) : poser `OPENCODE_DISABLE_CLAUDE_CODE_SKILLS=1` dans `~/.zshrc`. Sans elle, OpenCode verrait les skills du repo deux fois, par `~/.claude/skills` et par ses liens (dédoublonnage supposé, pas mesuré). La coupure retire aussi les 10 skills claude.ai de `~/.claude/skills/synced/`, faits pour l'environnement de claude.ai.
- Tâche 8 : les règles passent à OpenCode par `instructions: ["{repo}/rules/*.md"]` dans un `opencode.json` installé, pas par un `AGENTS.md` généré comme le prévoyait le cadrage. Mesuré le 2026-10-23 : le glob charge chaque fichier, avec son chemin absolu, dans `core/instructions`. Aucune copie à tenir à jour, et `~/.config/opencode/AGENTS.md` reste libre pour le vivant. `install.py` fusionne désormais tout fichier déclaré par `settings`, sous le nom de sa source.
- Tâche 8 : le scope `paths:` des 4 règles scopées est redit en tête de chacune, sur une ligne **Portée**. Les deux principes d'`ai-principles.md` réduits à leur titre ont retrouvé le texte d'avant `6c59ff6`. Les deux changements vivent dans le cœur et ne changent rien sous Claude : le banc Claude charge toujours 17 fichiers d'instructions.
- Tâche 9 : les lectures interdites passent à OpenCode par `policies` (`tool.use`, `read:<fin>` et `read:*/<fin>`) plutôt que par `permissions`. Une policy passe après les règles d'agent et les approbations enregistrées, donc ni `--auto` ni « Allow always » ne la lève (doc `policies.mdx`). À Claude, elles passent par `permissions.deny`, sous la forme `Read(//**/<fin>)`.
- Tâche 9, mesuré le 2026-10-26 sur un leurre hors du home, avec un mot témoin : Claude refuse le Read en `bypassPermissions`, ce qui tranche la question ouverte du cadrage. Il refuse aussi le `cat` du même fichier. Sous OpenCode, le `read` est refusé (« Blocked by configuration policy ») et le `cat` laisse sortir le témoin.
- Tâche 9 : une entrée à exception (`sauf`) n'est pas traduite pour Claude, où un `deny` gagne toujours. `.env.*` n'est donc interdit que sous OpenCode, et `.env.example` y reste lisible.
- Tâche 9 : le banc OpenCode fixe son modèle (`openrouter/recursive/flint-v1.0:free`, celui du 2026-10-23). Le 2026-10-26, le défaut était passé à un modèle `opencode-go` que le fournisseur refusait.
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
- Des paragraphes propres à Claude vivent dans des règles neutres, que lit aussi OpenCode : la section « Déplacer un projet existant » de `workspaces.md` (liens de `~/.claude`) et le hook `UserPromptSubmit` de `codegraph.md`. Le cadrage les renvoie à l'adaptateur.
- `rules/references/` n'est installé ni pour Claude (le manifeste ne lie que `rules/*.md`) ni pour OpenCode. Les règles y renvoient par chemin relatif.
- Lecture d'un secret par le shell sous OpenCode : `cat` passe, mesuré à la tâche 9. Le fermer demande un garde du cœur sur l'action `shell`, qui reconnaisse une lecture de fin interdite.
- La fusion remplace une liste entière : un `policies` posé à la main dans le vivant `opencode.json` serait écrasé par celui de `deny.yaml`. Le vivant n'en a pas aujourd'hui.
