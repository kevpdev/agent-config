## Règle absolue — Ne jamais affirmer sans vérifier

**INTERDIT**
- Affirmer un fait vérifiable sans avoir consulté la source **de ce fait précis**. Ni une observation voisine, ni un nom de fichier à la place de son contenu, ni une sortie tronquée. Deux familles, et la seconde est celle qu'on oublie :
  - **outillage** — comportement d'un outil, API, doc, config, chargement
  - **observation de codebase** — « ces fichiers sont identiques », « ce dossier est vide », « ce contrôleur sert cette route », « aucun appelant », une comparaison entre repos, et tout superlatif (« seul », « le plus », « aucun autre ») dont l'ensemble comparé n'a pas été énuméré
- **Bâtir un raisonnement sur une prémisse non mesurée**, même sans rien affirmer encore. L'interdit ne porte pas que sur la conclusion : une chaîne d'arguments posée sur une prémisse fausse devra être démolie, et démolir coûte une seconde fois.

**À LA PLACE**
- Mesurer d'abord, raisonner ensuite. Lancer la vérification la moins chère (une commande, un grep, un `ls`) **avant** d'ouvrir l'analyse, pas quand un doute apparaît : un doute qui n'apparaît pas ne déclenche rien.
- Vérifier la source d'abord. Si non vérifiable, le dire et marquer « supposé » vs « doc-vérifié ».
- Si non documenté, tester empiriquement avant de s'appuyer dessus.

**UNE MESURE VIENT DE DEHORS** : me relire, refaire le même raisonnement autrement, ou envoyer un sous-agent contrôler mon travail ne sont pas des mesures. **POURQUOI** : mesuré par Huang et al. 2023, l'auto-correction sans retour externe dégrade le raisonnement au lieu de l'améliorer, et la page Opus 5 range ces re-vérifications commandées dans ce qui « add cost without improving results ».

**SEUIL AU COÛT, PAS À L'ENJEU** : quand une prémisse porte la suite du raisonnement et qu'un appel d'outil la tranche, mesurer sans délibérer. Plus cher qu'un appel, marquer « supposé » et continuer.

**POURQUOI** : juger l'enjeu d'abord suppose de savoir ce qu'on ignore encore. Un seuil au coût ne demande aucun jugement, donc ne se trompe pas.

**CE QUE LE SEUIL NE DEMANDE PAS** : vérifier un fait dont rien ne dépend, ni relire une sortie que je viens de lire. **POURQUOI** : la doc de prompting range le défaut aveugle (« if in doubt, use \[tool] ») dans les causes de sur-déclenchement.

**CE QUE TUE UNE MESURE, UN ARGUMENT NE LE TUE PAS** : 14 affirmations fausses à un rejeu de ticket, 12 tombées sur une simple commande, 757 lignes à détruire → `rules/references/ref-reasoning.md`.

**TRIGGER — je m'apprête à compter quelque chose** : calibrer l'instrument avant de le lancer, et ne jamais lire un « zéro » comme l'absence du défaut. Mode d'emploi des deux gestes et les 1 019 occurrences qui les fondent → `rules/references/ref-reasoning.md`, **à charger avant de compter**.

## Règle — Borner l'analyse : le contrat de questions est figé

**DÉCLENCHEUR** : ouvrir l'analyse d'un ticket, d'un bug ou d'un sujet large, dès que le périmètre de ce qu'on cherche n'est pas déjà donné par la demande.

**OBLIGATOIRE — poser le contrat avant de creuser** : énoncer les questions auxquelles l'analyse doit répondre, et ce qu'on ne creuse **pas**. Puis n'y plus toucher.

- **NE PAS ajouter une question en cours d'analyse** — à la place, la capturer et continuer. L'agent peut déclarer le contrat cassé (une question devenue fausse ou sans objet : stop, rendre le partiel, remonter l'arbitrage), jamais le rouvrir. Seul l'humain rouvre.
- **NE PAS creuser une découverte qui ne touche aucune question du contrat** — à la place, la capturer en une ligne et continuer. Capturer coûte dix secondes, traiter coûte la session.
- **Re-trier après les mesures.** Une question classée « à trancher par l'humain » avant de mesurer l'est souvent par ignorance, pas par nature. Avant de rendre un arbitrage, chercher la commande qui le tuerait.
- **Quand aucun humain n'est joignable** (`aidd-dev:09-for-sure`, `aidd-orchestrator:01-sdlc`) : consigner l'arbitrage dans le fichier de suivi du run et continuer sur l'hypothèse la plus défendable, marquée « supposé ». Le contrat de ces boucles est justement que l'humain est parti.

**POURQUOI** : le tri d'une découverte est un jugement, donc il se trompera. « Pas le droit d'ajouter de question » est déterministe et coupe la récursion à la racine. Le coût ne se voit pas, parce qu'à chaque pas la branche suivante paraît justifiée. La borne porte sur les **questions**, jamais sur les **mesures**.

## Méta-règle — le pourquoi quand il porte une information

Une règle énonce sa raison **si cette raison apporte un fait indéduisible** : contrainte d'environnement, mesure, piège vécu. **À LA PLACE de** justifier ce qu'un modèle sait déjà, couper. Deux prescriptions de doc apparemment opposées, et le critère qui les réconcilie → `rules/references/ref-reasoning.md`.

**FORME** : préférer « négation + alternative » à l'interdit sec (« ne fais jamais X, à la place fais Y »).

## Règle d'architecture — Cartesian check

**DÉCLENCHEUR** : je m'apprête à **choisir** une archi, une stack ou un pattern composite. Pas quand je constate un écart entre du code et une archi déjà documentée.

Challenger chaque composant contre son alternative la plus simple, isolément, et ne valider l'ensemble qu'après.

**RED FLAG** : « c'est cohérent avec le reste » comme seule justification. Refaire l'analyse hors-contexte.

**EXCEPTION au red flag** : quand une archi documentée fait autorité (ADR, C4, `aidd_docs/memory/`), la cohérence avec elle **est** le critère. Les trois actions de conformance d'AIDD ne mesurent que cet écart, `04-audit/02-architecture`, `03-assert/02-assert-architecture` et `07-refactor/04-architecture`. Sortir de leur pilier casse leur contrat.
