# Convention — Rédaction de mes skills (FR)

Comment j'écris un skill perso pour qu'il reste propre et lisible. À relire avant d'en créer ou d'en refondre un.

## D'où ça vient

C'est un fork français des règles de l'AIDD (`aidd-context:04-skill-generate`, fichier `references/skill-authoring.md`). Je garde le jeu de règles, qui a fait ses preuves. J'y change deux choses, et c'est tout :

- **R10** passe de « anglais imposé » à **français**. Mes skills perso sont pour moi, pas pour du partage d'équipe.
- **R12** ajoute « toujours le pourquoi », qui manque à l'AIDD trop sobre.

Deux règles (R1, R6) ne sont vérifiées par aucun outil, même côté AIDD. C'est par là qu'un skill dérive. Le lint de `../actions/02-validate.md` les couvre ; à surveiller à la main hors de ce skill.

## Les règles

- **R1. SKILL.md est un routeur pur** : description, table d'actions, règles transverses. Zéro logique métier.
  - **Exception mono-fichier.** Un skill à responsabilité unique peut vivre en `SKILL.md` seul, sans `actions/`. Il porte alors sa méthode inline, ce n'est pas une violation. On ne découpe que si deux conditions apparaissent : plusieurs actions distinctes, ou de la connaissance de référence à charger à la demande (R7). Seuil d'alerte : au-delà de ~150 lignes, se demander ce qui peut sortir. Pourquoi : imposer routeur + actions à un skill de 80 lignes trahit l'esprit de R1 (garder le contexte léger), on remplace un fichier par quatre sans rien gagner.
- **R2. Un skill = un domaine.** Domaine-outil, un nom singulier (`slack`). Domaine-activité, un verbe (`review`). Voir Nommage.
- **R3. Références à un seul niveau.** Une référence n'en appelle jamais une autre.
- **R4. SKILL.md sous 500 lignes.** Au-delà, découper en références.
- **R5. `description` = quoi + quand.** 3e personne, sous 1024 caractères, pas de XML.
  - Tout le « quand » vit ici, pas dans le corps.
  - Triggers explicites et un peu insistants. Le modèle sous-déclenche, donc sur-liste.
  - Le nom de l'artefact en tête. Une parenthèse pour définir, pas un tiret.
  - Clause « NE PAS utiliser pour X (→ frère) » seulement si un skill voisin peut se déclencher à tort.
- **R6. Zéro doublon.** Un fait, un seul home. Les gabarits vivent dans `assets/`, les actions les citent.
- **R7. Rôle des dossiers.** `references/` se LIT. `assets/` se COPIE ou s'INJECTE. `evals/` se JOUE par un exécuteur, et n'est jamais lu par le skill lui-même.
  - Un `evals/eval.json` porte des scénarios en données pures, `query` + `expected_behavior`, sans aucun appel d'outil. Pourquoi : l'exécuteur est forcément spécifique à l'agent et vit dans son wrapper. Un skill qui nomme un agent ne tourne plus sous un autre.
- **R8. Chaque action suit l'anatomie et porte un `## Test`.** En mono-fichier (pas d'`actions/`), c'est `SKILL.md` qui porte le `## Test`, dès qu'il produit un artefact vérifiable.
  - **Ne pas confondre deux natures.** Un critère que le skill applique **pendant** qu'il travaille est un contrôle de sortie, il reste inline (`## Contrôle de sortie`) puisqu'il sert à chaque exécution. Un scénario qui juge **si le skill marche** est une éval, elle part dans `evals/` et `## Test` n'en garde que le pointeur. Pourquoi : une éval inline se paie en contexte à chaque invocation pour une vérification qui ne tourne jamais à ce moment-là.
- **R9. Pas de section vide.** J'omets une section optionnelle sans contenu. Jamais de placeholder « ## X → Aucun ».
- **R10. Contenu en français** (frontmatter, corps, actions, références). Seuls les en-têtes d'anatomie restent en anglais (voir plus bas, ce sont des mots-clés de structure).
- **R11. Une idée par phrase.** Je coupe une phrase qui dépasse la ligne. Exceptions : la `description` mono-ligne et les cellules de tableau.
- **R12. Toujours le pourquoi.** Une règle énonce sa raison, pas seulement l'ordre.
  - Pourquoi : un LLM suit mieux une raison qu'un ordre sec. Sans le pourquoi, il viole plus souvent la règle et ne sait pas la transposer à un cas non prévu.
  - Le pourquoi tient en une ligne. Ce n'est pas une permission de rallonger, R11 tient toujours.

## Anatomie d'une action

Un fichier par action, numéroté quand l'ordre compte (`01-<slug>.md`). Ces parties, dans cet ordre :

- `# NN - Titre` + une phrase : ce que fait l'action.
- `## Input` : OPTIONNEL, prose ou bullets libres. Omis si rien. Pas de bloc de données figé.
- `## Output` : OBLIGATOIRE, une ligne ou une petite forme inline.
- `## Process` : petites étapes numérotées, une responsabilité chacune.
  - Chaque étape démarre par un label en gras d'un mot (ex. **Détecter.**), puis des phrases impératives courtes. Deux phrases valent mieux qu'un point-virgule.
  - Sous-bullets pour une branche, une condition (« si X, alors Y »), ou un retour en arrière.
  - Étapes agnostiques de l'outil. Les détails par outil (chemins, formats) vivent dans une référence.
  - La décision de flux vit dans l'étape, pas derrière un pointeur. La référence ne porte que la donnée consultée.
  - `→` seulement pour une chaîne de flux, jamais `->`.
- `## Test` : une liste de vérifs simples. Une commande, un contrôle d'artefact, ou un effet observable. Déterministe autant que possible. Pour une action pilotée par le modèle, on vérifie une propriété observable de la sortie (sa structure, un champ requis), pas une valeur exacte. Exécution réelle, jamais un `*.test.js` mocké.

Les en-têtes `Input` / `Output` / `Process` / `Test` restent en anglais. Pourquoi : ce sont des repères de structure de la famille AIDD, pas de la prose. Les garder rend mes skills reconnaissables et alignés. Tout le reste est en français.

## SKILL.md (le routeur)

Frontmatter YAML + corps markdown.

- `name` en kebab-case, sous 64 caractères, **égal au nom du dossier**. Pas de deux-points, slash, point, préfixe de plugin. Mots réservés interdits : `anthropic`, `claude`. Regex `^[a-z0-9]+(-[a-z0-9]+)*$`.
- `description` : selon R5, forme FR « <quoi>. Utiliser quand <triggers>. NE PAS utiliser pour <X> (→ frère). »
- Corps = routeur pur. La table d'actions mappe chaque numéro et slug à un rôle et un input. J'énonce le flux, soit une chaîne séquentielle, soit une carte trigger → action. Les auto-skips sont dits explicitement.

`name` n'est pas le token d'invocation. L'adresse se construit à partir du plugin et du dossier. Un deux-points ou un préfixe dans `name` casse le chargement.

## Nommage

- **Domaine-outil, un nom singulier** : `slack`, `notion`.
- **Domaine-activité, un verbe** : `review`, `plan`, `test`.
- Fichiers d'action en kebab-case verbe (`post-message`, `run-tests`). Préfixe numéroté quand l'ordre est strict ou qu'un groupement aide la lecture. Le slug ailleurs, c'est le nom sans le préfixe.
- À éviter : préfixe redondant (`skill-slack`), noms vagues (`helper`, `utils`), gérondifs (`reviewing`).

## Check de collision

Avant de créer un skill, lister les skills installés et chercher un recouvrement de description. Si deux skills se déclenchent sur la même phrase, l'un est de trop. Fusionner, renommer, ou resserrer. Dans le doute, demander.

## Ce que rien ne vérifie automatiquement

L'étape `05-validate` de l'AIDD relance juste le `## Test` de chaque action. Elle ne voit pas :

- **R1** : un SKILL.md qui regonfle en logique métier au lieu de router.
- **R6** : un fait recopié à deux endroits.

Ce sont les deux dérives les plus fréquentes (aidd-pilot était tombé dans les deux). Le lint de `../actions/02-validate.md` les remonte.
