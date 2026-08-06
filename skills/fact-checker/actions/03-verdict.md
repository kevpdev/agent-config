# 03 - Trancher

Pondère les entrées rapportées, rend un verdict par affirmation, et assume l'abstention quand les sources manquent.

## Input

Les entrées structurées de `02-rechercher`, et la table d'affirmations de `01-decomposer` pour le contrôle de complétude.

## Output

Le rapport rempli d'après le gabarit `../assets/rapport-fact-check.md`.

## Process

1. **Pondérer.** Noter chaque source par son `tier` et son biais connu, en s'appuyant sur `../references/sources-par-domaine.md`. Une affirmation soutenue uniquement par des sources de biais convergent est un signal de faiblesse, pas de force.
2. **Exiger l'extrait.** Ne trancher qu'appuyé sur un extrait verbatim cité. Pas d'extrait, le verdict est « non vérifiable ». *Pourquoi :* c'est l'extrait qui rend le verdict réfutable par le lecteur.
3. **Contrôler la contre-recherche.** Refuser le mot « consensus » tant qu'aucune entrée `contre` ou `nuance` n'a été cherchée. Le seuil chiffré de sources indépendantes et le plafond de confiance associé sont dans `../references/sources-par-domaine.md`, section « Règle transverse ».
4. **Trancher.** Attribuer `vrai`, `plutôt vrai`, `trompeur` (fait exact, cadrage biaisé), `faux`, ou `non vérifiable`. Ajouter la confiance (haut, moyen, bas), fonction du tier des sources, de leur nombre et de leur indépendance.
5. **Abstenir.** « Non vérifiable » est un verdict de première classe, pas un échec. Ne jamais fabriquer une conclusion pour rendre un rapport complet.
6. **Synthétiser.** Remplir le gabarit. Séparer ce qui est vérifié, ce qui reste interprétation de l'auteur, et ce qui reste ouvert. Si l'entrée portait une thèse d'ensemble, dire ce qu'elle vaut une fois les faits recomposés, sans aller au-delà des sources.

## Test

- Le compte des affirmations du rapport égale celui de la table de 01. Aucune ne disparaît en route.
- Chaque verdict autre que « non vérifiable » porte au moins une URL et un extrait verbatim.
- Chaque affirmation sortie de 02 avec zéro entrée porte « non vérifiable » dans le rapport.
- Calibrage sur un cas positif fabriqué : glisser une affirmation invérifiable dans l'entrée, et vérifier que le rapport abstient au lieu de conclure. Sans cette cible, on ne distingue pas un skill qui abstient d'un skill qui n'a pas eu l'occasion de le faire.
- Les interprétations de 01 apparaissent dans leur section propre, qualifiées et non tranchées.
