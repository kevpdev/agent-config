# Annexe à la passe B — déclenchement mesuré et bras contrefactuel

**Grille** : `audits/grille-harnais.md` au commit `b18acea`. La passe B a tourné contre `cf5877a` ; la grille a bougé depuis, cette annexe ne rejoue aucune cascade et ne rend aucun verdict CX — elle n'apporte que des **mesures**. Arbre `audits/` propre à l'écriture (`rules/reasoning.md` modifié par une session parallèle, hors périmètre).

**Rapport de rattachement** : `audits/2026-08-11-audit-agent-config-skills-experts.md`, **immuable et non modifié**. Cette annexe s'y ajoute, elle ne le corrige pas.

**Statut** : annexe de mesure. Elle ferme deux trous que la passe B avait explicitement laissés ouverts — le C3 niveau 2 plafonné (M10) et le « aucun bras contrefactuel » capturé au plan de campagne.

---

## Contrat

**Deux questions, figées avant la première session** (pré-enregistrements dans le scratchpad de la session : `preenregistrement-declenchement.md`, `preenregistrement-contrefactuel.md`).

1. Les non-déclenchements observés sont-ils systématiques ou du bruit à n=1 ?
2. Une session **sans le skill** satisfait-elle les critères que le skill s'est lui-même donnés dans son `evals/eval.json` ?

**Ce qui n'est pas creusé** : aucune réécriture de `description`, aucun verdict de cascade, aucune modification du repo. Le lanceur du bras nu est une **copie jetable** dans le scratchpad ; `wrappers/claude/scripts/run-skill-evals.py` n'a pas bougé.

**Montage** : `claude -p`, modèle opus, juge haiku, worktree jetable par scénario, sans `--force` (les runs forcés ne laissent pas de trace au registre — mesuré le 2026-08-06, non réfuté depuis). Bras nu = le même lanceur avec l'outil `Skill` ajouté à `--disallowedTools`.

---

## Question 1 — le déclenchement est probabiliste, pas cassé

Scénario nominal de chaque expert, lu **au registre** (un `tool_use` de l'outil `Skill` nomme le skill ouvert), jamais aux marqueurs.

| Expert | run 1 | run 2 | run 3 | taux |
|---|---|---|---|---|
| `security-reviewer` *(témoin)* | ✓ | ✓ | ✓ | **3/3** |
| `agentic-architect` | ∅ | ✓ | ✓ | **2/3** |
| `backend-architect` | ∅ | ✓ | ✓ | **2/3** |
| `code-reviewer` | ∅ | ∅ | ✓ | **1/3** |
| `frontend-expert` | ∅ | ∅ | ✓ | **1/3** |
| `ai-engineering` | ✓ | — | — | 1/1 |
| `brain-expert` | ✓ | — | — | 1/1 |
| `database-expert` | ✓ | — | — | 1/1 |
| `devops-expert` | ✓ | — | — | 1/1 |

**Verdict, par la règle figée d'avance** : aucun expert n'est à 0/3. Le défaut n'est pas « la description ne route pas », c'est « elle route une fois sur deux ». Une réécriture de `description` sur cette base dégraderait aussi bien qu'elle améliorerait, et à n=3 rien ne saurait faire la différence.

**Ce que ça invalide** : la lecture d'une première session isolée où 4 experts sur 9 n'avaient pas démarré. Elle décrivait une observation vraie et un diagnostic faux. **À n=1, un déclenchement probabiliste est indiscernable d'une panne** — c'est le vrai enseignement, et il vaut pour toute mesure de déclenchement à venir.

**Hypothèse tuée au passage** : la correspondance littérale entre la requête et une phrase déclencheuse citée dans la `description` n'explique rien. Un seul skill sur 9 a une correspondance exacte (`security-reviewer`, « audit sécurité ») ; `database-expert`, `devops-expert`, `brain-expert` et `ai-engineering` se déclenchent tous sans.

---

## Question 2 — le bras contrefactuel

**Calibration d'abord** : 0 chargement sur les 9 sessions du bras nu, alors que `security-reviewer` s'ouvrait 3 fois sur 3 dans le bras de contrôle. Le blocage tient ; les ∅ sont de vrais ∅.

Les deux bras rejugés **dans le même lot par le même juge**, depuis les transcripts enregistrés — comparer deux verdicts rendus par deux appels distincts mélangerait l'effet du skill et la variance du juge.

| Expert | chargé | nu | Critères perdus sans le skill |
|---|---|---|---|
| `backend-architect` | 3/3 | **0/3** | dit ce qu'il ne sait pas ; réclame 2 contraintes manquantes ; ne rend pas de reco confiante sans contrainte |
| `brain-expert` | 2/3 | **0/3** | ne généralise pas à une population non précisée ; distingue l'expert récurrent du novice |
| `code-reviewer` | 3/3 | 1/3 | section « Bloquants » présente ; verdict tranché parmi 3 |
| `security-reviewer` | 3/3 | 2/3 | ne signale aucun risque tiré d'un fichier hors périmètre |
| `ai-engineering` | 3/3 | 2/3 | exige golden set + seuil chiffré avant la prod |
| `frontend-expert` | 3/3 | 2/3 | champ « Framework détecté » |
| `agentic-architect` | 3/3 | 3/3 | **aucun** |
| `database-expert` | 3/3 | 3/3 | **aucun** |
| `devops-expert` | 3/3 | 3/3 | **aucun** |

### Ce que les 6 apportent : de la retenue, pas de la connaissance

Le modèle nu répond **bien** sur le fond dans presque tous les cas. Ce qu'il perd est d'une autre nature : sans `backend-architect`, il recommande une architecture complète pour « une API de facturation pour des PME » sans rien demander ; avec, il refuse de trancher et réclame charge attendue, taille d'équipe, stack. Même motif pour `brain-expert` (ne généralise pas) et `security-reviewer` (ne déborde pas du périmètre fourni).

**Conséquence pour la refonte** : un corps d'expert se justifie par ses **freins** — les négations de `## Règles strictes`, les exigences de format qui forcent un aveu (« Contexte assumé », « Bloquants ») — plus que par ses blocs de savoir. Un bloc de connaissance que le modèle possède déjà ne perd aucun critère quand on le retire ; un frein, si.

### Ce que les 3 à « aucun » veulent dire, et ce qu'ils ne veulent pas dire

Par la règle figée d'avance : **ce n'est pas la preuve que ces skills sont inutiles, c'est la preuve que leur propre éval ne sait pas montrer ce qu'ils apportent.** Défaut de l'éval avant d'être un défaut du skill. `agentic-architect` nu a rendu la bonne réponse (« pas d'agent — un cron et un script ») ; son éval ne demande rien qu'un modèle compétent ne fasse déjà.

**Action** : réécrire les 3 évals concernées autour d'un critère que le modèle nu **échoue**, puis rejouer le bras nu. Tant que ce critère n'existe pas, ces 3 skills n'ont pas de test qui les distingue de leur absence.

---

## Question 3 — les listes de frères, ou pourquoi le verdict M3 de la passe B est faux

*Section ajoutée après le commit initial de cette annexe, le même soir, sur mesure nouvelle. Le contrat n'est pas rouvert : c'est la même question 2 appliquée à une instruction précise, avec le même montage.*

**Le verdict contesté** : la passe B (M3) juge la liste `## Ne pas s'activer pour` du corps comme un doublon C4 de la clause `NE PAS` du frontmatter, et prescrit « une seule copie, la clause du frontmatter est la surface qui route ».

**Pourquoi les 9 scénarios négatifs ne pouvaient pas trancher** : dans les 9, le skill visé ne s'est **jamais chargé** (registre vide ou nommant le frère). Son corps n'entrait donc jamais en contexte, et sa liste n'avait aucune occasion d'agir. Mesurer la coupe avec ces scénarios en déclenchement libre aurait rendu « aucun changement » quel que soit le contenu du corps.

**Le montage qui tranche** : les 9 négatifs joués en **mode forcé**, qui charge le corps et isole le comportement du déclenchement. Calibré sur `security-reviewer` — 3 marqueurs sur 3 en forcé, 0 sur 3 dans le bras nu, donc le forçage charge bien le corps.

| Bras | Listes de frères | Redirections correctes |
|---|---|---|
| 1 | en place | **7 / 9** |
| 2 | retirées (547 mots) | **5 / 9** |

Règle de décision annoncée **avant** de voir le bras 2 : si le taux tombe, la coupe est abandonnée et les listes restaurées. Il est tombé, elles sont restaurées.

**Ce que les deux régressions disent.** `frontend-expert` et `security-reviewer` **nomment toujours** le bon frère — la clause du frontmatter continue de router. Ce qu'ils perdent est ailleurs : ils répondent d'abord dans leur propre cadre. `security-reviewer` rend un verdict sécurité complet avant de renvoyer, `frontend-expert` tranche « gRPC est éliminé d'office » au lieu de passer la question intacte.

**Conséquence** : la clause du frontmatter **route**, la liste du corps **retient**. Deux fonctions distinctes qui se ressemblent à la lecture, pas deux copies d'une même instruction. Le verdict C4 de M3 est **mesuré faux** et ne doit pas descendre dans les chantiers de refonte.

**Limite déclarée** : une session par bras. Deux bascules sur neuf peuvent être du bruit — c'est exactement le piège de la question 1. La restauration reste néanmoins le côté prudent, puisqu'elle conserve un frein dont la question 2 a montré la valeur.

## Captures hors grille

- **Faux positif prouvé de l'instrument à marqueurs.** `database-expert` a été jugé « déclenché » dans le bras nu : ses deux `trigger_markers` étaient dans la sortie alors qu'aucun skill n'avait pu s'ouvrir. Combiné au faux négatif de `brain-expert` (chargé, marqueurs absents — mesuré le 2026-08-11), **un marqueur ment dans les deux sens**. Le registre est le seul signal direct.
- **Conséquence sur le lanceur** : le commentaire de `trigger_verdict` justifie l'absence de droit de veto du registre par « l'inverse n'a pas été observé ». Il l'est maintenant, dans un sens : marqueur présent sans chargement. Le veto reste néanmoins mauvais — il transformerait ce faux positif en faux négatif sur les sessions où le registre est muet. **À trancher entre deux passes, pas ici.**
- Le lanceur ne sait pas jouer un bras nu : `--disallowedTools` est en dur (`WRITE_TOOLS`) et la racine se dérive de `__file__`, ce qui interdit une copie hors du repo. Deux frictions rencontrées ce soir, aucune corrigée.

---

## À réviser entre deux audits

1. **Un scénario de déclenchement se mesure à n≥3**, jamais à n=1, et toujours avec un témoin connu-positif dans le même lot. À porter dans `skills/audit-harnais/` et dans la convention `skill-craft` (R7).
2. **Le C3 niveau 2 de la grille est trop généreux** : il se satisfait de l'existence d'un `evals/eval.json` à `trigger_markers`. Trois évals sur neuf sont ici vertes sans rien discriminer. Un niveau supérieur devrait exiger qu'au moins un critère soit **échoué par le modèle nu**.
3. **Le bras contrefactuel devient un mode du lanceur**, pas une copie jetable — sinon il ne sera pas rejoué.

## Report vers les chantiers de la note de cadrage

- **Chantier évals** : réécrire les évals d'`agentic-architect`, `database-expert`, `devops-expert` autour d'un critère discriminant ; ajouter le bras nu au lanceur.
- **Chantier corps d'experts** : le dédoublonnage prescrit par la passe B reste valide et **s'oriente** — couper d'abord dans les blocs de savoir, garder les freins. Aucun frein n'est retiré sans mesure.
- **Sans objet** : la piste « réécrire les descriptions qui ne déclenchent pas ». Aucune n'est à 0/3.
- **Retiré** : « ramener les deux listes de frères à une seule copie » (M3). Mesuré faux, cf. question 3. Les 4 autres items de dédoublonnage sont livrés (`41b4afd`).

## Traçabilité

Sessions jouées : 20 (contrôle, 2 lots de 10) + 9 (bras nu) + 18 re-jugements + 1 (calibration du forçage) + 18 (les deux bras de la question 3). Coût mesuré : 5,69 $ + 5,32 $ + 3,41 $ + 0,38 $ + 0,46 $ + 3,21 $ + 3,27 $ = **21,74 $**. Artefacts (transcripts `run.jsonl`, pré-enregistrements, script de comparaison) dans le scratchpad de la session — **volatils**, non versionnés : les chiffres ci-dessus sont à remesurer, pas à reprendre.
