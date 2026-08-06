# 01 - Décomposer

Réduit l'entrée à des affirmations vérifiables isolément, et dérive de leur domaine la stratégie de sources à viser.

## Input

L'entrée à vérifier : document, transcription, fil, ou thèse formulée en prose.

## Output

Une table `# | affirmation | domaine | stratégie de sources`, plus la liste séparée des **interprétations** écartées du champ factuel.

## Process

1. **Extraire.** Découper l'entrée en affirmations atomiques. Une affirmation porte un seul fait, tranchable sans dépendre d'une autre. Si la trancher demande d'en trancher une seconde, couper encore.
2. **Séparer.** Distinguer le fait (« l'UE prépare le règlement X ») de l'interprétation (« c'est de la surveillance de masse »). Le fait part en vérification, l'interprétation part dans la liste à part. *Pourquoi :* une interprétation n'a pas de valeur de vérité, la traiter comme un fait fabrique un verdict qui n'existe pas.
3. **Catégoriser.** Attribuer un domaine à chaque affirmation : économie, politique/droit, histoire, sociologie, santé, sport, science. Le domaine ne crée pas d'agent, il **sélectionne** la stratégie de sources.
4. **Dériver.** Lire `../references/sources-par-domaine.md` et en tirer, pour chaque affirmation, la hiérarchie de sources à viser, le nombre de sources indépendantes requis pour parler de consensus, et les pièges du domaine.
5. **Signaler le vide.** Si une affirmation n'a pas de domaine identifiable, le dire dans la table plutôt que d'en inventer un. Sans domaine, l'action 02 cherche à l'aveugle.

## Test

- Chaque ligne de la table porte un domaine et une stratégie non vides, ou la mention explicite « domaine non identifiable ».
- Pour chaque affirmation, on peut nommer la source qui la trancherait. Si on n'y arrive pas, elle appartient aux interprétations et la table est à corriger.
- La liste des interprétations existe, même vide, et elle est explicitement vide plutôt qu'absente.
- Aucune affirmation de la table ne contient un adjectif évaluatif (« scandaleux », « massif ») sans chiffre attaché.
