# Références — `rules/aidd.md`

Les décisions datées, les sources et l'historique des sections de la règle. Jamais chargé automatiquement : la règle garde le déclencheur et un fait par pourquoi. Premiers extraits sortis de la règle le 2026-10-28 (issue #66), puis le 2026-11-02 à la réécriture de l'issue #79. Le contrat CI lui-même vit dans `ref-ci-github.md`.

---

## Chercher un skill — le pourquoi complet (2026-10-07)

**POURQUOI**, mesuré le 2026-10-07 : 9 issues écrites à la main alors qu'un skill existait, vu seulement quand l'utilisateur a posé la question. Aucun nom de skill ici, parce qu'ils dérivent, et `aidd_docs/` est le même signal que `memory-policy.md`. Ce signal a été remplacé par « un dépôt git » le 2026-11-02 (issue #79).

## Chercher un skill — l'état du garde (2026-10-07)

**ÉTAT DU GARDE, décidé le 2026-10-07, dépassé** : « `guard-aidd-skill-lookup.py` rappelle et ne bloque pas, la sortie `# aidd-skip: <raison>` reste libre. On ne le durcit que si on constate que les skills AIDD sont ignorés malgré leur présence. » Historique seulement : le garde refuse déjà (`deny`), voir la section suivante.

## Chercher un skill — le garde refuse, sur tout dépôt git (2026-11-02)

**Décidé le 2026-11-02 (issue #79)** : le garde garde son refus `deny`, et l'étend à tout dépôt git. Il ne vise que les gestes de livraison tapés à la main, dont la création d'issue et de PR. La sortie `# aidd-skip: <raison>` reste libre, donc un refus ne coûte qu'une ligne de justification. La mesure du 2026-10-07, 9 issues écrites à la main alors qu'un skill existait, justifie ce durcissement.

## CI GitHub — l'historique du contrat (2026-10-08)

**POURQUOI**, constaté le 2026-10-08 : la CI de `yt-transcriber` nommait ses jobs d'après ses outils (`check (ruff, pyright, pytest)`), donc le ruleset aurait changé avec chaque stack. Le contrat fixe les noms, et le script le mesure au lieu de laisser la relecture le deviner. Les trois noms fixes ont ensuite laissé place à une porte unique (issue `agent-config#8`) : `check` ne disait pas ce qu'il vérifiait et imposait le même découpage à toutes les stacks. Le README de `swapi` avait aussi été oublié dans la PR #1, relevé par l'utilisateur.

## AIDD partout — le changement de déclencheur (2026-11-02)

Jusqu'au 2026-11-02, la règle et son garde ne visaient que les dépôts portant un `aidd_docs/` (le garde testait `cwd/aidd_docs`). Le vault, `agent-config` et les projets sans mémoire AIDD n'avaient donc aucun workflow. Le cadrage `audits/2026-11-02-cadrage-workflow-coeur.md` (Q2, Q6, tâche 3) tranche qu'AIDD devient le workflow unique, et seul l'endroit où vivent les décisions change. L'issue #79 a porté la réécriture, et le garde teste depuis un `.git` (dossier, ou fichier dans un worktree) dans le `cwd` ou un parent.

**Lire par intention, liste d'origine** : mémoire du projet et génération d'artefacts de contexte, clarifier et remettre en cause, planifier et implémenter et contrôler (revue, tests, audit, débogage), versionner et livrer, produit et backlog, orchestrer de bout en bout. Sortie de la règle pour tenir son poids (issue #73), le « Use when » du catalogue porte la même information.

**Sous OpenCode**, AIDD s'installe par projet (« Flat only »), et `executor` et `checker` sont des agents de plugin Claude. Le rappel d'installation et leur équivalent relèvent de #61, chantiers C et B. La règle les nomme donc sous Claude Code sans rien promettre ailleurs.

## Borne de la boucle de correction — les sources (2026-11-02)

**Constat** : AIDD ne borne pas la boucle executor et checker. Aucun nombre de tours n'apparaît dans `aidd-orchestrator:01-sdlc`, `aidd-dev:02-implement`, `aidd-dev:09-for-sure` ni dans les agents `aidd-dev` (grep sur le cache du 2026-11-02). Le seul arrêt est `blocked` (`02-implement/references/blocked.md`), déclaré par l'executor lui-même.

| Juge du tour | Fourchette | Source |
|---|---|---|
| signal déterministe (tests, CI) | 1 à 3 tours utiles, plafonds publiés jusqu'à 10 | Self-Debugging : plafond 10, « successful debugging processes mostly end within 3 turns » ([arXiv 2304.05128](https://arxiv.org/pdf/2304.05128)) |
| LLM juge | 2 à 4 tours | Self-Refine : « up to a maximum of 4 iterations », gains décroissants ([arXiv 2303.17651](https://arxiv.org/html/2303.17651)) |
| le modèle se relit seul | 0 tour | après 2 tours, « performance drops on all benchmarks » ([arXiv 2310.01798](https://arxiv.org/html/2310.01798v1)) |

La boucle mêle les deux premières lignes, puisque le checker lance les tests mais rend un jugement de LLM. 3 tombe dans les deux fourchettes. La réparation de code est « bottlenecked by the model's ability to provide feedback » ([arXiv 2306.09896](https://arxiv.org/abs/2306.09896)). Anthropic recommande un plafond d'itérations sans chiffre ([Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)). Aucune étude ne compare directement 3 et 5 tours, le chiffre vient du recoupement.

**Pourquoi tous les modes** : en `auto`, la seule borne d'AIDD est « A finding already acted on is never routed twice » (`aidd-orchestrator` 2.4.0, `01-sdlc/references/03-check.md`). En `interactive`, « Only the user bounds this loop » (`references/mode.md`), mais une réparation qui ne touche que l'implémentation ne produit pas d'artefact nouveau et tourne sans pause. Hors SDLC, rien ne borne les boucles des petites et moyennes tâches.

**Exemple fondateur** : la PR #78 (issue #76) a convergé en 3 tours, scores 70, puis 86, puis 95, verdict « prêt ». Rien ne l'aurait arrêtée si elle avait tourné en rond.

**Routage** : le SDLC route d'après le sujet du finding (`03-check.md`). Le plan n'y est pas une cible à part, il vit dans Deliver. En `interactive`, un refus humain se route en plus par artefact refusé : contrat vers Frame, plan vers Deliver, résultat vers Deliver ou vers Frame s'il change ce qu'on construit (`mode.md`).

**Suite prévue** : un hook qui compte les appels au checker par travail et refuse le 4e sans accord humain, à cadrer à part s'il demande un état persistant.

## Où vit la mémoire — la source

Cadrage du 2026-11-02, Q6. Le vault tient ses décisions en fiches datées dans `decisions/` depuis le 2026-04-24. `aidd-dev:01-plan` n'exige pas de mémoire AIDD : il écrit son plan dans `aidd_docs/tasks/` « or in the source's own folder » (`actions/03-conclude.md`).

## Langue — le constat d'origine (2026-10-07)

**POURQUOI**, constaté le 2026-10-07 sur `yt-transcriber` : 14 fichiers de code mêlaient français et anglais, et le choix n'était écrit nulle part. Les titres de plan en anglais viennent du gabarit du skill, et le corps suit la langue de la conversation, sans règle qui les garantisse. Portée élargie de `aidd_docs/` à tout dépôt git le 2026-11-02 (issue #79) : le constat ne dépendait pas de la mémoire AIDD.

## Issue et PR draft — la mesure (2026-10-28)

Mesuré le 2026-10-28 : 2 brouillons d'issue sur 2 validés tels quels.

## Git hors run — la mesure (issue #90, 2026-11-03)

Jusqu'au 2026-11-03, commit, push et PR draft n'étaient permis sans question que pendant un run AIDD. La section s'étend à toute branche de travail après cette mesure.

- **Instrument** : `python3 tools/measure-approvals.py --days 31`, et les exports OpenCode de `tools/session-export.py` passés en argument. Calibré sur la session de #73 : 18 questions trouvées, dont 11 « oui » nus, conforme au comptage à la main.
- **Corpus** : 114 sessions Claude Code, 1 199 questions. Les 33 sessions OpenCode n'en portaient que 4, sans poids.
- **Chiffres** : « push de branche ou PR draft » (`branch push or draft PR`), 35 questions, 54 % de « oui » nus. « Commit » (`commit`), 119 questions, 36 %.
- **Lecture des 16 autres réponses push ou PR draft**, toutes lues : aucune ne refuse le geste. Deux demandent ce que la PR apporte, les autres portent sur le contenu ou sur un autre sujet.
- **Limite** : un « oui » nu ne prouve pas que la question était inutile. Le push sur la branche par défaut et le merge gardent leur question, quel que soit leur taux (50 % et 37 %).
- **Le « never » d'un repo** reste levé pendant un run seulement : la mesure dit qu'une question est redondante, pas qu'une consigne du repo peut être ignorée.
