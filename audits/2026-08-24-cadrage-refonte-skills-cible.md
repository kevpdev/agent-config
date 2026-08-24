# Refonte des skills perso — cadrage de la cible

Note de décision, figée le 2026-08-24. Elle fixe la cible de la refonte des skills de `skills/`, pour que `skill-craft` et `audit-harnais` s'adaptent dessus sans rouvrir un arbitrage. Elle décide, elle n'implémente pas. Le plan de refonte skill par skill sera produit par l'audit qui suivra. Le suivi des chantiers reste dans la note vault `0_INBOX/2026-08-10-cadrage-refonte-skills.md`, qui pointe ici.

Sources mesurées le 2026-08-24 : les 29 skills de `skills/`, la convention `skills/skill-craft/references/skill-authoring-fr.md`, la grille `audits/grille-harnais.md`, et le référentiel AIDD en lecture seule (versions du cache : context 2.6.2, dev 2.4.1, orchestrator 2.2.1, pm 2.4.2, refine 3.0.0, vcs 2.3.1). Le contrat d'écriture AIDD fait 19 règles : `aidd-context/2.6.2/skills/04-skill-generate/references/skill-authoring.md`, plus les gabarits `skill-template.md` et `action-template.md` du même skill.

## Arbitrages fondateurs

Posés par l'humain, ils ne se rediscutent pas dans les sessions d'adaptation.

- Le référentiel AIDD est en lecture seule. On s'en inspire, on n'y touche jamais.
- Le multi-CLI (codex, opencode…) est YAGNI. Rien n'est conçu pour lui.
- L'évaluateur lourd (`run-skill-evals.py`, 695 lignes) est remplacé par un système minimal : un lint mécanique et une éval comportementale. Les dossiers `evals/` se révisent contre le nouveau format au lieu de se jeter, la suppression ayant été proposée pour leur défaut, pas pour leur principe.
- Le système reste **agnostique** : le format des cas ne cite ni outil ni agent. On s'inspire de l'outillage d'Anthropic, on n'en dépend pas.
- On ne vérifie tout seul que ce qui se vérifie **correctement**. Aucun motif fragile.
- Les subagents s'emploient plus souvent quand c'est pertinent, agnostiques du modèle, en commençant simple. Le ratio performance sur coût prime.
- Le pattern Frame–Deliver–Checker de l'orchestrateur AIDD se généralise aux skills où il a du sens, borné à 3 passes.
- Les skills se préfixent par domaine.
- Les agents des skills découpés vivent dans le wrapper Claude.
- Cinq skills s'archivent avant la refonte (section suivante).

## 1. Archivage préalable

Cinq skills sortent du périmètre par suppression de leur dossier dans `skills/`, git les garde.

| Skill | Raison |
| --- | --- |
| `aidd-pilot` | l'orchestrateur AIDD (`aidd-orchestrator:01-sdlc`) le remplace, et son mode interactif est prévu upstream |
| `backend-architect` | peu utilisé depuis AIDD, équivalent natif dans les agents |
| `code-reviewer` | idem, `aidd-dev:05-review` et la review native couvrent le besoin |
| `docs-check` | idem, la recherche de doc est native |
| `frontend-expert` | idem |

L'archivage est le premier geste de la session d'adaptation, avant tout travail de refonte. Le périmètre tombe à **24 skills**. Les clauses NE PAS qui nomment un skill archivé se purgent au fil de la refonte.

## 2. Structure cible d'un skill (Q1)

### L'arbre, à la carte

Chaque dossier est optionnel, comme chez AIDD (`skill-tree.md` : « Omit `actions/`, `references/`, or `assets/` when empty »).

| Élément | Statut |
| --- | --- |
| `SKILL.md` | obligatoire. Seul sous ~150 lignes, routeur au-delà ou dès qu'il y a plusieurs actions |
| `actions/NN-<slug>.md` | si plusieurs actions distinctes |
| `references/*.md` | si de la connaissance se charge à la demande |
| `assets/*.md` | si un gabarit se copie dans un artefact. `skill-craft` y porte les deux gabarits de skill |
| `evals/` | si le skill porte des cas d'éval, au format de la section 4 |
| `scripts/` | non retenu. L'exécutable partagé vit dans `skills/_shared/`, l'outillage dans `wrappers/claude/scripts/` |

**POURQUOI pas de `scripts/` par skill** : le cache AIDD n'en porte qu'un sur 46 skills, hors arbre canonique, et le nôtre concentre déjà l'exécutable en deux homes qui suffisent.

### Deux gabarits font foi, la prose ne décrit que les deltas

L'anatomie ne se raconte pas dans une convention, elle se copie depuis un fichier. `skills/skill-craft/assets/` porte `skill-template.md` et `action-template.md`, francisés depuis les deux gabarits AIDD de `04-skill-generate/assets/`. Ils sont la source unique de la liste de sections, **et le lint la dérive d'eux** au lieu de la coder en dur.

**POURQUOI le gabarit plutôt que la prose** : une liste décrite en prose et une liste vérifiée par un script divergent au premier edit de l'une des deux. Une seule liste, lisible par l'humain comme par le script, ne peut pas dériver.

**Les en-têtes de structure sont ceux d'AIDD, en anglais, au mot près** : `## Actions`, `## Transversal rules`, `## References`, `## Assets`, `## Input`, `## Output`, `## Process`, `## Test`. Tout le reste (prose, labels d'étapes, cellules de table) est en français. La convention actuelle gardait déjà quatre en-têtes en anglais comme « repères de structure de la famille AIDD » ; l'alignement étend la règle aux quatre autres. **POURQUOI** : un lint sur une liste bilingue doit traiter les deux orthographes de chaque section, et c'est exactement le genre de tolérance qui laisse passer une section inventée.

### SKILL.md routeur, aligné sur la génération 2 d'AIDD

Le référentiel a deux générations rédactionnelles et sa spec décrit la seconde. On adopte la seconde.

- Frontmatter : `name`, `description` (R5 : quoi + quand, 3e personne, sous 1 536 caractères), `argument-hint` (ce que l'utilisateur apporte), `disable-model-invocation: true` si effet de bord (R13). Aucun autre champ.
- Titre, une phrase de portée.
- Le flux en **mermaid `TD`**, branches et back-edges compris. Une branche dite en prose est une branche manquante du flux (R7 AIDD). `rules/mermaid.md` écrase le défaut `LR` d'AIDD.
- `## Actions` : table à 2 colonnes, slug nu et impératif court, suivie de « Dérouler le flux. Ne lire que la prochaine action. »
- `## Transversal rules` : ce qu'aucune action ne porte seule. Une règle dite là ne se redit nulle part (R9 AIDD).
- `## References` et `## Assets` : chemin en backticks plus rôle en une ligne, par fichier.
- `## Test` : première ligne le mode de vérification (section 3), puis la table `| Cas | Preuve |` ou le geste manuel.

Le routeur ne porte rien qu'une action ou une référence pourrait porter (R10 AIDD). **POURQUOI** : le routeur se charge à chaque invocation, une action seulement à son tour.

**Un seul moule, y compris pour les mono-fichiers.** Un skill de conseil sans actions garde les mêmes en-têtes : sa phrase de portée absorbe le `## Rôle`, sa méthode vit sous `## Process`, ses interdits sous `## Transversal rules`. Le gabarit persona (`## Rôle`, `## Ne pas s'activer pour`, `## Règles strictes`) disparaît. **POURQUOI** : deux moules obligent le checker à deviner lequel s'applique avant de juger, et `## Ne pas s'activer pour` recopie la clause NE PAS de la description.

### Anatomie d'une action

Dans cet ordre, en-têtes d'anatomie en anglais et tout le reste en français (R10 de la convention perso).

Quatre sections, celles du gabarit `action-template.md`, ni plus ni moins.

| Section | Statut | Contenu |
| --- | --- | --- |
| `# NN - Titre` + une phrase | obligatoire | ce que fait l'action |
| `## Input` | optionnel | ce que l'action consomme, omis sinon |
| `## Output` | obligatoire | une ligne nommant ce qui est produit, avec son chemin d'écriture si fichier |
| `## Process` | obligatoire | étapes numérotées `**Label.** phrase impérative`, branches, boucles et gardes en sous-puces jamais numérotées |
| `## Test` | obligatoire | table `\| Cas \| Preuve \|`, chaque ligne observable par exécution réelle |

**Aucune section hors de cette liste.** Une section sans équivalent AIDD n'apporte pas de valeur : son contenu a déjà un home, et l'inventer ailleurs le rend invisible à qui lit le gabarit.

| Section perso supprimée | Où va son contenu |
| --- | --- |
| `## Contrôle de sortie` (23 fichiers) | un critère qui décide en cours de route devient une étape `**Garde.**` du `## Process` ; un critère qui constate devient une ligne du `## Test` |
| `## Ne pas s'activer pour` (9) | rien : c'est la clause NE PAS de la `description`, recopiée (doublon R6) |
| `## Rôle` (11) | la phrase de portée sous le titre |
| `## Règles strictes` (5) | `## Transversal rules` du routeur |
| `## Si ça casse` (3) | sous-puces de l'étape concernée du `## Process` |
| `## Garde-fou — vault requis` (7) | première étape du `## Process`, et une seule fois : le bloc est copié à l'identique dans les 7 skills `vault-*` |
| `## Contexte`, `## Méthode`, `## Sortie`, `## Verdict`, `## Délégation`, `## Flux`, `## Hors périmètre` | `## Input`, `## Output`, `## Process`, ou le flux mermaid du routeur |

La suppression de `## Contrôle de sortie` clôt au passage une contradiction : R8 et `01-scaffold` l'imposaient, la section anatomie de `skill-authoring-fr.md` l'omettait. **POURQUOI elle ne manque pas** : le `## Test` d'AIDD porte déjà l'observable en cours d'exécution (« le fichier est relu | aucun placeholder ne survit »), et le `## Process` porte déjà les gardes (« **Gate.** Quand tout candidat revient ❌, … ne pas passer à l'action 04 »). La séparation que R8 défendait tenait au fait que `## Test` ne portait qu'un pointeur vers `evals/`. Avec un `## Test` en table d'observables, elle n'a plus d'objet.

Une citation est un lien markdown relatif dans la phrase qui l'utilise, jamais un bloc à part ni un include `@` (R18 AIDD). Un bloc fencé est du contenu que l'action émet, pas de la structure (R12 AIDD).

### Référence et asset

- Une référence est plate et autonome. Un fait par ligne, en table ou en liste, la prose pour le reste (R15 AIDD). Elle nomme une sœur en backticks et ne la lie jamais.
- Un asset dit comment il se remplit et ce qui s'efface. Rien du scaffold ne survit dans l'artefact produit (R16 AIDD). Placeholders `<...>`, un seul format.

## 3. Ce qui se teste tout seul, et ce qui ne se teste pas (Q2)

**La coupure n'est pas par skill, elle est par affirmation.** Un même skill se vérifie tout seul sur ce qui se contrôle depuis sa sortie, et se relit à la main sur le reste. Chercher une liste de skills éligibles était la mauvaise question.

| Ce qu'on vérifie tout seul | Pourquoi c'est robuste |
| --- | --- |
| le **déclenchement** : le skill part quand il doit, et se tait quand il ne doit pas | verdict binaire, l'outil Skill a été appelé ou non. Marche sur les 24 skills, même ceux qui ne rendent que de la prose |
| l'**artefact** : le fichier produit existe, parse, et porte les sections de son gabarit | verdict par script, sans interprétation |

| Ce qu'on refuse d'asserter | Pourquoi |
| --- | --- |
| l'ordre des outils appelés | trop fragile, ça punit les chemins valides que personne n'avait prévus. Anthropic le déconseille nommément dans sa méthodo d'éval d'agents |
| une regexp sur de la prose | casse à la première variation valide de formulation |
| le style, le ton, « ça sonne juste » | ne se décompose pas en pass/fail. C'est de la relecture humaine, et les sources d'Anthropic le rangent là |

**Le problème d'éligibilité disparaît presque.** Le test de déclenchement se joue **outils coupés** : le skill se déclenche mais ne peut rien exécuter. `jira` et `vault-save` se testent donc sans aucun risque. Ne restent manuels que les affirmations refusées ci-dessus, et les artefacts écrits hors du dossier de travail.

**POURQUOI ce critère et pas « sortie réversible et vérifiable mécaniquement »** : la réversibilité est le travail du harnais, pas une propriété du skill — l'industrie simule le système externe au lieu de renoncer à tester. Et le vérifiable mécaniquement est trop strict : le format d'éval officiel d'Anthropic fait juger des affirmations en langage naturel. Le vrai critère documenté est qu'une affirmation se contrôle depuis la sortie seule.

## 4. Deux outils, pas trois étages (Q3)

### Le lint — mécanique, gratuit, à chaque fois

Il lit le fichier, n'exécute rien, tourne sur les 24 skills en une seconde. Six vérifications, toutes sans interprétation :

- le frontmatter parse (YAML strict) et porte `name`, `description`, `argument-hint`
- `name` est égal au nom du dossier
- la `description` tient sous 1 536 caractères
- les `##` du fichier correspondent à ceux du gabarit : aucune manquante, aucune en trop, dans l'ordre
- aucun placeholder `<...>` oublié
- aucun lien relatif mort

**Ce qu'il ne vérifie surtout pas** : tout ce qui demande de comprendre ce que le skill *fait*. Un grep sur « push » ou « commit » attrape `security-reviewer`, qui cite ces mots pour décrire du code qu'il relit sans rien exécuter. `skill-craft` le dit déjà : « ne pas compter les mots-clés, lire ce que le skill fait ».

### L'éval — exécution, payante, à la demande

Une session fraîche par cas, en `claude -p`. Elle ne rend que les deux verdicts de la section 3, déclenchement et artefact. Chaque skill porte un cas positif, et un cas négatif par frère cité en clause NE PAS.

**Le fichier d'évals ne contient que des données** : la requête, le déclenchement attendu, l'artefact attendu. Aucun nom d'outil, aucun nom d'agent. L'exécuteur est forcément spécifique à Claude et vit dans `wrappers/`. **POURQUOI** : tous les formats d'éval existants sont couplés à leur outil, et on veut pouvoir changer d'exécuteur sans réécrire les cas.

**Emprunt à la méthode officielle d'Anthropic, gratuit parce que c'est du tri et pas de l'outillage** : jouer chaque cas deux fois, avec le skill et sans lui. Une affirmation qui passe dans les deux cas ne mesure pas le skill, elle se supprime.

**Ce qui remplace `run-skill-evals.py`** : le même geste de session fraîche, sans juge LLM pour le comportement. Le corpus existant se révise contre ce format au lieu de se jeter, ses deux défauts connus corrigés — le champ `setup` non documenté qui écrit dans le repo réel disparaît, et les scénarios négatifs manquants s'ajoutent.

### Ce qui reste à un humain ou à une relecture

La chasse aux doublons (un même fait à deux endroits) ne se mécanise pas et n'a pas à tourner à chaque passe. Elle se fait au moment de la refonte, par relecture. **POURQUOI ce n'est pas un troisième étage** : un étage permanent qu'on ne joue jamais coûte de la doc et ne rend aucun verdict.

### Ce sur quoi on ne bâtit pas

**Aucun outil natif de Claude Code n'entre dans le lint ni dans l'éval.** Ni `claude plugin eval`, ni `/skill-doctor`, ni `claude plugin validate`. Ce sont des sources d'inspiration, jamais des dépendances.

**POURQUOI ce n'est pas leur maturité qui les écarte** : leur statut le jour de la décision n'est pas le critère, sinon la question se rouvrirait à chaque release. Le critère est l'agnosticisme posé en arbitrage fondateur. Un outil natif ne se justifierait que pour les skills du wrapper Claude, et cette exception est YAGNI tant qu'aucun besoin ne la réclame.

État constaté le 2026-08-24, pour mémoire et non comme condition : `claude plugin eval` et `/skill-doctor` sont en early access, absents de la doc publique et non activés ici. `claude plugin validate` est public et stable.

### Bornes et interdits

- **3 passes checker-corrections maximum.** Au-delà, le défaut est dans le diagnostic ou la frame, pas dans l'exécution. Même borne que `max_iterations` (défaut 3) d'`aidd-orchestrator:00-async-dev`, seule borne numérique du référentiel.
- **Anti-auto-notation conservé** : le contexte qui vient d'écrire un skill ne joue jamais son éval. Il rend la commande et déclare la passe non jouée.
- Aucun scénario de checker n'écrit dans le repo réel. Le champ `setup` de l'ancien schéma disparaît avec lui.

## 5. Doctrine subagents (Q4)

### Quand découper

- **Règle de locus**, reprise d'`aidd-pilot` avant archivage : « borné et sans interaction humaine → subagent ; persistant ou interactif → parent ». Un serveur meurt avec le subagent, un dialogue de confirmation n'y est pas possible.
- **Saturation du parent** : une recherche dont les dumps noieraient le contexte se délègue (pattern `fact-checker`).
- **Parallélisable** : des tâches indépendantes se lancent en un seul message, plusieurs appels.

### Comment découper

- **Commencer simple** : agent générique avec brief inline dans le `## Process` (pattern AIDD `01-bootstrap`). Un agent nommé ne se crée que quand le brief se répète entre skills ou porte un rôle durable.
- **Agents agnostiques** : pas de champ `model`, à l'inverse d'AIDD (executor sur sonnet, checker sur opus). Le ratio performance sur coût se règle à l'usage, pas dans le fichier.
- On garde du référentiel la **liste blanche de skills** en fin d'agent et l'interdiction de récursion (« Never delegate to another agent »).

### Où vivent les agents

Un agent nommé vit en `.md` dans `wrappers/claude/agents/`, déjà symlinké en `~/.claude/agents/` comme `doc-writer.md`. Jamais de dossier `agents/` dans un skill, même logique qu'AIDD dont les agents vivent au niveau plugin. Le skill qui dépend d'un agent le déclare dans son routeur. **POURQUOI le wrapper** : les agents sont propres au CLI Claude, un skill reste théoriquement portable.

### Frame–Deliver–Checker

Le pattern se généralise aux skills qui produisent un artefact vérifiable et bouclent dessus : une zone qui cadre le contrat, une qui produit, un checker indépendant qui juge contre le contrat. Sortie de boucle à 3 passes maximum, comme le checker de la section 4.

## 6. Préfixes par domaine et renommage (Q5)

Cinq domaines. Le préfixe dit le domaine d'usage, pas la nature technique. **Les noms de skill sont en anglais**, préfixe compris, seul le contenu reste français.

| Actuel | Cible | Domaine |
| --- | --- | --- |
| `agentic-architect` | `expert-agentic` | `expert-` : conseil et analyse sans effet de bord |
| `ai-engineering` | `expert-ai-engineering` | `expert-` |
| `brain-expert` | `expert-brain` | `expert-` |
| `database-expert` | `expert-database` | `expert-` |
| `devops-expert` | `expert-devops` | `expert-` |
| `security-reviewer` | `expert-security` | `expert-` |
| `mermaid-craft` | `expert-mermaid` | `expert-` |
| `fact-checker` | `expert-fact-check` | `expert-` |
| `vault-capture-projet` | `vault-capture-project` | `vault-` : le vault Obsidian |
| `vault-recap-raisonnement` | `vault-reasoning-recap` | `vault-` |
| `vault-capture`, `vault-load`, `vault-log-session`, `vault-save`, `vault-slides` | inchangés | `vault-` |
| `aidd-updates` | `aidd-custom-updates` | `aidd-custom-` : skills perso bâtis sur le framework AIDD |
| `memory-bootstrap` | `aidd-custom-memory-bootstrap` | `aidd-custom-` |
| `skill-craft` | `harness-skill-craft` | `harness-` : maintenance du harnais lui-même |
| `audit-harnais` | `harness-audit` | `harness-` |
| `doc-sync` | `harness-doc-sync` | `harness-` |
| `cadre-prompt` | `harness-prompt-framing` | `harness-` |
| `mr-review` | `dev-mr-review` | `dev-` : livraison quotidienne |
| `jira` | `dev-jira` | `dev-` |
| `test-runner` | `dev-test-runner` | `dev-` |

Ligne la plus discutable : `cadre-prompt` en `harness-` plutôt qu'en `expert-`, parce qu'il outille le dialogue avec l'agent.

**POURQUOI `aidd-custom-` et pas `aidd-`** : les skills du plugin s'affichent déjà en `aidd-*` (`aidd-dev:05-review`, `aidd-context:02-project-memory`…), et un skill perso au même préfixe s'y confond dans un listing. Le préfixe se donne au skill dont l'**objet** est le framework (l'amorcer, le mettre à jour). Un skill qui invoque un skill AIDD en sous-étape garde son domaine d'usage : `mr-review` appelle `aidd-dev:05-review` et reste en `dev-`.

Le renommage s'exécute skill par skill au fil de la refonte, jamais en bloc. Implications à traiter à chaque renommage : les clauses NE PAS des descriptions qui nomment des frères, `rules/mermaid.md` qui cite `mermaid-craft`, et les habitudes d'invocation `/nom`.

## 7. Deltas pour skill-craft et audit-harnais (Q6)

Listés pour la session d'adaptation, sans les implémenter ici.

### skill-craft (futur `harness-skill-craft`)

- Réécrire `references/skill-authoring-fr.md` contre cette note : anatomie génération 2 francisée (flux mermaid, table 2 colonnes, `## Test` en table), liste de sections **fermée** aux quatre d'AIDD, R4 justifié ou remesuré, R7 réécrite pour le nouveau format d'éval, R8 supprimée avec `## Contrôle de sortie`.
- Créer `skills/skill-craft/assets/skill-template.md` et `assets/action-template.md`, francisés depuis les gabarits AIDD. Ils deviennent la source de la liste de sections, et `01-scaffold` les copie au lieu de dérouler l'anatomie en prose.
- Ajouter au lint la règle qui tient la fermeture : les `##` du fichier se comparent à ceux du gabarit, tout en-tête en trop est un échec avec le home de remplacement en message. **POURQUOI un lint et pas une consigne** : une section inventée est exactement ce qu'une convention en prose ne rattrape pas, 23 fichiers l'ont prouvé.
- Règles nouvelles : ce qui se vérifie tout seul et ce qui se refuse (section 3), la doctrine subagents (locus, agnosticisme, wrapper), Frame–Deliver–Checker et sa borne, les préfixes de domaine dans le nommage.
- `01-scaffold` écrit les cas d'éval du skill neuf, cas positif et cas négatif par frère cité en clause NE PAS.
- `02-validate` se réduit : ce que le lint fait mécaniquement en sort, il ne lui reste que la relecture des doublons. Ses propres cas d'éval se révisent au nouveau format.

### audit-harnais (futur `harness-audit`) et la grille

- C3 sur les descriptions garde un instrument mécanique, et il se renforce : le déclenchement se teste en verdict binaire, cas positif et cas négatif, sur tous les skills. Le verdict « `ls <skill>/evals/` » se remplace par la présence d'un cas négatif par frère cité en clause NE PAS, ce que la grille nommait déjà comme son angle mort.
- Les passes C et D de l'audit skills prennent cette note comme source de conformité de construction, ce que la grille prévoit déjà en déléguant ce point hors d'elle.

### Outillage

- Un script de lint dans `wrappers/claude/scripts/`, six vérifications, sans LLM.
- Un exécuteur d'évals dans `wrappers/claude/scripts/`, réduit à deux verdicts et sans juge LLM.
- `run-skill-evals.py` et son test réduits au nouveau format, ou réécrits. La section « Jouer les évals des skills » du README se met à jour.

## Hors périmètre

- Identifier skill par skill les candidats subagents : rôle de l'audit.
- Le support multi-CLI : YAGNI.
- Une session d'évaluation complète : assumée légère, ajustée à l'usage.
- Les modifications de skills, de la grille ou de l'outillage : sessions suivantes.

## Captures versées à l'audit

- Le garde-fou vault (`OBSIDIAN_VAULT_PRO`) est copié à l'identique dans les 7 skills `vault-*`.
- Trois skills écrivent des fichiers versionnés sans `disable-model-invocation` : `audit-harnais`, `memory-bootstrap`, `skill-craft`.
- `_shared/` n'a aucun statut dans la convention d'écriture.
- Deux captures ouvertes de la grille concernent les skills : `grille-harnais.md` lignes 349 et 358.
