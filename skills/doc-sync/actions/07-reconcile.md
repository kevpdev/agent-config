# 07 - Réconcilier et signaler les docs-décision

Compare doc-vs-code à HEAD quand l'ancre git est non fiable, et signale les écarts sur les docs-décision sans jamais les écraser.

## Input

- Les cibles de régime **décision** classées en action 02, quelles qu'elles soient — la table des régimes de [regimes-de-doc.md](../references/regimes-de-doc.md) en donne la liste, cette action n'en tient pas sa propre copie.
- Tout scope où l'ancre git est non fiable (features mergées, doc peut-être touchée après un merge non documenté), ou tout contrat partagé de coordinateur.

## Output

Une liste de dérives : pour chaque affirmation factuelle, ce que la doc affirme vs ce que le code dit réellement, avec le repo autorité par fait. Pour chaque écart sur une doc-décision : les deux issues proposées, en attente d'arbitrage. **Aucune édition** du contrat/décision.

## Process

1. **Réconcilier (délégué).** Quand l'ancre git est non fiable, ou pour toute doc-décision, ne pas diff : **comparer doc-vs-code à HEAD**. C'est le modèle mental par défaut du régime décision ; le diff n'est qu'une optimisation quand l'ancre est fiable.
   > Sous-agent : « Lis la doc cible (README / `aidd_docs/memory/*` / contrat partagé). Pour chaque affirmation factuelle (endpoints, schéma DB, classes clés, statuts/enums), vérifie-la contre le code **du/des repo(s) qui l'implémentent** à HEAD. Rends la liste des **dérives** : ce que la doc affirme vs ce que le code dit réellement, avec le repo autorité pour chaque fait.
   >
   > **Choisis ton instrument par affirmation, la question est « symbole ou texte ? »** Une classe, une méthode, qui appelle quoi, ce qu'un changement casse → l'outil de symboles du projet. La même question à travers plusieurs dépôts → son outil inter-dépôts. **Du SQL, une migration, une clé de properties, un template CI, une URL littérale → grep**, scopé sur les dossiers d'enfants et jamais lancé depuis la racine du parent.
   >
   > **Trois pièges, chacun rend une réponse fausse qui a l'air juste.** Un outil de graphe indexe des symboles et rien d'autre : un zéro sur un fichier de données n'est pas une absence, c'est une question hors de son périmètre. Une URL de front se lit dans le fichier de déclaration de routes du projet, **jamais** dans le graphe, qui déduit la route de l'arborescence des fichiers. Et un zéro ne se lit comme une absence qu'après l'avoir calibré sur un symbole dont tu sais qu'il est là. »
   - En coordinateur, le sous-agent lit le code des **enfants** (front et backend selon le fait). Autorité par fait :

     | Fait | Repo autorité | Instrument |
     |---|---|---|
     | Endpoints (la méthode et sa signature) | **backend** | outil de symboles |
     | Schéma DB, migrations | **backend** | **grep** — un graphe de symboles n'indexe pas les fichiers de données |
     | Réponses/DTO API | **backend** | outil de symboles |
     | Routes UI, URL des écrans | **front** | le **fichier de déclaration de routes**, jamais le graphe |
     | Comportement front, ce qui est consommé | **front** | outil de symboles |

   - **Le contrat partagé est une question inter-dépôts par nature**, et c'est le seul endroit du flux qui en pose. Un contrat qui enjambe les enfants affirme qu'un symbole d'un dépôt est consommé par un autre : l'outil mono-dépôt ne sait pas répondre, ses appelants ne couvrant que son propre index. Passer par l'outil inter-dépôts du projet quand il en expose un.
     - *Sa réserve, à connaître avant de s'y appuyer : chez Winggy-v3 cet outil lit les références non résolues des index **sans les resynchroniser**. Après la bascule de branche du pré-vol (action 01), sa réponse peut donc porter sur un index périmé. Pour une affirmation dont la fraîcheur décide, passer par l'outil mono-dépôt, qui resynchronise sa cible avant de répondre.*

   - Immunisé à la contamination (ignore qui a changé quoi). Limite assumée : capture la **dérive descriptive**, pas les décisions/intentions d'une feature — pour ça, le diff + `/10-learn` (actions 02 à 04) reste meilleur.
2. **Signaler.** Pour chaque écart relevé sur une doc-décision, présenter **décision affirme X / code fait Y** de façon précise.
   - Pourquoi ne pas écraser : quand le code s'écarte d'une décision (ex. le backend ajoute un champ `category` non prévu au contrat), le skill ne peut pas savoir si c'est une bonne découverte à entériner ou une bavure à corriger. Réécrire la décision seul graverait peut-être un bug dans la loi.
3. **Arbitrer.** Proposer les deux issues — entériner la découverte (via `/10-learn`) ou corriger le code — et **attendre l'arbitrage**. Aucune édition automatique du contrat/décision.
   - Si deux enfants se **contredisent** sur le même fait (back renvoie X, front attend Y) → ne pas deviner : décrire la divergence et laisser arbitrer.

## Test

- La comparaison porte sur doc-vs-code à HEAD, pas sur un diff de commits.
- **Le prompt de dispatch porte lui-même la règle « symbole ou texte ? » et ses trois pièges.** Un prompt qui se contente de nommer l'outil n'a pas tourné : le harnais n'injecte que les **noms** des outils MCP au sous-agent, jamais leurs descriptions — vérifié le 2026-08-27. Ce qui n'est pas dans le prompt ne lui parvient pas.
- Chaque écart sur une doc-décision est formulé « décision affirme X / code fait Y » avec le repo autorité identifié.
- Aucun edit n'est appliqué à **aucune** des surfaces que la table des régimes classe en décision : la sortie s'arrête à la proposition d'issues. Vérifier contre la table, pas contre une liste mémorisée — sinon une surface ajoutée depuis passe le test sans être couverte.
- Une contradiction entre deux enfants est signalée comme divergence, pas tranchée par le skill.
