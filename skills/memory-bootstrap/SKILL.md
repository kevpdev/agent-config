---
name: memory-bootstrap
description: >
  Rattache les repos enfants d'un orchestrateur parent à la memory AIDD centralisée du parent, et
  maintient l'index racine `aidd_docs/memory/coding-assertions.md` que `aidd-dev:03-assert` lit par
  chemin codé en dur. Détecte les enfants orphelins (pas de dossier memory) et les entrées périmées
  (dossier memory sans repo), affiche la preuve d'outillage de chacun, puis n'écrit que ce qui est
  confirmé. Utiliser quand l'utilisateur dit "j'ai cloné un nouveau repo dans le parent", "rattache
  cet enfant à la memory", "mes enfants ne sont pas dans la memory", "amorce la memory du parent",
  "il manque le fichier d'assertions", "un coéquipier veut utiliser le parent comme orchestrateur",
  ou "/memory-bootstrap". NE PAS utiliser pour un mono-repo (→ `aidd-context:02-project-memory`, qui
  y est chez lui), ni pour resynchroniser une doc que le code a fait dériver (→ `doc-sync`), ni pour
  écrire quoi que ce soit dans un repo enfant.
---

# memory-bootstrap

Amorce la memory AIDD d'un **orchestrateur parent** : un repo sans code applicatif propre, qui héberge la memory de N repos enfants autonomes. Il produit deux choses par enfant rattaché — un `aidd_docs/memory/<enfant>/tooling.md` qui décrit son outillage réel, et une ligne dans l'index racine qui dit quelles commandes font **porte**.

> [!important] Pourquoi un index à la racine, et pas seulement des dossiers par enfant
> Le hook `update_memory.js` ne scanne que la **racine** de `aidd_docs/memory/`, plus `internal/` et `external/`. Un `<enfant>/tooling.md` n'apparaît donc **jamais** dans le bloc `<aidd_project_memory>` : le fichier existe, mais rien ne dit qu'il existe. L'index racine, lui, est chargé en `@`-référence et nomme les chemins enfants — c'est lui qui les rend atteignables. Il sert aussi de contrat à `aidd-dev:03-assert`, qui lit `aidd_docs/memory/coding-assertions.md` par chemin codé en dur (`03-assert/actions/01-assert.md`).

## Pourquoi pas `aidd-context:02-project-memory`

Il couvre le même besoin, en mono-repo seulement. Deux obstacles vérifiés, aucun contournable :

- Son `02-generate` porte le Test `find aidd_docs/memory -mindepth 2 -name '*.md'` returns nothing outside `internal/` and `external/`. Une memory par enfant **viole son propre contrat**.
- Il refuse de calculer un chemin : *« The destination is the one the table names. Never derive a path. »* On ne peut donc pas le rediriger vers `<enfant>/`.

Ce skill lui emprunte en revanche deux choses : la **forme** de ses templates (`assets/templates/memory/core/`) et son protocole de confirmation — montrer chaque candidat avec sa preuve, demander d'ajouter ou d'écarter, attendre la réponse.

## Le flux

```
01-scan  →  (tu confirmes)  →  02-attach
```

Il n'y a **pas** de mode « un enfant » distinct d'un mode « tous les enfants ». Le scan trouve ce qui manque, tu confirmes ce qui mérite d'être rattaché, l'attache boucle dessus. Un clone isolé et un amorçage complet suivent le même chemin. *Pourquoi : deux modes séparés dupliqueraient la même logique, donc le même bug à deux endroits.*

`01-scan` seul est utile : il audite le parent sans rien écrire.

## Actions

| Étape | Fichier | Rôle | Écrit |
|---|---|---|---|
| Scan | `actions/01-scan.md` | détecte les enfants, les orphelins, les entrées périmées, et la preuve d'outillage de chacun | rien |
| Attache | `actions/02-attach.md` | écrit `<enfant>/tooling.md`, propose sa ligne d'index, applique ce qui est validé | oui, au parent |

## Règles transverses

- **Ne jamais écrire dans un repo enfant.** Toute sortie atterrit sous `aidd_docs/memory/` du parent. *Pourquoi : les enfants sont des repos d'équipe ; y déposer un `aidd_docs/` est un problème de gouvernance, pas une commodité technique.*
- **L'index pointe vers les enfants, jamais l'inverse.** Un `tooling.md` ne référence pas l'index. *Pourquoi : une back-référence est un doublon à maintenir, donc un doublon qui divergera.*
- **Ne rien committer.** Le skill laisse le working tree au parent. *Pourquoi : le rattachement se relit avant d'entrer dans l'historique.*

Deux règles gouvernent l'écriture et vivent là où elle a lieu, dans `actions/02-attach.md` : le partage d'autorité entre ce qui s'écrit seul et ce qui se propose (étapes 3 et 4), et la provenance des gabarits (étape 1).
