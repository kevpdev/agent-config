# Pratiques en test — strate 2 du manifeste IA

**Ce fichier n'est pas de la doctrine, c'est un banc d'essai.** Il porte des pratiques **non validées**, chargées exprès : une pratique jamais chargée n'est jamais exercée, donc jamais validable. Le tri par durée de vie du manifeste n'est pas cassé tant que l'étiquette dit la vérité — même discipline que la strate 3, qui marque ses entrées `🧪 non validé, à surveiller`.

**La promotion en strate 1 se décide au MOC** (`$OBSIDIAN_VAULT_PERSO/3 GARDEN/MOC/MOC - Manifeste IA.md`), jamais ici. Ce fichier ne fait qu'exposer la pratique à l'usage et accumuler des observations.

**POURQUOI ce fichier existe** : `ai-principles.md` porte la strate 1, faite pour ne pas vieillir — donc abstraite, donc sans prise sur un cas concret. Une règle qui ne porte que le *pourquoi* ne se déclenche pas. Les pratiques ci-dessous portent le *quoi faire*.

---

## 1. Livrer par incréments vérifiés

**DÉCLENCHEUR** : produire plus d'un artefact, ou plus d'une centaine de lignes, dans une même passe.

**À LA PLACE DE** générer le lot complet puis tout relire → vérifier chaque incrément **avant** d'écrire le suivant. Un incrément non vérifié ne compte pas comme livré.

**POURQUOI** : la relecture en bloc invite à rationaliser ce qui est déjà écrit, pas à le vérifier. Et le coût de correction croît avec le volume déjà produit — à la fin, corriger une ligne demande de relire l'artefact entier.

**EN TEST DEPUIS** 2026-07-30.
**OBSERVATION** : ~400 lignes de fiches mémoire écrites d'un bloc puis validées en bloc → 7 affirmations non vérifiées, dont 2 fausses. Confirmée par l'échec, **n=1, sans contrefactuel** (la version incrémentale n'a pas été faite pour comparer).

---

## 2. Le contexte est du code

**DÉCLENCHEUR** : écrire ou modifier une doc, une règle, un skill, une fiche de mémoire.

**À LA PLACE DE** traiter un artefact de contexte comme de la prose libre → lui appliquer ce qu'on applique au code : versionné, relu, et **testé**. Un artefact de contexte sans test est du code sans test.

**POURQUOI** : le contexte pilote le comportement de l'agent aussi sûrement que le code pilote le programme. Une fiche fausse produit des décisions fausses, et son coût est différé — personne ne voit l'erreur au moment où elle entre.

**Ce que « testé » veut dire ici** : l'artefact porte un critère qu'on peut faire passer ou échouer. Pour une fiche descriptive, le test minimal est la **traçabilité** — chaque affirmation cite sa source ou porte son marqueur (`supposé`, `à confirmer`).

**EN TEST DEPUIS** 2026-07-30.
**OBSERVATION** : la couche mémoire d'un orchestrateur AIDD n'avait aucun test sur sa prose — seulement sur les commandes de son index. En ajouter un a attrapé 7 défauts réels le jour même. Appliquée une fois, tenue.

---

## 3. Capitaliser la leçon avant la fin de session

**DÉCLENCHEUR** : la session a produit une correction, un défaut découvert, une règle violée, ou une hypothèse tranchée.

**À LA PLACE DE** clore en résumant la leçon dans la réponse → la faire descendre dans un artefact : une **règle**, un **skill**, ou la **mémoire**. Une leçon qui reste dans la conversation est perdue à la compaction suivante.

**POURQUOI** : la conversation est le support le plus volatil de la chaîne. Ce qui n'en sort pas sera re-découvert au prix d'une session entière — ou pas du tout.

**Le bon foyer se choisit par la portée** : un fait sur un repo → mémoire du projet ; une manière de travailler → règle ; une procédure à rejouer → skill. En cas de doute, la règle, qui traverse les sous-agents.

**EN TEST DEPUIS** 2026-07-30.
**OBSERVATION** : la leçon des 7 affirmations est descendue le jour même dans `reasoning.md` (la règle) et dans le bloc `Test` de `memory-bootstrap` (le skill). Appliquée une fois, tenue.

---

## Ce qui n'est pas ici, et pourquoi

Quatre pratiques de strate 2 ont été **écartées de ce banc d'essai**. Ce n'est pas un oubli : une pratique qu'une règle ne peut pas exercer n'y gagne rien et dilue les autres.

| Pratique | Pourquoi elle n'est pas chargée |
| --- | --- |
| **Spécialiser le modèle par fonction** | Décision d'orchestration humaine — l'agent ne choisit pas son modèle |
| **Cross-review inter-modèles** | Idem : proposable, pas décidable par l'agent. Sa forme utile est un **skill** de vérification déléguée, pas une règle |
| **Chaîne spec → plan → décomposition** | Déjà couverte par `workflow.md` (« demander avant d'implémenter ») et par les skills AIDD. La recharger créerait un doublon, donc une dérive |
| **Reconstruire le contexte plutôt que rattraper une dérive** | Déclencheur non fiable : « quand la cohérence chute » exige de repérer soi-même sa propre dérive. Même défaut qu'un déclencheur de repli — un manque non repéré ne déclenche rien. À retenter si un signal observable émerge |

---

## Budget de ce fichier — 150 lignes

Un banc d'essai accumule par nature. **Au-delà de 150 lignes, ne pas laisser grossir** — arbitrer dans cet ordre :

1. **Supprimer** ce qui a été tranché : une pratique validée part au MOC en strate 1, une pratique démentie disparaît. Le banc d'essai n'est pas une archive.
2. **Scoper** avec un frontmatter `paths:`, comme `back-spring.md` et `front-react.md`, si une pratique ne concerne qu'un type de fichier.
3. **Redécouper** en fichiers par domaine, en dernier recours.

**POURQUOI ce plafond** : un fichier de règles gonflé fait ignorer les instructions qu'il contient — et ici, il diluerait en plus les règles **validées** au profit de pratiques qui ne le sont pas encore. Le coût du dépassement ne tombe pas sur ce fichier, il tombe sur les autres.
