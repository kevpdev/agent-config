## Diagrammes Mermaid — deux non-négociables

S'applique à tout diagramme Mermaid produit par toi, un sous-agent ou un skill.

- **Vertical par défaut** (`TD`/`TB`) — horizontal (`LR`) seulement si le flux est court et intrinsèquement séquentiel.
  POURQUOI : les pages et écrans de lecture sont en portrait ; un diagramme large déborde ou rétrécit illisiblement.
- **Zéro croisement de flèches** — réordonner les nœuds, regrouper en sous-graphes, ou introduire un nœud intermédiaire plutôt que laisser deux arêtes se croiser.
  POURQUOI : un croisement force le lecteur à suivre une ligne du doigt ; c'est le premier signal de désordre perçu.

**Ces deux critères ne suffisent pas, et ne prétendent pas suffire** — ils ne sont que l'alerte. Un diagramme écrit sur cette seule base rate les labels, un concept par nœud, la couleur porteuse de sens, les sous-graphes, le garde-fou de scission, et tout le craft propre au type (flowchart, sequence, ER, class, state, gantt). **Charger le skill `mermaid-craft` avant d'écrire un bloc `mermaid` non trivial** — il fait foi, et ne pas le charger sous prétexte que cette règle a l'air complète.

**POURQUOI ce découpage** : un diagramme surgit souvent dans une réponse sans qu'aucun skill soit invoqué — ces deux critères doivent donc être présents en permanence. Le détail, lui, ne sert qu'au moment de dessiner : le charger en continu ferait payer à chaque session un contexte utilisé quelques fois par mois.
