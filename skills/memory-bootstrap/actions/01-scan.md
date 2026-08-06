# 01 - Scanner

Relever les enfants git du parent, les deux dérives possibles, et la preuve d'outillage de chaque candidat. N'écrit rien.

## Input

Le CWD, qui doit être la racine de l'orchestrateur parent. Optionnellement un nom d'enfant, pour restreindre le scan à celui-là.

## Output

Trois listes et un verdict :

```
enfants git       : <chemin> (N)
orphelins         : enfant git sans aidd_docs/memory/<nom>/ — avec sa preuve d'outillage
périmés           : aidd_docs/memory/<nom>/ sans enfant git correspondant
index racine      : présent | absent
```

## Process

1. **Situer.** Confirmer que le CWD est bien un parent orchestrateur : un `aidd_docs/memory/` existe, et l'étape 2 rend au moins un enfant. Si le CWD n'a **aucun** projet enfant, s'arrêter et renvoyer vers `aidd-context:02-project-memory`, qui y est chez lui.
2. **Détecter les enfants.** Appeler le script partagé, **ne pas réimplémenter** :
   ```
   bash "$SKILLS_ROOT/_shared/detect-children.sh" --long
   ```
   La règle qu'il applique, ses contre-exemples mesurés et le `basename` du home memory vivent dans ses commentaires — un seul home (R6). *Pourquoi un script et pas la consigne d'avant : elle cherchait un `.git`, donc un projet enfant non versionné à part restait invisible. Un monorepo back+front y ressortait « mono-repo » et personne ne voyait que deux projets étaient sans porte.*
   - La colonne `MEMORY` sert directement l'étape 3 ; la colonne `BUILD` sert l'étape 4 (elle **nomme déjà** le manifeste, quand il y en a un).
3. **Croiser dans les deux sens.** Un enfant sans `aidd_docs/memory/<nom>/` est un **orphelin**. Un `aidd_docs/memory/<nom>/` sans enfant correspondant est une **entrée périmée** — hors `internal/` et `external/`, qui ne sont pas des enfants. *Pourquoi : sans le second sens, un projet retiré laisse une entrée qui survit jusqu'à ce qu'une session la remarque par hasard.*
4. **Chercher la preuve d'outillage.** Pour chaque orphelin, relever ce qui rend une porte possible : le manifeste déjà nommé par la colonne `BUILD`, un script de test, une commande de vérification. Nommer le fichier trouvé, pas une impression.
   - Aucune preuve → le marquer **sans porte**. Il pourra recevoir un `tooling.md` descriptif, mais aucune ligne d'index. *Pourquoi : un index rempli de lignes vides cesse d'être un contrat et redevient une liste.*
5. **Relever l'index.** Vérifier la présence de l'index racine et, s'il existe, quels enfants y figurent déjà. Un enfant présent dans l'index mais absent de la liste détectée est une entrée périmée de plus.
6. **Écarter ce qui a déjà été tranché.** Un enfant listé comme exclu dans l'index n'est **pas** re-proposé : le rappeler en une ligne, avec sa raison, et passer. Le relancer dans la liste des candidats ne se fait que si l'humain le demande. *Pourquoi : une question déjà répondue n'est plus une information, c'est du bruit qui fait rater les vraies — et un repo de doc ou de config resterait candidat à chaque run.*
   - Un exclu peut rester **utile comme source** (templates CI, config par environnement). Le signaler comme tel plutôt que le taire : n'avoir aucune porte à soi n'empêche pas de faire foi pour les portes des autres.
7. **Rendre.** Afficher les trois listes, chaque orphelin accompagné de sa preuve ou de sa mention « sans porte ». Demander lesquels rattacher et attendre la réponse. Ne rien écrire à cette étape.

## Test

- `git status --porcelain` rend la même sortie avant et après le scan : aucun fichier touché.
- La liste des enfants vient de `_shared/detect-children.sh`, pas d'une commande recopiée ici. Elle inclut un enfant placé directement à la racine du parent, un enfant groupé (`backend/<x>`), et un enfant **non versionné à part** (monorepo) — ce dernier est le cas que l'ancienne détection ratait entièrement.
- Chaque orphelin listé porte soit un chemin de fichier comme preuve d'outillage, soit la mention explicite « sans porte ».
- Un enfant listé comme exclu dans l'index n'apparaît pas dans les candidats au rattachement : il est rappelé une fois, avec sa raison, et rien n'est demandé à son sujet.
- Sur un projet **sans aucun enfant**, le scan s'arrête à l'étape 1 et ne propose aucun rattachement. Le critère est « zéro enfant détecté », **pas** « un seul `.git` » : un monorepo qui contient deux projets a bien des enfants et doit être scanné.
