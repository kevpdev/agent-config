# Références — `rules/ai-practices.md`

Les cas mesurés qui fondent chaque « EN TEST DEPUIS », et le registre des pratiques écartées du banc d'essai. Jamais chargé automatiquement : l'instruction et son pourquoi restent dans la règle, seule la preuve chiffrée descend ici.

**Statut particulier de ce fichier** : sur un banc d'essai, la preuve n'est pas qu'une justification — c'est le dossier d'instruction de la promotion. La règle garde donc le **statut** (date, n=, réussite ou échec), qui change la façon de traiter la pratique ; ici vivent le détail et le **seuil de sortie**.

**POURQUOI un seuil en qualité de preuve, et pas en fréquence** : compter les déclenchements suppose de les remarquer. Essayé et démenti le 2026-08-11 — une instruction demandant de signaler chaque déclenchement n'a rien produit sur deux contextes neufs, parce qu'elle demandait de repérer d'abord ce que celui qui ne repère pas ne repérera pas. Un seuil qui repose sur une observation **construite exprès** n'exige aucune vigilance de fond : on éprouve une pratique le jour où l'on décide de la trancher.

**Ce qui rend une observation concluante** : un **bras de contrôle**. Deux contextes neufs, la même tâche, un seul tenu à la pratique. Sans lui on ne compare qu'à une intuition, et le nombre d'observations n'y change rien — c'est le défaut du test du 2026-08-11, qui n'a pas pu départager « l'agent a désobéi » de « le déclencheur est trop large ». Protocole : le test de C7 dans `audits/grille-harnais.md`.

**Qui décide** : ce repo, à la passe `/audit-harnais`, qui lit déjà ces fichiers. Le vault est un bac à sable et une base de connaissance sur projets concrets — il alimente le banc, il ne le juge pas (décidé le 2026-08-10, cf. `audits/grille-harnais.md:5`).

---

## 1. Livrer par incréments vérifiés — 2026-07-30

**Confirmée par un échec, n=1 sans contrefactuel.** 400 lignes écrites et validées en bloc → **7 affirmations non vérifiées, dont 2 fausses**.

Pas de contrefactuel : on ne sait pas ce qu'aurait donné la même passe découpée en incréments. La pratique tient donc sur un mécanisme plausible (la relecture en bloc invite à rationaliser), pas sur une comparaison.

**Seuil de sortie** — une seule observation suffit si elle porte son bras de contrôle : la même tâche à deux contextes neufs, un tenu au découpage, l'autre libre, et une différence **mesurée** sur les défauts qui survivent. Sans ce bras, aucun nombre d'observations ne tranche.

**À corriger d'abord** : le déclencheur (« plus d'un artefact ») attrape des cas où la pratique n'achète rien — trois scripts indépendants, vérifier le premier n'informe pas le second. Le test du 2026-08-11 l'a exhibé sans pouvoir le trancher, faute de bras de contrôle. Un seuil ne peut pas départager une pratique dont le déclencheur est faux.

## 2. Le contexte est du code — 2026-07-30

**Appliquée une fois, concluante.** Le test ajouté a attrapé **7 défauts réels le jour même**.

**Seuil de sortie** — une observation où l'artefact **avec** son critère testable et le même **sans** divergent : un défaut attrapé d'un côté, passé de l'autre. Supprimer si écrire le critère coûte plus que le défaut qu'il attrape — mesuré, pas estimé.

## 3. Capitaliser la leçon avant la fin de session — 2026-07-30

**Appliquée une fois, tenue.** Aucun chiffre relevé — c'est la plus faiblement étayée des cinq, et celle dont la promotion demandera une observation neuve.

**Seuil de sortie** — la preuve ne peut pas venir de la session qui capitalise, seulement d'une session **ultérieure** : un artefact produit ici, rechargé et utilisé plus tard. Une seule occurrence tranche, et le bras de contrôle est gratuit — il suffit que la session ultérieure n'ait pas été amorcée pour le chercher. Supprimer si les artefacts ne sont jamais rechargés : ce serait de l'archivage, pas de la capitalisation.

## 4. Une instruction dupliquée s'élimine — 2026-07-31

**n=1, deux défauts du même jour :**

- Un sous-agent a **sauté un skill** au motif que la règle résiduelle suffisait — la couche partielle qui a l'air complète supprime le chargement de l'autre.
- Un **conflit d'ordre** entre une règle et le template d'un skill n'est apparu qu'à l'exécution, invisible à la relecture des deux fichiers séparément.

Le second cas est le plus instructif : relire les deux copies ne révèle pas la divergence, parce qu'aucune des deux n'est fausse isolément.

**Seuil de sortie** — un découpage où un contexte neuf, **sondé**, charge bien la couche à la demande au lieu de s'arrêter à la couche partielle. Le sondage est le bras de contrôle : sans lui on ne distingue pas « il a chargé » de « il n'en a pas eu besoin ». Supprimer si un « délibérément partiel » se fait sauter quand même : ce serait le défaut d'origine sous un autre nom.

## 5. Charger le journal avant de répondre sur le passé — 2026-08-05

**n=1, et c'est un échec.** À la question « où en sommes-nous sur la config agentique », réponse rendue : aucune trace d'audit n'existe. Elle était dans le log du **31 juillet**.

La règle existait déjà sous une autre forme et n'a pas suffi — c'est la raison pour laquelle elle est descendue dans le banc d'essai plutôt que de rester dans `rules/`.

**Seuil de sortie, différent des autres** — un **second échec la supprime**, sans attendre de preuve positive : deux formulations successives restées sans effet montrent que le défaut n'est pas adressable par une règle de prose, et il faut alors un mécanisme déterministe ou rien. Pour la promouvoir : une question sur le passé où le journal est chargé avant la réponse, dans une session **qui n'a pas été amorcée pour ça** — c'est là le bras de contrôle.

---

## Ce que la prose ne peut pas déclencher — 0/3 le 2026-08-11

Deux instructions écrites pour instrumenter le banc lui-même, trois contextes neufs, aucun déclenchement.

- **« Signaler le déclenchement »** (98 mots, en-tête de `ai-practices.md`) — **0/2**. Elle demandait de remarquer d'abord qu'une pratique avait joué : celui qui ne remarque pas est exactement celui qui ne signalera pas.
- **« Passer le test comportemental avant le commit, au-delà de 60 mots »** (65 mots) — **0/1**. Déclencheur mécanique cette fois — écrire une règle, compter ses mots — et pourtant inerte. L'agent a écrit une règle de **562 mots** et l'a commitée sans aucun test.

**Ce que le second cas apprend, et que le premier ne disait pas** : rendre le déclencheur observable ne suffit pas. Les mêmes contextes neufs ont bien appliqué `reasoning.md` — l'un a marqué son seuil de 400 lignes comme convention posée et non comme chiffre mesuré — et la calibration de `workflow.md` — un autre a calibré sa regex sur 22 exemples, dont un cas fautif qui passait. Ces vérifications-là **font partie de livrer l'artefact**. Lancer une expérience séparée pour savoir si sa propre prose sert à quelque chose n'améliore pas l'artefact : ça entre en concurrence avec « finir la tâche », et ça perd.

**Conséquence** : le protocole est valide — trois verdicts nets rendus le même jour — mais il ne se déclenche que par l'humain. **Skill, jamais règle.** Parké dans `audits/grille-harnais.md` le temps de l'audit `skills/`.

## Écartées du banc d'essai

Décision du harnais, consignée ici : ces quatre pratiques ne sont **pas chargées**. Critère commun — une pratique qu'une règle ne peut pas exercer dilue les autres sans rien gagner. Le vault peut les porter comme matière de réflexion ; ça ne les remet pas au banc.

- **Spécialiser le modèle par fonction** et **cross-review inter-modèles** → décisions d'orchestration humaine, l'agent ne les prend pas. La forme utile de la seconde est un skill de vérification déléguée, pas une règle.
- **Chaîne spec → plan → décomposition** → écartée le 2026-07-30 comme doublon de `workflow.md` et des skills AIDD. **Motif périmé depuis** : `workflow.md` a été supprimé le 2026-08-11. Le doublon ne subsiste que côté skills AIDD — à revérifier avant de la reprendre au banc, plutôt que de la traiter comme tranchée.
- **Reconstruire le contexte plutôt que rattraper une dérive** → déclencheur non fiable : il exige de repérer soi-même sa propre dérive. À retenter si un signal observable émerge.
