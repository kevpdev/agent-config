# Chargement des instructions par agent — Claude Code et OpenCode

> Instantané du 2026-11-05, issue #105, étapes 1 et 2. Commit du repo : `e82404a`. Commit de la grille : `50674cc` (`audits/grille-harnais.md`).

## Objectif

Poser côte à côte ce que chaque agent du harnais charge, et à quel moment. Une décision « permanent ou à la demande » s'appuie ensuite sur cette base, et sur un mécanisme que les deux agents possèdent.

Les statuts :

- **doc-vérifié** : lu dans la doc officielle, avec la date de lecture.
- **mesuré** : constaté sur cette machine, avec la commande.
- **supposé** : ni lu ni mesuré.

## Ce que chaque agent charge

| Mécanisme | Claude Code | OpenCode | Statut et source |
|---|---|---|---|
| démarrage, global | `~/.claude/CLAUDE.md`, puis `~/.claude/rules/*.md` sans `paths:` | `~/.config/opencode/AGENTS.md` (repli `~/.claude/CLAUDE.md`), puis le tableau `instructions` | doc-vérifié le 2026-11-04 (`code.claude.com/docs/en/memory.md`, `opencode.ai/docs/rules`) |
| démarrage, global, sur cette machine | `CLAUDE.md` (123 mots) et 20 liens dans `~/.claude/rules/`, 7 913 mots | `instructions` vaut `agent-config/rules/*.md`, 7 346 mots. Aucun `~/.config/opencode/AGENTS.md` | mesuré, `wc -w`, `ls`, `opencode.json` |
| démarrage, projet | `CLAUDE.md` du dossier courant et des parents, sinon `AGENTS.md` | `AGENTS.md` en remontant, sinon `CLAUDE.md` | doc-vérifié le 2026-11-04 |
| sous-dossier | `CLAUDE.md` chargé quand un fichier du sous-dossier est lu | rien | doc-vérifié le 2026-11-04 |
| scope par chemin, `paths:` | chargé quand Read, Write ou Edit touche un fichier correspondant | ignoré, donc la règle se charge partout | doc-vérifié le 2026-11-04. Le README (section sur `paths:`) en tire l'interdit |
| import `@path` | chargé avec le fichier qui l'importe, sans économie | non lu | doc-vérifié le 2026-11-04 |
| skill | description permanente, corps à l'invocation | pareil, par l'outil `skill` | doc-vérifié le 2026-11-04 (`opencode.ai/docs/skills`) |
| référence pointée | lue par un outil, sur consigne | pareil, la doc recommande ce chargement paresseux | doc-vérifié le 2026-11-04 |
| hook qui injecte du contexte | `SessionStart` : `aidd-updates.py` (`additionalContext`). `UserPromptSubmit` : `codegraph prompt-hook` | aucun plugin n'injecte de contexte. `harness-guards` n'intercepte que `tool.execute.before` | mesuré, `~/.claude/settings.json` et `grep` sur `plugins/harness-guards/index.ts` |
| règles propres à un agent | `wrappers/claude/rules/` (`plan-mode`, `memory-policy`), 567 mots | aucune | mesuré, `wc -w` |

Les deux agents partagent trois mécanismes : le permanent, le skill et la référence pointée. Le scope par chemin et par sous-dossier n'existe que sous Claude Code. Un hook qui injecte du contexte n'existe que sous Claude Code sur cette machine.

Un écart reste ouvert. L'audit `2026-10-22-cadrage-harnais-agnostique.md` dit qu'OpenCode lit `disable-model-invocation` (doc v2). La page v1 lue le 2026-11-04 dit le contraire. La version installée est la v2.2.5. Statut : non tranché.

## Une alerte fait-elle lire sa référence ?

`tools/measure-reference-loads.py --days 31` rend zéro lecture hors maintenance, sur 110 sessions. Ce zéro ne mesure pas l'usage. Le script ne compte que l'outil `Read`, et les références passent surtout par `Bash`. Sur 31 jours, les appels d'outil qui nomment une référence se répartissent en 171 `Bash`, 47 `Write`, 27 `Edit` et 8 `Read`.

Recompté en ajoutant les lectures shell (`cat`, `sed -n`, `head`, `grep`…), toujours sans les sessions qui éditent la référence, aucune référence ne dépasse 4 sessions sur 110. `ref-ponctuation.md` arrive en tête avec 4 sessions, puis `ref-autorite-des-conventions.md` avec 3.

La bonne mesure compare au déclencheur, pas au total des sessions. Elle se calcule pour les déclencheurs visibles dans un appel d'outil, avec une règle restée permanente comme témoin :

| Déclencheur | Sessions où il tombe | Ce qui doit être fait | Sessions où c'est fait | Type de règle |
|---|---|---|---|---|
| Edit ou Write sur `.github/workflows/` ou `dependabot.yml` | 4 | lire `ref-ci-github.md`, lancer `check-ci-contract.py` | 2 | alerte et référence |
| Edit ou Write d'un hook, ou de `disable-model-invocation` | 14 | lire `ref-portes.md` | 2 | alerte et référence |
| Edit ou Write d'un bloc ` ```mermaid ` | 16 | invoquer `mermaid-craft` | 3 | alerte et skill |
| `mkdir`, `git clone` ou `git init` sous `Workspaces/` | 14 | invoquer `dev-init-project` | 0 | skill |
| Edit ou Write de code dans un repo qui porte un `.codegraph/` | 24 | appeler `codegraph_explore` | 6 | **règle complète, permanente** |

La règle CodeGraph est chargée en entier dans chaque session, et elle n'est suivie qu'une fois sur quatre. Un format « alerte et référence » ne fait donc pas moins bien qu'une règle complète permanente, sur cet échantillon.

Ces chiffres sont des indices, pas des taux :

- Chaque colonne « déclencheur » est un indice approché. La règle CodeGraph ne vise qu'un changement de signature, pas chaque modification de code. Un `mkdir` ou un `git clone` ne crée pas forcément un projet neuf, et `dev-init-project` est récent.
- La règle Mermaid ne demande le skill que pour un diagramme « non trivial ».
- Les échantillons vont de 4 à 24 sessions.

Le script `measure-reference-loads.py` est aveugle aux lectures shell. C'est une limite qu'il annonce dans son en-tête, mais sous le mode bypass c'est le cas majoritaire.

## Conséquence pour le classement (étape 3)

La mesure ne justifie pas de garder une section en permanent par peur que sa version « alerte et référence » soit moins suivie. Le classement estimé de l'issue n'a pas à être revu à la baisse sur ce motif.

Une section déplacée reste mieux tenue quand un garde déterministe rattrape l'oubli. C'est le cas de la CI, avec `check-ci-contract.py` lancé avant de pousser.

## Suite

Les étapes 3 et 4 de l'issue sont en pause. Le rappel des règles devient une brique du framework de mémoire `kevpdev/hypomnesis`, qui fixera d'abord son protocole (issues #2 et #3 de ce dépôt). Cet audit lui sert de mesure de départ.

## Commandes

- Comptes de mots : `wc -w ~/.claude/CLAUDE.md`, `cat ~/.claude/rules/*.md | wc -w`, `cat rules/*.md | wc -w`, `cat wrappers/claude/rules/*.md | wc -w`.
- Lectures de référence : `python3 tools/measure-reference-loads.py --days 31`, puis un recomptage `Read` et `Bash` et le rapprochement avec chaque déclencheur, par des scripts jetables de la session du 2026-11-05, non versionnés.
