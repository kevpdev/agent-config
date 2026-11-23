# 03 - Appliquer

Monte les plugins, applique les patchs du plan, et laisse une trace de la transition pour la prochaine
machine.

## Input

Un plan en `statut: planifie`, explicitement validé par l'humain dans le tour courant.

## Output

Les plugins montés, les fichiers du repo patchés, une entrée de `CHANGELOG-aidd.md` proposée, et
`statut: applique`.

## Process

1. **Vérifier le mandat.** Ne rien lancer sans un accord de l'humain dans ce tour. Un plan écrit hier
   n'est pas un accord.
   - Pourquoi : appliquer sur la foi d'un plan déjà sur disque reproduit exactement l'auto-update que
     ce montage remplace.
2. **Monter.** Pour chaque runtime de `runtimes`, et pour lui seul, lancer ses commandes de montée
   (`../references/detecteur.md`, « Commandes de montée, par runtime »).
   - Sur échec d'un runtime ou d'un plugin, s'arrêter et le dire. Ne pas patcher des appels vers une
     version qui n'est pas installée.
3. **Vérifier chaque runtime.** Lancer la vérification de la même table pour chaque runtime monté,
   puis `--refresh` et `--etat` : `retards` doit être vide.
4. **Patcher.** Appliquer les remplacements du tableau du plan, un fichier à la fois.
   - Après chaque fichier, re-grep l'ancien nom dans tout le repo. Zéro occurrence restante, sinon
     dire lesquelles subsistent.
5. **Tracer.** Proposer l'entrée de `CHANGELOG-aidd.md` au format des sections existantes, c'est-à-dire
   une transition et non un état.
   - Ne jamais y écrire les versions installées sur cette machine, l'avertissement en tête du fichier
     l'interdit et une version écrite là devient fausse à la montée suivante.
6. **Clore.** Lancer `--marquer-applique`, puis rappeler que les skills et agents ne sont pas
   rechargés à chaud, donc qu'il faut redémarrer la session.
7. **Ne pas committer.** Laisser le diff en l'état et le dire.
   - Pourquoi : le commit est un geste d'approbation, il revient à l'humain qui assume ce qui est
     livré.

## Test

| Cas | Preuve |
| --- | --- |
| la vérification de chaque runtime de `runtimes` (`../references/detecteur.md`) | rend les versions cibles du plan |
| `runtimes` ne contient que `opencode` | aucune commande du runtime Claude n'est proposée ni lancée |
| `grep -rn '<chaque ancien nom>' skills/ rules/ wrappers/` | rend zéro occurrence |
| `--etat` relancé après l'action | rend `statut: applique`, et `--notify` ne produit plus rien |
| `bash tools/test-all.sh` | reste vert |
| `git status` | montre un diff non committé, et aucune écriture hors du repo sauf le fichier d'état |
