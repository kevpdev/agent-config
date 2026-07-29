# 05 - Réconcilier et signaler les docs-décision

Compare doc-vs-code à HEAD quand l'ancre git est non fiable, et signale les écarts sur les docs-décision sans jamais les écraser.

## Input

- Les cibles de régime **décision** classées en action 02, quelles qu'elles soient — la table des régimes du `SKILL.md` en donne la liste, cette action n'en tient pas sa propre copie.
- Tout scope où l'ancre git est non fiable (features mergées, doc peut-être touchée après un merge non documenté), ou tout contrat partagé de coordinateur.

## Output

Une liste de dérives : pour chaque affirmation factuelle, ce que la doc affirme vs ce que le code dit réellement, avec le repo autorité par fait. Pour chaque écart sur une doc-décision : les deux issues proposées, en attente d'arbitrage. **Aucune édition** du contrat/décision.

## Process

1. **Réconcilier (délégué).** Quand l'ancre git est non fiable, ou pour toute doc-décision, ne pas diff : **comparer doc-vs-code à HEAD**. C'est le modèle mental par défaut du régime décision ; le diff n'est qu'une optimisation quand l'ancre est fiable.
   > Sous-agent : « Lis la doc cible (README / `aidd_docs/memory/*` / contrat partagé). Pour chaque affirmation factuelle (endpoints, schéma DB, classes clés, statuts/enums), vérifie-la contre le code **du/des repo(s) qui l'implémentent** à HEAD. Rends la liste des **dérives** : ce que la doc affirme vs ce que le code dit réellement, avec le repo autorité pour chaque fait. »
   - En coordinateur, le sous-agent lit le code des **enfants** (front et backend selon le fait). Autorité par fait :

     | Fait | Repo autorité |
     |---|---|
     | Endpoints, schéma DB, réponses/DTO API | **backend** |
     | Routes UI, comportement front, ce qui est consommé | **front** |

   - Immunisé à la contamination (ignore qui a changé quoi). Limite assumée : capture la **dérive descriptive**, pas les décisions/intentions d'une feature — pour ça, le diff + `/10-learn` (actions 02/03) reste meilleur.
2. **Signaler.** Pour chaque écart relevé sur une doc-décision, présenter **décision affirme X / code fait Y** de façon précise.
   - Pourquoi ne pas écraser : quand le code s'écarte d'une décision (ex. le backend ajoute un champ `category` non prévu au contrat), le skill ne peut pas savoir si c'est une bonne découverte à entériner ou une bavure à corriger. Réécrire la décision seul graverait peut-être un bug dans la loi.
3. **Arbitrer.** Proposer les deux issues — entériner la découverte (via `/10-learn`) ou corriger le code — et **attendre l'arbitrage**. Aucune édition automatique du contrat/décision.
   - Si deux enfants se **contredisent** sur le même fait (back renvoie X, front attend Y) → ne pas deviner : décrire la divergence et laisser arbitrer.

## Test

- La comparaison porte sur doc-vs-code à HEAD, pas sur un diff de commits.
- Chaque écart sur une doc-décision est formulé « décision affirme X / code fait Y » avec le repo autorité identifié.
- Aucun edit n'est appliqué à **aucune** des surfaces que la table des régimes classe en décision : la sortie s'arrête à la proposition d'issues. Vérifier contre la table, pas contre une liste mémorisée — sinon une surface ajoutée depuis passe le test sans être couverte.
- Une contradiction entre deux enfants est signalée comme divergence, pas tranchée par le skill.
