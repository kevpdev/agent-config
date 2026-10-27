# 05 - Contrôler la mémoire

Fait juger la mémoire par un checker qui ne l'a pas écrite, et route chaque constat vers l'action qui le répare.

## Input

Les fichiers touchés par `deliver-memory` et le plan cadré. En `--audit`, tout le scope, puisqu'une entrée gardée à tort n'a produit aucune édition.

## Output

Un rapport au gabarit `aidd-context/skills/02-project-memory/assets/report.md`, écrit sous `aidd_docs/tasks/<aaaa_mm>/<aaaa_mm_jj>_memory-check/report.md`, avec le routage de chaque constat. Aucune édition de mémoire.

## Process

1. **Dispatcher un checker neuf.** Un seul `aidd-dev:checker`, avec dans son prompt :
   - le chemin absolu de [`../references/memory-criteria.md`](../references/memory-criteria.md), comme extension de sa checklist, car il ne le trouvera pas seul dans le projet ;
   - le chemin de `aidd-context/skills/02-project-memory/references/review-protocol.md`, pour les faits que le code contredit ;
   - la règle d'instrument des règles transverses, écrite en clair.
2. **Ne pas lui déléguer `02-project-memory` en bloc.** Garder son protocole et son gabarit, sauter sa correspondance structurelle. Sur un home centralisé, elle classerait chaque fichier d'enfant en orphelin.
3. **Router chaque constat** vers une seule action.

   | Constat | Repart vers |
   | --- | --- |
   | critère non tenu, doublon, copie d'un fichier du disque, hausse non justifiée | `frame-memory` |
   | fait faux ou périmé, chemin ou commande inexistant | `deliver-memory` |
   | écart sur un document de décision | `reconcile`, et il sort du cycle |

4. **Borner.** Le rapport ouvre sur `Passe n sur 3` et la liste des constats déjà déclarés réparés. Trois contrôles au plus.
   - **Garde.** Zéro constat actionnable, sortie nominale. Un constat déclaré réparé qui revient, ou un lot qui ne rétrécit pas, arrêt immédiat. Les constats partis à `reconcile` ne comptent pas dans le lot.
   - *Pourquoi trois : une passe répare un constat bien diagnostiqué, la deuxième ce que la réparation a cassé. Une troisième signale un diagnostic faux.*
5. **Échouer fermé.** Hors sortie nominale, ne jamais déclarer le banc à jour ni rien annuler. Le rapport nomme les constats non réparés et joint `git diff --stat -- aidd_docs/memory/`.

## Test

| Cas | Preuve |
| --- | --- |
| le prompt de dispatch | cite le chemin absolu de `memory-criteria.md` et la règle d'instrument |
| le rapport | existe au chemin attendu et s'ouvre sur `Passe n sur 3` |
| une sortie non nominale | le rapport joint le `git diff --stat`, le banc n'est pas déclaré à jour |
| `git status --porcelain aidd_docs/memory/` avant et après | même sortie |
