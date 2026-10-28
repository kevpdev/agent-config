## Diagrammes Mermaid — deux non-négociables

S'applique à tout diagramme Mermaid produit par toi, un sous-agent ou un skill.

- **Vertical par défaut** (`TD`/`TB`) — horizontal (`LR`) seulement si le flux est court et intrinsèquement séquentiel.
  POURQUOI : les pages et écrans de lecture sont en portrait. Un diagramme large déborde ou rétrécit illisiblement.
  **CE DÉFAUT ÉCRASE CELUI D'AIDD, qui dit l'inverse** : `aidd-context:09-mermaid`, fichier `references/mermaid-conventions.md`, déclare « *Flow direction defaults to `LR` unless the source implies another* ». Ne pas lire ce `LR` comme le défaut au motif que c'est le skill qui dessine.
- **Zéro croisement de flèches** — réordonner les nœuds, regrouper en sous-graphes, ou introduire un nœud intermédiaire plutôt que laisser deux arêtes se croiser.
  POURQUOI : un croisement force le lecteur à suivre une ligne du doigt. C'est le premier signal de désordre perçu.

**Charger le skill `mermaid-craft` avant d'écrire un bloc `mermaid` non trivial**, il fait foi. Ces deux critères ne sont que l'alerte.

Raison du découpage entre règle et skill → `rules/references/ref-mermaid.md`.
