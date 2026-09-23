# Contrat du document

Ce que le fichier HTML livré doit contenir, en plus de ce que le gabarit porte déjà. L'action `write` le lit avant de remplir le gabarit. Les règles de rédaction vivent à part, dans `controles-redaction.md`.

## Le lecteur visé

Le document se lit à froid, sans avoir suivi la conversation qui l'a produit. Un lecteur qui ne lit que le titre, le sommaire, l'encadré « En bref » et la grille de décision doit repartir avec la bonne décision.

C'est un seul fichier HTML autonome, en français, écrit comme la note de décision d'un architecte technique à ses collègues.

## Structure, dans cet ordre

| # | Bloc | Ce qu'il porte |
| --- | --- | --- |
| 1 | titre `h1` | en casse de phrase |
| 2 | sommaire | juste sous le titre, des liens vers chaque section |
| 3 | introduction | deux ou trois phrases qui annoncent le fil conducteur |
| 4 | schéma du parcours | les étapes de bout en bout, le numéro de section sous chaque étape |
| 5 | légende du code couleur | seulement s'il y en a un |
| 6 | encadré « En bref » | 3 à 5 phrases complètes, une par conclusion clé |
| 7 | sections numérotées | le numéro existe parce que les sections suivent le parcours |
| 8 | recommandation argumentée | par question à trancher : ce qui est recommandé, pourquoi, et quand l'autre option reste valable |
| 9 | limites et contraintes | défauts connus, limites d'API, coûts, dépendances, points non vérifiés à tester sur le corpus réel |
| 10 | points d'attention | regroupés par phase, par exemple extraction, segmentation, exploitation |
| 11 | grille de décision | deux ou trois cartes « Choisir X si… », puis un paragraphe sur ce qui ne change pas quel que soit le choix |
| 12 | sources | liens, date de consultation, origine éditeur ou tiers, mention des valeurs illustratives |

Une section numérotée contient, selon le besoin :

- un tableau comparatif, avec une ligne par critère
- une analogie courte dans un encadré dédié, pour chaque notion clé
- au moins une illustration
- des exemples tirés du domaine réel, jamais génériques
- du code court quand il clarifie un contrat ou un calcul (DTO, schéma JSON, fonction de calcul).

## Illustrations

Toutes en SVG inline, sans image externe. Le document en porte au minimum cinq :

1. un schéma de flux du parcours complet
2. une comparaison avant/après ou option A/option B, sur le même objet
3. un schéma du cas difficile, avec les zones problématiques mises en évidence
4. un arbre ou un flux de décision, avec les branches de repli et de revue humaine
5. un calcul décomposé, avec les valeurs du domaine.

Les règles communes à toutes :

- Le code couleur est sémantique et constant dans tout le document. Les quatre rôles et leurs couleurs sont ceux du gabarit, que la légende annonce. Aucune couleur ne sert à décorer.
- Les couleurs viennent des variables CSS du gabarit, pour que les schémas suivent le mode sombre.
- Chaque figure porte une légende d'une ou deux phrases, qui dit ce qu'il faut retenir et non ce qu'on voit.
- Aucun texte ne chevauche un autre ni ne déborde de sa boîte. Vérifier les coordonnées et la longueur des libellés.
- Un schéma large défile horizontalement sur mobile, avec une largeur minimale de 640 px environ.

## Design et impression

Le gabarit porte la colonne, les deux polices, la palette et son mode sombre, les encadrés typés et tout le bloc `@media print`. Ne pas les réinventer au remplissage, et ranger chaque nouveau bloc dans une classe que le bloc d'impression couvre déjà.

La police à chasse fixe des blocs de code s'ajoute aux deux familles du texte. C'est une exception à la limite de deux familles, validée le 2026-09-23, car un code en police proportionnelle perd son alignement.

Ce que le gabarit ne peut pas porter à lui seul :

- Pas de marqueurs 01/02/03 décoratifs sur les sections.
- Pas de `<details>` pour du contenu qui doit figurer dans le PDF, parce qu'il s'imprime replié.
- À éviter au remplissage : fond crème avec accent terracotta, noir avec un seul accent acide, cartes identiques avec ombre grise partout, étiquettes en capitales au-dessus des titres, métadonnées séparées par des points médians, flèches ajoutées aux liens.
