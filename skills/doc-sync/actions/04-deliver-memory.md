# 04 - Livrer la mémoire

Écrit le plan validé par `frame-memory`, en déléguant à `/10-learn` quand il peut écrire au bon endroit.

## Input

Le plan de mémoire validé, et le home de chaque cible lu dans `scope.md`.

## Output

Les fichiers de mémoire mis à jour, chaque édition rattachée à une ligne du plan.

## Process

1. **Vérifier que le home est propre**, à la première entrée seulement, jamais sur un retour de la boucle de contrôle, direct depuis `check-memory` ou via `frame-memory`. `git status --porcelain -- <home mémoire du scope>` (`aidd_docs/memory/`, ou `aidd_docs/memory/<enfant>/`) doit être vide dans chaque repo. Sinon, s'arrêter et nommer les fichiers modifiés, sauf opt-in « WIP non commité » posé par `01-detect-scope`. *Pourquoi : `10-learn` comme l'édition directe mêleraient leurs edits aux modifications en cours, et git ne sait plus les séparer.*
2. **Choisir la voie.** `aidd-context:10-learn` disponible et home à plat (mono-repo, ou enfant distribué lancé chez lui) : déléguer. Sinon, éditer en direct.
   - **Garde.** Home centralisé (`aidd_docs/memory/<enfant>/`), ne pas déléguer : `10-learn` écrit à plat et toucherait la racine du parent.
3. **Déléguer.** Invoquer `/10-learn` avec le scope et les verdicts du plan. *Pourquoi les verdicts : ses quatre poids ignorent si un fait est reconstructible, et sans eux un fait inférable repasse.*
   - Un fait descriptif que `10-learn` ne retient pas peut quand même demander une mise à jour : il passe en édition directe.
4. **Éditer en direct.** Lire la structure du fichier avant de l'éditer et s'y conformer. Edits ciblés, jamais de réécriture complète. Un pointeur s'écrit comme un chemin, jamais comme un résumé de ce qu'il pointe.
5. **Déporter avant de supprimer.** Un fait qui devient pointeur doit exister au home destinataire avant que sa copie parte.
6. **Rejouer ce qui dépendait d'une correction.** `grep` le fait corrigé dans le home, et relancer la mesure de chaque affirmation qui le cite. *Pourquoi : mesuré le 2026-08-21, deux des treize faits faux d'un contrôle étaient des régressions créées par la passe elle-même.*

## Test

| Cas | Preuve |
| --- | --- |
| chaque hunk de `git diff aidd_docs/memory/` | correspond à une ligne du plan |
| un fichier de régime décision | absent du diff |
| un home centralisé | édité en direct, aucun appel à `10-learn` |
| le home mémoire modifié et non commité à la première entrée, sans opt-in WIP | arrêt avant toute écriture, le fichier est nommé, `git diff` inchangé |
| un retour de `check-memory` après une première passe | pas d'arrêt sur les fichiers que la passe précédente a écrits |
