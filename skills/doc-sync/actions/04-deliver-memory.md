# 04 - Livrer la mémoire

Écrit le plan validé par `frame-memory`, en déléguant à `/10-learn` quand il peut écrire au bon endroit.

## Input

Le plan de mémoire validé, et le home de chaque cible lu dans `scope.md`.

## Output

Les fichiers de mémoire mis à jour, chaque édition rattachée à une ligne du plan.

## Process

1. **Choisir la voie.** `aidd-context:10-learn` disponible et home à plat (mono-repo, ou enfant distribué lancé chez lui) : déléguer. Sinon, éditer en direct.
   - **Garde.** Home centralisé (`aidd_docs/memory/<enfant>/`), ne pas déléguer : `10-learn` écrit à plat et toucherait la racine du parent.
2. **Déléguer.** Invoquer `/10-learn` avec le scope et les verdicts du plan. *Pourquoi les verdicts : ses quatre poids ignorent si un fait est reconstructible, et sans eux un fait inférable repasse.*
   - Un fait descriptif que `10-learn` ne retient pas peut quand même demander une mise à jour : il passe en édition directe.
3. **Éditer en direct.** Lire la structure du fichier avant de l'éditer et s'y conformer. Edits ciblés, jamais de réécriture complète. Un pointeur s'écrit comme un chemin, jamais comme un résumé de ce qu'il pointe.
4. **Déporter avant de supprimer.** Un fait qui devient pointeur doit exister au home destinataire avant que sa copie parte.
5. **Rejouer ce qui dépendait d'une correction.** `grep` le fait corrigé dans le home, et relancer la mesure de chaque affirmation qui le cite. *Pourquoi : mesuré le 2026-08-21, deux des treize faits faux d'un contrôle étaient des régressions créées par la passe elle-même.*

## Test

| Cas | Preuve |
| --- | --- |
| chaque hunk de `git diff aidd_docs/memory/` | correspond à une ligne du plan |
| un fichier de régime décision | absent du diff |
| un home centralisé | édité en direct, aucun appel à `10-learn` |
