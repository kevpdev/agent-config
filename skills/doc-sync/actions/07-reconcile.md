# 07 - Réconcilier un document de décision

Compare un document de décision au code à HEAD et signale chaque écart, sans jamais l'écrire.

## Input

Les lignes de régime décision de `scope.md`, les documents sans ancre git fiable, et les constats routés par `check-memory`.

## Output

Une liste d'écarts, chacun formulé « la décision affirme X, le code fait Y », avec le repo qui fait foi et les deux issues possibles. Aucune édition.

## Process

1. **Comparer à HEAD, par sous-agent.** « Lis DOC. Pour chaque affirmation vérifiable (endpoint, schéma, classe, statut), vérifie-la contre le code du repo qui l'implémente, à HEAD. Rends ce que la doc affirme, ce que le code fait, et le repo qui fait foi. » Ajouter la règle d'instrument des règles transverses, en clair.
   - En coordinateur, le contrat partagé enjambe les enfants : passer par l'outil inter-dépôts du projet s'il en expose un.
   - Une URL de front se lit dans le fichier de déclaration des routes, jamais dans un graphe de symboles.
2. **Signaler** chaque écart sous la forme « décision affirme X, code fait Y ».
3. **Proposer les deux issues** : entériner l'écart (par `/10-learn` si la décision vit en mémoire AIDD) ou corriger le code. Attendre l'arbitrage.
   - Deux enfants qui se contredisent sur un même fait : décrire la divergence, ne pas trancher.

## Test

| Cas | Preuve |
| --- | --- |
| chaque écart rendu | porte X, Y et le repo qui fait foi |
| `git status --porcelain` avant et après | même sortie |
