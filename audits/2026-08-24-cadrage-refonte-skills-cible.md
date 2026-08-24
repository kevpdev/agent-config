# Refonte des skills perso — cadrage de la cible

Note de décision, figée le 2026-08-24. Elle fixe la cible de la refonte des skills de `skills/`, pour que `skill-craft` et `audit-harnais` s'adaptent dessus sans rouvrir un arbitrage. Elle décide, elle n'implémente pas. Le plan de refonte skill par skill sera produit par l'audit qui suivra. Le suivi des chantiers reste dans la note vault `0_INBOX/2026-08-10-cadrage-refonte-skills.md`, qui pointe ici.

Sources mesurées le 2026-08-24 : les 29 skills de `skills/`, la convention `skills/skill-craft/references/skill-authoring-fr.md`, la grille `audits/grille-harnais.md`, et le référentiel AIDD en lecture seule (versions du cache : context 2.6.2, dev 2.4.1, orchestrator 2.2.1, pm 2.4.2, refine 3.0.0, vcs 2.3.1). Le contrat d'écriture AIDD fait 19 règles : `aidd-context/2.6.2/skills/04-skill-generate/references/skill-authoring.md`, plus les gabarits `skill-template.md` et `action-template.md` du même skill.

## Arbitrages fondateurs

Posés par l'humain, ils ne se rediscutent pas dans les sessions d'adaptation.

- Le référentiel AIDD est en lecture seule. On s'en inspire, on n'y touche jamais.
- Le multi-CLI (codex, opencode…) est YAGNI. Rien n'est conçu pour lui.
- L'évaluateur lourd (dossiers `evals/`, `run-skill-evals.py`) est remplacé par un checker minimal : lint, conformité au template, review autonome pour les seuls skills éligibles. Les autres se testent à la main.
- Est non éligible à la review autonome tout skill qui porte un arbitrage humain non inférable, un outil externe, une auth requise, ou une écriture sensible (MCP, réseau en écriture).
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
| `evals/` | **supprimé partout** (section 4) |
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

La suppression de `## Contrôle de sortie` clôt au passage une contradiction : R8 et `01-scaffold` l'imposaient, la section anatomie de `skill-authoring-fr.md` l'omettait. **POURQUOI elle ne manque pas** : le `## Test` d'AIDD porte déjà l'observable en cours d'exécution (« le fichier est relu | aucun placeholder ne survit »), et le `## Process` porte déjà les gardes (« **Gate.** Quand tout candidat revient ❌, … ne pas passer à l'action 04 »). La séparation que R8 défendait tenait à l'existence des `evals/` ; sans eux, elle n'a plus d'objet.

Une citation est un lien markdown relatif dans la phrase qui l'utilise, jamais un bloc à part ni un include `@` (R18 AIDD). Un bloc fencé est du contenu que l'action émet, pas de la structure (R12 AIDD).

### Référence et asset

- Une référence est plate et autonome. Un fait par ligne, en table ou en liste, la prose pour le reste (R15 AIDD). Elle nomme une sœur en backticks et ne la lie jamais.
- Un asset dit comment il se remplit et ce qui s'efface. Rien du scaffold ne survit dans l'artefact produit (R16 AIDD). Placeholders `<...>`, un seul format.

## 3. Éligibilité à la review autonome (Q2)

Les quatre critères d'exclusion, opérationnalisés depuis l'inventaire du 2026-08-24 :

| Critère | Ce qui disqualifie | Ce qui ne disqualifie pas |
| --- | --- | --- |
| arbitrage humain non inférable | une gate bloquante par design (`memory-bootstrap` : « attendre la réponse ») | une question bornée dont la réponse se pré-fournit dans le prompt de test (`cadre-prompt` : une question maximum) |
| outil externe | un outil à installer ou configurer (`glab`, Slidev) | l'outillage natif de l'agent, recherche web comprise |
| auth requise | token, login, MCP authentifié (`jira`) | — |
| écriture sensible | MCP en écriture, réseau en écriture, push, commit | écrire un fichier local que la session peut relire |

**Le flag est la première ligne du `## Test` du SKILL.md** : « Review autonome » ou « Test manuel : \<geste\> ». Il se juge une fois, à l'échafaudage par `skill-craft` ou à la refonte, contre les quatre critères. **POURQUOI cette forme** : déclaratif et grep-able, le checker ne re-devine rien à chaque run, et aucun champ de frontmatter non standard n'est inventé, le comportement de Claude Code sur un champ inconnu n'étant pas vérifié.

Répartition attendue sur les 24 skills : ~9 éligibles (les 6 experts restants, `mermaid-craft`, `fact-checker`, `cadre-prompt`), le reste en test manuel.

## 4. Le checker (Q3)

### Les `evals/` disparaissent

Les dossiers `evals/` se suppriment sur les 24 skills, et `run-skill-evals.py` (695 lignes) avec eux, git les garde. Décision rejouée sans biais de conservation : le corpus dérive déjà (champ `setup` non documenté chez `audit-harnais` qui écrit dans le repo réel, zéro scénario négatif chez `skill-craft` contre sa propre règle) et une passe coûte 5 à 6 $. Un checker qui **dérive ses scénarios du skill lui-même** ne dérive jamais : la `description` est le contrat de déclenchement à tester, les gardes du `## Process` et les tables `## Test` sont le comportement attendu à juger.

### Trois étages

| Étage | Nature | Ce qu'il vérifie |
| --- | --- | --- |
| ① lint | script déterministe, sans LLM | frontmatter qui parse (YAML strict), champs R5 et R13, seuils R1 (~150) et R4 (500), **sections comparées à celles du gabarit** (aucune manquante, aucune en trop, dans l'ordre), flag de test présent, placeholders résiduels, liens relatifs morts |
| ② template | jugement, l'action validate de `skill-craft` | anatomie des actions, doublons R6, tri des natures R8, sections vides R9 |
| ③ review autonome | agent checker, skills flagués seulement | session fraîche via `claude -p` : le déclenchement se vérifie sur la sortie, le comportement se juge contre les tables `## Test` et les gardes du `## Process`, plus un cas négatif dérivé des clauses NE PAS de la description |

La mécanique de session fraîche de l'étage ③ reprend ce que `run-skill-evals.py` a éprouvé : `claude -p`, verdict de déclenchement séparé du verdict de comportement, mesure du 2026-08-06 à l'appui (7/8 sur opus, 0/8 sur sonnet à requêtes identiques).

### Bornes et interdits

- **3 passes checker-corrections maximum.** Au-delà, le défaut est dans le diagnostic ou la frame, pas dans l'exécution. Même borne que `max_iterations` (défaut 3) d'`aidd-orchestrator:00-async-dev`, seule borne numérique du référentiel.
- **Anti-auto-notation conservé** : le contexte qui vient d'écrire un skill ne joue jamais l'étage ③. Il rend la commande et déclare la passe non jouée.
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

- Réécrire `references/skill-authoring-fr.md` contre cette note : anatomie génération 2 francisée (flux mermaid, table 2 colonnes, `## Test` en table), liste de sections **fermée** aux quatre d'AIDD, R4 justifié ou remesuré, R7 et R8 réécrites sans `evals/` ni `## Contrôle de sortie`.
- Créer `skills/skill-craft/assets/skill-template.md` et `assets/action-template.md`, francisés depuis les gabarits AIDD. Ils deviennent la source de la liste de sections, et `01-scaffold` les copie au lieu de dérouler l'anatomie en prose.
- Ajouter au lint la règle qui tient la fermeture : les `##` du fichier se comparent à ceux du gabarit, tout en-tête en trop est un échec avec le home de remplacement en message. **POURQUOI un lint et pas une consigne** : une section inventée est exactement ce qu'une convention en prose ne rattrape pas, 23 fichiers l'ont prouvé.
- Règles nouvelles : le flag d'éligibilité et ses quatre critères, la doctrine subagents (locus, agnosticisme, wrapper), Frame–Deliver–Checker et sa borne, les préfixes de domaine dans le nommage.
- `01-scaffold` décide l'éligibilité à l'échafaudage, avant d'écrire la description.
- `02-validate` devient l'étage ② du checker. Ses propres `evals/` sautent comme les autres.

### audit-harnais (futur `harness-audit`) et la grille

- C3 sur les descriptions change d'instrument : le scénario d'éval stocké n'existe plus, la falsifiabilité d'un contrat de routage passe par l'étage ③ du checker, joué à la demande. Le verdict mécanique « `ls <skill>/evals/` » de la grille se remplace par « le flag de `## Test` et l'étage ③ ».
- Les passes C et D de l'audit skills prennent cette note comme source de conformité de construction, ce que la grille prévoit déjà en déléguant ce point hors d'elle.

### Outillage

- Un script de lint (étage ①) dans `wrappers/claude/scripts/`.
- Un agent checker (étage ③) dans `wrappers/claude/agents/`.
- `run-skill-evals.py` et son test retirés. La section « Jouer les évals des skills » du README se réécrit pour le checker.

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
