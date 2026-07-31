---
name: mermaid-craft
description: >
  Critères de qualité d'un diagramme Mermaid : orientation, croisements, labels, couleur
  porteuse de sens, sous-graphes, et adaptation par type (flowchart, sequence, ER, class,
  state, gantt/journey). Utiliser quand on produit ou relit un diagramme Mermaid — "fais un
  schéma", "diagramme cette archi", "ce diagramme est illisible", "quel type de diagramme
  pour", ou avant d'écrire un bloc mermaid non trivial. NE PAS utiliser pour décider de
  l'architecture elle-même (→ backend-architect / agentic-architect), ni pour publier le
  schéma dans le vault (→ vault-recap-raisonnement, qui appelle ce skill pour les critères).
---

# Skill — Mermaid Craft

## Rôle

Tu produis des diagrammes Mermaid lisibles d'un coup d'œil, y compris sur un écran en portrait.

**POURQUOI** : un diagramme est un outil de décision visuel. Mal structuré ou surchargé, il coûte plus à lire qu'il n'informe — l'inverse de son but.

## Règles communes (tout type)

**Les deux non-négociables — vertical par défaut, zéro croisement de flèches — vivent dans `rules/mermaid.md`**, chargée en permanence, donc déjà présente quand ce skill se lit. Ne pas les redire ici et ne pas en écrire de variante : une seule source, sinon les deux dérivent au premier edit. Ce fichier porte tout le reste.

- **Labels courts et synthétiques** — nom ou nom+verbe, jamais une phrase. Détail long → note séparée, pas dans le nœud.
- **Un concept par nœud** — si un nœud décrit deux choses, le scinder.
- **Couleur = sens, jamais décoration** — colorer pour porter une information (rôle, état, couche, criticité), pas pour « faire joli ». Rester sobre : quelques classes (`classDef`) réutilisées, contraste lisible en clair comme en sombre. Pas de couleur → pas de perte d'information.
- **Regrouper avec des sous-graphes** quand des nœuds partagent une couche/domaine/phase — la structure visuelle doit refléter la structure logique.
- **Sens de lecture unique** — le flux principal va du haut vers le bas ; les retours/boucles sont l'exception visible, pas la norme.

## Adaptation par type

- **Flowchart** : `TD` ; sous-graphes pour les phases/couches ; une décision = un losange avec sorties étiquetées (`oui`/`non`) et non croisées ; éviter les nœuds à plus de 3 sorties.
- **Sequence** : acteurs ordonnés de gauche à droite selon leur premier appel (minimise les croisements de messages) ; grouper les échanges liés en `alt`/`opt`/`loop` ; activations (`activate`) pour montrer la durée de vie.
- **ER** : cardinalités explicites sur chaque relation ; n'afficher que les attributs porteurs de sens pour le propos du schéma, pas tout le modèle physique.
- **Class** : visibilité et types utiles seulement ; relations d'héritage verticales, associations horizontales ; pas d'attribut cosmétique.
- **State** : un seul état initial `[*]` ; transitions nommées par l'événement déclencheur ; états composites pour regrouper.
- **Gantt / Journey** : réserver aux dimensions temps/expérience ; sections pour regrouper ; ne pas détourner pour un flux logique (→ flowchart).

## Garde-fou

Si respecter « vertical » ou « zéro croisement » rend le diagramme illisible (graphe trop dense), c'est le signal que le diagramme fait trop : le scinder en plusieurs vues plutôt que sacrifier la lisibilité.

## Test

Trois critères qui passent ou échouent, à vérifier sur le diagramme rendu :

1. Il tient dans une largeur d'écran en portrait, sans scroll horizontal.
2. Aucune arête n'en croise une autre.
3. Retirer toutes les couleurs ne fait perdre aucune information — et chaque couleur employée vient d'une classe `classDef` nommée.

Un diagramme qui échoue sur 1 ou 2 se corrige par réordonnancement ou scission (cf. garde-fou), jamais en acceptant l'écart.
