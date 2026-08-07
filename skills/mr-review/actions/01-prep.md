# 01 - Préparer

Met la MR en état d'être relue : périmètre exact du diff, branche locale, suite de tests lancée.

## Input

Le numéro de MR (`449`) ou son URL. Le repo si la session n'est pas dans le clone concerné.

## Output

Une fiche courte : titre de la MR, **son état** (`opened`, `merged`, `closed`), branche source → cible,
`base_sha`, `head_sha`, nombre de commits, nombre de fichiers touchés, résultat chiffré de la suite de
tests. Plus une branche locale de revue.

L'état est relevé ici parce que `04-route` en dépend : une MR déjà mergée ne reçoit pas le même retour
qu'une MR ouverte. Le mesurer, ne pas le supposer d'après la date ou le nom de branche — et le recouper
côté git, la pointe de la branche cible étant la source qui fait autorité sur ce qui est déployé
(`git branch -r --contains <head_sha>`).

## Process

1. **Vérifier l'accès, avant tout le reste.** Tester `glab auth status` et lire son code de retour —
   codes et pièges dans `references/glab-et-base-du-diff.md`.
   - Code non nul → **s'arrêter immédiatement**. Rendre à l'utilisateur la cause lue dans la sortie
     (token expiré, hôte injoignable) et la commande à lancer pour y remédier, typiquement
     `glab auth login`. Ne rien lire d'autre, ne rien deviner, ne pas enchaîner.
   - Le contrôle passe en premier parce qu'un échec d'accès plus tard dans l'étape ressemble à un
     périmètre introuvable, et se corrige alors au mauvais endroit.
2. **Situer.** Identifier le repo, depuis l'URL de la MR ou depuis le clone courant. Si plusieurs
   clones cohabitent sous un repo parent, retenir celui dont le remote correspond au projet de la MR.
3. **Récupérer.** Lire les métadonnées de la MR — voir la référence pour les commandes. Il faut le
   titre, la description, les branches source et cible, `diff_refs`, la liste des commits et la liste
   des fichiers touchés.
   - Si `diff_refs` est nul, l'appel utilisé était celui de liste. Refaire l'appel unitaire.
   - Un appel qui sort en code non nul est traité comme l'étape 1 : arrêt et alerte, **après** avoir
     nommé la cause. Un `401` est un problème de token. Un `404` a **trois** causes, et la troisième
     n'est pas un problème d'accès : mauvais `iid`, projet interdit, ou **commande lancée hors du
     clone** — `glab api` résout l'hôte depuis le remote git du répertoire courant (détail et
     contournement dans la référence). Écarter la troisième avant d'annoncer les deux autres : c'est la
     seule qui se corrige sans rien demander à personne.
4. **Rafraîchir.** `git fetch --all --prune` sur le clone. Un clone en retard rend `base_sha`
   introuvable localement, ce qui ressemble à une base fausse alors que c'est un `fetch` manquant.
5. **Lire la base.** Prendre `diff_refs.base_sha` et `diff_refs.head_sha` tels quels. Ne rien
   dériver : la référence explique pourquoi `git merge-base` et le nombre de commits donnent un faux
   résultat, chacun de façon silencieuse.
6. **Contrôler.** Comparer le nombre de fichiers touchés côté GitLab et côté local. Un écart n'est
   acceptable que s'il s'explique par un renommage — critère détaillé dans la référence.
   - Si l'écart ne s'explique pas, **s'arrêter** et le dire. Ne pas rendre de revue sur un périmètre
     douteux : le reviewer paraîtrait confiant sur les mauvaises lignes.
7. **Basculer.** Créer la branche locale de revue sur `head_sha`, nommée d'après la MR. Une branche
   nommée évite de reviewer par accident depuis l'ancienne branche encore sortie.
8. **Tester.** Lancer la suite du repo. La recette vit dans la mémoire projet
   (`aidd_docs/memory/<projet>/tooling.md`) quand elle existe, sinon se déduire du gestionnaire de
   build.
   - Toujours en repartant d'un build propre. Une classe compilée d'une autre branche produit des
     erreurs massives qui n'ont rien à voir avec la MR, et qu'on impute à tort au diff.
   - Un échec ne bloque pas la suite. Il devient un fait de la fiche, et sa cause se reproduit avant
     d'être énoncée.

## Contrôle de sortie

- La branche locale de revue existe et pointe sur `head_sha`.
- `git diff --name-only <base_sha>..<head_sha>` rend une liste non vide, et la comparaison d'ensembles
  avec la liste GitLab ne laisse aucun chemin inexpliqué.
- La fiche porte tous les éléments listés en `## Output`, chacun renseigné — aucun « inconnu ».
- Le résultat des tests est un chiffre (nombre de tests, d'échecs, d'erreurs), pas une appréciation.

## Test

Scénarios dans `evals/eval.json`. Ils portent le cas de l'échec d'accès : c'est le seul comportement de
cette action qu'aucun contrôle de sortie n'atteint, puisqu'il se juge sur ce que l'action **ne** fait
pas — ne pas dériver la base à la main, ne pas créer de branche, ne pas enchaîner.
