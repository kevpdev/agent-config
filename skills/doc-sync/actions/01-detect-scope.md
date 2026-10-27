# 01 - Détecter le scope

Choisit l'entrée, détecte où vivent le code et la doc, et fait confirmer le scope avant toute édition.

## Input

- Le répertoire courant, à la racine du repo ou du coordinateur.
- Le flag `--audit` éventuel, et l'opt-in « WIP non commité » éventuel.

## Output

L'en-tête de `$(git rev-parse --git-dir)/doc-sync/scope.md` : l'entrée, la topologie, la branche et le SHA de chaque dépôt, et la liste des fichiers confirmée.

## Process

1. **Choisir l'entrée, avant tout le reste.** `--audit` la tranche. Sans flag, « la doc a pris du retard » est un diff, « relis la doc, elle a dérivé » est un audit.
   - **Garde.** Si les deux lectures tiennent, demander. *Pourquoi : un diff pris pour un audit rend « rien de touché » et s'arrête sur un faux succès.*
2. **Détecter la topologie.** Lancer `bash "$SKILLS_ROOT/_shared/scripts/detect-children.sh" --long` depuis la racine.
   - Aucun enfant donne un mono-repo. Sinon c'est un coordinateur : la colonne `MEMORY` donne le home de mémoire de chaque enfant, la colonne `VCS` dit s'il commite à part.
   - **Garde.** `$SKILLS_ROOT` vide, s'arrêter et le dire. La commande sortirait en 127 et accuserait le script au lieu de la config.
   - Lancé depuis un sous-dossier, le script rend « mono-projet » à tort. Ne jamais réimplémenter la détection ici.
3. **Vérifier la branche.** Chaque dépôt du run doit être sur sa branche par défaut, alignée sur le remote. Lire le défaut au serveur avec `git remote set-head origin -a`, puis `git symbolic-ref --short refs/remotes/origin/HEAD`.
   - **Garde.** Un dépôt ailleurs ou en retard, rendre la main en le nommant. Ne pas basculer soi-même.
   - *Pourquoi lire au serveur : `origin/HEAD` se pose au clone et aucun fetch ne le rafraîchit. Mesuré le 2026-08-27, 3 dépôts sur 33 annonçaient un défaut périmé.*
4. **Ancrer.** Établir le scope selon l'entrée.

   | Entrée | Scope proposé |
   | --- | --- |
   | diff, cas normal | `base=$(git log -1 --format=%H -- <docs du repo>)`, puis `git diff --name-only $base...HEAD` |
   | diff, features mergées sans doc | pas d'ancre fiable, les documents concernés partent à `reconcile` contre HEAD |
   | WIP opt-in | `git diff --name-only HEAD`, en avertissant que c'est du non-validé |
   | `--audit` | pas d'ancre : les documents éligibles eux-mêmes, avec `wc -w` par fichier |

5. **Confirmer.** Montrer commits et fichiers par dépôt, puis faire confirmer ou élaguer.
   - En `--audit`, proposer un seul fichier par défaut, le plus lourd. Élargir reste possible, nommément. *Pourquoi : mesuré le 2026-08-21, 5 fichiers ont rendu 31 constats, plus que ce que trois passes de contrôle réparent.*
   - En coordinateur, faire confirmer quels documents du parent tiennent le rôle de contrat partagé. Aucun nom de fichier n'est conventionné.
6. **Écrire l'en-tête** de `scope.md`. Aucun autre fichier n'est touché à ce stade.

## Test

| Cas | Preuve |
| --- | --- |
| un run lancé avec `$SKILLS_ROOT` vide | le skill s'arrête et nomme la variable |
| un dépôt sur une branche de feature | le skill rend la main en le nommant, sans `git checkout` |
| un run `--audit` | `scope.md` porte un décompte de mots par fichier et aucun range de commits |
| `git status --porcelain` avant et après l'action | même sortie, rien n'a été édité |
