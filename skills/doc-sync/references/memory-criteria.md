# Critère d'inclusion en mémoire

Ce qui mérite d'exister dans une mémoire AIDD. Lu par `frame-memory` pour trancher, par `deliver-memory` pour écrire, et tendu au checker par `check-memory`.

## Ce que ce fichier ajoute à AIDD

AIDD note chaque candidat sur quatre poids (durabilité, réutilisation, pertinence, risque) dans `aidd-context/skills/10-learn/references/assessment.md`, qui fait foi. Ses règles de contenu vivent dans `aidd-context/skills/02-project-memory/references/memory-rules.md`. Aucun des quatre poids ne regarde si le fait est **reconstructible** : un fait durable et risqué peut se relire en trois secondes dans un `pom.xml`. D'où trois dimensions.

| Dimension | Question | Mesure |
| --- | --- | --- |
| inférable | un agent le reconstruit-il depuis le repo ? | nommer le fichier qui le porte, ou « aucun » |
| coût de ré-inférence | combien de lectures pour le rebâtir ? | un fichier, faible. Plusieurs repos, élevé |
| stabilité | bouge-t-il quand le code bouge ? | un port, une version ou un compte dérivent. Une décision ou un piège non |

## Le verdict, en trois issues

1. **Garder** un fait non inférable ou propre au repo : décision, convention, piège vécu, pourquoi d'un choix.
2. **Garder aussi** un fait inférable dont le coût de ré-inférence est élevé **et** la dérive faible, par exemple le graphe d'appels que seuls dix-sept dépôts reconstituent. Les deux conditions sont conjointes : une seule donne un pointeur.
3. **Sortir tout le reste**, en laissant un pointeur de chemin, jamais une copie.

**Le refus sans score** : une entrée qui recopie un fichier du disque n'entre pas. Ni arbre de fichiers, ni schéma, ni liste de scripts, ni extrait de config.

## Un fait, un home

Le home est là où le fait est produit.

| Nature du fait | Son home |
| --- | --- |
| comportement du code, endpoint, schéma | le repo qui l'implémente |
| détail d'outillage d'un enfant | la fiche de cet enfant |
| commande qui fait porte, et son prérequis | l'index racine |
| décision, contrat partagé | régime décision, signalé et jamais réécrit |

Signaler un doublon nomme les deux chemins et celui qui garde le fait.

## Le piège, deux tests avant de l'écrire

**D'où part le lecteur qui se trompe ?** Du code (fichier absent, valeur contre-intuitive) : le piège se justifie. D'une copie fausse de la mémoire : supprimer la copie, et n'écrire aucun piège. *Mesuré le 2026-08-21, ce second cas a produit l'essentiel d'un +28 % sur le fichier le plus lourd d'un banc.*

**Combien de cibles partagent la cause ?** Une : le piège vit chez elle. Plusieurs : chez la cause, une seule fois, et les symptômes se suppriment. La cause sans fiche : la créer.

**Trois calibrages**, à rejouer si ces tests changent.

| Cas | Verdict attendu |
| --- | --- |
| `mvnw` commité sans le bit `x`, donc `./mvnw` seul rend « Permission non accordée » | piège légitime, home unique chez la cause |
| une fiche affirmait présent un fichier absent du repo | suppression, aucun piège |
| un service sans `Dockerfile`, parce qu'un dépôt tiers porte l'image | piège légitime, home chez le dépôt de l'image |

## Le coût, rendu visible sans cible

- **Aucun plafond chiffré.** *Mesuré le 2026-08-20 : sous un plafond de 6 000 mots, une passe a fini à 9 591, retenue par l'exception légitime du graphe d'appels.*
- **Afficher le `wc -w` de la racine** à chaque passe, sans le comparer à rien. Compter en mots, jamais en lignes.
- **Justifier une hausse, jamais un niveau.** Une passe de pointeur monte, parce qu'un chemin est plus long qu'un numéro de port : elle se justifie en nommant les copies retirées. Une consolidation monte aussi : elle rend le nombre de homes du fait, avant et après.
- **Relire un fichier qui dépasse 2× la médiane** de son home, sans obligation de le réduire.

## Contrôle de sortie

Un candidat passe s'il porte le fichier qui le rend inférable ou « aucun », son verdict, et sa réconciliation `10-learn` (`new`, `covered`, `updates`, `supersedes`, `retracts`). Sans fichier ni « aucun », il n'a pas été mesuré.
