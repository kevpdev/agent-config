# 02 - Attacher

Écrire le `tooling.md` de chaque enfant confirmé, puis proposer sa ligne dans l'index racine.

## Input

La liste des enfants confirmés au rattachement, issue de `01-scan`, chacun avec sa preuve d'outillage ou sa mention « sans porte ».

## Output

Sous `aidd_docs/memory/` du parent : un `<enfant>/tooling.md` par enfant confirmé, et un index racine `coding-assertions.md` amendé. Plus un relevé de ce qui a changé et de ce qui reste à arbitrer.

## Process

1. **Prendre le gabarit sur un frère.** Avant d'écrire un `tooling.md`, en lire un existant et en reprendre les sections, l'ordre, le format des tables et le ton. Aucun frère → reprendre la forme du template `core/tooling` ou `core/testing` d'`aidd-context:02-project-memory`. *Pourquoi : une forme divergente au milieu de fichiers déjà homogènes se lit comme une erreur, et personne ne la corrige ensuite.*
2. **Lire l'outillage à la source.** Ouvrir le manifeste de build, les scripts, la config de test et la config CI de l'enfant. Relever la commande de test, la commande de build, les linters présents, et les prérequis d'infra qu'un test exige. Ne jamais reprendre une valeur depuis un README.
   - Une valeur non retrouvée dans le code ou la config se marque **à confirmer**, jamais en affirmation. *Pourquoi : une commande fausse dans l'index fait échouer une porte pour une raison qui n'a rien à voir avec le code.*
3. **Écrire le `tooling.md`.** Cible `aidd_docs/memory/<enfant>/tooling.md`, au parent. Il décrit ce que le code fait déjà, donc il s'écrit sans arbitrage.
   - Enfant déjà présent → **réviser le fichier en place**, en gardant les passages que l'humain a écrits. Ne jamais en créer un second. *Pourquoi : sans révision en place, un second passage duplique tout et l'index se remplit de doublons.*
4. **Proposer les lignes d'index.** Pour chaque enfant portant une preuve d'outillage, composer sa ligne dans les tables de l'index, remplie des commandes relevées, avec ses prérequis bloquants. Les **soumettre** avant d'écrire : c'est l'humain qui décide lesquelles font porte.
   - Un enfant marqué « sans porte » ne reçoit **aucune** ligne de commande. Il va dans la section de l'index qui recense les repos sans porte, avec la raison constatée et ce qui tient lieu de validation.
   - *Pourquoi cette asymétrie avec l'étape 3 : décrire un outillage est un constat, en faire une porte de commit est une décision.*
5. **Amender l'index, pas le réécrire.** Insérer ou réviser les lignes validées en gardant la forme et l'ordre en place. Un enfant déjà listé voit sa ligne révisée.
   - Une **entrée périmée** relevée au scan se signale et ne s'enlève que sur accord explicite. *Pourquoi : un dossier sans repo peut être un clone momentanément absent plutôt qu'un repo retiré.*
6. **Rendre.** Lister les fichiers écrits, les lignes ajoutées ou révisées, et ce qui reste en attente d'arbitrage.

## Test

- Chaque enfant confirmé a un `aidd_docs/memory/<enfant>/tooling.md` sous le parent.
- Le repo enfant n'a pas bougé : `git -C <enfant> status --porcelain` rend la **même sortie avant et après** l'action. Comparer les deux, ne pas exiger un arbre propre — un enfant peut être sale pour des raisons étrangères au skill, et l'exiger vide ferait échouer le test sans qu'il y ait de défaut.
- Relancer l'action sur un enfant déjà rattaché ne crée ni second fichier ni seconde ligne : le nom de l'enfant apparaît une seule fois par table de l'index.
- Un enfant marqué « sans porte » figure dans la section des repos sans porte et dans aucune table de commandes.
- Aucune commande de l'index ne provient d'un README : chaque valeur est retrouvable dans le code, la config ou la CI de l'enfant, ou porte la mention « à confirmer ».
- L'index reste chargeable en `@`-référence : il est à la racine de `aidd_docs/memory/`, pas dans un sous-dossier.
