# Audit du harnais — passe `rules/` du 2026-08-21

**Grille** : commit `a945687`, arbre de travail **propre** au lancement et à la clôture (`git diff -- audits/grille-harnais.md` vide).
**Modèle de la passe** : Claude Opus 5 (`claude-opus-5[1m]`). Page de prompting fetchée le **2026-08-21**, plus la page « Prompting best practices » et « Effective context engineering » le même jour. Sans ces dates, aucun verdict C1b n'est relisable.
**Instrument C7** : médiane remesurée à **36 mots/bloc** sur 13 fichiers, donc alerte à **72 mots**. Les passes précédentes tournaient à 60, dérivé d'une médiane de 32.

## Contrat

Les critères C1 à C8 de la grille, sur les **13 fichiers non scopés** de `rules/` et `wrappers/claude/rules/`, plus l'output style actif. Rien d'autre. Une découverte hors grille se capture en une ligne sans se creuser.

**Exclus** : `rules/back-spring.md` et `rules/front-react.md`, qui portent un frontmatter `paths:` et sortent du périmètre C6 (mesuré : `grep -l '^paths:' rules/*.md`). Leur cascade appartient à une passe « règles scopées ». La grille elle-même, qu'un audit ne touche pas pendant qu'il court.

**Découpage** : 121 instructions. Compté fichier par fichier, jamais repris d'un rapport antérieur.

**État d'entrée, remesuré** : **5 547 mots** de règles + output style, contre une cible de ~3 950. Le rapport du 2026-08-11 laissait la couche à 3 134, donc elle a regagné **2 413 mots (+77 %)**. Les descriptions de skills passent de 2 206 sur 26 skills à **2 597 sur 29**. Permanent réel : **8 144 mots**.

| Fichier | Mots | Delta depuis le 2026-08-11 |
|---|---|---|
| `reasoning.md` | 922 | 841 → 922 (dont +97 de la passe du jour, commit `04ff86c`) |
| `autorite-des-conventions.md` | 879 | **créé depuis, et non commité dans git** |
| `profil.md` | 642 | né du découpage de `style.md` par médium |
| `reponse.md` | 521 | idem |
| `plan-mode.md` | 504 | **99 → 504, soit +405** |
| `ai-principles.md` | 462 | inchangé |
| `ponctuation.md` | 351 | inchangé |
| `style.md` | 342 | découpé |
| `mermaid.md` | 205 | inchangé |
| `redaction.md` | 195 | découpé |
| `memory-policy.md` | 184 | inchangé |
| `commit-convention.md` | 137 | inchangé |
| `tooling.md` | 119 | inchangé |
| `chat-style.md` (output style) | 84 | inchangé |

## Cascade par instruction

Base : **mesuré** = commande ou citation de source à l'appui. **jugé sur pièce** = lecture du texte, sans sondage ni A/B. **supposé** = non vérifiable dans cette passe.

### `reasoning.md` — 23 instructions

| # | Instruction | Sortie | Action | Base |
|---|---|---|---|---|
| 1 | INTERDIT affirmer sans source | survit, C1b « contredit un défaut » | garder | mesuré |
| 2 | INTERDIT prémisse non mesurée | survit | garder | mesuré |
| 3 | mesurer d'abord, vérif la moins chère | survit | garder | mesuré |
| 4 | marquer supposé / doc-vérifié | survit | garder | jugé sur pièce |
| 5 | tester empiriquement si non documenté | survit | garder | jugé sur pièce |
| 6 | une mesure vient de dehors | survit | garder | mesuré |
| 7 | SEUIL AU COÛT | survit | garder | mesuré |
| 8 | ce que le seuil ne demande pas | survit | garder | mesuré |
| 9 | pointeur ref-reasoning (14/12/757) | survit, C5 3e ligne | garder | mesuré |
| 10 | TRIGGER comptage | survit, C5 3e ligne | garder | mesuré |
| 11–17 | contrat de questions (7 instructions) | survivent | garder | jugé sur pièce |
| 18–19 | méta-règle du pourquoi + FORME | survivent | garder | mesuré |
| 20–23 | Cartesian check (4 instructions) | survivent | garder | mesuré |

**C1b tranché par la doc** : la page Opus 5 prescrit de retirer la re-vérification de sa **propre sortie**, jamais le **grounding**. Citation : « *Claude Opus 5 verifies its own work without being told to. If your prompt contains explicit verification instructions […] remove them* ». Les instructions 1 à 5 ne font que du grounding, et la page « Prompting best practices » publie ce prompt-là comme recommandé : « *Never speculate about code you have not opened […] Never make any claims about code before investigating* ». Aucune ne sort en C1b.

**C7** : l'instrument signale 107 mots sur le bloc `**INTERDIT**`. C'est un artefact d'unité de mesure : il empile les instructions 1 et 2, qui pèsent ~55 et ~50 séparément, donc sous l'alerte. Aucun vrai dépassement.

**C8** : cohérent. Une réserve, l'instruction 18 (méta-règle du pourquoi) est **orpheline** au sens de C8, puisqu'elle prescrit comment écrire une règle et non comment raisonner. Son foyer naturel serait `redaction.md` ou `skill-craft`. **Gardée quand même** : `skill-craft` ne se charge qu'à l'invocation, et « c'est déjà écrit ailleurs » n'est une raison de supprimer que si cet ailleurs est chargé (C5 de la grille). Le déplacement vers `redaction.md` reste ouvert et ne change pas le poids.

### `autorite-des-conventions.md` — 14 instructions

| # | Instruction | Sortie | Action | Base |
|---|---|---|---|---|
| 1 | DÉCLENCHEUR deux sources divergentes | survit | garder | jugé sur pièce |
| 2 | ne jamais demander laquelle suivre | survit, C1b « contredit un défaut » | garder | mesuré |
| 3 | POURQUOI, run du 2026-08-19 | survit C1–C5, **C7 à 75** | extraire la preuve | mesuré |
| 4–5 | la coupe forme/fond + LE TEST | survivent, **C7 à 79** | extraire l'exemple | mesuré |
| 6 | à la place du ressenti, cas front-react | survit, **C7 à 91** | extraire la citation | mesuré |
| 7 | POURQUOI la coupe passe avant | survit | garder | jugé sur pièce |
| 8 | la hiérarchie 0 à 4 | survit, **C7 à 143** | découper, la preuve sort | mesuré |
| 9 | POURQUOI le repo devant le harnais | survit | garder | jugé sur pièce |
| 10 | le niveau 0, cas Winggy/guard | survit, compris dans les 143 | extraire | mesuré |
| 11 | le niveau 4 se pose quelque part | survit | garder | jugé sur pièce |
| 12–13 | la portée + son pourquoi | survivent, **C7 à 98** | extraire | mesuré |
| 14 | ce que l'inversion ne touche pas | survit | garder | jugé sur pièce |

**C5 sous le nouveau dosage** (grille `a945687`) : re-dériver cette hiérarchie demande de lire les conventions du repo, les règles du harnais et de compter la forme dominante, donc **bien plus de 3 appels d'outil**. Le déclencheur tombe à chaque session de développement. Deuxième ligne du dosage : **garder au permanent**. C'est le premier verdict que la révision du jour rend possible ; avant elle, cette instruction n'avait aucune case.

**C7, le verdict lourd de la passe** : **5 blocs sur 14 dépassent l'alerte, pour 486 des 879 mots du fichier**. Le dépassement est porté par la quatrième part à chaque fois, le cas vécu et sa citation : le run du 2026-08-19, la citation de `front-react.md`, le couple `vcs.md`/`guard-no-claude-in-commit.sh` de Winggy, les globs de `back-spring.md`. Action prescrite par la grille : **extraire vers `rules/references/ref-autorite-des-conventions.md`**, l'instruction gardant impératif, pourquoi en une ligne et trigger. Gain estimé **~350 mots**, à remesurer après coupe.

**C8** : cohérent, avec un **trou nommé**. La hiérarchie couvre le garde déterministe, le repo, mon harnais, la forme dominante et mon arbitrage. Elle ne porte **aucun niveau pour le défaut d'un framework installé**, or c'est exactement le cas du conflit mermaid ci-dessous. Versé à réviser.

**Hors cascade, hygiène** : le fichier **n'est dans aucun commit** (`git status` le donne en `??`). Il se charge pourtant, `sync-rules.sh` comptant ses 15 liens. Un `rm` du dossier le perdrait sans trace.

### `profil.md` — 12 instructions

| # | Instruction | Sortie | Action | Base |
|---|---|---|---|---|
| 1 | niveau technique + conséquence | survit | garder | jugé sur pièce |
| 2–4 | contraintes cognitives + pourquoi | survivent | garder | jugé sur pièce |
| 5 | mode de compréhension | survit | garder | jugé sur pièce |
| 6–7 | parler comme à un collègue, les 3 tics | survivent, **C7 à 121** | extraire les paires | mesuré |
| 8–9 | DÉCLENCHEUR compte rendu + lecture à froid | survivent, **C7 à 178** | extraire la table | mesuré |
| 10 | MESURE mesure-reponses.py | survit | garder | mesuré |
| 11 | les 4 puces de voix | survit | garder | jugé sur pièce |
| 12 | rapport à la progression | survit | garder | jugé sur pièce |

**C1a** : le profil de l'opérateur est la définition même du non-inférable. Aucun contexte neuf ne devine la contrainte de mémoire de travail ni le registre attendu. Survit sans discussion.

**C7** : 2 blocs sur 12 dépassent, 299 mots. Le fichier déclare déjà une annexe (`ref-style.md`, « autres paires »), donc l'extraction a un foyer existant. Gain estimé **~80 mots**.

**C1b, cas aligné à signaler** : la page Opus 5 dit « *Positive examples of the communication style you want tend to be more effective than instructions about what not to do* ». Ce fichier porte déjà des paires ❌/✅ et une table de substitution, donc il est du bon côté de la prescription. Rien à corriger.

**C8** : cohérent.

### `reponse.md` — 12 instructions

| # | Instruction | Sortie | Action | Base |
|---|---|---|---|---|
| 1 | dernière ligne = question d'action | survit | garder | jugé sur pièce |
| 2 | référence rappelée en trois mots | survit, **C7 à 111** | comprimer, garder le pourquoi | mesuré |
| 3 | une ancre visuelle par bloc | survit | garder | jugé sur pièce |
| 4 | tableau dès 2 options | survit | garder | jugé sur pièce |
| 5–8 | couper à la reco, ses 2 pourquoi, hors périmètre, mesure | survivent, **C7 à 185, RED FLAG** | réécrire | mesuré |
| 9 | les cinq phases | survit | garder | jugé sur pièce |
| 10–11 | ré-ancrage + sa forme | survivent | garder | jugé sur pièce |
| 12 | POURQUOI global et non output style | survit | garder | mesuré |

**C7, RED FLAG de la grille** : sur le bloc « Couper à la reco », l'impératif fait ~25 mots quand les deux POURQUOI, le hors-périmètre et la MESURE en font ~160. La grille prescrit « l'instruction argumente plus qu'elle ne prescrit, réécrire avant de trancher ». Gain estimé **~90 mots**.

**C4** : le motif « une reco / catalogue » ne sort qu'une fois sur les 13 fichiers (`grep -nEi`), donc pas de doublon interne au repo. Le doublon est avec le system prompt natif, et il porte sur `style.md`, pas sur celui-ci — voir plus bas.

**C8** : cohérent. La règle 5 et la règle 1 se complètent au lieu de se recouvrir, l'une coupant le corps, l'autre imposant la clôture.

### `plan-mode.md` — 11 instructions

| # | Instruction | Sortie | Action | Base |
|---|---|---|---|---|
| 1–3 | appeler EnterPlanMode, ni bypass ni demande détaillée, pourquoi | survivent, C1b « contredit un défaut de l'outil » | garder | mesuré |
| 4–7 | dire la reco avant l'appel, ses 3 pourquoi, ce qui ne se rouvre pas | survivent | garder | mesuré |
| 8–11 | EXCEPTION skill AIDD, sa limite, ses 2 pourquoi | survivent | garder | mesuré |

**C1b, le cas le plus solide de la passe** : la description de l'outil affirme exiger le consentement de l'utilisateur, et le fichier mesure que l'invite n'apparaît pas, `settings.json` ne portant aucun bloc `permissions` qui la rétablirait. Une instruction qui contredit un défaut constaté de l'outil est le cœur non-inférable de C1b.

**C5 sous le nouveau dosage** : le déclencheur, « une analyse dont la conclusion appellera des edits », est nommé par la grille elle-même comme exemple d'événement. Mais il tombe dans la quasi-totalité de mes sessions de travail, et la re-dérivation coûte largement plus de 3 appels. Deuxième ligne du dosage, **garder au permanent**.

**C7** : **aucun bloc au-dessus de 72**. La formulation est donc conforme instruction par instruction, alors que le fichier pèse 504 mots. Le poids est un fait C6, pas un défaut C7. Voir la capture sur le trou de la table C7.

**C8** : cohérent, et remarquablement, puisque l'exception AIDD et la règle générale déclarent explicitement leur frontière (« ce que l'exception ne couvre pas »). C'est la forme que le conflit mermaid n'a pas.

### `style.md` — 7 instructions

| # | Instruction | Sortie | Action | Base |
|---|---|---|---|---|
| 1 | périmètre, toute production écrite | survit | garder | jugé sur pièce |
| 2 | un verdict concret d'abord | survit, **C7 à 75** | comprimer | mesuré |
| 3 | **une reco, pas un catalogue** | **sort en C1b / C4** | **supprimer, garder l'increment** | **mesuré** |
| 4 | ancrer sur du vérifiable | survit | garder | jugé sur pièce |
| 5 | les deux sens de « concret » | survit | garder | jugé sur pièce |
| 6 | densité | survit | garder | jugé sur pièce |
| 7 | marquer l'incertain | survit | garder | jugé sur pièce |

**Le seul verdict de suppression de la passe.** Le system prompt du harnais porte déjà les deux moitiés de l'instruction 3, dans son bloc « Context management » : « *Do not […] narrate options you will not pursue. If you are weighing a choice, give a recommendation, not an exhaustive survey* ». La règle dit « ne pas lister les options en laissant l'arbitrage au lecteur, ni énumérer des pistes qu'on ne suivra pas ». C'est le même geste, sur les deux moitiés.

**Base du verdict** : citation du system prompt tel qu'injecté dans la session du 2026-08-21. Aucun grep ne peut le confirmer, la grille nommant ce trou en C4 (« la couche la plus lourde du contexte permanent n'est dans aucun fichier du repo »).

**Ce qui survit à la suppression** : l'increment « trancher, puis donner le critère qui a fait pencher » et « l'alternative se mentionne en une ligne, seulement si elle reste défendable », ~20 mots que le natif ne porte pas, à fondre dans l'instruction 2. Gain net **~45 mots**.

**Précédent et réserve** : la suppression de l'instruction #2 de `reasoning.md` le 2026-08-11 a été décidée sur le même motif, en notant que le natif est « un texte non versionné, non differable, qui change à chaque release du harnais ». La même réserve vaut ici, et c'est l'argument **pour** supprimer plutôt que contre : garder une règle dont tout le contenu amende un texte non versionné produit un doublon volatil.

**C8** : cohérent. L'instruction 7 renvoie explicitement à `reasoning.md` au lieu de recopier, ce qui est le motif C4-propre.

### `ai-principles.md` — 13 instructions

| # | Instruction | Sortie | Action | Base |
|---|---|---|---|---|
| 1–3 | cadre, pourquoi ce fichier, note d'autorité | survivent | garder | jugé sur pièce |
| 4 | la méthodologie avant l'outil | survit | garder | jugé sur pièce |
| 5 | le déterministe encadre le probabiliste | survit | garder | jugé sur pièce |
| 6 | adapter le médium à l'intention | survit | garder | jugé sur pièce |
| 7 | **l'agent sert l'intention, pas la commande** | doublon partiel du natif | **réduire au titre** | mesuré |
| 8 | une limite d'outil révèle une représentation | survit | garder | jugé sur pièce |
| 9 | combiner plutôt que remplacer | survit | garder | jugé sur pièce |
| 10 | **on assume ce qu'on livre** | doublon partiel du natif | **réduire au titre** | mesuré |
| 11 | ne pas déléguer ce qu'on ne sait pas évaluer | survit | garder | jugé sur pièce |
| 12 | l'échec du modèle est un signal | survit | garder | jugé sur pièce |
| 13 | le résultat prime sur le volume | survit | garder | jugé sur pièce |

**C3, exception assumée par la grille** : ce fichier ne prescrit rien, donc il n'est pas falsifiable, mais il est le repli quand une règle concrète est muette. « Il se **réduit** (titres + une ligne de pourquoi), il ne se supprime pas. »

**Les deux doublons partiels** : le natif porte « *Interpret ambiguity the way a careful colleague would: make routine judgment calls yourself, and check in only when different readings of the request would lead to materially different work* », ce qui recouvre l'instruction 7. Et « *For actions that are hard to reverse or outward-facing, confirm first* » recouvre la moitié opérante de l'instruction 10. Les deux gardent leur titre et leur ligne de pourquoi, leur corps de trois phrases sort. Gain estimé **~60 mots**.

**C8** : cohérent, avec une note d'en-tête déjà corrigée par la grille (l'autorité est le repo, pas le vault).

### `mermaid.md` — 5 instructions

| # | Instruction | Sortie | Action | Base |
|---|---|---|---|---|
| 1 | périmètre, y compris sous-agent et skill | survit | garder | jugé sur pièce |
| 2 | **vertical par défaut `TD`/`TB`** | survit, **conflit C8 de couple** | **déclarer sa portée** | **mesuré** |
| 3 | zéro croisement de flèches | survit | garder | jugé sur pièce |
| 4 | charger `mermaid-craft`, ne pas sauter | survit, C5 3e ligne | garder | jugé sur pièce |
| 5 | POURQUOI ce découpage | survit | garder | jugé sur pièce |

**Le conflit, mesuré, et c'est la forme exacte du piège Cartesian check.** Deux défauts opposés mot pour mot :

- `rules/mermaid.md` : « **Vertical par défaut** (`TD`/`TB`) — horizontal (`LR`) seulement si le flux est court et intrinsèquement séquentiel. »
- `aidd-context/2.6.2/skills/09-mermaid/references/mermaid-conventions.md:8` : « *Flow direction defaults to `LR` unless the source implies another.* »

`mermaid.md` revendique l'autorité sur « tout diagramme Mermaid produit par toi, un sous-agent **ou un skill** », donc elle prétend déjà écraser le défaut du skill AIDD. Mais elle ne le **nomme pas**, et le skill énonce le sien dans sa propre référence. Un agent qui charge `09-mermaid` lit `LR` comme défaut sans jamais voir la contradiction.

**Pourquoi ma règle gagne sur le fond** : son POURQUOI porte un fait d'environnement indéduisible, « les pages et écrans de lecture sont en portrait ». Le défaut AIDD est génerique. Et par la coupe forme/fond d'`autorite-des-conventions.md`, l'orientation est de la **forme**, donc négociable, mais aucune source de niveau 1 ne la déclare ici.

**Action prescrite** : ajouter à l'instruction 2 la clause qui nomme le conflit, sur le modèle de l'exception Cartesian corrigée le même jour. Coût **~20 mots**, et c'est le seul ajout de la passe.

**C8 de couple** : la grille demande d'inclure l'annexe déclarée dans le verdict. `mermaid-craft` n'a pas été ouvert, la passe `skills/` en ayant la charge. Verdict rendu sur le couple `mermaid.md` + convention AIDD seulement, et dit tel quel.

### `ponctuation.md` — 6 instructions

Les 6 survivent, aucun bloc au-dessus de 72, base jugé sur pièce sauf l'instruction 1 (mesure du 2026-08-05) et l'instruction 5 (commande de comptage), mesurées.

**C5** : global par nature, et le fichier porte lui-même la démonstration. Son ancien `paths:` ne listait que des dossiers du vault, donc la règle était inerte en session de code, là où le défaut était le pire. Verdict « survit C5 », pas « non applicable ».

**Rejeu de l'instrument dans cette passe**, instrument calibré d'abord sur le contre-exemple de la règle (2 tirets, 1 point-virgule, l'instrument voit le positif) : **0,21 point-virgule et 1,06 tiret de prose pour 1 000 mots** sur le corpus des règles, contre une cible de 1,09. Tenue avec un facteur 5.

**C8** : cohérent.

### `redaction.md` — 6 instructions

Les 6 survivent, aucun dépassement C7, base jugé sur pièce. **C4** : le couple `style.md` / `reponse.md` / `redaction.md` déclare ses deltas et renvoie aux voisins au lieu de recopier, vérifié par grep sur « dernière ligne » et « question de clôture », qui ne sortent que dans les deux fichiers qui s'opposent explicitement. **C8** : cohérent.

### `memory-policy.md` — 4 instructions

Les 4 survivent, aucun dépassement, base jugé sur pièce sauf l'instruction 4 (sondage sous-agent du 2026-07-20), mesurée à l'époque et **non remesurée dans cette passe** — marquée telle quelle.

**C4 contre le natif** : le system prompt porte « *Don't save what the repo already records (code structure, past fixes, git history, CLAUDE.md) or what only matters to this conversation* », ce qui recouvre la moitié générique de l'instruction 1. L'increment survit et il est réel : `aidd_docs/` et le vault sont nommés comme les foyers de la couche projet, ce que le natif ne dit pas. Garder.

**C8** : cohérent.

### `commit-convention.md` — 4 instructions

Les 4 survivent. **C2 exemplaire** : l'invariant est porté par `guard-no-claude-in-commit.sh`, la règle est réduite à un pointeur et interdit explicitement de recopier la liste des types, en citant la divergence déjà vécue. C'est la forme que C2 prescrit.

**Pas de conflit avec `aidd-vcs:01-commit`, mesuré** : le skill prescrit « conventional unless the project sets another convention », « imperative mood », et ne porte aucune mention de co-auteur ni d'IA (`grep -rniE "co-auth|claude|generated"` sur ses 4 fichiers, aucune sortie sur ces motifs). Les deux sources s'accordent.

**C8** : cohérent.

### `tooling.md` — 4 instructions

Les 4 survivent. **C2 exemplaire**, même forme que `commit-convention.md` : `guard-bash-tooling.py` porte l'invariant et la raison, la règle garde deux lignes pour éviter d'écrire la commande fautive et le dit (« un hook ne parle qu'après coup »).

**Tension mineure avec la couche session** : l'instruction du mode bypass injectée dans cette session recommande « *make file changes with sed, heredocs, or short scripts* », quand l'instruction 2 interdit le heredoc **imbriqué** dans un `bash -lc`. Les deux périmètres ne se recouvrent pas, donc ce n'est pas un conflit. Signalé pour qu'une passe future ne le rouvre pas.

**C8** : cohérent.

### `chat-style.md` — 1 instruction

Survit. Le fichier ne porte volontairement aucun critère, il renvoie à la couche globale et explique pourquoi (un critère laissé là ne traverse ni les sous-agents ni un autre wrapper). 84 mots, verdict trivial.

## Captures hors grille

Notées en une ligne, non creusées, conformément au contrat.

1. **`rules/autorite-des-conventions.md` n'est dans aucun commit** alors qu'il se charge à chaque session. Hygiène git, pas un critère de la grille.
2. **La table C7 n'a pas de ligne pour « sous l'alerte, mais quatrième part présente ».** Cas rencontré sur `plan-mode.md` : onze instructions toutes sous 72 mots, un fichier à 504, et une quatrième part bien réelle. La table ne prescrit « garder tel quel » que si la quatrième part est **absente**.
3. **La hiérarchie d'`autorite-des-conventions.md` n'a aucun niveau pour le défaut d'un framework installé.** Le conflit mermaid ne se range ni en niveau 1 (le repo ne déclare rien) ni en niveau 2 (les deux sources sont extérieures au repo).
4. **`git config core.hooksPath` n'est pas configuré** sur ce repo. Les gardes passent par les hooks du harnais, pas par git. Constaté en lançant l'inventaire, hors périmètre C2 de cette passe.
5. **Les descriptions de skills ont gagné 391 mots et 3 skills** sans passe d'audit. La grille dit que c'est le premier poste du permanent et qu'il n'a pas de cible avant la passe 9.

## Verdict C6

**5 547 mots à l'entrée, cible ~3 950, dépassement de 1 597.**

Les actions prescrites par la cascade rendent, en estimation à remesurer après coupe :

| Fichier | Action | Gain estimé |
|---|---|---|
| `autorite-des-conventions.md` | C7, extraire 5 quatrièmes parts vers une référence | ~350 |
| `reponse.md` | C7 red flag, réécrire « couper à la reco » | ~90 |
| `profil.md` | C7, extraire 2 tables vers `ref-style.md` | ~80 |
| `ai-principles.md` | C3, réduire 2 principes doublonnés à leur titre | ~60 |
| `style.md` | C1b/C4, supprimer « une reco, pas un catalogue » | ~45 |
| `mermaid.md` | déclarer la portée contre le défaut AIDD | **+20** |
| **Total** | | **~605** |

**La cascade seule ne ramène pas la couche à la cible.** 5 547 − 605 laisse **~4 942 mots**, soit encore 992 au-dessus. C'est le même constat que la passe du 2026-08-10, où l'estimation « ~40 % retirables » n'avait rendu que 30 %.

Le reste demande une décision humaine sur la sortie d'un fichier entier, pas un verdict de cascade — et la grille l'interdit explicitement à l'audit : « on ne supprime pas une instruction survivante pour tenir un chiffre ». Les deux seuls candidats à une sortie, par leur poids et la nature de leur déclencheur, sont `autorite-des-conventions.md` (879, déclencheur limité aux sessions de développement) et `plan-mode.md` (504, dont les onze instructions passent toutes C7).

## Après la passe — actions appliquées et décision humaine

Cette section est postérieure à la cascade. Elle ne modifie aucun verdict ci-dessus, elle enregistre ce qui a été fait avec.

**Les six actions ont été appliquées le 2026-08-21.** Résultat remesuré : **5 547 → 5 192 mots**, soit **355 gagnés** et non les ~605 estimés. Troisième estimation trop optimiste de la session, même cause chaque fois : le gain a été chiffré avant que le texte de remplacement soit écrit. Détail par fichier :

| Fichier | Avant | Après | Ce qui a bougé |
|---|---|---|---|
| `autorite-des-conventions.md` | 879 | 724 | 5 quatrièmes parts vers `ref-autorite-des-conventions.md` |
| `profil.md` | 642 | 548 | 2 paires vers `ref-style.md`, une gardée |
| `reponse.md` | 521 | 420 | red flag C7 réécrit, rappel-trois-mots comprimé |
| `style.md` | 342 | 290 | « une reco, pas un catalogue » supprimée, increment fondu |
| `ai-principles.md` | 462 | 468 | 2 principes réduits, mais la mention du natif coûte plus que le corps retiré |
| `mermaid.md` | 205 | 246 | ajout de la clause de portée contre le défaut AIDD |

**`ai-principles.md` a grossi de 6 mots au lieu de maigrir de 60.** Nommer le doublon natif dans la règle coûte plus que les trois phrases retirées. Le gain n'est donc pas en mots, il est en absence de doublon volatil, et il faut le dire ainsi.

**C7 remesuré** : 8 blocs au-dessus de 72 contre 11 avant. Les deux plus gros restants (`autorite-des-conventions.md` à 143 et 98) sont des **artefacts d'unité de mesure**, l'instrument `awk` fusionnant une section `##` avec son tableau, là où le découpage du cadrage compte quatre instructions de ~30 mots chacune. Le découpage manuel fait foi, la grille le dit. Aucune instruction du découpage ne dépasse l'alerte après les actions, sauf les blocs à exemples positifs de `profil.md`, gardés parce que la page Opus 5 les prescrit.

**Décision humaine du 2026-08-21 — la cible chiffrée de C6 est retirée.** Un plafond en mots fabrique un dilemme que rien ne tranche : il met une instruction survivante en concurrence avec un nombre, alors que la grille interdit par ailleurs de couper l'une pour tenir l'autre. C6 mesure et publie désormais le poids, sa trajectoire et ses contributeurs, sans rendre de verdict de dépassement. La question devient « qu'est-ce que la couche a acheté avec sa croissance », et ce sont C1 et C7, par instruction, qui décident. Appliqué à la grille **après** cette passe, donc dans un commit postérieur à `a945687` que le prochain audit citera.

**Ce que ça change au verdict C6 ci-dessus** : le « dépassement de 1 597 » se lit désormais comme une mesure, pas comme une faute. Les 5 192 mots restants n'appellent aucune coupe supplémentaire au titre du budget.

## À réviser entre deux audits

1. **Ajouter à la table C7 la ligne « sous l'alerte, quatrième part présente ».** Sans elle, un fichier lourd fait d'instructions toutes courtes n'a aucune action prescrite, alors que sa quatrième part est extractible. Cas mesuré : `plan-mode.md`, 504 mots, zéro dépassement.
2. **Le seuil de 3 appels d'outil du dosage C1 n'a été appliqué qu'en jugement, jamais par sondage.** Les deux verdicts qui en dépendent (`autorite-des-conventions.md`, `plan-mode.md`) sont « jugé sur pièce » sur cet axe. Un sondage sous-agent les confirmerait ou les renverserait.
3. **Aucun A/B à bras de contrôle n'a tourné dans cette passe.** Tous les verdicts C1b reposent sur la doc, qui a suffi, ou sur la pièce. Conforme à la grille, qui réserve l'A/B aux cas où la doc est muette et la suppression plausible, mais ça borne ce que la passe démontre.
4. **La médiane C7 a bougé de 32 à 36 mots/bloc en dix jours.** Une alerte dérivée de la médiane du corpus qu'elle juge monte quand le corpus grossit, donc elle se desserre exactement quand il faudrait qu'elle serre. À trancher : figer le seuil, ou l'indexer sur autre chose que le corpus mesuré.
5. **Le doublon avec le system prompt natif n'a aucun instrument.** Les deux verdicts de cette passe qui en dépendent (`style.md#3`, `ai-principles.md#7` et `#10`) reposent sur une citation de contexte, non reproductible par commande. C'est le trou que la grille nomme en C4 sans proposer de mécanisme.
