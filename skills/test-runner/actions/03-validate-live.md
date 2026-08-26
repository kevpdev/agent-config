# 03 - Valider en live

Joue les suites existantes et exerce l'API réelle, puis rend des faits. Ne juge pas la feature.

## Input

La `recipe` de `01-discover`, et l'app tenue vivante par `02-lifecycle`.

## Output

Le verdict de validation, consommé par le caller, la boucle d'`aidd-orchestrator:01-sdlc` par
exemple.

```
{ rungCovered: unit|integration|api|none, pass: bool, evidence: [...], notCovered: [...] }
```

## Process

1. **Garde.** Avant toute opération listée dans `paidOps`, exiger une confirmation humaine explicite.
   Jamais d'appel payant en silence.
   - Une opération payante refusée n'échoue pas la validation, elle part dans `notCovered`.
2. **Jouer les suites.** Lancer la suite existante via la `testCommand` découverte, `unit` puis
   `integration`, et rendre `{ kind, pass, failed[], regressions[] }` pour chacune.
   - « Sans régression » veut dire rejouer la suite pertinente complète, pas seulement le test neuf.
3. **Exercer l'API.** Frapper en curl un endpoint réel de l'app lancée, quand aucun test
   d'intégration ne couvre la couche visée.
   - Garder les requêtes et les réponses réelles comme preuve, telles quelles dans `evidence`.
4. **Rendre.** Remonter dans `notCovered` toute couche qu'aucune preuve n'a pu couvrir : gap de
   découverte, opération payante refusée, suite de tests absente.

## Test

| Cas | Preuve |
| --- | --- |
| lancer la validation sur un repo qui porte une op payante, sans répondre à la confirmation | zéro appel payant dans les logs, l'op est dans `notCovered` |
| lancer la validation quand `testCommand` est non couverte | `rungCovered` vaut `api` ou `none`, jamais `unit` |
| comparer les tests joués au test neuf du changement | la suite pertinente complète est jouée, pas seulement le test neuf |
| relire l'`evidence` d'un exercice d'API | les requêtes et réponses curl réelles y figurent, non reformulées |
| relire un verdict rendu avec un `gaps` non vide en entrée | `notCovered` n'est pas vide, `pass: true` ne masque aucune couche |
