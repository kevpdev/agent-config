# Banc d'essai — pratiques en test

Compagnon vivant de `grille-harnais.md`, comme elle non horodaté : git porte son historique. Cinq pratiques **non validées**, candidates à devenir des règles. **La promotion comme la suppression se décident ici, à la passe `/audit-harnais`** — une pratique promue monte dans `rules/ai-principles.md`, une pratique démentie disparaît.

**Jamais chargé en contexte permanent, et c'est un changement du 2026-08-11.** Ce banc vivait dans `rules/ai-practices.md` (988 mots, 25 % de la couche chargée) au motif qu'« une pratique jamais chargée n'est jamais exercée, donc jamais validable ». **Cet argument est mort le jour où les seuils sont passés à la qualité de preuve** : les cinq exigent désormais un bras de contrôle, donc une expérience montée exprès, et aucun ne peut être satisfait par « la pratique a joué pendant le travail normal ». Charger le banc n'achetait donc plus sa promotion — seulement de la dilution des règles validées.

**Le vault alimente, il ne juge pas** : bac à sable et base de connaissance sur projets concrets (décidé le 2026-08-10, cf. `grille-harnais.md`).

*Pas de budget de lignes ici, contrairement à la version chargée : un fichier non chargé ne dilue rien. Ce qui le borne, c'est le nombre de pratiques en attente — cinq est déjà beaucoup pour un banc dont chaque sortie coûte une expérience.*

---

## Comment une pratique sort du banc

**Un seuil en qualité de preuve, pas en fréquence.** Compter les déclenchements suppose de les remarquer. Essayé et démenti le 2026-08-11 : une instruction demandant de signaler chaque déclenchement n'a rien produit sur deux contextes neufs, parce qu'elle demandait de repérer d'abord ce que celui qui ne repère pas ne repérera pas.

**Ce qui rend une observation concluante : un bras de contrôle.** Deux contextes neufs, la même tâche, un seul tenu à la pratique. Sans lui on ne compare qu'à une intuition, et le nombre d'observations n'y change rien — c'est le défaut du test du 2026-08-11, qui n'a pas pu départager « l'agent a désobéi » de « le déclencheur est trop large ». Protocole : le test de C7 dans `grille-harnais.md`, et la branche **C1b** pour juger si la pratique est déjà portée nativement.

---

## 1. Livrer par incréments vérifiés

**DÉCLENCHEUR** : produire plus d'un artefact, ou plus d'une centaine de lignes, dans une même passe.

**À LA PLACE DE** générer le lot complet puis tout relire → vérifier chaque incrément **avant** d'écrire le suivant. Un incrément non vérifié ne compte pas comme livré.

**POURQUOI** : la relecture en bloc invite à rationaliser ce qui est déjà écrit, pas à le vérifier. Et le coût de correction croît avec le volume déjà produit — à la fin, corriger une ligne demande de relire l'artefact entier.

**STATUT** — en test depuis 2026-07-30. Confirmée par un échec, n=1 sans contrefactuel : 400 lignes écrites et validées en bloc → **7 affirmations non vérifiées, dont 2 fausses**. On ne sait pas ce qu'aurait donné la même passe découpée. La pratique tient sur un mécanisme plausible, pas sur une comparaison.

**SEUIL DE SORTIE** — une seule observation suffit si elle porte son bras de contrôle : la même tâche à deux contextes neufs, un tenu au découpage, l'autre libre, et une différence **mesurée** sur les défauts qui survivent. Sans ce bras, aucun nombre d'observations ne tranche.

**À CORRIGER D'ABORD** : le déclencheur (« plus d'un artefact ») attrape des cas où la pratique n'achète rien — trois scripts indépendants, vérifier le premier n'informe pas le second. Le test du 2026-08-11 l'a exhibé sans pouvoir le trancher, faute de bras de contrôle. Un seuil ne peut pas départager une pratique dont le déclencheur est faux.

## 2. Le contexte est du code

**DÉCLENCHEUR** : écrire ou modifier une doc, une règle, un skill, une fiche de mémoire.

**À LA PLACE DE** traiter un artefact de contexte comme de la prose libre → lui appliquer ce qu'on applique au code : versionné, relu, et **testé**. Un artefact de contexte sans test est du code sans test.

**POURQUOI** : le contexte pilote le comportement de l'agent aussi sûrement que le code pilote le programme. Une fiche fausse produit des décisions fausses, et son coût est différé — personne ne voit l'erreur au moment où elle entre.

**Ce que « testé » veut dire** : l'artefact porte un critère qu'on peut faire passer ou échouer. Pour une fiche descriptive, le test minimal est la **traçabilité** — chaque affirmation cite sa source ou porte son marqueur (`supposé`, `à confirmer`). Pour une règle ou un skill, le test est **comportemental** : donner à un contexte neuf une tâche qui devrait la déclencher, **fixer les critères de réussite avant de lire la réponse**, puis juger. Compter les lignes ou vérifier qu'un bloc est présent ne teste rien du comportement — la seule chose que la règle prétend produire.

**STATUT** — en test depuis 2026-07-30. Appliquée une fois, concluante : le test ajouté a attrapé **7 défauts réels le jour même**.

**SEUIL DE SORTIE** — une observation où l'artefact **avec** son critère testable et le même **sans** divergent : un défaut attrapé d'un côté, passé de l'autre. Supprimer si écrire le critère coûte plus que le défaut qu'il attrape — mesuré, pas estimé.

## 3. Capitaliser la leçon avant la fin de session

**DÉCLENCHEUR** : la session a produit une correction, un défaut découvert, une règle violée, ou une hypothèse tranchée.

**À LA PLACE DE** clore en résumant la leçon dans la réponse → la faire descendre dans un artefact : une **règle**, un **skill**, ou la **mémoire**. Une leçon qui reste dans la conversation est perdue à la compaction suivante.

**POURQUOI** : la conversation est le support le plus volatil de la chaîne. Ce qui n'en sort pas sera re-découvert au prix d'une session entière — ou pas du tout.

**Le bon foyer se choisit par la portée** : un fait sur un repo → mémoire du projet ; une manière de travailler → règle ; une procédure à rejouer → skill.

**STATUT** — en test depuis 2026-07-30. Appliquée une fois, tenue, **aucun chiffre relevé** : c'est la plus faiblement étayée des cinq, et celle dont la promotion demandera une observation neuve.

**SEUIL DE SORTIE** — la preuve ne peut pas venir de la session qui capitalise, seulement d'une session **ultérieure** : un artefact produit ici, rechargé et utilisé plus tard. Une seule occurrence tranche, et le bras de contrôle est gratuit — il suffit que la session ultérieure n'ait pas été amorcée pour le chercher. Supprimer si les artefacts ne sont jamais rechargés : ce serait de l'archivage, pas de la capitalisation.

## 4. Une instruction dupliquée s'élimine, elle ne se hiérarchise pas

**DÉCLENCHEUR** : découper un artefact de contexte en couche permanente + couche à la demande — règle + skill, `CLAUDE.md` + référence.

**À LA PLACE DE** répéter le critère dans les deux couches en désignant laquelle fait foi → ne l'énoncer qu'une fois, et faire dire à la couche permanente qu'elle est **délibérément partielle**.

**POURQUOI** : une note de préséance documente le risque de dérive au lieu de le retirer — deux copies ne divergent qu'au premier edit, et rien n'empêche cet edit. Pire, une couche résiduelle qui a l'air complète *supprime* le chargement de l'autre.

**STATUT** — en test depuis 2026-07-31. n=1, deux défauts du même jour :

- Un sous-agent a **sauté un skill** au motif que la règle résiduelle suffisait — la couche partielle qui a l'air complète supprime le chargement de l'autre.
- Un **conflit d'ordre** entre une règle et le template d'un skill n'est apparu qu'à l'exécution, invisible à la relecture des deux fichiers séparément.

Le second cas est le plus instructif : relire les deux copies ne révèle pas la divergence, parce qu'aucune des deux n'est fausse isolément.

**SEUIL DE SORTIE** — un découpage où un contexte neuf, **sondé**, charge bien la couche à la demande au lieu de s'arrêter à la couche partielle. Le sondage est le bras de contrôle : sans lui on ne distingue pas « il a chargé » de « il n'en a pas eu besoin ». Supprimer si un « délibérément partiel » se fait sauter quand même : ce serait le défaut d'origine sous un autre nom.

**Observation du 2026-08-11, non comptée comme preuve** : `03-consolider.md` renvoie à « la cible courante » de la grille au lieu de recopier le chiffre, et a traversé sans dérive la scission de C6 en deux plafonds — pendant que quatre pointeurs recopiés vers `workflow.md` sont devenus faux. Pas de bras de contrôle, donc pas un seuil franchi.

## 5. Charger le journal avant de répondre sur le passé

**DÉCLENCHEUR** : l'utilisateur demande où on en était, le reste-à-faire d'une tâche, ou l'historique d'une décision. Une question dont la réponse vit dans les session logs et non dans le code courant.

**CONDITION** : seulement si un home de session logs existe. Le vérifier factuellement (`test -d "$OBSIDIAN_VAULT_PRO"`), pas au jugé.

**À LA PLACE DE** répondre de mémoire → charger le journal d'abord (`/vault-load`, scopé sur l'id de task s'il est repérable), puis répondre depuis le contexte chargé. Aucun push automatique n'existe : par défaut aucune source n'est chargée, et rien ne signale son absence.

**POURQUOI** : une réponse tirée de la mémoire de session a l'air complète, donc rien ne déclenche la vérification.

**STATUT** — en test depuis 2026-08-05, et c'est un **échec**. À la question « où en sommes-nous sur la config agentique », réponse rendue : aucune trace d'audit n'existe. Elle était dans le log du **31 juillet**. La règle existait déjà sous une autre forme et n'a pas suffi — c'est la raison de sa présence au banc plutôt que dans `rules/`.

**SEUIL DE SORTIE, différent des autres** — un **second échec la supprime**, sans attendre de preuve positive : deux formulations successives restées sans effet montrent que le défaut n'est pas adressable par une règle de prose, et il faut alors un mécanisme déterministe ou rien. Pour la promouvoir : une question sur le passé où le journal est chargé avant la réponse, dans une session **qui n'a pas été amorcée pour ça** — c'est là le bras de contrôle.

---

## Ce que la prose ne peut pas déclencher — 0/3 le 2026-08-11

Deux instructions écrites pour instrumenter le banc lui-même, trois contextes neufs, aucun déclenchement.

- **« Signaler le déclenchement »** (98 mots) — **0/2**. Elle demandait de remarquer d'abord qu'une pratique avait joué : celui qui ne remarque pas est exactement celui qui ne signalera pas.
- **« Passer le test comportemental avant le commit, au-delà de 60 mots »** (65 mots) — **0/1**. Déclencheur mécanique cette fois — écrire une règle, compter ses mots — et pourtant inerte. L'agent a écrit une règle de **562 mots** et l'a commitée sans aucun test.

**Ce que le second cas apprend, et que le premier ne disait pas** : rendre le déclencheur observable ne suffit pas. Les mêmes contextes neufs ont bien appliqué `reasoning.md` — l'un a marqué son seuil de 400 lignes comme convention posée et non comme chiffre mesuré — et une calibration de regex sur 22 exemples, dont un cas fautif qui passait. Ces vérifications-là **font partie de livrer l'artefact**. Lancer une expérience séparée pour savoir si sa propre prose sert à quelque chose n'améliore pas l'artefact : ça entre en concurrence avec « finir la tâche », et ça perd.

**Conséquence** : le protocole est valide — trois verdicts nets rendus le même jour — mais il ne se déclenche que par l'humain. **Skill, jamais règle.** Parké dans `grille-harnais.md` le temps de l'audit `skills/`.

## Écartées du banc d'essai

Décision consignée : ces quatre pratiques ne sont **pas retenues**. Critère commun — une pratique qu'une règle ne peut pas exercer dilue les autres sans rien gagner. Le vault peut les porter comme matière de réflexion ; ça ne les remet pas au banc.

- **Spécialiser le modèle par fonction** et **cross-review inter-modèles** → décisions d'orchestration humaine, l'agent ne les prend pas. La forme utile de la seconde est un skill de vérification déléguée, pas une règle.
- **Chaîne spec → plan → décomposition** → écartée le 2026-07-30 comme doublon de `workflow.md` et des skills AIDD. **Motif périmé depuis** : `workflow.md` a été supprimé le 2026-08-11. Le doublon ne subsiste que côté skills AIDD — à revérifier avant de la reprendre au banc, plutôt que de la traiter comme tranchée.
- **Reconstruire le contexte plutôt que rattraper une dérive** → déclencheur non fiable : il exige de repérer soi-même sa propre dérive. À retenter si un signal observable émerge.
