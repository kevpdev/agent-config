# Convention — Rédaction de mes skills (FR)

Ce qui reste à décider quand les deux gabarits ont déjà répondu. À relire avant de créer ou de refondre un skill.

## Les gabarits font foi, pas cette page

L'anatomie ne se raconte pas, elle se copie : [`skill-template.md`](../assets/skill-template.md) et [`action-template.md`](../assets/action-template.md). Ils portent la liste des sections, leur ordre et leur statut. `wrappers/claude/scripts/lint-skills.py` la dérive d'eux au lieu de la coder.

**Aucune section hors de cette liste.** Une section perso n'apporte pas de valeur : son contenu a déjà un home, et l'inventer ailleurs le rend invisible à qui lit le gabarit.

**POURQUOI cette page ne redit pas la liste** : une liste décrite en prose et une liste vérifiée par un script divergent au premier edit de l'une des deux. Une seule liste ne peut pas dériver.

## D'où ça vient, et les cinq deltas

Fork français des 19 règles d'AIDD (`aidd-context:04-skill-generate`, fichier `references/skill-authoring.md`). Le jeu de règles est gardé, cinq choses changent.

| Delta | Contenu |
| --- | --- |
| langue | le contenu est en français, seuls les huit en-têtes de structure restent en anglais (R10) |
| pourquoi | il s'écrit quand il porte un fait indéduisible, ce qu'AIDD ne demande jamais (R12) |
| flux | mermaid `TD` et non `LR` : `rules/mermaid.md` écrase le défaut d'AIDD |
| évals | le dossier `evals/` et son format n'existent pas chez AIDD (R7) |
| nommage | préfixe de domaine obligatoire, voir « Nommage » |

## Les règles

- **R1. SKILL.md est un routeur pur** : portée, flux, table d'actions, règles transverses. Zéro logique métier. Il ne porte rien qu'une action ou une référence pourrait porter, parce qu'il se charge à chaque invocation quand une action ne se charge qu'à son tour.
  - **Exception mono-fichier.** Un skill à responsabilité unique vit en `SKILL.md` seul, sa méthode sous `## Process` à la place de la table d'actions. Ce n'est pas une violation, et le moule ne change pas. On découpe quand apparaissent plusieurs actions distinctes, ou de la connaissance de référence à charger à la demande (R7).
- **R2. Un skill = un domaine.** Domaine-outil, un nom singulier (`jira`). Domaine-activité, un verbe (`review`).
- **R3. Références à un seul niveau.** Une référence n'en appelle jamais une autre. Elle nomme une sœur en backticks et ne la lie jamais.
- **R4. Pas de plafond de lignes sur un routeur.** R1 et le lint le bornent déjà. Seule alerte : au-delà de ~150 lignes, un mono-fichier se demande ce qui peut sortir en actions ou en références.
  - *Le plafond de 500 lignes que cette page portait avant le 2026-08-24 est supprimé, faute d'avoir jamais servi : mesuré sur les 24 skills du repo, le plus gros `SKILL.md` fait 119 lignes.*
- **R5. `description` = quoi + quand.** 3e personne, sous 1 536 caractères (plafond du listing Claude Code, doc vérifiée le 2026-08-11 ; 1 024 est la limite de la spec API, plus basse), pas de XML.
  - Tout le « quand » vit ici, pas dans le corps.
  - Triggers explicites et un peu insistants. Le modèle sous-déclenche, donc sur-liste.
  - **Sauf en invocation manuelle (R13)** : pas de liste de phrases, la description dit par quoi le skill s'appelle. Une phrase déclencheuse sur un skill manuel promet un comportement qui n'existe plus.
  - Le nom de l'artefact en tête. Une parenthèse pour définir, pas un tiret.
  - Clause « NE PAS utiliser pour X (→ frère) » seulement si un skill voisin peut se déclencher à tort. Chaque frère qu'elle nomme se paie un cas d'éval négatif (R7).
- **R6. Zéro doublon.** Un fait, un seul home. Les gabarits vivent dans `assets/`, les actions les citent. Une citation est un lien markdown relatif dans la phrase qui l'utilise, jamais un bloc à part ni un include `@`, que rien ne résout.
- **R7. Rôle des dossiers.** `references/` se LIT. `assets/` se COPIE. `evals/` se JOUE par un exécuteur externe, et n'est jamais lu par le skill lui-même. Pas de `scripts/` par skill : l'exécutable partagé vit dans `skills/_shared/`, l'outillage dans `wrappers/claude/scripts/`.
  - **Un `evals/eval.json` ne porte que des données.** Aucun nom d'outil, aucun nom d'agent, aucune commande. L'exécuteur est forcément spécifique à l'agent et vit dans son wrapper. Un skill qui nomme un agent ne tourne plus sous un autre.
  - Champs d'un cas. `skill` et `query` sont requis. `id` nomme le cas, et sur un négatif il nomme le frère couvert. `expect_trigger` vaut `true` par défaut, `false` sur un négatif. `artifact` porte `path` (un glob) plus `template` ou `sections`, quand le cas produit un fichier. `files` liste des fixtures voisines sous `evals/fixtures/`, réservé aux cas à artefact.
  - **Le champ `artifact` choisit le mode d'exécution, et c'est mécanique.** Sans lui, le cas tourne **outils coupés** : le skill part sans rien pouvoir exécuter, donc un skill à effet de bord se teste sans risque. Avec lui, le cas tourne outils ouverts dans un worktree jetable, seul moyen de constater un fichier.
  - **Un cas positif par skill, et un cas négatif par frère vivant cité en clause NE PAS.** Vérifier qu'un skill part ne vérifie pas qu'il ne part pas à tort, et c'est l'autre moitié que mesurent les collisions de déclencheurs.
  - **Un skill à invocation manuelle (R13) n'a pas de cas positif mesurable, et n'en écrit pas.** Mesuré le 2026-08-24 : un `/<nom>` injecte le skill côté client, donc il ne laisse aucune trace au registre, là où un déclenchement automatique en laisse une. Son corpus n'a que des cas négatifs, ce qui est le contrat qui compte pour lui — il ne doit jamais partir tout seul.
  - **Deux cas qui mesurent la même affirmation n'en valent qu'un.** Trois requêtes qui vérifient toutes « le skill part » se réduisent à celle qui couvre la formulation la plus représentative.
  - **Un cas à artefact fournit son entrée, il ne la décrit pas.** Mesuré le 2026-08-06 : trois évals de revue de code décrivaient le code en prose, et la session répondait « je ne vois pas le code » — un échec qui ne dit rien du skill. Une fixture voisine sous `evals/fixtures/` se déclare alors, et l'exécuteur la copie dans le worktree.
  - **Le taux de déclenchement dépend d'abord du modèle.** Mesuré le 2026-08-06 sur quatre skills en deux répétitions, à skills, requêtes et règles identiques : 7/8 sur `opus` contre 0/8 sur `sonnet`, deux des quatre passant de 0/2 à 2/2. **À LA PLACE de** réécrire une `description` sur un déclenchement rouge → rejouer sur le modèle réellement utilisé. Une éval jouée sur un modèle plus petit mesure un agent qu'on n'exécute pas.
  - **Trier avant de garder : jouer chaque cas deux fois, avec le skill et sans lui.** Un cas qui passe dans les deux ne mesure pas le skill, il se supprime. C'est un geste de relecture au moment de la refonte, pas un flag de l'exécuteur.
  - *Le numéro R8 reste vacant depuis le 2026-08-24 : la règle qu'il portait est morte avec la section perso qu'elle imposait, et le pourquoi vit dans `audits/2026-08-24-cadrage-refonte-skills-cible.md`, section 2. Ne pas le réaffecter, des rapports d'audit le citent.*
- **R9. Pas de section vide.** Une section optionnelle sans contenu s'omet. Jamais de placeholder « ## X → Aucun ».
- **R10. Contenu en français** : frontmatter, corps, actions, références, labels d'étapes et cellules de table. Huit en-têtes de structure restent en anglais, au mot près, parce que ce sont des mots-clés de la famille AIDD et non de la prose : `Actions`, `Transversal rules`, `References`, `Assets`, `Input`, `Output`, `Process`, `Test`.
  - **POURQUOI les huit et pas quatre** : un lint sur une liste bilingue doit traiter les deux orthographes de chaque section, et c'est exactement le genre de tolérance qui laisse passer une section inventée.
- **R11. Une idée par phrase.** Une phrase qui dépasse la ligne se coupe. Exceptions : la `description` mono-ligne et les cellules de tableau.
- **R12. Le pourquoi quand il porte une information.** Une règle énonce sa raison **si cette raison apporte un fait indéduisible** : contrainte d'environnement, mesure, piège vécu. **À LA PLACE de** justifier ce qu'un modèle sait déjà, couper.
  - Une valeur arbitraire (seuil, constante, délai) se justifie toujours : sans sa raison, personne ne sait comment la recalculer.
  - Le pourquoi tient en une ligne. Ce n'est pas une permission de rallonger, R11 tient toujours.
  - `rules/reasoning.md`, section « Méta-règle », fait foi.
- **R13. Mode d'invocation déclaré.** Un skill à effet de bord porte `disable-model-invocation: true` et s'appelle par `/<nom>`. Sans effet de bord, le champ est omis et le skill reste auto-déclenchable.
  - Compte comme effet de bord : écrire un fichier versionné, committer, pousser, supprimer, déplacer, envoyer sur le réseau. Lire, analyser et conseiller n'en sont pas.
  - **POURQUOI le champ et pas une meilleure description** : le déclenchement par phrase est probabiliste, donc il se trompera. Sur une action réversible ça coûte un paragraphe inutile, sur un `git push` ça coûte un commit non voulu. Le champ est le seul mécanisme déterministe disponible.

## Ce qui se vérifie tout seul, et ce qui se refuse

**La coupure est par affirmation, jamais par skill.** Un même skill se vérifie tout seul sur ce qui se contrôle depuis sa sortie, et se relit à la main sur le reste. Chercher une liste de skills éligibles est la mauvaise question.

| Ce qui se vérifie tout seul | Pourquoi c'est robuste |
| --- | --- |
| le **déclenchement** : le skill part quand il doit, se tait quand il ne doit pas | verdict binaire, le registre de la session nomme les skills ouverts. Marche même sur un skill qui ne rend que de la prose |
| l'**artefact** : le fichier produit existe, parse, et porte les sections de son gabarit | verdict par script, sans interprétation |

| Ce qu'on refuse d'asserter | Pourquoi |
| --- | --- |
| l'ordre des outils appelés | trop fragile, ça punit les chemins valides que personne n'avait prévus |
| une regexp sur de la prose | casse à la première variation valide de formulation |
| le style, le ton, « ça sonne juste » | ne se décompose pas en pass/fail, c'est de la relecture humaine |

**Le déclenchement se joue outils coupés** : le skill part mais ne peut rien exécuter. Un skill à effet de bord se teste donc sans risque, et le problème d'éligibilité disparaît presque. Ne restent manuels que les trois refus ci-dessus, et les artefacts écrits hors du dossier de travail.

**Aucun outil natif de Claude Code n'entre dans le lint ni dans l'éval.** Ni `claude plugin eval`, ni `/skill-doctor`, ni `claude plugin validate`. Ce sont des sources d'inspiration, jamais des dépendances : le critère est l'agnosticisme, pas leur maturité, sinon la question se rouvre à chaque release.

## Doctrine subagents

| Quand découper | Signe |
| --- | --- |
| **locus** | borné et sans interaction humaine → subagent ; persistant ou interactif → parent. Un serveur meurt avec le subagent, un dialogue de confirmation n'y est pas possible |
| **saturation** | une recherche dont les dumps noieraient le contexte du parent se délègue |
| **parallélisable** | des tâches indépendantes se lancent en un seul message, plusieurs appels |

- **Commencer simple** : agent générique avec brief inline dans le `## Process`. Un agent nommé ne se crée que quand le brief se répète entre skills ou porte un rôle durable.
- **Agents agnostiques du modèle** : pas de champ `model`, à l'inverse d'AIDD. Le ratio performance sur coût se règle à l'usage, pas dans le fichier.
- **Un agent nommé vit en `.md` dans `wrappers/claude/agents/`**, jamais dans un dossier `agents/` du skill — même logique qu'AIDD, dont les agents vivent au niveau plugin. Le skill qui en dépend le déclare dans ses règles transverses. *Les agents sont propres au CLI, un skill reste théoriquement portable.*
- Un agent garde sa liste blanche de skills en fin de fichier, et l'interdiction de déléguer à un autre agent.

## Frame–Deliver–Checker

Le pattern s'emploie sur un skill qui produit un artefact vérifiable et boucle dessus : une zone qui cadre le contrat, une qui produit, un checker indépendant qui juge contre le contrat.

- **3 passes maximum.** Au-delà, le défaut est dans le diagnostic ou dans le cadrage, pas dans l'exécution. Même borne que le `max_iterations` d'`aidd-orchestrator:00-async-dev`, seule borne numérique du référentiel.
- **Anti-auto-notation** : le contexte qui vient d'écrire un skill ne joue jamais son éval. Il rend la commande et déclare la passe non jouée.
- Aucun cas de checker n'écrit dans le repo réel.

## Nommage

**Le nom d'un skill est en anglais, préfixe compris. Seul le contenu est français.**

| Préfixe | Domaine |
| --- | --- |
| `expert-` | conseil et analyse, sans effet de bord |
| `vault-` | le vault Obsidian |
| `aidd-custom-` | skills perso dont l'**objet** est le framework AIDD |
| `harness-` | maintenance du harnais lui-même |
| `dev-` | livraison quotidienne |

- **POURQUOI `aidd-custom-` et pas `aidd-`** : les skills du plugin s'affichent déjà en `aidd-*`, et un skill perso au même préfixe s'y confond dans un listing. Un skill qui invoque un skill AIDD en sous-étape garde son domaine d'usage, il ne change pas de préfixe.
- Fichiers d'action en kebab-case verbe (`post-message`, `run-tests`), préfixe numéroté quand l'ordre est strict. Le slug, c'est le nom sans le préfixe.
- À éviter : préfixe redondant (`skill-slack`), noms vagues (`helper`, `utils`), gérondifs (`reviewing`).

## Check de collision

Avant de créer un skill, lister les skills installés et chercher un recouvrement de description. Si deux skills se déclenchent sur la même phrase, l'un est de trop : fusionner, renommer, ou resserrer. Dans le doute, demander.

## Ce que le lint ne voit pas

Deux dérives échappent à tout contrôle mécanique, ici comme chez AIDD. Ce sont les deux plus fréquentes, et elles se relisent à la main au moment de la refonte.

| Dérive | Ce qu'elle donne |
| --- | --- |
| **R1** | un `SKILL.md` qui regonfle en logique métier au lieu de router |
| **R6** | un même fait recopié à deux endroits, dont la copie périmée survit |
