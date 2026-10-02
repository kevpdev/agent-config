# lenses/_technique.md : module transversal

Chargé dès qu'une affirmation technique apparaît (chiffre de performance, version, norme, calcul, spécification), quel que soit le domaine. Il s'ajoute aux lentilles et ne compte pas dans le plafond de deux lentilles par question.

Les noms de sources cités dans les lentilles viennent de la connaissance générale du modèle et n'ont pas été vérifiés lors de la rédaction du kit. Ils orientent la recherche, ils ne remplacent pas l'ouverture de la page (V2).

## Les cinq questions

Pour chaque affirmation technique clé, répondre par écrit avant de l'étiqueter.

1. **Quelle version, norme ou édition, et à quelle date ?** Un chiffre sans version est périmé ou invérifiable. À consigner dans le champ `claim` ou dans une note de l'affirmation.
2. **Dans quelles conditions la mesure ou la performance a-t-elle été obtenue ?** Laboratoire ou terrain, charge nominale ou réelle, environnement, jeu de test, configuration. Un résultat sans ses conditions ne se compare à rien.
3. **Qui a produit le chiffre ?** Fabricant, éditeur, tiers indépendant. À consigner dans `interet_source`. Un chiffre du fabricant se rétrograde d'un cran sans corroboration indépendante (P6).
4. **L'ordre de grandeur est-il plausible ?** Comparer à un cas connu ou à un calcul simple. Un écart d'un facteur dix ou plus est un signal d'erreur d'unité ou de périmètre, à lever avant de citer.
5. **Le domaine touche-t-il la sécurité des personnes ou la responsabilité légale ?** Structure, électricité, gaz, médical, sécurité informatique en production. Si oui, S1 s'applique : sources primaires, aucune conclusion personnalisée, renvoi à un professionnel qualifié.

## Règles de calcul

- Tout calcul se fait avec un outil de calcul ou étape par étape, jamais de tête (V9). Le résultat est accompagné de ses unités et de ses hypothèses.
- Conversions d'unités et de devises : écrire le taux ou le facteur utilisé et sa date.
- Un résultat calculé n'est jamais *Établi* sur la seule foi du calcul. Il hérite de l'étiquette de la plus faible de ses données d'entrée.

## Pièges fréquents du module

- Benchmark d'éditeur présenté comme comparaison neutre (SRC4).
- « Ça marche chez moi » ou retour d'expérience isolé pris pour une garantie (RAI2).
- Performance de laboratoire appliquée à l'usage réel (RAI5).
- Précision illusoire : trois décimales sur une mesure à dix pour cent d'incertitude (RAI6).
