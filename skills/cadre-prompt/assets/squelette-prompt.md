# Gabarits de prompt, un par type

Trois squelettes à injecter dans la réponse. Le type se détecte avec le tableau du `SKILL.md`.

**Règles communes aux trois.** Une section sans contenu s'omet, jamais de placeholder. La section
`## Ce qui est supposé` se place en dernier et n'apparaît que si une hypothèse a été posée. Les
sections `## Faits déjà mesurés` et `## Prémisses fausses à ne pas hériter` n'existent que si la
session en cours a réellement mesuré quelque chose.

---

## Type 1 — Exécution

```markdown
<Mode d'exécution attendu, si la demande en dépend.>

## Ce qu'il faut faire

<Le verbe, l'objet, le périmètre. Repris de l'ébauche, resserré.>

## Critères d'acceptation

- <Un critère vérifiable, avec la commande ou l'artefact qui le prouve.>
- <Un autre.>

## Ce qu'on ne touche pas

- <Fichier, dossier ou comportement explicitement hors périmètre.>

## Contraintes

- <Contrainte d'outillage, de convention ou d'environnement, une par ligne.>

## Ce qui est supposé

- ⚠️ supposé : <l'hypothèse, et ce qui change si elle est fausse.>
```

---

## Type 2 — Analyse

```markdown
<Mode d'exécution attendu. Une analyse qui conclura sur des modifications se mène en plan mode.>
Livrable attendu : <le document ou la décision, nommé>.

## Contexte

<Ce qui a amené la demande, au passé, factuel. Pas de justification.>

## Ce que je veux

<Le résultat visé, et ce qu'on en fera ensuite.>

## Contrat de questions — figé, ne pas l'élargir en cours d'analyse

Une découverte hors de ces questions se capture en une ligne et on continue.

- **Q1** — <question fermée, dont la réponse est vérifiable>
- **Q2** — <…>

**Hors périmètre** : <ce qu'on ne creuse pas, et pourquoi en trois mots>.

## Sources de vérité — à lire avant de mesurer

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

<Section à omettre quand le prompt vise un agent dont les règles globales portent déjà ces
consignes. À garder quand il part vers un autre outil, un autre modèle, ou un lecteur humain.>

- Mesurer avant de raisonner, calibrer chaque comptage sur un cas positif avant de croire un « zéro ».
- Challenger chaque composant isolément contre son alternative la plus simple.
- Marquer visiblement ce qui est supposé et ce qui est mesuré ou doc-vérifié.
- Une reco par question, pas un catalogue d'options.

## Ce qui est supposé

- ⚠️ supposé : <l'hypothèse, et ce qui change si elle est fausse.>
```

---

## Type 3 — Exploration

```markdown
Phase exploration. <Le sujet, en une phrase.>

## Ce que je cherche à comprendre

<Le flou à lever, tel quel. Ne pas le transformer en question fermée : ce serait changer de type.>

## Condition d'arrêt

<L'une des trois formes, une seule.>
- Quand <fait observable> est établi.
- Après <n> échanges, on fait le point même si rien n'est tranché.
- Quand j'ai de quoi <décision à prendre>, sans aller plus loin.

## Ce que je ne veux pas encore

- Pas de conclusion, pas de reco, pas de découpage en tickets. On ouvre, on ne referme pas.
- Pas de plan d'exécution, même partiel.

## Ce qu'on fait des découvertes hors sujet

Les capturer en une ligne et continuer. Ne pas les creuser.

## Ce qui est supposé

- ⚠️ supposé : <l'hypothèse, et ce qui change si elle est fausse.>
```
