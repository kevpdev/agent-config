# Audit `agent-config` — passe `skills/` C1 : le corps de `doc-sync`

Instantané immuable, 2026-08-25.

**Grille** : `audits/grille-harnais.md` au commit **`599c7eb`**, arbre **propre** (`git diff -- audits/grille-harnais.md` vide au cadrage et à la clôture) — verdicts rejouables.
**Modèle** : Claude Opus 5 (`claude-opus-5[1m]`). Page de prompting fetchée le **2026-08-25**, autorité de C1b. Ses prescriptions s'inversent d'une génération à l'autre : les verdicts C1b de ce rapport datent de ce modèle.
**Arbre de travail** : `wrappers/claude/rules/plan-mode.md` et `wrappers/claude/settings.json` modifiés, hors périmètre, non lus.
**Protocole** : skill `audit-harnais` (01-cadrer → 02-cribler → 03-consolider).

**Verdict en une phrase** : sur 107 instructions, **5 sortent pleinement** de la cascade (2 en C1a, 3 en C1b), **7 se réduisent ou changent de niveau** (4 réductions C1b, 3 déplacements C5) et **21 sont des doublons** dont 15 internes au même fichier — et les deux défauts les plus lourds sont exactement les deux que la convention du repo annonce comme invisibles au lint, de la logique métier dans un routeur (R1) et un fait recopié à deux endroits (R6), l'instrument mécanique en attrapant 12 quand la relecture en trouve 19 de plus.

---

## Contrat

**Périmètre** : les 9 fichiers du corps de `skills/doc-sync/` — `SKILL.md`, les 7 actions, `references/memory-criteria.md`. **10 632 mots, 107 instructions.**

**Critères** : C1→C5 puis C7 par instruction, C8 par fichier **et par couple** (le `SKILL.md` déclare `references/memory-criteria.md` en annexe). **C6 hors périmètre** — la grille pose qu'un corps de skill ne se charge qu'à l'invocation. Relevé de contrôle en clôture, sans verdict.

**Hors crible** : le bloc `description` du frontmatter, jugé en passe A le 2026-08-11 ; il n'entre que comme surface de comparaison C4. Les 23 autres skills (passes ultérieures).

**Entrées figées, non rejugées** : les arbitrages du `audits/2026-08-24-cadrage-refonte-skills-cible.md` (préfixe de domaine, format d'éval minimal, Frame–Deliver–Checker borné à 3 passes, doctrine subagents) et la convention `skills/skill-craft/references/skill-authoring-fr.md`, que la grille désigne comme source normative des skills perso. C'est contre eux que se juge la conformité de construction.

**Convention de découpage, figée au cadrage** : une étape `## Process` numérotée = une instruction, ses sous-puces *Pourquoi* comprises ; une sous-puce à impératif autonome compte à part ; les lignes de `## Test` ne sont pas des instructions mais la commande de vérification de l'instruction correspondante, jugée en C3 avec elle ; une puce de section normative du routeur = une instruction. Détail des 107 : le découpage a été rendu à l'utilisateur avant le premier verdict et approuvé.

**Alerte C7 remesurée sur ce corpus : 69 mots**, soit 2× la médiane de **34,5** sur 124 blocs normatifs (`## Test` exclu). Le 60 de la couche `rules/` et le 130 des descriptions ne se transportent pas — la grille l'exige pour un corpus neuf. À 69, **43 blocs sur 124 dépassent (35 %)**.

---

## Mesures d'ouverture

| Mesure | Commande | Sortie |
|---|---|---|
| Poids du corps | `find skills/doc-sync -type f \| xargs cat \| wc -w` | **10 632 mots**, 9 fichiers |
| Répartition | `wc -w` par fichier | `SKILL.md` 2 019 · `01` 1 718 · `05` 1 358 · `04` 1 099 · `03` 1 034 · `07` 543 · `02` 625 · `06` 386 · `references/memory-criteria` 1 850 |
| Lint mécanique | `python3 wrappers/claude/scripts/lint-skills.py` | **12 FAIL** sur `doc-sync`, tous réels — voir la note sur le douzième |
| Corpus d'éval | `ls skills/doc-sync/evals` | **absent** |
| Médiane des blocs | script de comptage, `## Test` exclu | 34,5 mots sur 124 blocs · max **562** (étape 1 de `01`) |
| Page Opus 5 | fetch | 2026-08-25 |
| Citations croisées | `grep -rn doc-sync --include='*.md' skills rules wrappers` | 1 seule, `memory-bootstrap/SKILL.md:12`, clause NE PAS |

**Calibrage de l'instrument de grep, et le faux zéro qu'il a évité.** Le premier lot de greps C4 a rendu **zéro sur huit motifs**. La cause n'était pas l'absence de doublon : la liste de cibles incluait `CLAUDE.md`, absent de la racine du repo, ce qui faisait échouer chaque `grep` en entier. Recalibré sur un motif dont la présence était certaine (`un fait, un seul home`, connu en `skill-authoring-fr.md:51`), l'instrument a rendu les doublons listés plus bas. *C'est le trigger de `rules/reasoning.md` : ne jamais lire un zéro comme l'absence du défaut.*

**Le douzième défaut n'est pas un faux positif, contrairement au premier jugement de cette passe.** `placeholder skills/doc-sync/actions/06-sync-readme.md : <X>` porte un diagnostic imprécis — le chevron est une variable de brief de sous-agent, pas un reste de gabarit. Mais le lint a une convention déclarée et il l'applique : son `check_placeholders` retire le code inline avant de chercher (`INLINE_CODE.sub("", …)`), et son docstring pose que « un chevron dans du code inline est de la notation, pas un reste ». Le fichier pose son chevron **nu**. **12 défauts réels**, dont celui-ci se répare en entourant `<X>` de backticks, sans rien retirer au brief. *Corrigé après mesure du code du lint, le premier jugement ayant été rendu sur la forme du message et non sur l'instrument.*

---

## Cascade par instruction

Base : **mesuré** (commande citée) · **jugé sur pièce** (pas de sondage ni d'A/B dépensé) · **supposé**.

### `SKILL.md` — 25 instructions, 1 767 mots

| # | Instruction | Sortie | Action prescrite | Base |
|---|---|---|---|---|
| S1 | portée : memory + README, ni doc inline ni hook | survit → C7 (72 m) | extraire le pourquoi déduisible (« le planning repart d'une base fausse ») ≈ 25 m | jugé sur pièce |
| S2 | deux entrées, un seul flux | survit → C7 (98 m) | extraire le *Pourquoi un mode et non une action* — méta-commentaire de conception, quatrième part | jugé sur pièce |
| S3 | comment l'entrée se choisit — demander si les deux lectures tiennent | **C1b partiel** | l'impératif double le natif (« *check in only when different readings of the request would lead to materially different work* », system prompt Claude Code, repris tel quel par la page Opus 5). **Garder le seul piège mesuré** : l'entrée par diff sur une intention d'audit rend « aucune surface touchée », donc l'erreur ressemble à un succès. 106 → ≈ 45 m | mesuré (page Opus 5, 2026-08-25) |
| S4 | chaîne d'actions par régime | survit (38 m) | conforme au fond ; **le gabarit veut un `flowchart TD`**, pas une chaîne fléchée en prose (viole aussi `rules/ponctuation.md`) | mesuré (gabarit) |
| S5 | triptyque frame / deliver / check | **hors crible** | le pattern est un arbitrage figé au contrat (2026-08-24). Non rejugé ; la tension avec la page du jour est en capture. Criblé sur C7 seul : 85 m, le *Pourquoi trois étapes et non une* porte un fait indéduisible, **garder** | mesuré (contrat de passe) |
| S6 | cycle borné à deux retours, échec fermé | survit → C4 | **doublon de `skill-authoring-fr.md:113`** (« 3 passes maximum »), qui fait foi. Réduire à un pointeur | mesuré (grep) |
| S7 | en coordinateur, le flux vaut par repo | survit → C7 (84 m) | **découper** : le bloc empile Boulot 1, Boulot 2, résolution du home et arrêt si `02` est vide — quatre instructions sous un numéro | mesuré (comptage) |
| S8 | table des sept actions | survit → C4 (186 m) | la colonne `Input` recopie l'`## Input` de chaque action, et sort du gabarit (`\| Action \| Fait \|`). Supprimer la colonne | mesuré (gabarit) |
| S9 | table des régimes reflet / décision | **C5 — mauvais niveau** | logique métier dans un routeur (R1). `02`, `04` et `07` la citent tous trois comme source unique : **déplacer** en `references/`, pas supprimer. 168 m | mesuré (grep des trois citations) |
| S10 | cas limite `coding-assertions` | **C5 — mauvais niveau** | même verdict, suit S9 en référence. 81 m | jugé sur pièce |
| S11 | où passe la coupe dans une surface décision | **C4 — doublon quasi textuel de A4.9** | 99 + 116 = **215 mots pour un fait**. Une seule survit, celle de l'action, là où le geste se fait | mesuré (lecture des deux blocs) |
| S12 | la doc ne couvre que le validé | survit → C4 | doublon interne de **S17**. Garder ici, supprimer le garde-fou | mesuré |
| S13 | topologie : autorité universelle, homes variables | **C5 + C4** | doublon de A1.4 / A1.5, qui portent le geste. 98 m | mesuré |
| S14 | règle d'édition directe — lire la structure d'abord | **C1b — doublon du natif** | le system prompt porte « *Write code that reads like the surrounding code: match its comment density, naming, and idiom* ». Le pourquoi déclaré est déduisible. **Sort** — et le geste est déjà redit dans A4.4 et A6.2 : trois occurrences pour un comportement natif | mesuré (system prompt) |
| S15 | dépendance `10-learn` optionnelle | survit → C4 (34 m) | redit par A4.1. Garder une occurrence | mesuré |
| S16 | pré-conditions | survit → C4 (62 m) | doublon de A1.4 sur distribué / centralisé | mesuré |
| S17 | GF validé only | **C4** | ⊂ S12 | mesuré |
| S18 | GF régime avant édition | **C4** | ⊂ S9 | mesuré |
| S19 | GF autorité = le code qui implémente | **C4** | ⊂ S13 et A7.2 | mesuré |
| S20 | GF scope confirmé | **C4** | ⊂ A1.15 | mesuré |
| S21 | GF édition ciblée only | **C4** | ⊂ A4.4 et A6.3 | mesuré |
| S22 | GF une entrée qui recopie un fichier n'entre pas | **survit, exemplaire** | pointeur assumé et déclaré (« le critère complet vit dans `references/`, ce garde-fou est le seul volet à connaître **avant** de charger »). C'est le modèle de découpage que C5 prescrit | mesuré |
| S23 | GF vérifier avant d'affirmer | **C4 — doublon du permanent** | `rules/reasoning.md:1` « Ne jamais affirmer sans vérifier », chargé à **chaque** session. Un skill n'a pas à le redire | mesuré (grep) |
| S24 | GF s'arrêter si rien à faire | **C4** | ⊂ A2.5 | mesuré |
| S25 | GF hors périmètre : doc inline à chaud ailleurs | **C4** | ⊂ S1, qui dit déjà « pas de doc inline, pas de hook ». Le pourquoi (doc à chaud vs à froid) se verse dans S1 | mesuré |

**C8 du fichier** : **7 des 9 garde-fous sont des doublons internes** des sections qui les précèdent, soit ≈ 200 mots qui répètent 700. Quatre sections portent de la logique métier qu'une action ou une référence pourrait porter (S9, S10, S11, S13), ce qui est la dérive R1 que la convention nomme comme invisible au lint. Sept sections hors gabarit, `## Transversal rules` et `## Test` absentes, aucun bloc mermaid. **1 767 mots pour un routeur dont le gabarit attend une portée, un flux, une table, des règles transverses et un test.**

### `actions/01-detect-scope.md` — 17 instructions, 1 670 mots

| # | Instruction | Sortie | Action prescrite | Base |
|---|---|---|---|---|
| A1.1 | opt-in WIP averti | survit (31 m) | garder | jugé sur pièce |
| A1.2 | mode `--audit`, étapes 1-2 inchangées | survit (37 m) | garder | jugé sur pièce |
| A1.3 | détecter mono-repo | survit | garder | jugé sur pièce |
| A1.4 | coordinateur : distribué vs centralisé | survit → C4 | porte le fait que S13 et S16 répètent. **C'est ici que le fait vit** | mesuré |
| A1.5 | conséquence commit selon `VCS = propre / parent` | survit | garder — piège nommé (`git -C` sans `.git`) | jugé sur pièce |
| A1.6 | les deux commandes de détection | **survit, C2 conforme** | la détection est déjà un script (`_shared/detect-children.sh`), la prose est réduite à son appel. C'est le sort que C2 prescrit | mesuré |
| A1.7 | se lancer depuis la racine du parent | **survit, exemplaire** | faux zéro mesuré le 2026-08-21 (31 enfants vs « mono-projet »), et le `## Test` porte le contrôle calibré. **C3 niveau 2** | mesuré |
| A1.8 | chemin absolu, pas `$SKILLS_ROOT` | **survit → capture C2** | contrainte d'environnement mesurée. Son test (`grep -nE '^[[:space:]]*bash .*\$'`) est un **check mécanique jamais câblé** → voir captures | mesuré |
| A1.9 | ne pas réimplémenter la détection | survit | piège vécu, non inférable | jugé sur pièce |
| A1.10 | lire les colonnes MEMORY et VCS | **C1a — inférable à coût faible** | la sortie du script nomme ses colonnes. **Supprimer** ou replier dans A1.6 | mesuré (sortie du script) |
| A1.11 | confirmer le contrat partagé, pas de nom conventionné | survit | garder | jugé sur pièce |
| A1.12 | si aucune doc ne joue ce rôle → Boulot 1 | survit | garder | jugé sur pièce |
| A1.13 | table situation → scope | survit → C7 (237 m) | **découper** : six situations dont deux portent leur propre garde | mesuré |
| A1.14 | en `--audit`, ne pas chercher de base | survit | garder | jugé sur pièce |
| A1.15 | confirmer / élaguer commits + fichiers | **survit, appuyé par la doc** | la page Opus 5 prescrit l'inverse d'un retrait : « *For narrow tasks, constrain scope explicitly* ». S20 le répète au routeur | mesuré |
| A1.16 | en `--audit`, un fichier par défaut | **survit, exemplaire** | mesuré le 2026-08-21 : 5 fichiers → 31 constats, quand le cycle en tolère 3 passes | mesuré |
| A1.17 | ne pas confondre le scope et le home | survit (20 m) | garder | jugé sur pièce |

**C8** : cohérent, et c'est le meilleur fichier du corpus sur C3 — deux de ses neuf lignes de `## Test` sont des **commandes**, dont un contrôle calibré qui dit ce que la commande doit rendre depuis deux répertoires différents. **C7 : son étape 1 pèse 562 mots en un seul numéro**, le plus gros bloc du corpus, ce qui est le cas « dépassement porté par l'impératif » — le cadrage l'a découpée en 8.

### `actions/02-classify-impact.md` — 6 instructions, 601 mots

| # | Instruction | Sortie | Action prescrite | Base |
|---|---|---|---|---|
| A2.1 | table pattern de chemin → impact / régime / cible | **C1a — inférable, et volatile** | ses patterns sont Java/Spring (`*Controller*`, `*Dto*`, `*Repository*`) : sur un projet Node ou Python elle ne matche rien, et le skill ne déclare aucune restriction de stack. Réduire à l'axe régime, que A2.4 sait déjà router | jugé sur pièce |
| A2.2 | en `--audit`, sauter cette table | survit | piège nommé : sans la ligne, l'audit s'arrête sur un faux négatif | jugé sur pièce |
| A2.3 | les noms de sections README ne sont pas figés | **C1b — doublon du natif** | même geste que S14, même autorité. Supprimer | mesuré |
| A2.4 | router par régime, lire la table du `SKILL.md` | **survit, exemplaire** | c'est le pointeur anti-doublon, avec son pourquoi mesurable (« une énumération dupliquée finit par omettre une surface ajoutée depuis ») | jugé sur pièce |
| A2.5 | arrêter si vide, ne rien inventer | survit réduit | l'arrêt est natif (« *stop short of actions clearly beyond what was asked* ») ; « ne pas inventer de mises à jour pour justifier le run » est le contre-défaut, non inférable. Garder la seconde moitié | mesuré |
| A2.6 | cette étape ne se déclenche pas en `--audit` | survit | garder | jugé sur pièce |

**C8** : cohérent. Le fichier est le plus petit et le mieux articulé du corpus sur ses deux régimes d'entrée.

### `actions/03-frame-memory.md` — 12 instructions, 1 006 mots

| # | Instruction | Sortie | Action prescrite | Base |
|---|---|---|---|---|
| A3.1 | en `--audit`, la seconde source devient unique | survit | garder | jugé sur pièce |
| A3.2 | charger le critère + les quatre poids du framework | survit | garder — désigne la source qui fait foi et ne la recopie pas | mesuré |
| A3.3 | lister les candidats : deux sources, dont l'existant | **survit, exemplaire** | « une passe qui n'examine que le neuf laisse grossir le banc à chaque run » — fait indéduisible | jugé sur pièce |
| A3.4 | en `--audit`, première source vide, seconde élargie | survit | garder | jugé sur pièce |
| A3.5 | sur un retour de `05`, ne pas relister | **survit, exemplaire** | relister rouvre des candidats tranchés, ce qui fait grossir le lot — or le lot qui ne rétrécit pas est le signal d'arrêt de `05`. Articulation non inférable | jugé sur pièce |
| A3.6 | mesurer avant de noter, nommer le fichier | survit réduit → C4 | l'impératif double `rules/reasoning.md` (permanent). **L'increment est l'instrument** : nommer le fichier, pas l'estimer. Garder l'instrument, couper le générique | mesuré (grep) |
| A3.7 | regrouper par cause, geste mécanique (grep) | **survit, exemplaire** | C3 niveau 2, porte sa commande. Le pourquoi est un fait : « deux pièges qui se ressemblent passent pour deux faits distincts » | jugé sur pièce |
| A3.8 | ne pas chercher de cause à un symptôme unique | survit | cite `reasoning.md` en pointeur au lieu de recopier le contrôle de superlatif. Conforme C4 | mesuré |
| A3.9 | trancher : conditions conjointes de l'exception | **C4 — doublon textuel de R6** | le critère vit dans la référence. Réduire à « appliquer le verdict du critère » | mesuré |
| A3.10 | réconcilier dans la taxonomie `10-learn` | survit (25 m) | garder | jugé sur pièce |
| A3.11 | afficher le coût en deux nombres | survit → C4 (112 m) | doublon de R15 / R16. Garder le **second** nombre (les symptômes supprimés), qui n'est nulle part ailleurs, et pointer pour le premier | mesuré |
| A3.12 | rendre le plan, soumettre une sortie sur du texte humain | survit réduit | « confirmer avant une action difficile à annuler » est natif ; l'**asymétrie** (décrire le code est un constat, retirer une phrase humaine est une décision) ne l'est pas. Garder l'asymétrie | mesuré |

**C8** : cohérent. Neuf des douze lignes de `## Test` sont des critères de relecture, pas des commandes — C3 niveau 3.

### `actions/04-deliver-memory.md` — 9 instructions, 1 070 mots

| # | Instruction | Sortie | Action prescrite | Base |
|---|---|---|---|---|
| A4.1 | vérifier `10-learn` et le home | survit → C4 | redit S15 | mesuré |
| A4.2 | garde-fou home centralisé : ne pas déléguer à `10-learn` | **survit, exemplaire** | comportement mesuré d'un outil externe (`10-learn` écrit à plat), donc non inférable et non re-dérivable sans le lancer | jugé sur pièce |
| A4.3 | déléguer cas A en passant les verdicts de `03` | survit | le pourquoi porte un fait : le scoring du framework ignore si le fait est reconstructible | mesuré |
| A4.4 | éditer en direct cas B | **C4** | ⊂ S14 (natif) + S21. Ne garder que le cas B lui-même, sans redire la règle de style | mesuré |
| A4.5 | déporter avant de supprimer | **survit, exemplaire** | « l'inverse perd le fait entre les deux edits, et rien ne le signale » — ordre non inférable | jugé sur pièce |
| A4.6 | rejouer ce qui descendait de la prémisse | **survit → C7 (259 m)** | **ne double pas `reasoning.md`** : celui-ci dit de ne pas affirmer sans vérifier, pas de rejouer les mesures d'une prémisse corrigée. Les trois cas mesurés du 2026-08-21 (≈ 110 m) sont la quatrième part → **extraire vers la référence** | mesuré |
| A4.7 | ne pas remplacer un décompte par une explication | survit | son *pourquoi le redire ici* est honnête : une reformulation contourne le refus dur sans le contredire | jugé sur pièce |
| A4.8 | différer les décisions vers `07` | **C4** | ⊂ S18 et S9 | mesuré |
| A4.9 | exception cadrée : prose de détail d'un index de portes | **C4 — doublon de S11** | garder **celle-ci**, supprimer S11 : le geste se fait ici | mesuré |

**C8** : cohérent. L'étape 5 est le seul endroit du corpus où un cas mesuré est cité avec ses trois occurrences — d'où le dépassement C7, qui se répare par extraction et non par coupe.

### `actions/05-check-memory.md` — 12 instructions, 1 325 mots

**Statut du fichier avant les instructions** : son existence relève de l'arbitrage Frame–Deliver–Checker du 2026-08-24, **figé au contrat de cette passe**. Aucune de ses instructions n'est jugée sur le principe de la vérification indépendante — elles descendent la cascade sur les autres critères, comme le reste du corpus.

| # | Instruction | Sortie | Action prescrite | Base |
|---|---|---|---|---|
| A5.1 | en `--audit`, le checker juge le scope entier | survit, exemplaire | ferme un trou réel : une entrée gardée à tort ne produit aucune édition, donc le checker ne la voit jamais. Cas mesuré le 2026-08-21 | jugé sur pièce |
| A5.2 | dispatcher un checker frais indépendant | **hors crible sur le principe** → survit sur C7 | pattern figé au contrat. Sur la formulation : 88 m, dont un *Pourquoi* qui porte un fait indéduisible (« celui qui vient d'écrire juge sa propre intention, pas son résultat »). **Garder tel quel** | mesuré (contrat de passe) |
| A5.3 | lui tendre le critère par son chemin absolu | survit | contrainte d'environnement : le checker n'étend sa checklist qu'avec celle du **projet**, et le critère vit dans le harnais | mesuré |
| A5.4 | ajouter le protocole de passe périmée | survit | garder | jugé sur pièce |
| A5.5 | ne pas déléguer en bloc à `02-project-memory:03-check` | **survit, exemplaire** | faux positif structurel mesuré : son `structure.md` dit « flat, never nested », donc il classerait chaque `<enfant>/tooling.md` en orphelin | mesuré |
| A5.6 | router les constats : table constat → action | survit → C7 (182 m) | garder, c'est le cœur ; sous l'alerte par ligne | jugé sur pièce |
| A5.7 | la hausse ne se déclenche pas sur une passe de pointeur | survit → C4 | doublon de R16, mais **assumé et déclaré** (« le checker est dispatché en contexte neuf, il ne voit qu'un décompte qui monte »). C'est le modèle S22 : alerte minimale + pointeur | mesuré |
| A5.8 | le compteur vit dans le rapport, pas dans le contexte | **survit, exemplaire** | fait indéduisible : un checker en contexte neuf n'a aucun souvenir de la passe précédente | jugé sur pièce |
| A5.9 | borne dure : deux retours au maximum | survit → C4 | **doublon de `skill-authoring-fr.md:113`** (« 3 passes maximum »), qui fait foi, et de S6. Trois expressions de la même borne dans deux fichiers et une convention | mesuré (grep) |
| A5.10 | trois sorties avant la borne | survit, exemplaire | « un compteur seul laisse tourner deux passes inutiles » | jugé sur pièce |
| A5.11 | les constats routés vers `07` ne comptent pas dans le lot | **survit, exemplaire** | mesuré : 4 constats sur 31, un lot qui ne pouvait pas descendre sous 4, donc un signal d'arrêt qui ne mesurait plus rien | mesuré |
| A5.12 | échouer fermé, ne rien annuler seul | survit → C4 | ⊂ S6 pour l'échec fermé ; « ne rien annuler » est l'increment, à garder | mesuré |

**C8** : cohérent, et c'est le fichier le plus soigné du corpus après la référence — chacune de ses trois sorties de boucle porte sa raison mesurée, et deux d'entre elles (A5.8, A5.11) portent un fait qu'aucun contexte neuf ne reconstruit. Seul défaut : A5.9 exprime une troisième fois une borne que S6 et la convention portent déjà.

### `actions/06-sync-readme.md` — 4 instructions, 353 mots

| # | Instruction | Sortie | Action prescrite | Base |
|---|---|---|---|---|
| A6.1 | ordonner memory puis README | survit (17 m) | garder | jugé sur pièce |
| A6.2 | analyser par sous-agent | **C1b — contredit par la doc du jour** | « *Do not delegate work you can finish yourself in a handful of tool calls* ». Lire un README et proposer des edits de section en est un. Le motif déclaré (« préserver le contexte parent ») est le critère de **saturation** de la convention, qui ne tient pas pour un fichier de cette taille. **Supprimer la délégation**, garder le brief comme consigne de lecture directe | mesuré (page Opus 5 + convention) |
| A6.3 | edits ciblés, jamais de réécriture | **C4** | ⊂ S21 et A4.4 | mesuré |
| A6.4 | proposer le commit doc par repo | **C1b partiel — doublon du natif** | « *Commit or push only when the user asks* » et « *For actions that are hard to reverse or outward-facing, confirm first* » sont dans le system prompt. **Garder le seul fait non inférable** : en coordinateur centralisé, un changement produit deux commits dans deux repos git | mesuré (system prompt) |

**C8** : le fichier ne survit qu'à moitié — deux de ses quatre instructions sortent, et une troisième est un doublon. Ce qui reste tient en ≈ 80 mots.

### `actions/07-reconcile.md` — 4 instructions, 508 mots

| # | Instruction | Sortie | Action prescrite | Base |
|---|---|---|---|---|
| A7.1 | réconcilier doc-vs-code à HEAD par sous-agent | **survit** — et c'est le contraste avec A6.2 | ici la délégation est le cas que la page Opus 5 **valide** : « *a wide multi-file investigation* », plusieurs repos enfants à lire. La même doc tranche les deux dans des sens opposés, sur le critère du volume | mesuré (page Opus 5) |
| A7.2 | autorité par fait : table backend / front | survit → C4 | doublon de S13 et S19. **C'est ici que la table vit** | mesuré |
| A7.3 | signaler « décision affirme X / code fait Y », ne pas écraser | **survit, cœur du skill** | le pourquoi est un fait : le skill ne peut pas distinguer une découverte à entériner d'une bavure à corriger | jugé sur pièce |
| A7.4 | arbitrer : deux issues, ne pas deviner une divergence | survit réduit | « attendre l'arbitrage » est natif ; la divergence entre deux enfants est l'increment | mesuré |

**C8** : cohérent. Le fichier porte la seule limite explicitement assumée du corpus (« capture la dérive descriptive, pas les décisions d'une feature »), ce qui est un bon signal C3.

### `references/memory-criteria.md` — 18 instructions, 1 807 mots

| # | Instruction | Sortie | Action prescrite | Base |
|---|---|---|---|---|
| R1 | ce que le fichier ajoute, et ce qu'il ne recopie pas | **survit, exemplaire** | C4 appliqué à lui-même : il nomme les deux fichiers du framework qui font foi et refuse de les recopier | mesuré |
| R2 | les trois dimensions : inférable, coût, stabilité | **survit, cœur non inférable** | aucun des quatre poids du framework ne regarde si le fait est reconstructible. Fait mesurable et vérifié dans la source citée | mesuré |
| R3 | verdict 1 — garder le non inférable | survit | garder | jugé sur pièce |
| R4 | verdict 2 — exception coût élevé + dérive faible | survit | garder | jugé sur pièce |
| R5 | verdict 3 — sortir, laisser un pointeur | survit | garder | jugé sur pièce |
| R6 | les deux conditions sont conjointes | **survit** | c'est A3.9 qui sort, pas R6 : le critère vit ici | mesuré |
| R7 | refus dur : une copie de fichier n'entre pas | **survit, exemplaire** | S22 en est le pointeur assumé au routeur. Modèle de découpage C5 | mesuré |
| R8 | un fait, un home + table des homes | survit | **pas** un doublon de R6 de `skill-authoring-fr.md` malgré la formule identique : l'objet est le banc de mémoire d'un projet audité, pas un skill. Deux domaines, même adage | mesuré (grep + lecture) |
| R9 | le piège coûte plus que le fait qu'il corrige | survit | fait mesuré : c'est pourquoi une passe de correction fait grossir ce qu'elle corrige | jugé sur pièce |
| R10 | test d'existence — d'où part le lecteur | **survit, exemplaire** | mesuré le 2026-08-21 : ce cas a produit l'essentiel d'un +28 % sur le fichier le plus lourd du banc | mesuré |
| R11 | test du home — combien de cibles partagent la cause | **survit, exemplaire** | mesuré : trois causes uniques portaient 54, 52 et 11 mentions | mesuré |
| R12 | le renvoi va du symptôme vers la cause | survit | articule explicitement avec l'interdit de `memory-bootstrap` au lieu de le contredire en silence | mesuré |
| R13 | trois calibrages à rejouer | **survit, exemplaire — C3 niveau 2** | les trois calibrages **sont** les cas d'éval du critère, avec leur verdict attendu. C'est la seule commande de vérification du corpus qui teste une règle de jugement | mesuré |
| R14 | aucun plafond chiffré | survit | mesuré le 2026-08-20 : une passe sous plafond de 6 000 a fini à 9 591 | mesuré |
| R15 | afficher le décompte à chaque passe | survit | garder — A3.11 en est la copie, c'est elle qui se réduit | mesuré |
| R16 | justifier une hausse, jamais une valeur (+ 2 cas nommés) | **survit tel quel, malgré 432 m** | le plus gros bloc du corpus, et **c'est sa bonne place** : la grille prescrit que les cas vécus descendent dans une référence non chargée. Ils y sont. Aucune extraction à faire | mesuré (comptage) |
| R17 | relire ce qui dépasse 2× la médiane ; compter en mots | survit | le « compter en mots, jamais en lignes » porte sa mesure (125 lignes pour 266 mots) | mesuré |
| R18 | le refus est la seule borne dure + contrôle de sortie | survit | garder | jugé sur pièce |

**C8, et C8 par couple** : `memory-criteria.md` est le meilleur fichier du corpus — **18 instructions, aucune sortie de cascade**, cinq exemplaires, et le seul endroit où une règle de jugement porte ses cas de calibrage. Le couple `SKILL.md` ↔ annexe ne porte **aucune contradiction** : S22 déclare l'annexe et son propre périmètre partiel, R18 confirme que le refus est la borne dure.

**Une articulation implicite à rendre explicite, seul défaut C8 du couple** : R15 dit que le décompte « se rend, il ne se compare à rien », R17 pose un déclencheur de relecture à 2× la médiane. Les deux tiennent (l'un sur la racine, l'autre par fichier), mais rien ne le dit — un lecteur qui cite R15 en extrait conclut qu'aucun seuil n'existe.

---

## Le résultat principal — la délégation d'analyse se tranche au volume

**Ce que la passe a mesuré sur la délégation, et ce qu'elle n'a pas eu à juger.** Deux actions confient une analyse à un sous-agent, `06-sync-readme` et `07-reconcile`. La page de prompting Opus 5 les tranche en sens **opposés**, sur un critère unique et vérifiable :

> Delegation pays off on genuinely independent, sizeable tracks of work […] **Do not delegate work you can finish yourself in a handful of tool calls**

- **`A7.1` survit** : lire le code de N repos enfants pour comparer doc-vs-code à HEAD est le cas que la même page valide nommément, « *a wide multi-file investigation* ».
- **`A6.2` sort** : lire un `README.md` et proposer des edits de section se fait en une poignée d'appels. Le motif déclaré par l'action (« préserver le contexte parent ») est le critère de **saturation** de la convention, qui suppose des dumps capables de noyer un contexte — un README ne les produit pas.

**Ce n'est donc pas la délégation qui est en cause, c'est son volume**, et le critère est utilisable parce qu'il rend deux verdicts différents sur deux instructions du même skill.

**Ce que cette section ne traite pas, et volontairement.** La vérification indépendante par sous-agent — `S5` au routeur et l'action `05-check-memory` — relève de l'arbitrage Frame–Deliver–Checker du `2026-08-24-cadrage-refonte-skills-cible.md`, entré au contrat de cette passe comme **acquis**. Le contrat de questions ne se rouvre pas en cours d'analyse : la tension mesurée avec la page du jour est consignée en **capture**, non creusée, et aucune des 12 instructions de `05` ne reçoit de verdict de suppression à ce titre. Elles sont criblées sur les autres critères comme le reste du corpus.

---

## Conformité de construction

Contre `skills/skill-craft/assets/*-template.md` et `references/skill-authoring-fr.md`, que la grille désigne comme sources normatives.

| Écart | Mesure | Règle |
|---|---|---|
| `argument-hint` absent | lint | gabarit — et le skill **prend** un argument (`--audit`) |
| 7 sections hors gabarit dans `SKILL.md` | lint | « Aucune section hors de cette liste » |
| `## Transversal rules` absente | lint | obligatoire au gabarit |
| `## Test` absente du `SKILL.md` | lint | obligatoire au gabarit |
| aucun bloc mermaid | lecture | gabarit : `flowchart TD` sous le titre. `## Flux` le remplace en prose fléchée |
| `evals/` absent | `ls` | R7. Le skill est en `disable-model-invocation`, donc R13 ne lui demande **pas** de cas positif — mais il cite `aidd-vcs:01-commit` en clause NE PAS, donc il doit **un cas négatif** |
| préfixe de domaine absent | lecture | arbitrage du 2026-08-24. `doc-sync` → `dev-doc-sync` selon la table des préfixes |
| logique métier dans le routeur | S9, S10, S11, S13 | R1, et c'est la dérive que la convention nomme comme invisible au lint |
| fait recopié à deux endroits | 15 doublons internes | R6, l'autre dérive invisible au lint |
| chaîne à flèches en prose | S4, `SKILL.md:31-33` | `rules/ponctuation.md` |

**Les deux dérives que la convention annonce comme invisibles au lint sont toutes deux présentes**, et ce sont les deux plus lourdes du rapport. L'instrument mécanique en attrape 12 ; la relecture en trouve 19 de plus.

---

## Captures hors grille

Notées en une ligne, non creusées.

- **C2 non câblé, `01-detect-scope`** : son `## Test` porte `grep -nE '^[[:space:]]*bash .*\$'` — un check mécanique, écrit comme un critère de relecture. Il aurait sa place dans `lint-skills.py`, qui ne le porte pas.
- **Le message du lint sur les placeholders nomme mal ce qu'il mesure.** Il dit « placeholder du gabarit resté » alors que sa convention réelle est « chevron hors backticks ». Le verdict est juste, son libellé envoie chercher le mauvais défaut — il a coûté un faux jugement à cette passe. Reformuler le message est un correctif de `lint-skills.py`, hors périmètre ici.
- **`memory-bootstrap` n'a pas d'`evals/` non plus**, alors qu'il cite `doc-sync` en clause NE PAS. Le cas négatif manque des deux côtés de la même frontière.
- **A2.1 suppose une stack Java/Spring** sans que le skill déclare de restriction. Un `doc-sync` lancé sur un projet Node passe l'étape 1 de `02` sans qu'aucun pattern matche.
- **Le rapport de la passe A du 2026-08-11 annonçait 26 descriptions**, le corpus en porte 24 après l'archivage de 5 et l'arrivée de 3. Aucun verdict de cette passe n'en dépend.
- **Tension entre la page Opus 5 du 2026-08-25 et l'arbitrage Frame–Deliver–Checker du 2026-08-24.** La page liste `"use a subagent to verify"` parmi les instructions à retirer et ajoute « *The same applies to legacy harness scaffolding that adds separate verification steps* ». L'arbitrage étant figé au contrat, **non creusé** : ni verdict, ni recommandation. Deux faits à verser à qui le reprendra — la page du 2026-08-11, seule disponible quand l'arbitrage a été posé, ne portait pas la clause sur les sous-agents vérificateurs ; et A5.1 ne fait pas une re-vérification, puisqu'en `--audit` le checker examine des entrées que l'action `04` n'a jamais touchées (même distinction que la passe C1b de `reasoning.md` du 2026-08-11, « retirer la re-vérification de sa propre sortie, jamais le grounding »).

---

## À réviser entre deux audits

Propositions pour la grille, à décider par l'humain. **La grille n'a pas été touchée** (`git diff -- audits/grille-harnais.md` vide).

1. **C5 n'a pas de case pour un corps de skill.** Ses trois lignes parlent de `paths:` et du contexte permanent. Sur un corps, la vraie question est le **niveau** — routeur, action, ou référence — et c'est ce qui a produit quatre verdicts de cette passe (S9, S10, S11, S13). La grille les a reçus hors table, exactement comme les 26 descriptions de la passe A. **Troisième passe consécutive à rendre son verdict principal hors de la table de C5.**
2. **C7 n'a pas de case pour une instruction dont le dépassement est à sa bonne place.** R16 pèse 432 mots dans une référence non chargée, ce que la grille prescrit par ailleurs. Le tableau des quatre cas de C7 rend « extraire la quatrième part » — ce qui serait faux ici, la référence **étant** la destination. Une ligne « déjà en référence non chargée → garder tel quel » referme le trou.
3. **C3 gagnerait à nommer le calibrage d'une règle de jugement.** R13 (« trois calibrages, à rejouer si ces tests sont réécrits ») est le seul objet du corpus qui teste une règle non mécanisable, et le gradient C3 ne le prévoit pas : ce n'est ni un hook, ni une commande de vérification, ni un impératif court. C'est un cas d'éval d'un critère de jugement.
4. **Le seuil C7 de 69 mots vaut pour ce corpus seul**, comme le 130 des descriptions valait pour le sien. Trois corpus, trois médianes : `rules/` à 32, descriptions à 86, corps de skill à 34,5. Le geste de remesure est déjà dans la grille ; ce qui manque, c'est de le dire pour les passes de corps restantes.

### Le protocole `audit-harnais`, et non la grille — trou mesuré pendant cette passe

Distinct des quatre points ci-dessus : ceux-là visent la grille, celui-ci vise le skill qui l'exécute. À décider par l'humain, **après** clôture de la passe — éditer le protocole en cours de passe est la même faute que toucher la grille.

**Le défaut** : rien dans les trois actions ne dit ce qu'il advient d'une mesure qui contredit une entrée que le contrat déclare acquise. Trois faits le montrent.

1. **La catégorie « entrées figées, non rejugées » est absente du protocole** (`grep` sur les trois actions et le `SKILL.md` : rien) et présente dans **2 rapports sur 2** qui en avaient besoin — la passe A du 2026-08-11 l'a inventée, cette passe l'a réinventée sans la connaître. C'est le signal que la grille elle-même utilise pour conclure qu'un critère ne mesure pas ce qu'il prétend.
2. **`01-cadrer` connaît les exclusions, pas les acquis.** Son étape 2 prescrit de « lister les exclusions demandées ». Une exclusion est ce qu'on ne lit pas ; un acquis est ce qu'on lit **sans le juger**. Le protocole n'a que la première catégorie, donc la seconde se réinvente à chaque passe.
3. **Le déclencheur et son instruction sont à sept étapes d'écart.** Le fetch de la page de prompting est prescrit aux étapes 1 et 4 de `02-cribler`, sous le mot « autorité de C1b ». Le geste de capture arrive à l'étape 8. Rien entre les deux ne dit que le contrat borne ce que la cascade peut juger, et « autorité » pousse à lire la page comme un verdict.

**Correctif proposé, deux lignes et non une refonte** :

- `01-cadrer`, étape 2 — une catégorie **« acquis »** à côté des exclusions : ce que le contrat fait entrer sans le juger, avec sa source.
- `02-cribler`, étape 5 (« Descendre ») — une ligne posant qu'une mesure contredisant un acquis produit une **capture**, jamais un verdict de cascade.

*Pourquoi à ces deux endroits et non dans les règles transverses du routeur : le déclencheur tombe pendant le cadrage puis pendant la descente, or une règle transverse se lit à l'ouverture et pas au moment du geste.*

---

## Relevé de contrôle C6 — sans verdict

Le corps d'un skill ne se charge qu'à l'invocation, la grille l'exclut de C6. Relevé pour mémoire, en cas de bascule d'une instruction vers le permanent :

| Couche | Mots |
|---|---|
| `SKILL.md` (chargé à chaque invocation du skill) | 2 019 |
| 7 actions (chargées une à leur tour) | 6 763 |
| `references/memory-criteria.md` (chargée par `03`, `04` et le checker) | 1 850 |
| **Total** | **10 632** |

Aucun verdict de dépassement — C6 ne compare plus à une cible depuis le 2026-08-21.

---

## Ce que la passe n'a pas dépensé, et le dit

- **Aucun A/B à bras de contrôle.** Les cinq sorties C1b sont rendues sur la doc, qui nomme leur comportement natif. Aucune ne repose sur un A/B, que la grille exige pour ce que la doc ne tranche pas — et aucune sortie n'a été rendue sur ce terrain-là.
- **Une erreur de conduite de la passe, corrigée avant le rendu et consignée ici.** Le premier jet de ce rapport faisait de la tension Opus 5 / Frame–Deliver–Checker son résultat principal, alors que le contrat déclarait cet arbitrage acquis. Le protocole prescrivait une capture non creusée : c'est ce qu'elle est désormais. Aucun verdict de cascade n'a changé de valeur, seul le cadrage de `S5` et `A5.2` est passé de « C1b, non appliqué » à « hors crible, criblé sur C7 seul ».
- **Aucun sondage C1a.** Les verdicts d'inférabilité (A1.10, A2.1) sont « jugés sur pièce », dits tels quels.
- **Aucun test comportemental C7.** Les extractions proposées ne sont pas mesurées, la grille les réserve aux instructions au-dessus de l'alerte et les échantillonne — aucun échantillon n'a été tiré.
