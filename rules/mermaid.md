## Diagrammes Mermaid — critères transverses

S'applique à tout diagramme Mermaid produit par toi, un sous-agent ou un skill.

**POURQUOI** : un diagramme est un outil de décision visuel. Mal structuré ou surchargé, il coûte plus à lire qu'il n'informe — l'inverse de son but. Ces critères garantissent qu'il reste lisible d'un coup d'œil, y compris sur un écran en portrait.

### Règles communes (tout type)

- **Vertical par défaut** (`TD`/`TB`) — ne passer en horizontal (`LR`) que si le flux est intrinsèquement séquentiel et court.
  POURQUOI : les pages et écrans de lecture sont en portrait ; un diagramme large déborde ou rétrécit illisiblement.
- **Zéro croisement de flèches** — réordonner les nœuds, regrouper en sous-graphes, ou introduire un nœud intermédiaire plutôt que laisser deux arêtes se croiser.
  POURQUOI : un croisement force le lecteur à suivre une ligne du doigt ; c'est le premier signal de désordre perçu.
- **Labels courts et synthétiques** — nom ou nom+verbe, jamais une phrase. Détail long → note séparée, pas dans le nœud.
- **Un concept par nœud** — si un nœud décrit deux choses, le scinder.
- **Couleur = sens, jamais décoration** — colorer pour porter une information (rôle, état, couche, criticité), pas pour « faire joli ». Rester sobre : quelques classes (`classDef`) réutilisées, contraste lisible en clair comme en sombre. Pas de couleur → pas de perte d'information.
- **Regrouper avec des sous-graphes** quand des nœuds partagent une couche/domaine/phase — la structure visuelle doit refléter la structure logique.
- **Sens de lecture unique** — le flux principal va du haut vers le bas ; les retours/boucles sont l'exception visible, pas la norme.

### Adaptation par type

- **Flowchart** : `TD` ; sous-graphes pour les phases/couches ; une décision = un losange avec sorties étiquetées (`oui`/`non`) et non croisées ; éviter les nœuds à plus de 3 sorties.
- **Sequence** : acteurs ordonnés de gauche à droite selon leur premier appel (minimise les croisements de messages) ; grouper les échanges liés en `alt`/`opt`/`loop` ; activations (`activate`) pour montrer la durée de vie.
- **ER** : cardinalités explicites sur chaque relation ; n'afficher que les attributs porteurs de sens pour le propos du schéma, pas tout le modèle physique.
- **Class** : visibilité et types utiles seulement ; relations d'héritage verticales, associations horizontales ; pas d'attribut cosmétique.
- **State** : un seul état initial `[*]` ; transitions nommées par l'événement déclencheur ; états composites pour regrouper.
- **Gantt / Journey** : réserver aux dimensions temps/expérience ; sections pour regrouper ; ne pas détourner pour un flux logique (→ flowchart).

### Garde-fou

Si respecter « vertical » ou « zéro croisement » rend le diagramme illisible (graphe trop dense), c'est le signal que le diagramme fait trop : le scinder en plusieurs vues plutôt que sacrifier la lisibilité.
