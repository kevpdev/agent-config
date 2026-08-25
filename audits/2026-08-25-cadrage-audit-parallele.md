# Audit parallèle par skill — proposition d'architecture

Note de **proposition**, posée le 2026-08-25 en clôture de la passe `skills/` C1. Elle ne décide rien : la grille se révise entre deux audits, par l'humain. Elle fixe la cible discutée pour que la décision n'ait pas à re-dériver le raisonnement.

**Ce qu'elle propose de changer dans la grille** : la section Méthode pose « **Une passe = un sous-domaine** », donc un découpage **horizontal** — une passe traverse N skills sur une seule couche. La proposition est de passer au découpage **vertical**, une passe par skill, toutes ses couches, parallélisé en sous-agents.

## Le défaut mesuré que ça corrige

C8 se juge « par fichier **et par couple** ». Or la `description` d'un skill et son corps ne sont jamais dans la même passe : celle de `doc-sync` a un verdict du 2026-08-11, son corps un verdict du 2026-08-25. **Aucun critère ne peut donc voir une contradiction entre les deux**, et la passe C1 a dû déclarer la description « hors crible, surface de comparaison C4 seulement ».

## Le prix, et il est nommable

Deux critères sont inter-skills par construction, et un sous-agent qui ne voit qu'un skill ne peut pas les rendre.

| Critère | Pourquoi il ne se parallélise pas |
| --- | --- |
| **C7** | son alerte est **2× la médiane du corpus**. Trois corpus mesurés à ce jour rendent trois seuils, 60, 130 et 69. Un agent qui ne voit qu'un skill ne peut pas calculer la médiane du lot |
| **C4** | deux agents auditant `doc-sync` et `memory-bootstrap` en parallèle trouvent chacun le même doublon et prescrivent chacun de garder le fait **chez soi**. Aucun ne voit qu'il est l'autre moitié |
| **C6** | déjà global, déjà résolu en consolidation. Aucun changement |

**Le risque de fond** : la note d'ouverture d'`audit-harnais` dit que le skill existe parce que « deux audits ont divergé sur la même grille (2026-08-10) ». N instances parallèles multiplient ce risque par N. Ce qui le contient est ce qui a été posé le 2026-08-25 — les **conventions figées** d'`axes-protocole.md`, que chaque sous-agent reçoit et ne rouvre pas.

## L'architecture proposée — quatre phases

### Phase 1 — cadrage macro, central, non parallélisable

Ce qui doit être calculé **une fois** avant tout fan-out, parce qu'aucun sous-agent ne peut le produire depuis son périmètre.

- L'inventaire et le commit de la grille, comme aujourd'hui.
- Les **médianes C7 par couche**, donc les seuils que les sous-agents recevront. Un seuil reçu, jamais dérivé sur place.
- La **carte des faits partagés inter-skills** : quels faits vivent à plus d'un endroit, et où. C'est elle qui rend C4 jugeable ensuite.
- Les **conventions figées** du registre, à passer verbatim à chaque sous-agent.

### Phase 2 — batch parallèle, un sous-agent par skill

Critères rendus par le sous-agent : **C1, C2, C3, C5, C8**, plus **C7 avec le seuil reçu**.

**Pool déterministe fixe, 3 pour commencer.** Extensible par paliers, 3, 6 ou 9, selon la difficulté et le coût du lot. *Pourquoi un pool fixe et non « autant que de skills » : le coût est linéaire au nombre d'agents et la doc du modèle courant prescrit de plafonner la délégation, « **cap delegation** […] set deterministic caps on how many agents can be launched ». Un palier se décide avant le lancement, il ne se négocie pas pendant.*

**Un sous-agent qui trouve un doublon hors de son skill le remonte, il ne le tranche pas.** Il n'en voit qu'un côté.

### Phase 3 — checker central, qui compare les résultats entre eux

Il ne relit pas chaque verdict, il **croise** les rendus. Trois sorties, et la troisième est un apport que le découpage horizontal ne produit pas.

| Ce que le croisement montre | Sortie |
| --- | --- |
| un doublon dont les deux côtés sont remontés | tranché ici, un seul home survit |
| C6, la somme des survivantes | rendu en consolidation, sans verdict de dépassement |
| **deux sous-agents divergent sur le même objet** | l'humain tranche, **et la divergence part au registre comme axe** |

**Pourquoi la divergence vaut plus que sa résolution** : deux instances qui lisent la **même** grille et rendent deux verdicts différents sur le **même** objet mesurent une **ambiguïté de la grille**. Et c'est le seul signal du dispositif qui soit une mesure venue de dehors, puisque les deux bras ne se sont pas parlé — ce que `rules/reasoning.md` exige et qu'une relecture ne fournit jamais. Elle entre au registre avec **deux occurrences d'un coup**, donc elle peut franchir la porte immédiatement.

### Phase 4 — cycle de correction borné

Selon ce que la phase 3 rend :

- **désaccord tranchable par une mesure** — une commande, un grep, un comptage le règle : le cycle la lance et continue, sans passer par l'humain ;
- **désaccord portant sur un acquis ou une convention figée** : l'humain tranche, le contrat bornant ce que la cascade peut juger ;
- **divergence entre deux sous-agents sur le même objet** : l'humain, toujours.

*Pourquoi ce tri et non « tranchable par le LLM ou pas » : « tranchable » est un jugement, donc il se trompera, et le dispositif entier existe pour retirer les jugements des endroits où un comptage suffit. Les trois lignes ci-dessus se décident sans apprécier quoi que ce soit.*

**Borne : 3 passes maximum**, celle de `skill-authoring-fr.md` section Frame–Deliver–Checker, elle-même alignée sur le `max_iterations` d'`aidd-orchestrator:00-async-dev`, seule borne numérique du référentiel. Au-delà, le défaut est dans le diagnostic ou le cadrage, pas dans l'exécution.

**Le cycle ne touche que les artefacts audités.** Jamais la grille, jamais le protocole `audit-harnais`. *Pourquoi cette clôture est non négociable : une boucle autorisée à corriger son propre instrument perd le bras de contrôle que la porte d'`axes-protocole.md` installe. Un défaut du protocole se capture et attend deux passes indépendantes, il ne s'auto-répare pas.*

## Ce qui reste à trancher par l'humain

1. **Passer au vertical, ou garder l'horizontal.** La grille porte aujourd'hui une raison explicite pour l'horizontal — « le scope concentre le contexte, les fichiers d'un même sous-domaine se comparent entre eux ». La phase 1 rend cette comparaison autrement, elle ne la supprime pas. À décider quand même, c'est un renversement de la section Méthode.
2. **Le palier de départ du pool.** 3 proposé. Aucune mesure ne le fonde, c'est un choix de coût.
3. **Qui porte la phase 3.** Un sous-agent checker frais, ou la session parente. Le pattern Frame–Deliver–Checker dit un checker indépendant ; la page de prompting du modèle courant dit de ne pas déléguer une vérification à un sous-agent. La tension est la même que celle capturée par la passe C1, elle n'est pas rouverte ici.

## Statut

**Proposition, non appliquée.** Elle attend une décision humaine entre deux audits, et son application demanderait une révision de la grille (section Méthode) plus une refonte du protocole `audit-harnais` en quatre phases.
