# Audit `agent-config` — passe C1b sur `rules/reasoning.md`

**Grille** : `audits/grille-harnais.md` au commit `6269981`, **arbre propre** (`git diff --stat` vide). Verdicts rejouables.

**Modèle de la passe** : **Claude Opus 5**. Page de prompting `platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5` **fetchée le 2026-08-11**. Sans ces deux informations un verdict C1b n'est pas relisable — les prescriptions s'inversent d'une génération à l'autre.

**Verdict en une phrase** : sur 19 instructions, **une seule sort en C1b** (29 mots) ; le fichier n'est pas une rustine de génération précédente, mais il porte **337 mots de déclencheurs rares facturés à chaque session** — et le défaut est C5, pas C1b.

---

## Contrat

| | |
|---|---|
| Sous-domaine | `rules/` — un seul fichier, `rules/reasoning.md` (1 071 mots) |
| Annexe déclarée | `rules/references/ref-reasoning.md` (310 mots), entrée dans le périmètre C8. Vérifié **non chargé** : absent de `~/.claude/rules/` (11 liens, 11 règles, `reasoning.md` seul) |
| Critères couverts | **C1b** en priorité, **C1a** pour ce que le routage y envoie, **C4** (dont doublon par conséquence), **C5**, **C7**, **C8** |
| Exclusions | **C6** hors passe par construction (une somme, jamais une instruction) — mesuré quand même en consolidation. Les autres fichiers de `rules/`. Le sous-domaine `skills/`, en cours dans une session parallèle |
| Découpage | **19 instructions**, comptées dans le fichier et validées par l'humain avant criblage |

### Ce que la doc tranche, et ce qu'elle ne tranche pas

Les deux passages que la page consacre au retrait, **verbatim** :

> *Claude Opus 5 verifies its own work without being told to. If your prompt contains explicit verification instructions ("include a final verification step for any non-trivial task," "use a subagent to verify"), remove them: instructions like these cause over-verification on Claude Opus 5, and removing them reduces wasted tokens with no loss in quality. The same applies to legacy harness scaffolding that adds separate verification steps.*

> *Avoid instructing re-checks it already performs ("double-check your answer," "re-verify before responding")*

**Les deux visent la re-vérification de sa propre sortie. La page ne dit rien du grounding** — consulter une source externe avant d'affirmer. C'est la distinction qui décide de cette passe : `reasoning.md` prescrit du grounding **en amont** de l'affirmation, jamais un re-contrôle **en aval** du travail. L'hypothèse d'ouverture (« le fichier est trop restrictif pour un modèle qui se vérifie seul ») ne se vérifie donc pas sur pièce.

### Calibrage de l'instrument — le zéro n'est pas rendu à l'aveugle

`reasoning.md` porte lui-même le trigger « un comptage qui rend zéro ». Appliqué à cette passe : un verdict C1b proche de zéro peut signifier que le défaut est absent, ou que le routage est aveugle. **Positif connu, exhibé à la main** — `789c710:rules/workflow.md:25-30`, supprimé depuis :

> `## Règle — Vérifier après édition d'un fichier de build`
> `**OBLIGATOIRE**`
> `- Après édition d'un fichier de build (migration, fixture, config CI, dépendances) : lancer la **suite complète**, pas un spot-check, **et** un `git diff` de contrôle avant de déclarer *done*.`

C'est un pas de vérification séparé, ajouté avant de déclarer *done* : du *legacy harness scaffolding* au sens littéral de la page. Passé au routage de cette passe → **disqualifié**. L'instrument voit le positif, donc le 1/19 mesuré plus bas est un vrai 1/19 et non une cécité.

**Négatif de contrôle** : instruction #1 (consulter la source de ce fait précis) → page muette, aucun équivalent natif trouvé → conservée. L'instrument distingue les deux cas.

---

## Cascade par instruction

Mots mesurés par `awk` sur la plage de lignes du découpage. Médiane du fichier : **40 mots/bloc** contre **32** pour le harnais (2026-08-10, 10 fichiers) — 25 % plus lourd. Alerte C7 à ~60 mots.

| # | Instruction | Lignes | Mots | Nature | Sortie | Action | Base |
|---|---|---|---|---|---|---|---|
| 1 | Affirmer sans consulter la source **de ce fait précis** (2 familles) | 4-6 | 107 | comportement | survit C1b → **alerte C7** | Extraire la 4ᵉ part : la liste d'exemples de la famille « observation de codebase » descend en références, l'impératif garde les deux noms de famille | mesuré |
| 2 | Expliquer **pourquoi** une erreur antérieure a été commise | 7 | 29 | comportement | **SORT EN C1b** | **Supprimer** — doublon avec le system prompt natif | mesuré |
| 3 | Bâtir un raisonnement sur une prémisse non mesurée | 8 | 40 | comportement | survit | Garder | jugé sur pièce |
| 4 | Mesurer d'abord, la moins chère **avant** d'ouvrir l'analyse | 11 | 34 | comportement | survit | Garder | jugé sur pièce |
| 5 | Marquer « supposé » vs « doc-vérifié » | 12 | 20 | comportement | survit C1b ; **C4 quasi-doublon assumé** | Garder — `style.md:13` porte la même exigence côté écrit **et cite `reasoning.md`** : pointeur déclaré, pas doublon aveugle | mesuré |
| 6 | Si non documenté → tester empiriquement | 13 | 11 | comportement | survit | Garder | jugé sur pièce |
| 7 | **SEUIL AU COÛT, PAS À L'ENJEU** (+ POURQUOI) | 17-19 | 60 | comportement | survit — pile à l'alerte | Garder. C'est le **plafond** des 12 obligations, pas une 13ᵉ | mesuré |
| 8 | Ce que tue une mesure, un argument ne le tue pas | 21 | 45 | comportement | survit | Garder — 4ᵉ part déjà sortie en références | mesuré |
| 9 | TRIGGER — échec CI / test / build, reproduire localement | 23 | 54 | comportement | survit C1b ; **défaut C5, hors table** | Déclencheur rare facturé en permanent. **Aucun cas mesuré dans l'annexe** ; origine `8e05c34` | mesuré |
| 10 | TRIGGER — comptage à « zéro » (corpus relu + instrument aveugle) | 25-30 | **166** | comportement | survit C1b (le cas le plus proche du couperet) ; **alerte C7** ; **défaut C5** | Le plus gros bloc du fichier, 16 % à lui seul. Extraire la 4ᵉ part ; l'annexe porte déjà les 1 019 occurrences | mesuré |
| 11 | TRIGGER — session log / récap, marquer daté et confronter | 32 | 78 | comportement | survit C1b ; **alerte C7** ; **défaut C5** | **Aucun cas mesuré dans l'annexe** ; origine `4b40d1c`. Candidat à la suppression sèche par la règle de décision du 2026-08-11 (ADR 4) — arbitrage humain | mesuré |
| 12 | OBLIGATOIRE — poser le contrat de questions avant de creuser | 36-38 | 54 | comportement | survit | Garder — cité comme autorité par `audit-harnais/actions/01-cadrer.md:16` | mesuré |
| 13 | NE PAS ajouter une question en cours d'analyse | 40 | 44 | comportement | survit | Garder | mesuré |
| 14 | NE PAS creuser une découverte hors contrat | 41 | 32 | comportement | survit | Garder | mesuré |
| 15 | Re-trier après les mesures | 42 | 35 | comportement | survit | Garder | mesuré |
| 16 | Méta-règle — toute règle énonce sa raison | 48-50 | 49 | **fait (convention)** | **C1a — inférable, coût faible** | **Candidat à la suppression, non tranché** : 10 des 11 fichiers de règles portent un POURQUOI, la convention se lit dans un seul fichier ouvert. Mais la grille la cite comme autorité (C7, ligne 167) — la supprimer orpheline cette citation | mesuré |
| 17 | FORME — négation + alternative | 52 | 23 | **fait (convention)** | survit C1a | Garder — visible dans **4** fichiers sur 11 seulement, 14 occurrences : pas inférable à coût faible, contrairement au #16 | mesuré |
| 18 | Cartesian check — décomposer, challenger isolément | 58-60 | 28 | comportement | survit ; **C4 : 6 copies ailleurs** | Garder **ici** : `reasoning.md` est l'occurrence permanente, donc le propriétaire désigné. Les copies vivent dans `backend-architect`, `frontend-expert`, `database-expert`, `agentic-architect`, `_shared/llm-decision-grid.md`, `aidd-pilot` — leur retrait est **déjà prescrit** par la passe `skills/` experts (194 mots) | mesuré |
| 19 | RED FLAG — « par cohérence avec le reste » | 63 | 11 | comportement | survit ; idem #18 | Garder | mesuré |

**Somme** : 1 061 mots sur les 19 blocs, pour un fichier de 1 071 — les 10 mots d'écart sont les deux titres de section et le `POURQUOI` de section (ligne 15), qui n'appartiennent à aucun bloc autonome.

### Le seul verdict C1b — instruction #2

Le harnais Claude Code injecte, section *Corrections* :

> *don't ruminate or give a detailed account of the mistake or tally past errors*

Vérifié **absent du repo et de `~/.claude`** : c'est du natif, donc invisible à tout grep du domaine — le troisième cas de cet angle mort après « déléguer par défaut » (`workflow.md`) et AP4 (`ai-principles.md`). Le geste prescrit est identique : ne pas rendre compte d'une erreur passée. Doublon → une seule occurrence survit, et c'est la native.

**Ce que la suppression perd, et il faut le dire** : le natif **exempte explicitement les blocs de pensée** (« *This instruction does not apply to thinking blocks* ») ; #2 ne prévoit pas cette exemption. Retirer #2 relâche donc la contrainte dans le raisonnement interne. La borne native est délibérée et mieux fondée que l'absence de borne — mais le changement est réel, pas nul.

### Le vrai défaut du fichier — C5, et la table de la grille ne le porte pas

Cinq blocs se déclenchent sur un événement rare, et sont chargés dans **chaque** session :

| # | Déclencheur | Mots |
|---|---|---|
| 9 | un échec CI / test / build | 54 |
| 10 | un comptage qui rend « zéro » | 166 |
| 11 | un session log ou un récap | 78 |
| 18 | une revue d'archi ou de design | 28 |
| 19 | idem #18 | 11 |
| | **Total** | **337** — 31 % du fichier |

`paths:` ne les sauve pas : leur déclencheur est un **événement**, pas un fichier ouvert, donc le frontmatter les rendrait inertes — exactement la limite que C5 documente pour les 26 descriptions de skills.

**Or la table de C5 n'a que deux lignes** : « identifiable par un chemin → `paths:` » et « global par nature → garder global ». Aucune ne couvre « déclencheur rare, non identifiable par un chemin ». C'est le cas qui a emporté quatre des six règles de `workflow.md` le 2026-08-11 (« facturées à chaque session pour servir quelques fois par mois ») : **ce verdict a été rendu hors table**, et la présente passe doit le rendre hors table une seconde fois. → `## À réviser entre deux audits`.

### C8 — le couple `reasoning.md` + `ref-reasoning.md`

**Aucune contradiction.** L'annexe ne fonde que trois blocs : #1 et #8 (rejeu VW3-3256, 14 affirmations fausses dont 12 tombées sur une mesure, 757 lignes détruites) et #10 (les 1 019 points-virgules). Elle ne contredit ni la règle ni son pourquoi, et c'est le défaut C8 gagné le matin même qui est ici **absent**.

**Asymétrie relevée, sans verdict** : 16 des 19 blocs n'ont aucun cas mesuré dans l'annexe. Deux d'entre eux sont des `TRIGGER` — #9 et #11 — c'est-à-dire précisément la forme la plus coûteuse (54 et 78 mots) et celle que l'ADR du 2026-08-11 (4) désigne comme suspecte : une règle instaurée à chaud après un incident, sans mesure, se supprime plutôt que se teste. Le constat est mesuré ; l'arbitrage est humain.

### Un chiffre de la grille qui ne se reproduit pas

La grille porte « **15 obligations de vérification distinctes** » (`audits/grille-harnais.md`, item C1b de `reasoning.md`, écrit le 2026-08-11 au matin). Remesuré sur le découpage à 19 blocs : **12** blocs prescrivent une mesure (#1, #3, #4, #5, #6, #8, #9, #10 ×2, #11, #15), **13** si l'on compte séparément les deux sous-puces du #10. Le #7 n'en est plus une — c'est désormais un plafond.

Je ne cherche pas la cause de l'écart : un raisonnement passé n'a pas de source consultable (#2, dont c'est exactement l'objet). Le chiffre à retenir est **12**, sur ce découpage, à cette date. La grille est à corriger — hors passe, par l'humain.

---

## Consolidation — C6

Commande de la grille, relancée le 2026-08-11 :

```
règles non scopées + output style ...... 3 055
descriptions de skills (26, parseur YAML)  2 206
MEMORY.md du projet courant ............... absent
                                        --------
permanent réel .......................... 5 261
```

**Cible de 3 950 sur la couche de règles : tenue, 895 mots de marge.** `reasoning.md` en représente **35 %** à lui seul (1 071 / 3 055) — premier fichier de la couche, et de loin.

Aucun dépassement, donc aucune suppression n'est imposée par C6. Tout ce que cette passe prescrit relève de C1b (1 cas), C5 (5 cas) et C7 (3 alertes) — c'est-à-dire du gaspillage, jamais du budget.

**Gains disponibles, par nature du verdict** :

| Verdict | Blocs | Mots | Fermeté |
|---|---|---|---|
| C1b — doublon natif | #2 | 29 | **Tranché par la doc** |
| C1a — convention inférable | #16 | 49 | Candidat ; bloqué par la citation de la grille |
| C7 — 4ᵉ part extractible | #1, #10, #11 | ~150 sur 351 | Prescrit par la grille, à rédiger |
| C5 — déclencheur rare | #9, #11 | 132 | **Hors table — arbitrage humain** |

---

## Captures hors grille

Notées en une ligne, non creusées (contrat de questions).

1. **Le Cartesian check existe en 7 formulations** dont une permanente (`reasoning.md` #18/#19) et six à la demande. Le retrait des copies est déjà prescrit par la passe `skills/` experts ; rien à faire ici, mais personne ne vérifie que le propriétaire désigné reste `reasoning.md` après ce retrait.
2. **`style.md:13` cite `reasoning.md` pour l'incertain** — un pointeur inter-règles dans la couche permanente. Aucun critère ne juge si un pointeur entre deux fichiers **tous les deux chargés** achète quoi que ce soit, ou s'il ne fait que payer deux fois.
3. **La médiane de bloc du harnais (32 mots, 2026-08-10) n'a pas été remesurée** depuis la suppression de `workflow.md` et de `ai-practices.md`. L'alerte C7 à ~60 mots en dérive, donc elle juge contre un corpus qui n'existe plus. Même défaut de transport que le seuil de 130 des descriptions.
4. **L'annexe `ref-reasoning.md` ne couvre que 3 blocs sur 19** et aucun critère n'exige une couverture minimale. Un couple règle+annexe peut donc être cohérent (C8 vert) tout en laissant 16 instructions sans preuve.

---

## À réviser entre deux audits

Propositions, non appliquées — la grille ne se touche pas pendant une passe.

1. **C5 — ajouter la troisième ligne à la table.** « Déclencheur rare, non identifiable par un chemin » n'a pas de case, et deux passes consécutives ont dû rendre ce verdict hors table (`workflow.md` le 2026-08-11 sur 4 règles ; `reasoning.md` ici sur 5 blocs, 337 mots). Action candidate : sortir vers un skill invoqué, ou vers un fichier de références, avec pour test « le déclencheur est-il un fichier ou un événement ? ». **C'est le manque le plus coûteux relevé par cette passe** — plus que tout verdict C1b.
2. **C7 — remesurer la médiane du harnais avant d'appliquer l'alerte.** La grille le prescrit déjà pour les passes `skills/` 7 et 9 (« elles n'héritent pas de ce 130 ») mais pas pour la prose. Généraliser : toute alerte dérivée d'une médiane se remesure sur le corpus courant.
3. **C8 — la couverture de l'annexe n'est pas un critère.** 3 blocs fondés sur 19 passent C8 au vert. Candidat : exiger qu'un `TRIGGER` porte un cas mesuré, ou soit marqué « instauré sans mesure » — ce qui rendrait la règle de décision de l'ADR 4 applicable mécaniquement au lieu d'au jugement.
4. **Corriger le chiffre « 15 obligations de vérification »** dans l'item C1b de `reasoning.md` : la valeur remesurée sur le découpage à 19 blocs est **12**.
5. **Un doublon natif est le troisième du même type.** « Déléguer par défaut », AP4, et maintenant #2. C4 nomme l'angle mort mais son test reste « énumérer à la main ». Trois occurrences justifient de se demander s'il existe un moyen moins fragile d'énumérer le system prompt natif — question ouverte, aucune piste mesurée.
