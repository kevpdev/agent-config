# Cadrage — la grille cible d'audit du harnais

Note de décision, 2026-08-26. Elle juge **l'instrument**, jamais le harnais qu'il mesure.

**Ce qu'elle tranche** : les huit critères de `audits/grille-harnais.md` sont-ils tous pertinents,
portent-ils des trous, et existe-t-il une liste plus simple et plus robuste.

**Grille au moment du cadrage** : commit `599c7eb`, inchangée depuis le 2026-08-25. Les quatre
propositions du rapport de cette date n'ont donc jamais été appliquées.

**Ce qui n'est pas tranché ici** : le coût d'un critère et le verdict « overkill », qui demandent un
modèle de coût. L'architecture du skill `audit-harnais`. Le contenu de `audits/axes-protocole.md`,
qu'une passe seule alimente.

---

## Contrat et convention de comptage

**La convention s'écrit avant le premier chiffre**, parce que le repo a déjà mesuré qu'un entier sans
convention ne se reproduit pas : « nombre d'obligations » a pris trois valeurs en un jour sur le même
fichier (`grille-harnais.md:364`), et `axes-protocole.md` porte la même leçon sur « nombre
d'instructions » (P2).

| Terme | Ce qu'il compte |
|---|---|
| **un verdict** | une décision rendue par une passe, quel que soit le nombre d'objets qu'elle couvre. Un verdict de groupe sur 26 descriptions compte pour **un**, et le nombre d'objets est donné à part |
| **hors table** | l'action prescrite ne figure dans aucune ligne du tableau, du gradient ou de la liste de cas que le critère porte **au commit de grille que la passe cite en en-tête** |
| **encore hors table** | le même verdict, rejoué contre `599c7eb` |
| **une passe** | un rapport daté de `audits/`. Il y en a **8**, pas trois : le chiffre trois est le nombre de corpus dont C7 a mesuré la médiane |

**Calibrage de l'instrument.** Le comptage est une lecture, donc il peut être aveugle. Positif
exhibé d'avance : le rapport du 2026-08-25 déclare lui-même « la grille les a reçus hors table » pour
S9, S10, S11 et S13. Négatif exhibé d'avance : le rapport du 2026-08-21 rend son verdict C5 sur
`plan-mode.md` par la deuxième ligne du dosage, nommément citée. L'instrument sépare les deux cas.

**Les huit passes**, dans leur ordre de commit de grille :

| Sigle | Rapport | Grille |
|---|---|---|
| R1 | `2026-08-10-audit-agent-config-c1-c4.md` | `2c9fc31` |
| R2 | `2026-08-10-audit-agent-config-rules.md` | `5327bdd` |
| R3 | `2026-08-11-audit-agent-config-rules-reasoning-c1b.md` | `6269981` |
| R4 | `2026-08-11-audit-agent-config-skills-descriptions.md` | `1ad0dac` |
| R5 | `2026-08-11-audit-agent-config-skills-experts.md` | `cf5877a` |
| R6 | `2026-08-11-…-skills-experts-annexe-declenchement.md` | `b18acea` (annexe de mesure, aucune cascade) |
| R7 | `2026-08-21-audit-agent-config-rules.md` | `a945687` |
| R8 | `2026-08-25-audit-agent-config-skills-doc-sync.md` | `599c7eb` |

---

## Q1 — les verdicts tombés hors de leur propre table

### Le compte

| Critère | Verdicts hors table à la date | Encore hors table | Objets couverts | Passes concernées |
|---|---|---|---|---|
| C1a | 3 | **3** | 29 | R3, R5 |
| C1b | 9 | **9** | 9 | R7, R8 |
| C2 | 9 | **9** | 9 | R2, R4, R8 |
| C3 | 5 | **2** | ~25 | R2, R4, R5, R6, R8 |
| C4 | *sans objet* | *sans objet* | — | C4 ne porte **aucune table** |
| C5 | 7 | **4** | 39 | R3, R4, R8 |
| C6 | *sans objet* | *sans objet* | — | C6 ne porte aucune table |
| C7 | 7 | **3** | ~24 | R3, R4, R5, R7, R8 |
| C8 | 6 | **6** | 6 | R3, R5, R7, R8 |

**36 verdicts encore hors table**, répartis sur sept critères.

### C1a — 3 verdicts, tous ouverts

| Verdict | Source | L'action rendue | Pourquoi hors table |
|---|---|---|---|
| `reasoning.md` #16 | R3:66 | « candidat à la suppression, **non tranché** » | la table rend « supprimer ». Le verdict est suspendu par une dépendance externe (la grille cite #16 comme autorité), cas qu'aucune ligne ne prévoit |
| les 19 `references/` des experts | R5:156-163, R5:258 | « placées en C1, sort **suspendu** faute de sondage » | aucune ligne « non jugé ». Le rapport refuse de supprimer 6 252 mots sur un verdict sur pièce, et il a raison |
| M2, `## Quand t'activer` (9 copies) | R5:55, R5:84 | « sort en C1 » sur un motif **temporel** | ni C1a (rien à retrouver) ni C1b (ce n'est pas un comportement). L'information arrive après la décision qu'elle prétend informer |

**Ce que le compte cache, et qui compte davantage** : le test de C1a, le sondage d'un contexte neuf,
a été joué **2 fois sur 8 passes** (R1:28, R2:19), et les deux fois marqué « approximé » pour la même
raison structurelle — un sous-agent hérite des règles globales, donc son contexte n'est jamais neuf
(R1:32). R5 ne l'a pas joué (interdit de session), R7 ni R8 non plus (R8:324, « aucun sondage C1a »).

### C1b — 9 verdicts, tous ouverts, tous la même cause

Aucune ligne de la table ne porte « **doublon partiel du natif, garder l'increment** ». Les quatre
lignes rendent « supprimer » ou « garder », jamais « réduire ».

| Verdict | Source | L'increment gardé |
|---|---|---|
| `style.md` #3 | R7:149 | trancher, puis donner le critère qui a fait pencher (~20 mots) |
| `ai-principles.md` #7 | R7:173 | le titre et sa ligne de pourquoi |
| `ai-principles.md` #10 | R7:176 | idem, la moitié non native |
| S3, doc-sync | R8:58 | le piège mesuré (un diff sur une intention d'audit rend « aucune surface »), 106 → 45 mots |
| A2.5 | R8:116 | « ne pas inventer de mises à jour pour justifier le run », le contre-défaut |
| A3.12 | R8:136 | l'asymétrie constat / décision sur du texte humain |
| A6.2 | R8:182 | le brief, en consigne de lecture directe |
| A6.4 | R8:184 | en coordinateur centralisé, un changement produit deux commits |
| A7.4 | R8:195 | la divergence entre deux enfants |

**Le test de C1b n'a jamais tourné.** L'A/B à bras de contrôle qu'exige la grille est joué **0 fois
sur 8 passes**, dit tel quel par R7:309 et R8:322. Les 9 verdicts ci-dessus, plus les 5 sorties sèches
de R8, reposent tous sur la lecture de la page de prompting ou du system prompt. C1b est donc un
**contrôle documentaire**, pas un critère de jugement, et la grille le présente comme l'inverse.

### C2 — 9 verdicts, tous ouverts

La table porte trois mécanismes : hook git, hook harnais, aucun. Deux cas réels n'y sont pas.

| Verdict | Source | Le mécanisme réel |
|---|---|---|
| `vault-save` | R4:82 | `disable-model-invocation: true`, un champ de frontmatter |
| `vault-log-session` | R4:83 | idem |
| `aidd-pilot` | R4:89 | idem |
| `doc-sync` | R4:93 | idem |
| `memory-bootstrap` | R4:94 | idem |
| B1, `back-spring.md` | R2:142 | checkstyle couvre la **présence**, le jugement reste prose |
| F2, `front-react.md` | R2:153 | `eslint-plugin-testing-library` couvre une part |
| F3, `front-react.md` | R2:154 | règles eslint de nommage, même forme |
| A1.8, doc-sync | R8:95 | un check mécanique **écrit mais jamais câblé** dans `lint-skills.py` |

Deux trous distincts. Le premier est un mécanisme absent de l'énumération. Le second est la
**couverture partielle** : aucune ligne ne dit ce que devient la prose quand un linter en prend la
moitié.

### C3 — 5 verdicts, 2 ouverts

| Verdict | Source | Statut |
|---|---|---|
| 13 skills sans éval, « niveau 3 » | R4:78-94 | **refermé** par `aa11542`, qui a nommé l'éval dans le gradient |
| les 9 experts, « niveau 2 plafonné » | R5:169-191 | **refermé** par la clause du cas négatif |
| PR6, `ai-practices.md` | R2:124 | « gradient 4 → déplacer vers le MOC », quand la table rend « supprimer ou reformuler » |
| 3 évals vertes qui ne discriminent rien | R6:114 | **ouvert** — le modèle nu passe les mêmes critères. Le niveau 2 se satisfait d'un fichier, jamais d'un pouvoir discriminant |
| R13, les trois calibrages | R8:283 | **ouvert** — un cas d'éval d'une **règle de jugement** n'est ni un hook, ni une commande, ni un impératif court |

### C4 — le critère n'a pas de table du tout

Le signal de la grille ne s'y applique donc pas, et c'est en soi le constat. Ce que C4 laisse au
jugement, mesuré :

| Manque | Source | Ce qu'il a coûté |
|---|---|---|
| **quelle copie survit** | R2:198, R8:10 | 21 doublons tranchés 21 fois au jugement dans la seule passe du 2026-08-25, la règle disant seulement « une seule occurrence » |
| **le doublon à fonctions distinctes** | R5:235 | verdict M3, **réfuté par mesure** — voir Q6 |
| **aucun instrument sur le natif** | R7:311, R3:160 | 3 verdicts de R7 et 1 de R3 reposent sur une citation de contexte, non reproductible par commande |

### C5 — 7 verdicts, 4 ouverts

| Verdict | Source | Statut |
|---|---|---|
| 5 blocs de `reasoning.md` | R3:98 | **refermé** par `b18acea`, troisième ligne de la table |
| 26 descriptions de skills | R4:179 | **refermé** par la deuxième ligne, « global par nature » |
| 4 règles de `workflow.md` | `grille-harnais.md:142`, `:353` | **refermé** par la même troisième ligne |
| S9, S10, S11, S13 de `doc-sync` | R8:64, :65, :68, :281 | **ouverts, sur un axe neuf** — la question n'est pas la portée mais le **niveau** : routeur, action, ou référence |

### C7 — 7 verdicts, 3 ouverts

| Verdict | Source | Statut |
|---|---|---|
| 19 dépassements sur 26 descriptions | R4:226 | **refermé** par le seuil de routage à 130 |
| #10 de `reasoning.md`, 97 → 94 mots | R3:60 | le dépassement était un **artefact d'unité de mesure**, pas une part compressible |
| 2 blocs d'`autorite-des-conventions.md` | R7:299 | même cause, l'instrument fusionne une section avec son tableau |
| M1, le prénom des personas | R5:197 | **ouvert** — le « décoratif » n'est aucune des quatre parts |
| `plan-mode.md`, 504 mots, 0 dépassement | R7:257 | **ouvert** — « sous l'alerte, mais quatrième part présente » n'a pas de ligne |
| R16, 432 mots dans une référence non chargée | R8:282 | **ouvert** — la table rend « extraire la quatrième part », or elle **est** à sa destination |
| la médiane bouge avec le corpus, 32 → 36 en dix jours | R7:310 | défaut d'instrument ouvert : l'alerte se desserre exactement quand il faudrait qu'elle serre |

### C8 — 6 verdicts, les 6 ouverts

| Verdict | Source | Pourquoi hors table |
|---|---|---|
| le prénom dans 5 corps sur 9 | R5:237 | l'incohérence ne vit dans **aucun** fichier, elle vit entre les fichiers d'un même moule |
| la sortie en `references/` faite par 8 sur 9 | R5:237 | même cause |
| un `## Test` qui promet plus que son `evals/` | R5:241 | C3 valide la présence du fichier, C8 ne compare pas un fichier à son voisin |
| l'annexe ne fonde que 3 blocs sur 19 | R3:148 | un couple peut être cohérent au vert en laissant 16 instructions sans preuve |
| l'instruction 18, orpheline mais **gardée** | R7:60 | la table rend « déplacer vers son vrai foyer ». Le verdict est « garder », parce que ce foyer n'est pas chargé |
| l'articulation implicite R15 / R17 | R8:224 | ni contradiction, ni redondance, ni orpheline, ni annexe fautive. Une articulation vraie mais tue |
| *(hors compte)* le conflit mermaid | R7:208 | deux sources **extérieures** au fichier, quand C8 se rend par fichier |

---

## Q2 — le signal d'auto-disqualification, et pourquoi il désigne le mauvais critère

La grille pose en C5 (`grille-harnais.md:150`) qu'« un critère qui envoie trois fois de suite ses
verdicts hors de sa propre table ne mesure pas ce qu'il prétend mesurer ».

### Le compte de C5 n'est pas à jour

Le rapport du 2026-08-25 écrit « **Troisième passe consécutive** à rendre son verdict principal hors
de la table de C5 » (R8:281). Deux faits le contredisent.

- **La série n'est pas consécutive.** Entre les passes hors table (R3, R4, plus le cas `workflow.md`)
  et R8, la passe du 2026-08-21 s'intercale et rend ses trois verdicts C5 **en table**. Deux d'entre
  eux, sur `autorite-des-conventions.md` et `plan-mode.md`, n'étaient possibles que grâce au patch —
  R7:79 le dit mot pour mot, « c'est le premier verdict que la révision du jour rend possible ».
- **Le compte additionne les deux côtés d'un patch.** La grille comptait déjà trois occurrences
  avant `b18acea`. R8 reprend cette phrase et se compte comme la troisième, ce qui mélange des
  verdicts rendus contre une table à deux lignes avec un verdict rendu contre une table à trois.

**Le trou de R8 reste réel et il est neuf** : ses quatre verdicts portent sur le **niveau** d'une
instruction dans un corps de skill, quand les trois lignes de C5 parlent toutes de portée.

### Le signal lui-même n'est pas mesurable en l'état

« Trois fois de suite » suppose un ordre de passes qui n'existe pas. R3 et R4 tournent le même jour
en sessions parallèles, R6 est une annexe de mesure sans cascade, et une passe qui ne rend aucun
verdict sur un critère n'est ni un succès ni un échec de ce critère. Le signal partage donc le défaut
qu'il prétend détecter, une grandeur sans convention écrite.

**À la place, la convention retenue ici** : compter les **passes distinctes ayant rendu au moins un
verdict encore ouvert aujourd'hui**, et à côté, le nombre de patchs déjà consommés.

| Critère | Passes concernées | Verdicts ouverts | Patchs déjà appliqués | Verdict |
|---|---|---|---|---|
| **C8** | 4 (R3, R5, R7, R8) | 6 | **0** | **disqualifié** |
| **C2** | 3 (R2, R4, R8) | 9 | **0** | **disqualifié** |
| **C1b** | 2 (R7, R8) | 9 | 0 | en alerte, et son test n'a jamais tourné |
| C7 | 3 (R5, R7, R8) | 3 | 1 | en alerte |
| C1a | 2 (R3, R5) | 3 | 0 | en alerte, et son test est structurellement approximé |
| C5 | 1 (R8) | 4 | **2** | **non disqualifié** — le patch a tenu, le trou restant est un axe neuf |
| C3 | 2 (R6, R8) | 2 | 1 | sain |
| C6 | — | — | — | ne rend aucun verdict, voir Q3 |

**C8 est le critère disqualifié par le signal de la grille, pas C5.** Il porte six trous ouverts sur
quatre passes, aucun n'a jamais été patché, et les six ont la même cause : sa portée s'arrête au
fichier.

---

## Q3 — chaque critère contre son alternative la plus simple

Chacun est jugé isolément. « C'est cohérent avec le reste de la grille » n'entre pas comme argument.

| Critère | Alternative testée | Verdict | Le fait qui tranche |
|---|---|---|---|
| **C1a** | fusionner dans un axe d'origine | **fusionner** | son sondage est joué 2 fois sur 8, et les 2 fois marqué approximé pour une raison structurelle qu'aucune passe ne peut lever (R1:32) |
| **C1b** | fusionner, même axe | **fusionner** | son A/B n'a **jamais** tourné, 0 fois sur 8. Il se tranche toujours par la doc, donc c'est un contrôle documentaire déguisé en critère de jugement |
| **C2** | supprimer, laisser C3 le couvrir | **garder**, comme valeur d'un axe de placement | il disqualifie réellement : 2 verdicts en 2026-08-10, 5 en 2026-08-11. C3 ne les aurait pas rendus, il juge la falsifiabilité d'une prose qui reste |
| **C3** | remplacer par un contrôle mécanique | **garder**, et le sortir de la cascade | c'est le seul critère mécanisable de bout en bout (`ls evals/`, comptage des cas négatifs). Il n'a pas sa place dans une cascade qui juge la présence |
| **C4** | garder tel quel | **fusionner avec C1b** | les deux posent la même question, « ce que porte l'instruction existe-t-il déjà ailleurs », et diffèrent seulement par l'ailleurs — le modèle, le harnais, ou un fichier. Séparés, ils laissent le natif dans un angle mort que ni l'un ni l'autre n'instrumente |
| **C5** | garder, avec une quatrième ligne | **remplacer par un axe de placement** | ses trois lignes ne sont pas trois cas, ce sont trois **destinations**. Un axe les porte toutes, plus celle qui manque, sans qu'une quatrième ligne soit à ajouter à chaque passe |
| **C6** | garder comme critère de cascade | **sortir de la cascade, garder le relevé** | **1 081 mots, le critère le plus lourd de la grille, et zéro instruction disqualifiée en 8 passes.** Ses deux verdicts de dépassement (R2:177, R7:264) ont tous deux été annulés par arbitrage humain, et il ne compare plus à une cible depuis le 2026-08-21 |
| **C7** | garder comme critère | **dégrader en relevé** | il ne juge jamais la présence, seulement la formulation, ce que la grille dit déjà. Et son alerte se desserre quand le corpus grossit (32 → 36 en dix jours), donc elle relâche exactement quand il faudrait qu'elle serre |
| **C8** | garder tel quel | **garder et élargir au groupe** | il porte 6 des trous ouverts, et les 6 ont la même cause. Le supprimer coûterait les défauts qu'aucun verdict par instruction ne voit, ce qui est sa raison d'être |

**Les quatre propositions du rapport du 2026-08-25 sont entrées ici comme candidates, pas comme
acquis.** Trois sont absorbées par la refonte (la case de niveau devient une valeur de l'axe B, le
dépassement à sa bonne place disparaît avec la dégradation de C7 en relevé, le calibrage d'une règle
de jugement entre dans le contrôle de testabilité). La quatrième, remesurer la médiane par corpus,
est déjà figée dans `axes-protocole.md` et reste telle quelle.

---

## Q4 — les trous, tous issus de Q1

Aucun n'est inventé. Chacun est ce qu'une passe a dû trancher hors table.

| # | Trou | Occurrences qui le fondent | Poids |
|---|---|---|---|
| T1 | **le verdict « réduire à l'increment »** n'existe nulle part | 9 (C1b), plus 3 des 9 de C2 | le plus fréquent des cinq |
| T2 | **le niveau** d'une instruction dans un corps de skill | 4 (C5, R8) | axe neuf, jamais patché |
| T3 | **le défaut de groupe**, qui ne vit dans aucun fichier | 2 (C8, R5) | invisible à C4 comme à C8 |
| T4 | **la couverture d'une annexe**, et le `## Test` qui promet plus que son éval | 2 (C8, R3 et R5) | un couple peut être vert en laissant 16 instructions sans preuve |
| T5 | **le doublon à fonctions distinctes** | 1 (C4, R5) | le seul verdict du corpus **réfuté par une mesure externe** |

---

## Q5 — les quatre candidates

Notées de 1 à 5. **Validité** : le critère attrape-t-il ce que les rapports ont attrapé, et rend-il
ses verdicts dans sa propre table. **Robustesse** : deux passes lisant la même grille rendent-elles
le même verdict.

| | **A** — les 8 patchés | **B** — minimale à 3 | **C** — deux axes | **D** — les 8 moins C6 |
|---|---|---|---|---|
| Critères | 8 | 3 | **4** | 7 |
| Mots (estimation) | ~9 800 | ~3 000 | **~2 500** | ~8 200 |
| Conventions à figer à côté | 3 | 3 | 3 | 3 |
| Trous refermés sur 5 | 5 | 3 | **5** | 3 |
| **Validité** | 5 | 3 | **5** | 4 |
| **Robustesse** | 2 | 4 | **4** | 3 |

**A — les 8 patchés.** Elle referme tout, par construction, et c'est sa faiblesse : c'est cette
grille qui a produit les 36 verdicts hors table. Chaque patch ajoute une ligne à une table sans
jamais réduire ce qu'il faut figer à côté d'elle, et `axes-protocole.md` existe précisément parce
que la grille ne suffisait pas. Robustesse basse aussi parce que huit critères à tables multiples
laissent le lecteur choisir sa ligne, défaut que R5:239 nomme déjà sur C7.

**B — minimale à 3.** Fusionne C1b avec C4, C2 avec C3, C5 avec C7, et sort C6 et C8. Elle est la
plus courte et la plus simple à tenir, mais elle **perd C1a** : « déjà porté ailleurs » ne couvre pas
« reconstructible du code », qui est une autre question. Le verdict de R2 sur `commit-convention.md`
disparaît sous cette candidate, et c'est un verdict qui a produit une vraie réduction.

**C — deux axes, deux contrôles, deux relevés.** Retenue. Détail ci-dessous.

**D — les 8 moins C6, plus le verdict ternaire.** Le patch minimal à fort rendement, et il reste
défendable : il conserve la nomenclature C1 à C8 à laquelle les huit rapports se réfèrent par leur
nom. Il referme T1 par le ternaire, mais laisse T2, T3 et T5 ouverts, puisque ce sont des défauts de
**forme** de la grille et non des lignes manquantes.

---

## La grille retenue — deux axes, deux contrôles, deux relevés

### La forme cascade est abandonnée, et ce n'est pas un pari

Elle n'est **déjà plus appliquée**. Les passes rendent des verdicts multi-critères sur une même
instruction, quand la cascade prescrit de sortir au premier critère disqualifiant :

- « **C5 + C4** » sur S13 (R8:68) ;
- « survit, C7 alerte, défaut C1, sort en C2 » sur `aidd-pilot` (R4:89), soit quatre critères ;
- « sort en C1b / C4 » sur `style.md` #3 (R7:149) ;
- « sort en C1+C2 » sur CC1 (R2:98).

Un profil multi-axes décrit donc ce que les passes font réellement, là où la cascade décrit ce
qu'elles étaient censées faire.

### Axe A — d'où vient ce que l'instruction porte ?

Une seule valeur, testée dans cet ordre.

| Valeur | Test | Absorbe |
|---|---|---|
| natif du modèle | la page de prompting du modèle courant le nomme | C1b |
| natif du harnais | le system prompt de l'outil le porte. Énumération à la main, aucun grep ne l'atteint | C1b, C4 |
| ailleurs dans le harnais | grep du motif, **puis** énumération des instructions à même effet | C4 |
| reconstructible du repo | sondage, compté en appels d'outil | C1a |
| nulle part | aucune des quatre | — |

### Axe B — à quel moment doit-elle être chargée ?

Une seule valeur. C'est un axe de **placement**, pas de portée, et c'est ce qui referme T2.

| Valeur | Test | Absorbe |
|---|---|---|
| un garde déterministe | l'invariant porte sur un artefact versionné ou un appel d'outil observable. Le mécanisme peut être un hook, un lint, ou un champ de frontmatter comme `disable-model-invocation` | C2, et son trou de mécanisme |
| le permanent | déclencheur à chaque session, ou re-dérivation à ≥ 3 appels | C5 lignes 1-2, dosage de C1 |
| une couche chargée à la demande | déclencheur événementiel, ou niveau — référence, corps de skill, action | C5 ligne 3, **et T2** |
| nulle part | l'axe A la donne déjà portée **au même moment de chargement** | — |

### Le verdict est ternaire, et il se lit du croisement

**Garder tel quel**, **réduire à l'increment que l'axe A ne couvre pas**, ou **sortir**. Le terme du
milieu referme T1, que 9 verdicts ont réclamé sans jamais l'obtenir.

**Le croisement referme T5.** Deux instructions de même contenu mais d'axe B différent ne sont pas
des copies. Le mécanisme couvre aussi la couverture partielle par un linter, cas B1 et F2 de R2 : le
garde prend ce qu'il peut observer, la prose garde l'increment de jugement.

### Contrôle 1 — testabilité

Rendu hors matrice. L'instruction porte-t-elle sa commande de vérification, son cas d'éval, ou son
calibrage ? Absorbe C3, plus les deux trous encore ouverts : une éval qui ne discrimine pas le modèle
nu ne compte pas, et le calibrage d'une **règle de jugement** est un objet testable à part entière.

### Contrôle 2 — cohérence

Rendu par fichier, par couple, **et par groupe**. Le troisième niveau referme T3, et la couverture de
l'annexe entre dans le deuxième, ce qui referme T4.

### Deux relevés, sans aucun verdict

- **Poids** — la somme du permanent, sa trajectoire depuis la passe précédente, ses contributeurs.
  C6 réduit à ce qu'il fait déjà réellement depuis le 2026-08-21.
- **Formulation** — l'alerte à 2× la médiane du corpus courant, remesurée par passe. Elle déclenche
  une relecture, elle ne rend pas de verdict. C7 sort du crible et ne fabrique plus de dépassements
  qui n'en sont pas.

---

## Q6 — le rejeu des verdicts existants

C'est le seul instrument de ce cadrage qui vienne de dehors : les verdicts sont écrits et immuables,
une candidate ne peut pas les arranger.

| Verdict témoin | Source | A | B | C | D |
|---|---|---|---|---|---|
| **M3, la liste de frères** — *contrôle négatif, la coupe dégrade 7/9 → 5/9* | R5:235, R6:99 | couper (**faux**) | couper (**faux**) | **garder les deux** | couper (**faux**) |
| S9, S10, S11, S13, « mauvais niveau » | R8:64 | table C5 patchée | critère 3 | **axe B** | hors table |
| `style.md` #3, doublon partiel du natif | R7:149 | ligne à ajouter | verdict du critère 1 | **ternaire** | **ternaire** |
| `vault-save`, `disable-model-invocation` | R4:82 | ligne C2 à ajouter | critère 2 | **axe B** | ligne C2 à ajouter |
| CC1, `commit-convention.md`, 11 appels | R2:98 | C1a | **perdu** | **axe A** | C1a |
| le prénom dans 5 corps sur 9 | R5:237 | ligne C8 à ajouter | **perdu** | **contrôle 2** | hors table |
| R16, 432 mots à sa bonne place | R8:282 | ligne C7 à ajouter | critère 3 | **relevé, pas de verdict** | ligne C7 |
| 3 évals qui ne discriminent rien | R6:114 | ligne C3 à ajouter | critère 2 | **contrôle 1** | ligne C3 |
| `plan-mode.md`, sous l'alerte, 4e part présente | R7:257 | ligne C7 à ajouter | critère 3 | **relevé** | ligne C7 |
| `ponctuation.md`, global par nature | R7:214 | C5 ligne 2 | critère 3 | **axe B, permanent** | C5 ligne 2 |

**Ce qui apparaît sous C** : un verdict explicite sur le moment de chargement pour chaque
instruction, là où la grille actuelle ne le demande qu'aux instructions qui déclenchent C5.

**Ce qui disparaît sous C** : les verdicts de dépassement C6, déjà éteints par décision humaine, et
les alertes C7 rendues comme des défauts alors qu'elles sont des déclencheurs de relecture.

**Ce qui survit inchangé** : les 5 sorties sèches de R8, les 2 sorties C2 de R2, les verdicts de
suppression pour doublon plein. La refonte ne renverse **aucun** verdict rendu, à une exception près,
M3, qu'une mesure avait déjà établi comme faux.

---

## Ce que ce cadrage ne tranche pas

- **Le coût d'un critère et le verdict « overkill »**, qui demandent un modèle de coût. Ils
  appartiennent au prompt suivant.
- **⚠️ supposé** : validité et robustesse pèsent également. Si la robustesse prime, B remonte au
  niveau de C. Si la validité prime, C et A se départagent sur le nombre de mots seul.
- **⚠️ supposé** : le domaine reste `agent-config`. Les axes sont censés valoir aussi pour le vault
  et les projets, mais aucune passe ne les y a jamais exercés.
- **La perte de nomenclature.** Les huit rapports citent C1 à C8 par leur nom. La grille cible doit
  porter une table de correspondance, sinon les verdicts existants deviennent illisibles.
- **Le skill `audit-harnais` ne tourne plus contre cette grille, et il ne s'agit pas d'une
  modernisation à faire plus tard.** Mesuré après la réécriture : **53 citations** de critères `CX`
  dans ses quatre fichiers, dont 38 dans la seule action `02-cribler`, et **11 instructions
  dépendent de la forme cascade** (« dérouler C1→C5 dans l'ordre et sortir au premier critère
  disqualifiant », « C6 ne se juge pas ici », « Recouper C8 »). Lancer une passe en l'état
  produirait des verdicts contre des critères qui n'existent plus. La refonte du skill est donc un
  **prérequis à la prochaine passe**, pas un chantier parallèle.
