# Contrôles de rédaction

Ce que le relecteur de l'action `check` reçoit, et rien d'autre. Les règles portent sur le texte visible du document hors blocs de code, libellés des schémas SVG compris.

Le texte doit se lire comme la note d'un ingénieur à ses collègues.

## Ponctuation

- **Le point-virgule est interdit.** Couper en deux phrases, ou relier par « et », « car », « donc », « alors que ».
- **Pas de deux-points explicatif en milieu de phrase**, quand « X : Y » veut dire « X, parce que Y ». Le deux-points reste permis pour introduire une citation, une liste d'exemples ou un libellé court (« Java : le contrat »), dans les tableaux, et dans les titres de forme « Sujet : précision ».
- **Pas de tiret cadratin (—) ni demi-cadratin (–)** comme ponctuation, balise `<title>` comprise.
- **Pas de point d'exclamation, pas de question rhétorique.** Une question est permise en titre seulement si la section y répond.
- **Typographie française.** Guillemets « », espace avant le deux-points, virgule décimale (2,35), espace des milliers (1 000), unités espacées (100 g, 5 L).

## Casse

- **Casse de phrase partout** : titres, intertitres, boutons, légendes, entrées du sommaire. On écrit « Choisir l'OCR », jamais « Choisir L'OCR » ni « Le LLM Lit, Le Code Compte ».
- **Pas de libellé en capitales**, sauf les identifiants techniques réels (FOOD, START_AND_END) et les sigles (OCR, PDF, HT).

## Tournures à bannir

- Les contrastes artificiels : « pas X mais Y », « X, pas Y », « ne tient pas tant à X qu'à Y », « il ne s'agit pas de… ». Énoncer directement ce qui est.
- Les formules dramatisantes et les slogans : « règle d'or », « le vrai piège », « le plus sournois », « la clé », « changer la donne », « en cascade », « gratuit » au sens figuré, « deux règles suffisent », « reste à savoir ».
- Les tournures emphatiques « c'est là que », « c'est ce qui », « c'est elle que », sauf si la phrase devient bancale sans elles.
- Les connecteurs de remplissage : « concrètement », « en somme », « en définitive », « il est important de noter que », « force est de constater ».
- Les fins de section en maxime, cette phrase courte et frappée qui résume ce qui vient d'être dit.
- Les triplets par réflexe, trois adjectifs ou trois exemples. Donner le nombre d'éléments que le sujet impose.
- Le gras suivi d'un deux-points en tête de chaque puce d'une liste. Préférer une phrase complète dont le début est en gras.
- Les superlatifs non sourcés (« le meilleur », « bien plus rapide ») et les exagérations (« au pixel près »).
- Les emojis.

## Registre

- Voix active, verbes simples.
- Chaque affirmation chiffrée porte sa source et sa date, ou la mention « à vérifier ».
- Chaque valeur fictive (score, prix, ligne de facture) est signalée comme illustrative.
- Les termes techniques anglais usuels restent en anglais (bbox, batch, matching). Tout le reste est en français.

## Étapes du contrôle

1. Juger chaque ligne « à trier » reçue du lint contre les règles ci-dessus. Le lint ne lit pas les SVG. Ses interdits sont corrigés, sauf ceux transmis comme restants, qui se signalent tels quels.
2. Relire le texte visible en entier, depuis le titre, et relever tout ce que le lint ne relève pas. Notamment les maximes, les triplets, les superlatifs, les questions rhétoriques, le gras suivi d'un deux-points, la typographie française (guillemets, espaces, virgule décimale) et toute tournure bannie dont la forme varie.
3. Comparer chaque chiffre, version et prix à la liste des sources reçue, selon les règles de la section « Registre ».
4. Vérifier les schémas : aucun texte qui déborde, libellés conformes aux règles de casse et de ponctuation, code couleur conforme à la légende, une légende sous chaque figure.
5. Vérifier qu'aucun `<details>` ne porte du contenu qui doit figurer dans le PDF.
6. Vérifier que la page commence par le titre puis le sommaire, et qu'elle se comprend sans la conversation d'origine.

## Format du rapport

Une ligne par problème, sans modifier le fichier :

```
[règle] extrait fautif (20 mots au plus) → réécriture proposée
```

Le rapport se termine par un verdict, « conforme » ou « à corriger ».
