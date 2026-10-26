# Suivi — refonte agnostique du harnais

Fichier de reprise du chantier. Le cadrage, qui fait foi, est dans `audits/2026-10-22-cadrage-harnais-agnostique.md`, avec le découpage en 13 tâches dans sa dernière section. Ce fichier ne porte que l'état. Il se met à jour à la fin de chaque tâche.

## Où vit le travail

- Depuis la bascule du 2026-10-26, `main` porte la refonte (#41, `7c466a8`), et le checkout principal `agent-config` est sur `main`. C'est lui que visent `~/.claude` et `~/.config/opencode`.
- On ne change jamais de branche dans `agent-config`, parce qu'un checkout y change les fichiers derrière les liens. Le travail se fait dans le worktree `~/Developpement/Workspaces/agent-config-v2`, sur une branche tirée d'`origin/main`, et les PR visent `main`. Après un merge, le vivant se met à jour par `bash tools/bascule.sh`, lancé depuis le worktree, jamais par un `git pull`.
- Le tag `pre-v2` sur `d284502` est le point de retour arrière. La liste des 68 liens de `~/.claude` à cette date est dans `audits/2026-10-22-liens-pre-v2.txt`.
- Le banc isolé est `~/.claude-bench`, connecté une fois par `/login`. Il sert à prouver ce que le worktree charge sans toucher `~/.claude`.

## Le flux d'une tâche

1. Cadrer la tâche, dire la recommandation, puis attendre l'accord. Ensuite, plan mode.
2. Ouvrir l'issue par `aidd-vcs:04-issue-create`, avec un titre, un corps et un label validés avant création.
3. Dans le worktree `agent-config-v2`, créer une branche depuis `origin/main`, puis ouvrir une PR draft vers `main` par `aidd-vcs:02-pull-request`. Pendant la refonte, les branches partaient de `harness-v2`, aujourd'hui supprimée.
4. Après le merge, mettre le vivant à jour par `bash tools/bascule.sh`, lancé depuis le worktree. `main` étant la branche par défaut, un `Closes #` dans la PR ferme l'issue.

Commits et PR suivent les Conventional Commits, sujet en anglais, sans aucune mention d'IA, PR comprise.

## État au 2026-10-26

| Tâche | Issue | PR | Merge dans `harness-v2`, branche de la refonte |
|---|---|---|---|
| 1. Worktree, tag, sauvegarde des liens | #15 | — | `7ab852b` |
| 2. `tools/install.py` et manifeste Claude | #16 | #17 | `69b4751` |
| 3. Banc isolé Claude | #18 | #19 | `8f1ee6a` |
| 4. Rangement : `wrappers/claude/hooks/`, `tools/` | #21 | #22 | `1b1265b` |
| 5. Cœur des gardes dans `hooks/`, adaptateur Claude | #23 | #24 | `73cab94` |
| 6. Plugin OpenCode `harness-guards`, banc OpenCode | #25 | #26 | `170bec3` |
| 7. Skills du repo servis à OpenCode par liens | #27 | #28 | `b693130` |
| 8. Rules du repo servies à OpenCode par `instructions` | #29 | #30 | `dd91ab4` |
| 9. Lectures interdites, `policy/deny.yaml` pour les deux agents | #31 | #32 | `078d579` |
| 10. Serveurs MCP, `mcp/servers.yaml` pour les deux agents | #33 | #34 | `1f50da0` |
| 11. Drivers `tools/drivers/`, évals et mesure des réponses sous OpenCode | #35 | #36 | `222c678` |
| 12. AIDD sous OpenCode sur `yt-transcriber`, modèles du banc sur l'abonnement Go | #37 | #38 | `e567333` |
| 13. Bascule, `tools/bascule.sh` et son retour | #39 | #40 | `716a83a` |

Les 13 tâches sont faites. `harness-v2` est entré dans `main` par #41 (`7c466a8`), et le vivant a basculé le 2026-10-26. `install.py --check` rend 0 écart sur `~/.claude` (68 liens et `settings.json`) et sur `~/.config/opencode` (28 liens et `opencode.json`), sans aucun lien pendant. Une session neuve de chaque agent charge le harnais : côté Claude, 17 rules du repo, les hooks du harnais résolus et codegraph connecté ; côté OpenCode, 12 skills auto, aucun des 14 manuels et 19 règles.

Le retour arrière se lance par `bash ~/Developpement/Workspaces/agent-config-v2/tools/bascule.sh --retour --etat ~/.local/state/agent-config/bascule/20261026-165427`.

**Prochaine étape** : les fils ouverts, plus bas, au choix.

## La référence de parité

Après chaque tâche, ces commandes doivent rendre ce qui suit :

```bash
cd ~/Developpement/Workspaces/agent-config-v2
bash tools/test-all.sh          # 19 batteries, 0 en échec
bash tools/bench.sh claude      # 17 rules d'origine worktree et le CLAUDE.md du banc, 26 skills du repo, 6 plugins, 8 hooks résolus dont 1 machine, codegraph connected, aucune fuite, Read du leurre refusé en bypass
bash tools/bench.sh opencode    # sur opencode-go/deepseek-v4.1-flash, quota imprimé avant la session ; commit signé refusé en permission.rejected, ls passe, 12 skills auto exposés, 0 des 14 manuels, 19 règles chargées, read du leurre refusé, codegraph_codegraph_explore appelé, ~/.config/opencode inchangé
```

- Le banc rend 100 skills au total : 26 du repo, 17 intégrés, 47 des plugins AIDD et 10 `anthropic-skills:*` du compte. À la tâche 3, il en rendait 43, parce que `init` ne listait pas encore les skills préfixés. Relancé sur `8f1ee6a`, il rend aussi 100, donc l'écart ne vient pas du repo.
- Depuis la tâche 10, le banc Claude charge 18 fichiers d'instructions. Le 18e est `~/.claude-bench/CLAUDE.md`, la section que `codegraph install` y écrit.
- Les 4 rules qui portent un `paths:` (`back-spring`, `front-react`, `backend-api`, `frontend-design`) ne se chargent pas dans une session vide. C'est attendu.
- Depuis la bascule, le vivant se contrôle directement : `python3 tools/install.py --agent claude --target ~/.claude` et `--agent opencode --target ~/.config/opencode`, lancés depuis `agent-config`, rendent 0 écart.

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
- Tâche 10 : pour Claude, `install.py` ne remplit pas lui-même le carnet `.claude.json`. `--fix` lance `codegraph install -t claude -l global -y` avec `CLAUDE_CONFIG_DIR` sur la cible. Mesuré le 2026-10-26 dans un HOME jetable : l'installateur 1.6.2 respecte cette variable, et pose aussi l'allow, le hook et la section de `CLAUDE.md`. Recopier ces trois effets les ferait diverger.
- Tâche 10 : pour OpenCode, `install.py` écrit lui-même `mcp.servers` dans `opencode.json`, sous la forme de `codegraph install --print-config opencode`. L'installateur ignore `OPENCODE_CONFIG_DIR` et écrirait dans le vivant, mesuré le même jour.
- Tâche 10 : sous OpenCode, l'outil s'appelle `codegraph_codegraph_explore`. La base ne garde pas les outils exposés, donc le banc prouve le branchement par un appel, abouti ou en erreur.
- Tâche 10, constaté le 2026-10-26 : un modèle du banc OpenCode qui ne trouvait pas l'outil a fouillé la machine pendant 105 appels. Un `env` a envoyé à son fournisseur `CLAUDE_CODE_MESSAGING_TOKEN`, un jeton de la session Claude qui lançait le banc. Il a aussi lu le schéma d'`opencode.db`, pas la table `credential`. Depuis, le banc retire les variables `CLAUDE*` et `ANTHROPIC*`, et la consigne dit de s'arrêter si l'outil manque.
- Tâche 11 : sous OpenCode, l'équivalent de `--tools Skill` est un agent `skill-only` dont la `permission` refuse tout sauf `skill`, lancé par `--agent`. Mesuré le 2026-10-26 : la session ouvre `security-reviewer`, ne lance ni `shell` ni `read`, et dit n'avoir que `skill`. Le driver le pose dans son dossier de config jetable, jamais dans `wrappers/opencode/opencode.json`, qui va au vivant.
- Tâche 11 : le driver OpenCode lit les skills ouverts, le texte et le coût sur la sortie `--format json`. Seuls les skills exposés viennent d'`opencode.db`, par les lecteurs de `tools/bench/opencode-report.py`.
- Tâche 11 : pas de mode artefact sous OpenCode. Il demanderait des outils ouverts et `--auto`, donc un shell libre pour un modèle gratuit.
- Tâche 11, mesuré le 2026-10-26 : `opencode/deepseek-v4.1-flash-free` répond `provider.quota`, `opencode/minimax-m3.1-flash-free` répond `provider.no-route`. Seul `openrouter/recursive/flint-v1.0:free` répond. Il appelle `skill` en boucle (40 appels sur le cas négatif de `security-reviewer`), donc son verdict FAIL dit surtout la faiblesse du modèle.
- Tâche 11 : taux de points-virgules natifs, sans la règle, dans `rules/references/ref-ponctuation.md`. DeepSeek 1,76 et 2,49, MiniMax 0,77, pour une cible de 1,09.
- Tâche 11, constaté le 2026-10-26 : `~/.config/opencode/cli.json` est apparu pendant une passe d'évals. C'est la TUI lancée à la main à 11:21:51 qui l'a migré depuis `tui.json` (log `migrated cli config`), pas le driver.
- Tâche 6 : `install.py --check` sur `~/.claude` rend les mêmes 14 écarts avant et après la tâche, donc la branche `settings` de Claude n'a pas bougé.
- Tâche 5 : le contrat du cœur est dans `hooks/check.py`. `exit 1` veut dire « entrée illisible », et chaque adaptateur décide quoi en faire. `skills_used: null` veut dire « inconnu », et le garde AIDD laisse alors passer.
- Tâche 5 : la parité de l'adaptateur Claude a été mesurée sur 963 commandes réelles tirées des transcripts, rejouées contre l'ancien et le nouveau garde. Résultat : 0 écart, et 35 refus identiques des deux côtés. Pour rejouer, il faut reprendre les anciens gardes par `git show 5af25cd:wrappers/claude/hooks/<garde>`.
- `git commit -m "fix: Claude"` **passe**, avant comme après la tâche 5 : nommer Claude n'est pas signer. Le critère de la tâche 6 dans le cadrage et la QA de l'issue #23 se testent donc avec `Co-Authored-By: Claude`.

- Tâche 12 : tout modèle lancé sous OpenCode passe par l'abonnement Go (10 $/mois), à la demande de l'utilisateur. La chaîne est `opencode-go/deepseek-v4.1-flash`, puis `opencode-go/minimax-m3.1-flash`, dans `tools/bench/opencode-go.py`. Un modèle hors `opencode-go/` est refusé avant toute session, même s'il répond. Mesuré le 2026-10-26 : les gratuits ne répondent pas (réglage Privacy, « Model unavailable »), et la variante Zen n'a pas de crédit.
- Tâche 12 : aucune API ne donne le quota Go restant (`opencode.ai/docs/go` renvoie à la console). Le contrôle additionne donc `session_v2.cost` d'`opencode.db` sur 5 h, 7 j et 30 j, contre 20 %, 50 % et 100 % du plafond mensuel (80 $ pour DeepSeek, 20 $ pour MiniMax), et refuse dès 80 %. `opencode stats` ne compte que par jours, donc il ne couvre pas les 5 h. Le contrôle ne voit pas une autre machine. Sur une erreur de limite Go, le banc et le driver rejouent une fois avec le modèle suivant. La forme exacte de cette erreur dans le flux n'est pas mesurée, et la fenêtre de 30 jours glissante est supposée.
- Tâche 12 : l'action TUI `usage.show` existe dans le schéma `opencode.ai/v2/cli.json`, mais Alt+U n'a rien affiché le 2026-10-26, et aucune des 119 routes de l'API locale ne sert l'usage.
- Tâche 12, Q1 : AIDD s'installe par `npx @ai-driven-dev/cli@5.5.0 setup --source remote --ai opencode --plugins all --yes`. Mesuré le 2026-10-26 sur `yt-transcriber` : les 467 fichiers de `.opencode/` et `opencode.json` sont identiques à l'archive `aidd-framework-opencode-flat-5.12.0.zip`. La CLI ajoute `.aidd/manifest.json` et `.aidd/cache/` au `.gitignore`. On la préfère à l'archive pour `doctor` et `update`.
- Tâche 12, Q2 : les 51 skills AIDD sont exposés sous leur nom aplati, sans espace de noms (`04-issue-create`, `01-sdlc`) et sans collision. La session du projet en voit 65 : 12 du repo, 51 d'AIDD, 2 d'OpenCode.
- Tâche 12, Q3 : le `opencode.json` du projet s'ajoute à celui du banc sans le remplacer. Les 19 règles, la policy de lecture, le refus du commit signé et codegraph restent verts dans le clone. Son `instructions` vise `.opencode/rules/**/*.md`, que l'archive 5.12.0 ne pose pas, donc AIDD n'ajoute aucune règle.
- Tâche 12 : `tools/bench/opencode.sh --project DIR` joue la session dans un `git clone --local` de DIR, hors du home. Seul ce qui est commité passe. La branche locale `chore/aidd-opencode` de `yt-transcriber` (`994b7b3`) a été supprimée après le merge, avec les restes `.aidd/` et `.opencode/` de l'installation.
- Tâche 13 : la bascule passe par `tools/bascule.sh`, lancé depuis le worktree, parce qu'avant l'avance `main` ne contient pas encore le script. Il refuse et n'écrit rien dans trois cas : `main` est sale, `origin/main` ne contient pas son commit, ou un PAS UN LIEN ou un INTRUS attend dans une cible. Une fois ces contrôles passés, il sauvegarde, fait avancer `main`, lance `install.py --fix` sur les deux agents et pose `OPENCODE_DISABLE_CLAUDE_CODE_SKILLS=1` dans `~/.zshrc`, le tout dans le même processus.
- Tâche 13 : le retour ne passe pas par l'ancien `sync-rules.sh`. Il repose les liens de la sauvegarde, restaure les fichiers, et remet `main` sur le commit d'avant par `git switch -C`, qui réécrit la branche locale seulement. Le plan prévoyait un `--detach`, mais un checkout détaché rendait une seconde bascule impossible sans `git switch main`, qui ferait lui-même pendre les liens.
- Tâche 13 : on ne fait aucune archive de `~/.config/opencode`, parce qu'une archive lirait `service.json`. Seuls les fichiers que le harnais écrit sont copiés.
- Tâche 13 : `tools/tests/test-bascule.sh` refait une cible Claude à partir des 68 liens de `audits/2026-10-22-liens-pre-v2.txt`, dans un clone jetable dont `origin` est un dépôt nu local. Mesuré le 2026-10-26 : la bascule, le retour et une seconde bascule rendent 0 écart. Après le retour, les liens et les empreintes sont identiques à l'avant.
- Tâche 13, constaté le 2026-10-26 : deux minutes après la bascule, Claude Code a réécrit `~/.claude/settings.json` après la confirmation du mode bypass, et la clé `model` y a disparu. `install.py --fix` l'a remise. Un `--check` après chaque relance de Claude Code attrape ce cas.
- Tâche 13 : la machine s'aligne sur le wrapper. Opus en `medium` est le défaut, par `effortLevel` dans `wrappers/claude/settings.json`. La clé `modelSettings`, que Claude Code avait écrite sur la machine (Opus en `medium`, Sonnet en `high`), est retirée, parce qu'elle passait devant le wrapper sans que le repo la voie. Sonnet ne sert que dans un projet qui le déclare dans son `.claude/settings.json`, comme le vault.
- Tâche 13 : contre le vivant, `tools/bench-report.py` compte comme « hook introuvable » les 14 hooks de l'application Orca, écrits en shell en ligne dans `~/.claude/settings.json`. Ils ne viennent pas du harnais. Le rapport est fait pour un banc, où ces hooks n'existent pas.

## Fils ouverts, hors du chemin critique

- Évals sous OpenCode : elles tournent désormais sur `opencode-go/deepseek-v4.1-flash`. Aucun verdict n'a encore été rejoué sur ce modèle.
- Banc OpenCode dans un dépôt vide, le 2026-10-26 : DeepSeek dit deux fois que `codegraph_explore` est absent de son catalogue, alors que le log porte « mcp connected server=codegraph tools=1 ». Dans le clone de `yt-transcriber`, il l'a appelé. La cause n'est pas cherchée.
- `aidd setup` laisse `.aidd/plugin-cache/` non suivi dans le projet : son `.gitignore` ne couvre que `.aidd/cache/`.
- Garder ou non `ponctuation.md` pour DeepSeek et MiniMax, à trancher sur les taux de la tâche 11.

- #20 : ranger `skills/_shared/` en `scripts/` et `references/`, avec un README. À faire entre deux tâches.
- Les plugins AIDD du banc sont plus récents que ceux du vivant, par exemple `aidd-vcs` 2.5.0 contre 2.4.0. C'est noté, pas corrigé.
- Le garde de mention d'IA ne couvre ni `gh api …/pulls`, ni `gh pr comment`, ni le format du titre de PR.
- Les branches mergées (`refactor/repo-layout`, `feat/claude-bench`, etc.) existent encore sur le dépôt distant.
- `skills_used` sous OpenCode : l'outil `skill` laisse `input.id` dans `opencode.db`, donc le plugin pourrait suivre les skills lancés. Tant que ce n'est pas fait, le garde AIDD ne refuse jamais sous OpenCode.
- Des paragraphes propres à Claude vivent dans des règles neutres, que lit aussi OpenCode : la section « Déplacer un projet existant » de `workspaces.md` (liens de `~/.claude`) et le hook `UserPromptSubmit` de `codegraph.md`. Le cadrage les renvoie à l'adaptateur.
- `rules/references/` n'est installé ni pour Claude (le manifeste ne lie que `rules/*.md`) ni pour OpenCode. Les règles y renvoient par chemin relatif.
- Lecture d'un secret par le shell sous OpenCode : `cat` passe, mesuré à la tâche 9. Le fermer demande un garde du cœur sur l'action `shell`, qui reconnaisse une lecture de fin interdite.
- La fusion remplace une liste entière : un `policies` posé à la main dans le vivant `opencode.json` serait écrasé par celui de `deny.yaml`. Le vivant n'en a pas aujourd'hui.
- La section `AGENTS.md` que `codegraph install` écrit pour OpenCode n'est pas posée. `rules/codegraph.md` est déjà chargé par `instructions`, et l'installateur écrirait dans le vivant.
- Un modèle gratuit du banc OpenCode lit tout ce que le banc lui laisse voir, et l'envoie à son fournisseur. Les variables Claude sont retirées, mais le `--auto` laisse encore le shell libre sur la machine.
