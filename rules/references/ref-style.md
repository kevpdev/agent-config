# Références — `style.md`, `profil.md`, `reponse.md`, `redaction.md`

Ce qu'aucun compteur ne remplace, et ce qui empêche de lire un chiffre de travers. Jamais chargé automatiquement.

**Ce fichier n'est pas un journal.** Les baselines vivent dans le docstring de `wrappers/claude/scripts/mesure-reponses.py`, qui les imprime à chaque exécution. Les récits de session vivent dans `logs/sessions/` du vault. Ici, seulement ce qui sert à réappliquer une règle.

---

## Les paires avant/après du registre collègue

`profil.md` nomme trois tics et n'en illustre qu'un. Les deux premiers sont invisibles à tout instrument, donc l'exemple est la seule prise sur eux. Cinq phrases réellement écrites, réécrites à côté.

| ❌ Écrit | ✅ Réécrit |
|---|---|
| « Comme `reasoning.md` porte lui-même le trigger "un comptage qui rend zéro", je calibrerai l'instrument sur un cas positif connu avant de conclure. La règle supprimée de `workflow.md` est du *legacy harness scaffolding* textuel. » | « Avant de dire "j'ai trouvé zéro problème", je vérifie que mon test sait en trouver un. Je lui donne un cas que je sais mauvais. S'il ne le voit pas, mon zéro ne prouve rien. » |
| « L'item C1b sur `reasoning.md` reste ouvert avec un sous-item pour le swap. C'est du C7, les 15 obligations de vérification sont intactes. » | « Le gros du travail sur ce fichier reste à faire. Ce qu'on vient de changer, c'est la formulation, pas le fond. » |
| « Le dépassement n'est pas porté par de l'argumentation mais par l'impératif. » | « Ce n'est pas du bavardage qu'il faut couper, il y a deux consignes collées ensemble. » |
| « Hors périmètre : `back-spring.md` et `front-react.md`, scopés par `paths:` donc hors couche chargée. » | « Je n'ai pas compté ces deux fichiers. Ils ne se chargent que quand tu ouvres du Java ou du TypeScript. » |
| « Cible 3 950 tenue avec 915 de marge, et elle n'a pas été atteinte par la cascade mais par tes deux décisions de fond. » | « L'objectif était 3 950 mots, on est à 3 035, donc c'est tenu large. Mais le gain vient de tes deux décisions de supprimer des fichiers, pas de l'audit. » |

**Les trois tics, dans l'ordre de nuisance** :

1. **Le nom abstrait qui remplace le verbe.** « Le dépassement est porté par l'impératif » au lieu de « il y a deux consignes collées ».
2. **Le code interne balancé comme si le lecteur l'avait en tête.** Un identifiant d'audit, un nom de couche, un critère numéroté.
3. **Trois idées dans une phrase**, tenues par un deux-points et un tiret. Seul un compteur de longueur l'approche, et à moitié.

Le quatrième, **l'ouverture-étiquette**, se compte et vit donc dans l'instrument, pas ici.

## « Concret » fait deux métiers, et c'est ce qui rend le conflit invisible

`style.md` demande un verdict concret d'abord, `profil.md` demande d'ouvrir sur l'exemple. Les deux disent « concret » sans parler de la même chose.

| Sens | Ce que ça fait | Exemple |
|---|---|---|
| Un chiffre, un chemin, une citation | **prouve**, c'est réfutable | « le fichier fait 591 mots » |
| Un exemple, une analogie, un schéma | **explique**, ça se comprend en une passe | « comme un `git pull` qui perdrait ses trois garde-fous » |

**Un lecteur a besoin des deux, et satisfaire le premier sens ne satisfait pas le second.** Une ouverture peut porter un chiffre et n'expliquer strictement rien. C'est pour ça que `style.md` porte la distinction en toutes lettres au lieu de dire « sois concret ».

## Ce que les compteurs ne voient pas

« Flou » n'est mesuré par aucun des sept compteurs et ne le sera pas. De « trop technique », le septième n'attrape que l'ouverture-étiquette, un tic sur quatre, celui qui a une forme. **Un zéro ne vaut donc jamais « la réponse est claire »**, c'est le trigger « un comptage qui rend zéro » de `reasoning.md` appliqué ici. La longueur, elle, ne dit rien de la densité : 150 mots creux restent creux.

Le détail des angles morts est dans le docstring de `mesure-reponses.py`, qui fait foi.

## Deux pièges d'estimation, tombés deux fois chacun

- **Chiffrer une réécriture de règle sur le contenu à déplacer** ignore le contenu à écrire, qui n'existe pas au moment où on estime. Raté d'un facteur 3,4 le 2026-08-11, raté de signe le 2026-08-12.
- **Un auto-diagnostic sur son propre tour est une hypothèse**, au même titre qu'une prémisse de codebase non vérifiée. Trois règles accusées, une seule coupable à la mesure. Réécrire les deux autres aurait ajouté du texte pour corriger des défauts inexistants.
