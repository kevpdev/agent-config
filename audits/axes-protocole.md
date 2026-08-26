# Axes d'amélioration du protocole d'audit

Registre vivant, alimenté par chaque passe du skill `audit-harnais`, jamais par une session ordinaire. Il porte deux choses de nature différente : les **conventions déjà figées**, qu'une passe lit et applique sans les rouvrir, et les **axes observés**, qui attendent une porte avant d'être appliqués.

Compagnon de `grille-harnais.md`, sur le modèle de `banc-pratiques.md`. La grille dit ce qu'un audit mesure, ce fichier dit ce que les audits ont appris de leur propre instrument.

## Comment il s'utilise

| Étage | Qui | Quand |
| --- | --- | --- |
| capturer | la passe qui observe | à sa clôture, en ajout, sans rien décider |
| compter | la passe suivante, qui lit ce fichier | mécanique, un comptage d'occurrences |
| appliquer | l'humain, via `skill-craft:02-validate` | hors passe, quand la porte est franchie |

**Aucune passe n'applique un axe qu'elle vient d'observer**, et aucune action n'appelle `skill-craft` toute seule.

**POURQUOI, et ce n'est pas une question de coût** : `rules/reasoning.md` pose qu'une mesure vient de dehors, avec Huang et al. 2023 en appui — l'auto-correction sans retour externe dégrade le raisonnement au lieu de l'améliorer. Une passe qui corrige le protocole avec lequel elle vient de juger n'a aucun bras de contrôle. C'est la même règle que la grille s'applique déjà à elle-même, « elle se révise **entre** deux audits, jamais pendant ».

## La porte — un comptage, pas une appréciation

Un axe s'applique quand **l'une** des deux conditions tient :

- il a été observé dans **deux passes indépendantes**, qui ne se sont pas lues l'une l'autre ;
- une mesure **hors de l'audit** le confirme, par la doc d'un outil, du code, ou le refus d'un garde.

En dessous, l'axe reste `ouvert` et rien ne bouge.

**POURQUOI ce seuil et pas un jugement de pertinence** : une observation isolée est une anecdote, et un modèle en produit à chaque passe. La même observation par deux passes qui ne se sont pas parlé est un défaut structurel.

*La grille portait un signal voisin, « trois fois de suite hors de sa propre table ». Le cadrage du 2026-08-26 l'a mesuré inapplicable, « de suite » supposant un ordre de passes qui n'existe pas — deux passes ont tourné le même jour en parallèle, et une annexe ne rend aucune cascade. La formulation retenue est celle de ce fichier, deux passes **indépendantes**. Le renvoi s'inverse donc : c'est cette porte qui fait foi, et la grille ne porte plus l'autre.*

**Purge** : un axe encore seul après **trois** passes se ferme en `fermé, anecdote`. Sans cette ligne le registre grossit, et un registre que plus personne ne lit ne vaut pas mieux que rien.

---

## Conventions figées

Ce qu'une passe applique **sans le rouvrir**, et sans le réinventer. Une convention entre ici quand une passe a dû la trancher faute de réponse dans le protocole.

### Découpage d'un fichier en instructions

Figée par la passe `skills/` C1 du 2026-08-25 (corps de `doc-sync`). Quatre cas que `01-cadrer` ne tranche pas.

| Cas | Convention |
| --- | --- |
| étape `## Process` numérotée | une instruction, ses sous-puces *Pourquoi* comprises |
| sous-puce portant un impératif autonome | compte à part — c'est le cas « dépassement porté par l'impératif » du relevé de formulation |
| bloc `## Input` ou `## Output` | ne compte que s'il porte un impératif, sinon c'est un contrat de données jugé au contrôle de cohérence |
| ligne de `## Test` | **pas** une instruction : c'est la commande de vérification de l'instruction correspondante, jugée avec elle au contrôle de testabilité. Un test orphelin est un constat de cohérence |
| puce d'une section normative d'un routeur | une instruction |

**POURQUOI la figer plutôt que la redécider** : la grille a mesuré que « nombre d'obligations » n'est pas une grandeur sans convention écrite, trois valeurs annoncées en un jour sur le même fichier. « Nombre d'instructions » a le même défaut. Deux passes aux conventions différentes rendent des comptages qui ne se comparent pas, et personne ne le voit puisque les deux sont des entiers.

### Seuil d'alerte du relevé de formulation

Il se remesure par corpus **et à chaque passe**, il ne s'hérite jamais. Ce tableau est le
**seul foyer** de ces chiffres : la grille y renvoie sans les recopier.

| Corpus | Médiane | Alerte | Mesurée le |
| --- | --- | --- | --- |
| couche `rules/` | 32 | 60 | 2026-08-10 |
| couche `rules/` | **36** | **72** | 2026-08-21 |
| descriptions de skills | 86 | 130 | 2026-08-11 |
| corps de skill | 34,5 | 69 | 2026-08-25 |

**La médiane d'un même corpus a bougé de 32 à 36 en dix jours**, donc l'alerte qui en dérive se
desserre exactement quand le corpus grossit. Une passe lit la ligne la plus récente de son corpus, et
la remesure de toute façon.

*La ligne du 2026-08-21 manquait à ce registre, créé quatre jours plus tard sans reprendre la mesure
de la passe précédente. Transcription réparée le 2026-08-26, aucune mesure neuve.*

---

## Axes observés

Statuts : `ouvert` (une occurrence, en attente) · `mûr` (porte franchie, applicable) · `appliqué` (avec sa date) · `fermé, anecdote` (seul après trois passes).

**P1 à P6 ont été observés contre le protocole d'avant la refonte du 2026-08-26**, quand `02-cribler` déroulait une cascade de huit critères. Leur texte n'est pas retouché, une observation datée ne se réécrit pas. Mais les trois axes encore ouverts se rejugent contre le protocole **refondu**, jamais contre celui qu'ils décrivent.

| # | Axe | Où ça se répare | Occurrences | Statut |
| --- | --- | --- | --- | --- |
| P1 | rien ne dit ce qu'il advient d'une mesure qui contredit une entrée que le contrat déclare acquise. La catégorie « acquis » est absente du protocole, et deux passes l'ont inventée sans le savoir | `01-cadrer` étape 2, une catégorie **« acquis »** à côté des exclusions | 2 — passe A du 2026-08-11, passe C1 du 2026-08-25 | **appliqué le 2026-08-25** |
| P2 | la convention de découpage doit être inventée à chaque passe, donc deux comptages d'instructions ne se comparent pas | résolu par ce registre, section « Conventions figées ». Aucun édit du protocole | 2 — passe C1 du 2026-08-25, plus le même défaut déjà mesuré par la grille sur « nombre d'obligations » | **appliqué le 2026-08-25** |
| P3 | le geste de capture arrive à l'étape 8 de `02-cribler` quand son déclencheur tombe aux étapes 1 et 4. Rien entre les deux ne dit que le contrat borne ce que la cascade peut juger, et « autorité de C1b » pousse à lire la doc comme un verdict | `02-cribler` étape 5, une ligne posant qu'une mesure contredisant un acquis produit une capture | 1 — passe C1 du 2026-08-25 | ouvert — **peut-être déjà couvert** : la définition de l'acquis posée par P1 porte son effet et renvoie à l'étape 8. À constater par la passe suivante, qui dira si le renvoi suffit. *Non fermé par la passe qui a écrit le correctif : juger l'effet de son propre édit n'est pas une mesure.* |
| P4 | l'étape « Batcher » ne demande pas de calibrer l'instrument avant de lire son résultat. Huit greps ont rendu zéro sur une cible inexistante, et le zéro a d'abord été lu comme une absence de doublon | `02-cribler` étape 2 | 3, **toutes de la même passe** — greps C4, vérification du travail d'un sous-agent, puis comptage de FAIL du lint avec un `grep -A30` qui débordait sur le skill suivant | ouvert — la porte demande deux passes **indépendantes**, et trois occurrences d'une même session n'en font pas deux. *À vérifier en priorité par la passe suivante : trois fois la même cause en une passe est le signal le plus fort du registre.* |
| P5 | un verdict sur un **instrument** a été rendu sur la forme de son message, sans lire son code. Un FAIL du lint a été déclaré « faux positif » à tort | couvert par P4 s'il est appliqué — le calibrage impose de lire l'instrument. Pas d'édit propre, ce serait le doublon que la grille sanctionne | 1 — passe C1 du 2026-08-25 | ouvert |
| P6 | `03-consolider` réserve `## À réviser entre deux audits` aux propositions touchant la **grille**. Une proposition touchant le **protocole** n'a aucune place, et la passe C1 a dû inventer une sous-section | `03-consolider`, cinquième intitulé imposé | 1 — passe C1 du 2026-08-25 | **appliqué le 2026-08-25** |

---

## Ce que ce fichier ne fait pas

- Il ne contient **aucun verdict d'audit**. Les verdicts vivent dans les rapports horodatés, immuables.
- Il ne révise **pas** la grille. Une proposition touchant la grille reste dans la section dédiée du rapport de passe, et se décide entre deux audits.
- Il ne se lit **pas** en session ordinaire. Seule une passe d'audit l'ouvre.
