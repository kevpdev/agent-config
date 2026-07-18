# 03 — validate-live : run-tests + exercise-api

Produit une **preuve** exploitable par le caller (ex. la ladder d'aidd-pilot). Ne juge pas la feature : rend des faits (pass/fail + evidence).

## run-tests(kind)

- Lance la suite **existante** (`kind` = unit | integration) via la `testCommand` découverte.
- « Sans régression » = rejouer la **suite pertinente complète**, pas seulement le test neuf.
- Rendre : `{ kind, pass: bool, failed[], regressions[] }`.

## exercise-api

- **curl live** contre un endpoint réel de l'app lancée. Sert quand aucune TI ne couvre la couche visée (backend).
- Rendre les requêtes/réponses réelles comme preuve.

## Garde-coût (avant toute op payante)

- Une op repérée `paidOp` (ex. extraction LLM live) → **confirmation humaine AVANT** exécution. Jamais d'appel payant en silence.
- La confirmation vit **côté parent** : un subagent ne peut pas la demander.

## Sortie

```
{ rungCovered: unit|integration|api|none, pass: bool, evidence: [...] , notCovered[]: [...] }
```

- `notCovered` remonte les couches qu'aucune preuve n'a pu couvrir (gaps de découverte, op payante refusée) → le verdict reste **honnête**, jamais « tout vert » par défaut.
