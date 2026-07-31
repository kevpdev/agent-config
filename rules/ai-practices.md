# Pratiques en test — strate 2 du manifeste IA

**Banc d'essai, pas doctrine.** Pratiques **non validées**, chargées exprès — une pratique jamais chargée n'est jamais exercée, donc jamais validable. La promotion en strate 1 se décide au MOC (`$OBSIDIAN_VAULT_PERSO/3 GARDEN/MOC/MOC - Manifeste IA.md`), jamais ici.

**POURQUOI ce fichier** : `ai-principles.md` porte la strate 1, abstraite par construction — elle ne porte que le *pourquoi*, donc ne se déclenche pas. Les pratiques ci-dessous portent le *quoi faire*.

---

## 1. Livrer par incréments vérifiés

**DÉCLENCHEUR** : produire plus d'un artefact, ou plus d'une centaine de lignes, dans une même passe.

**À LA PLACE DE** générer le lot complet puis tout relire → vérifier chaque incrément **avant** d'écrire le suivant. Un incrément non vérifié ne compte pas comme livré.

**POURQUOI** : la relecture en bloc invite à rationaliser ce qui est déjà écrit, pas à le vérifier. Et le coût de correction croît avec le volume déjà produit — à la fin, corriger une ligne demande de relire l'artefact entier.

**EN TEST DEPUIS** 2026-07-30 — confirmée par un échec (400 lignes écrites et validées en bloc → 7 affirmations non vérifiées, dont 2 fausses), n=1 sans contrefactuel.

---

## 2. Le contexte est du code

**DÉCLENCHEUR** : écrire ou modifier une doc, une règle, un skill, une fiche de mémoire.

**À LA PLACE DE** traiter un artefact de contexte comme de la prose libre → lui appliquer ce qu'on applique au code : versionné, relu, et **testé**. Un artefact de contexte sans test est du code sans test.

**POURQUOI** : le contexte pilote le comportement de l'agent aussi sûrement que le code pilote le programme. Une fiche fausse produit des décisions fausses, et son coût est différé — personne ne voit l'erreur au moment où elle entre.

**Ce que « testé » veut dire ici** : l'artefact porte un critère qu'on peut faire passer ou échouer. Pour une fiche descriptive, le test minimal est la **traçabilité** — chaque affirmation cite sa source ou porte son marqueur (`supposé`, `à confirmer`).

**EN TEST DEPUIS** 2026-07-30 — appliquée une fois : le test ajouté a attrapé 7 défauts réels le jour même.

---

## 3. Capitaliser la leçon avant la fin de session

**DÉCLENCHEUR** : la session a produit une correction, un défaut découvert, une règle violée, ou une hypothèse tranchée.

**À LA PLACE DE** clore en résumant la leçon dans la réponse → la faire descendre dans un artefact : une **règle**, un **skill**, ou la **mémoire**. Une leçon qui reste dans la conversation est perdue à la compaction suivante.

**POURQUOI** : la conversation est le support le plus volatil de la chaîne. Ce qui n'en sort pas sera re-découvert au prix d'une session entière — ou pas du tout.

**Le bon foyer se choisit par la portée** : un fait sur un repo → mémoire du projet ; une manière de travailler → règle ; une procédure à rejouer → skill. En cas de doute, la règle, qui traverse les sous-agents.

**EN TEST DEPUIS** 2026-07-30 — appliquée une fois, tenue.

---

## Écartées du banc d'essai

Une pratique qu'une règle ne peut pas exercer dilue les autres sans rien gagner :

- **Spécialiser le modèle par fonction**, **cross-review inter-modèles** → décisions d'orchestration humaine, l'agent ne les prend pas. La forme utile de la seconde est un skill de vérification déléguée, pas une règle.
- **Chaîne spec → plan → décomposition** → déjà couverte par `workflow.md` et les skills AIDD ; la recharger créerait un doublon, donc une dérive.
- **Reconstruire le contexte plutôt que rattraper une dérive** → déclencheur non fiable, il exige de repérer soi-même sa propre dérive. À retenter si un signal observable émerge.

## Budget — 150 lignes

Un banc d'essai accumule par nature. Au-delà, arbitrer dans cet ordre : **supprimer** ce qui a été tranché (validé → MOC en strate 1, démenti → disparaît), **scoper** par frontmatter `paths:`, **redécouper** par domaine en dernier recours.

**POURQUOI ce plafond** : un fichier de règles gonflé fait ignorer les instructions qu'il contient — et ici, il diluerait les règles **validées** au profit de pratiques qui ne le sont pas encore. Le coût du dépassement tombe sur les autres fichiers, pas sur celui-ci.
