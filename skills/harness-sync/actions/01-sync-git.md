# 01 - Aligner le dépôt local sur origin

Rapatrie les commits distants par fast-forward, et rien d'autre.

## Output

Une ligne de statut : « à jour », « mis à jour (fast-forward, N commits) », ou « KO » suivi de sa raison.

## Process

1. **Vérifier la propreté.** Lancer `git status --porcelain`.
   - **Garde.** Sortie non vide → arrêter ici, rendre KO « working tree non propre », ne jamais stasher ni annuler un changement à la place de l'humain.
2. **Vérifier la cible.** Résoudre l'upstream de la branche courante (`git rev-parse --abbrev-ref --symbolic-full-name @{u}`).
   - **Garde.** HEAD détaché ou pas d'upstream configuré → arrêter, rendre KO « branche sans cible », laisser l'humain choisir la branche à synchroniser.
3. **Récupérer l'état distant.** Lancer `git fetch` sur le remote de cet upstream.
   - **Garde.** Échec réseau ou authentification → arrêter, rendre KO avec la sortie brute de git, ne jamais la réinterpréter.
4. **Comparer les deux historiques.** Lire `git rev-list --left-right --count HEAD...@{u}` (ahead, behind).
   - Zéro partout → rendre « à jour », s'arrêter là.
   - Behind seul → passer à l'étape 5.
   - Ahead seul → arrêter, rendre KO « avance locale, rien poussé » : un push est une action visible pour autrui, jamais automatique.
   - Ahead et behind → arrêter, rendre KO « divergence » avec les deux journaux (`git log HEAD..@{u}` et `git log @{u}..HEAD`), jamais de merge ni de rebase joué à la place de l'humain.
5. **Fast-forward.** Lancer `git merge --ff-only @{u}`.
   - **Garde.** Échec malgré un cas « behind seul » détecté à l'étape 4 → arrêter, rendre KO avec la sortie brute de git : la situation est incohérente et se remonte telle quelle.
6. **Rendre le résultat.** Le nombre de commits rapatriés et le nouveau `HEAD`.

## Test

| Cas | Preuve |
| --- | --- |
| `echo x >> README.md` puis relance | KO « working tree non propre », `git status` toujours identique après |
| `git checkout --detach HEAD` puis relance | KO « branche sans cible » |
| dépôt déjà aligné sur son upstream | « à jour », aucune commande d'écriture jouée |
| dépôt en retard simple (`git reset --hard HEAD~1` sur une copie de test) | fast-forward joué, nombre de commits rapporté, `git status --porcelain` reste vide après |
| un commit local non poussé et un commit distant non tiré (divergence simulée sur une copie de test) | KO « divergence », les deux `git log` cités, `HEAD` inchangé |
