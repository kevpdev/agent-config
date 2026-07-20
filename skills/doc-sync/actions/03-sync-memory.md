# 03 - Synchroniser la memory AIDD

Met à jour la memory AIDD de régime reflet, par repo, en déléguant à `/10-learn` si disponible, sinon en édition directe.

## Input

Les cibles de régime **reflet** classées en action 02 qui touchent la memory (`aidd_docs/memory/*`), et le contexte du scope validé. En coordinateur : chaque enfant, plus le contrat au parent (traité en 05, pas ici).

## Output

La memory AIDD des repos concernés mise à jour (via `/10-learn` ou édition directe ciblée), memory d'abord car c'est la source relue par `/plan`.

## Process

1. **Vérifier.** Contrôler si `10-learn` est disponible (skill `aidd-context:10-learn` listé / framework AIDD présent).
2. **Déléguer (cas A — nominal).** Si `10-learn` est disponible, l'invoquer (`/10-learn`) avec le contexte du scope et les catégories de l'action 02.
   - Pourquoi déléguer : `10-learn` a déjà son pipeline scope → write → sync (gate d'approbation + refresh du bloc `<aidd_project_memory>`) et porte ses propres conventions. Le réécrire = divergence garantie.
   - Si `10-learn` ne voit aucune décision/convention durable, la memory descriptive (reflet : `codebase-map`, `api-docs`, `database`) peut quand même nécessiter une MAJ factuelle → basculer sur le cas B pour ces fichiers.
3. **Éditer en direct (cas B — fallback ou MAJ descriptive).** Si `10-learn` est absent, ou pour une MAJ descriptive directe, éditer les fichiers `aidd_docs/memory/*` **de régime reflet** concernés.
   - Appliquer la **règle d'édition directe** (routeur) : lire d'abord la structure/conventions existantes du fichier et s'y conformer.
   - Édition ciblée, jamais de réécriture complète.
4. **Différer les décisions.** Les docs-décision (memory `decisions`, contrat partagé) ne s'éditent **pas** ici en autonomie → régime décision, action 05.

## Test

- La memory de chaque repo concerné est mise à jour avant son README (ordre memory → README respecté).
- Si `10-learn` est disponible, le chemin nominal passe par son invocation, pas par une réécriture maison de son pipeline.
- Aucune édition sur une memory de régime décision (`decisions`) ni sur le contrat partagé dans cette action.
- En édition directe (cas B), la structure existante du fichier a été lue avant toute modification, et l'édition est ciblée (pas de fichier réécrit en entier).
