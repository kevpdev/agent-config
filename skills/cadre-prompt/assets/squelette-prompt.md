# Gabarit de prompt, six briques

Un seul squelette. Le type détecté avec le tableau du `SKILL.md` ne change pas les briques, il change
ce que chacune contient.

**Règles communes.** Une section sans contenu s'omet, jamais de placeholder. Exception : `## Libre`
s'écrit toujours, pour que l'absence de choix soit un choix visible. L'IA ne choisit librement que ce
que l'utilisateur n'a pas défini, et ce qu'il a défini (stack, conventions, procédure) va en
`## Contraintes`.
La section `## Ce qui est supposé` se place en dernier et n'apparaît que si une hypothèse a été posée.
Les sections `## Faits déjà mesurés` et `## Prémisses fausses à ne pas hériter` n'existent que si la
session en cours a réellement mesuré quelque chose.

## Ce que chaque brique porte, par type

| Brique | Exécution | Analyse | Exploration |
|---|---|---|---|
| **Contexte** | où on en est, ce qui existe déjà | ce qui a amené la demande, au passé, factuel, plus les sources de vérité | d'où vient le flou |
| **Effet** | ce qu'on voit à la fin, ce qu'on vérifie | la décision ou le document attendu, et ce qu'on en fera | le flou à lever, tel quel (une question fermée changerait de type) |
| **Périmètre** | ce qu'elle fait, ce qu'elle demande, ce qu'elle ne touche pas | le contrat de questions figé et son hors-périmètre non vide | pas de conclusion, pas de reco, pas de plan, découvertes hors sujet capturées en une ligne |
| **Contraintes** | règles non négociables, dont la stack, les conventions et la procédure que l'utilisateur a définies | idem | idem |
| **Libre** | ce que l'utilisateur n'a pas défini, l'IA y choisit seule (librairie, mise en page, noms) | la méthode, sauf mention | les pistes qu'elle ouvre |
| **Fini quand** | critères cochables, avec la commande ou l'artefact qui prouve, et la boucle « teste, compare, recommence » | le livrable nommé | une condition d'arrêt, une seule des trois formes ci-dessous |

## Squelette

```markdown
<Mode : lire, écrire ou exécuter. Pour « exécuter » : « commit avant ». Une analyse qui conclura sur
des modifications se mène en plan mode.>

## Contexte

<Selon la colonne du type.>

## Effet

<Selon la colonne du type. Ce qui doit être vrai à la fin, pas la marche à suivre.>

## Périmètre

<Exécution : fait / demande / ne touche pas.>
<Analyse : contrat figé, une découverte hors questions se capture en une ligne et on continue.>

- **Q1** — <question fermée, dont la réponse est vérifiable>

**Hors périmètre** : <ce qu'on ne creuse pas, et pourquoi en trois mots>.

<Exploration : pas de conclusion, pas de reco, pas de plan d'exécution, même partiel. On ouvre, on ne
referme pas.>

## Contraintes

- <Une par ligne. La stack, les conventions et la procédure que l'utilisateur a nommées, reprises
  telles quelles.>

## Libre

<Ce que l'utilisateur n'a pas défini, et que l'IA choisit seule. Si tout est défini : « rien, tout est
fixé ci-dessus ». Si rien ne l'est : « tout le reste ».>

## Fini quand

<Exécution : un critère cochable par ligne. Teste, compare au résultat attendu, corrige, recommence
jusqu'à ce que ça passe.>

<Analyse : « Livrable : <le document ou la décision, nommé>. »>

<Exploration : une seule des trois formes.>
- Quand <fait observable> est établi.
- Après <n> échanges, on fait le point même si rien n'est tranché.
- Quand j'ai de quoi <décision à prendre>, sans aller plus loin.

## Sources de vérité

<Analyse seulement, à lire avant de mesurer.>

| Chemin | Ce qu'il porte |
| --- | --- |
| `<chemin absolu ou relatif au repo>` | <en une ligne> |

## Faits déjà mesurés — ne pas les re-mesurer

| Fait | Détail et source |
| --- | --- |
| <fait> | <la commande, la doc ou l'appel d'API qui l'a produit> |

## Prémisses fausses à ne pas hériter

- <l'affirmation fausse, et ce qui est vrai à la place.>

## Méthode attendue

<Analyse seulement. À omettre quand le prompt vise un agent dont les règles globales portent déjà ces
consignes. À garder quand il part vers un autre outil, un autre modèle, ou un lecteur humain.>

- Mesurer avant de raisonner, calibrer chaque comptage sur un cas positif avant de croire un « zéro ».
- Challenger chaque composant isolément contre son alternative la plus simple.
- Marquer visiblement ce qui est supposé et ce qui est mesuré ou doc-vérifié.
- Une reco par question, pas un catalogue d'options.

## Ce qui est supposé

- ⚠️ supposé : <l'hypothèse, et ce qui change si elle est fausse.>
```

Exploration : ouvrir le prompt par « Phase exploration. <le sujet, en une phrase.> » à la place du mode.
