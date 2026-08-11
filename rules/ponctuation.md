# Ponctuation de prose — quatre substitutions

Un dosage à l'œil (« limite le `;` », « préfère `:` ») ne produit rien : mesuré le 2026-08-05 alors que la consigne de dosage était en vigueur, les recaps portaient 5,25 points-virgules pour 1 000 mots. Il faut des gestes locaux.

| À la place de | Écrire |
|---|---|
| un point-virgule qui empile deux propositions (« la parité est acquise ; M1 exerce en plus le rebranchement ») | deux phrases. Le `;` reste au code et aux énumérations d'une ligne de log. |
| un tiret cadratin qui remplace un point ou une virgule en pleine phrase (« Maven ne lit pas ce fichier — il faut le déclarer ») | un point, une virgule ou un deux-points. Le tiret reste au séparateur label/définition (`**label** — définition`), aux titres et aux cellules de tableau. |
| `=` pour « est » ou « vaut » (« enjeu réel = prudentiel ») | « le vrai enjeu est prudentiel ». Le `=` reste au code et aux paramètres. |
| une chaîne à flèches en prose (« index → shortlist → document ») | « on part de l'index, puis une shortlist, puis le document ». La flèche reste au code, aux diagrammes et aux index. |

Une phrase qui cumule les deux premiers tics :

- ❌ « Le score baisse — probablement à cause du bruit — donc on le recalibre ; le seuil actuel n'est plus fiable. »
- ✅ « Le score baisse, probablement à cause du bruit. On recalibre : le seuil actuel n'est plus fiable. »

**POURQUOI global et non scopé par `paths:`** : la ponctuation de prose n'est identifiable par aucun chemin. Elle vaut pour un recap de vault, un message de PR, une réponse de chat et un rapport de sous-agent. Scopée par chemin, elle ne se déclenche qu'en éditant un fichier du périmètre, donc jamais dans une réponse.

**TEST** : comptage sur la prose seule, tirets de titre, de tableau et de séparateur label exclus. Baselines, cibles et commande → `rules/references/ref-ponctuation.md`.
