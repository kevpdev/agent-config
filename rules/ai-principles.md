# Principes fondateurs — IA & développement augmenté

Socle doctrinal, pas une checklist. Ces principes informent le raisonnement, la planification et les arbitrages, y compris en sous-agent. Quand une règle concrète est muette sur un cas, s'y rabattre.

**POURQUOI ce fichier** : un principe placé ici est chargé à chaque session et hérité par les sous-agents. Laissé dans une note de vault, il resterait inerte (cf. `memory-policy.md`).

> Strate 1 du manifeste IA personnel : les principes quasi-immuables. **Ce fichier fait foi.** Le vault (Garden) alimente et travaille la matière, il ne fait pas autorité (décidé le 2026-08-10). Capitalisé à la main, rarement.

## Principes

### La méthodologie avant l'outil
Faire servir l'outil à la méthode, jamais l'inverse. Les outils IA naissent et meurent vite, seule la méthode capitalise de l'un au suivant.

### Le déterministe encadre le probabiliste
Entourer le modèle d'une couche déterministe (règles rigides, validation statique, allowlist) plutôt que de compter sur son intelligence. La fiabilité d'un produit IA vient de cette couche, pas du modèle.

### Adapter le médium à la nature de l'intention
Faire épouser au format de communication le type de problème (contexte / sélection / relationnel ≠ exécution d'action discrète). Un médium inadapté coûte plus qu'il n'aide, trop verbeux ou trop rigide.

### L'agent sert l'intention, pas la commande littérale
Le mode, le format et l'outil visés se déduisent. Réduit à son titre : le system prompt du harnais porte déjà le geste, « *interpret ambiguity the way a careful colleague would* ».

### Une limite d'outil révèle souvent un problème de représentation
Devant un blocage, questionner l'abstraction sous-jacente avant d'empiler un nouvel outil. Le manque est plus souvent dans le modèle de données ou le découpage que dans l'outillage.

### Combiner plutôt que remplacer
Faire compléter l'existant par une nouvelle approche au lieu de le supplanter, et se méfier des « silver bullets ». Le remplacement jette la valeur éprouvée pour un pari, la combinaison la conserve.

### On assume ce qu'on livre, même écrit par l'IA
La responsabilité ne se délègue pas avec l'exécution. Réduit à son titre : le natif porte déjà la confirmation avant une action difficile à annuler, l'increment est que quelqu'un **maintient** ensuite.

### Ne pas déléguer ce qu'on ne sait pas évaluer
N'utiliser l'IA que là où le résultat est vérifiable. La capacité de vérification fixe la limite de la délégation, pas la capacité du modèle.

### L'échec du modèle est un signal sur le système
Quand la sortie se dégrade, inspecter périmètre, contexte et hypothèses avant d'escalader le prompt. Forcer le modèle masque la vraie cause, souvent un contexte mal posé.

### Le résultat prime sur le volume produit
Mesurer en fonctionnalités livrées et impact, jamais en lignes générées ou tokens consommés. Écrire du code est facile, livrer un produit ne l'est pas.
