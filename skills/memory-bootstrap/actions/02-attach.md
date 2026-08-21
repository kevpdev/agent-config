# 02 - Attacher

Écrire le `tooling.md` de chaque enfant confirmé, puis proposer sa ligne dans l'index racine.

## Input

La liste des enfants confirmés au rattachement, issue de `01-scan`, chacun avec sa preuve d'outillage ou sa mention « sans porte ».

## Output

Sous `aidd_docs/memory/` du parent : un `<enfant>/tooling.md` par enfant confirmé, et un index racine `coding-assertions.md` amendé. Plus un relevé de ce qui a changé et de ce qui reste à arbitrer.

## Process

1. **Prendre le gabarit sur un frère.** Avant d'écrire un `tooling.md`, en lire un existant et en reprendre les sections, l'ordre, le format des tables et le ton. Aucun frère → reprendre la forme du template `core/tooling` ou `core/testing` d'`aidd-context:02-project-memory`. *Pourquoi : une forme divergente au milieu de fichiers déjà homogènes se lit comme une erreur, et personne ne la corrige ensuite.*
   - **Le gabarit donne la forme, jamais le contenu de `## Pièges connus`.** Un piège se réécrit depuis le code de l'enfant qu'on décrit, ou ne s'écrit pas. Reprendre celui du frère produit un fait faux, puisqu'il a été mesuré sur un autre repo.
   - **Un piège que plusieurs enfants partagent ne s'écrit qu'une fois, chez sa cause**, et les autres fiches ne le portent pas. Si la cause est un dépôt du workspace, sa fiche est son home ; s'il n'en a pas, c'est le signal qu'un producteur n'est pas documenté.
     - *Pourquoi, mesuré le 2026-08-21 sur un banc de 31 enfants : la section `## Pièges connus` existe dans 27 fiches pour 7 857 mots, soit 17 % du banc, et **aucune** source ne la prescrit — ni ce skill, ni le framework. Elle s'est propagée par la recopie du frère. Trois causes uniques y portaient 54, 52 et 11 mentions, et celle qui en portait le plus n'avait aucune fiche.*
2. **Lire l'outillage à la source.** Ouvrir le manifeste de build, les scripts, la config de test et la config CI de l'enfant. Relever la commande de test, la commande de build, les linters présents, et les prérequis d'infra qu'un test exige. Ne jamais reprendre une valeur depuis un README.
   - Une valeur non retrouvée dans le code ou la config se marque **à confirmer**, jamais en affirmation. *Pourquoi : une commande fausse dans l'index fait échouer une porte pour une raison qui n'a rien à voir avec le code.*
3. **Écrire le `tooling.md`.** Cible `aidd_docs/memory/<enfant>/tooling.md`, au parent. Il décrit ce que le code fait déjà, donc il s'écrit sans arbitrage. **Sans arbitrage ne veut pas dire sans vérification** — c'est la prose de la fiche, pas les commandes de l'index, qui affirme le plus.
   - **Chaque affirmation de la fiche porte sa trace ou son marqueur** : un chemin, un `fichier:ligne`, une sortie de commande — sinon `supposé` / `à confirmer`. C'est le point d'application de `reasoning.md` dans ce flux, et il couvre **toute** la prose, pas seulement les valeurs d'outillage de l'étape 2. *Pourquoi : une fiche est relue plus tard comme un constat établi. Une phrase non tracée y devient un fait, et plus rien ne signale qu'elle n'a jamais été vérifiée.*
   - **À LA PLACE de** conclure depuis une observation voisine → ouvrir la source de l'affirmation elle-même. Trois substitutions mesurées sur ce skill (2026-07-30) : un **nom de fichier** pris pour son contenu, un `find` **borné en profondeur** pris pour un dossier vide, un **décompte** de fichiers de test pris pour une mesure de couverture.
   - Un **superlatif** (« seul », « le plus », « aucun autre ») n'entre dans une fiche qu'accompagné de l'ensemble énuméré. *Pourquoi : c'est l'affirmation la plus coûteuse à démentir plus tard, et la moins chère à vérifier sur le moment.*
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
- **Aucun piège d'une fiche neuve ne se retrouve mot pour mot dans la fiche qui a servi de gabarit.** Un piège recopié n'a pas été mesuré sur l'enfant qu'il décrit.
- **Un piège présent dans plusieurs fiches est un défaut**, sauf si chaque occurrence cite une mesure faite sur son propre repo. Sinon il vit chez sa cause, et une seule fois.
- **La prose de chaque `tooling.md` passe le même contrôle que les commandes** : toute phrase affirmative est traçable (chemin, `fichier:ligne`, sortie de commande) ou marquée `supposé` / `à confirmer`. Contrôle rapide et suffisant : relever les **superlatifs** et les **comparaisons** de la fiche — chacun doit citer l'ensemble énuméré ou la mesure qui le fonde.
  - *Pourquoi cette ligne existe : jusqu'au 2026-07-30, ce bloc ne testait que les commandes de l'index. Sept affirmations non vérifiées sont passées par la prose des fiches, dont deux fausses. Ne pas restreindre ce test aux commandes en le « simplifiant ».*
- L'index reste chargeable en `@`-référence : il est à la racine de `aidd_docs/memory/`, pas dans un sous-dossier.
