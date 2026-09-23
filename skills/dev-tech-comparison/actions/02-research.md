# 02 - Rechercher

Réunit les faits sourcés et choisit l'objet qui servira de fil conducteur.

## Input

Le bloc d'entrées rendu par `frame`.

## Output

Une liste de sources datées, les écarts de version par capacité, le fil conducteur et la découpe des étapes par acteur. Le tout gardé dans le contexte pour `write` et transmis à `check`.

## Process

1. **Sourcer.** Chercher d'abord la documentation officielle (docs, changelog, fiche modèle), puis les annonces de l'éditeur, puis les benchmarks indépendants.
   - Chaque source garde son origine, éditeur ou tiers, et sa date de consultation.
   - Chaque prix et chaque numéro de version porte la date du relevé, par exemple « relevé en septembre 2026 ».
   - Une source imposée par les entrées se lit en premier.
2. **Mesurer les écarts de version.** Pour chaque capacité comparée, noter la version minimale qui la fournit et ce que font les versions antérieures, par exemple « paramètre accepté mais tableau vide ».
   - Un fait qu'aucune source ne confirme reste dans la liste, marqué « à vérifier ». Il ne disparaît pas.
3. **Choisir le fil conducteur**, selon la règle transverse « Un seul fil conducteur ». L'objet doit être assez riche pour traverser toutes les étapes. Exemple : un PDF de cinq pages contenant trois factures, suivi du scan jusqu'au calcul de masse.
4. **Découper par acteur.** Appliquer la règle transverse « Le calcul se fait en code » à chaque étape du parcours. Cette découpe donne le code couleur des schémas.

## Test

| Cas | Preuve |
| --- | --- |
| relire la liste des sources | chacune porte une date de consultation et la mention éditeur ou tiers |
| relire la découpe par acteur | chaque étape nomme son acteur, et aucun calcul n'est attribué au LLM |
