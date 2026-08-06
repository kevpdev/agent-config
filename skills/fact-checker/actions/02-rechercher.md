# 02 - Rechercher

Fait chercher les sources par un sous-agent, et n'accepte en retour que des entrées dont l'extrait est réfutable.

## Input

La table d'affirmations de `01-decomposer`, avec la stratégie de sources de chaque ligne.

## Output

Pour chaque affirmation, zéro à N entrées structurées (`claim_id`, `url`, `extrait`, `tier`, `date`, `angle`). Zéro entrée est une sortie valide, marquée « aucune source trouvée ».

## Process

1. **Déléguer.** Confier la recherche à un sous-agent générique (Explore, general-purpose). Ne jamais chercher dans ce contexte. *Pourquoi :* les dumps de recherche saturent le contexte parent alors que seule la conclusion compte.
2. **Briefer.** Donner au chercheur l'affirmation et la stratégie de sources dérivée en 01. Sans la stratégie, il retombe sur le premier média qui sort en tête de recherche.
3. **Exiger le format.** Le chercheur rend chaque source sous cette forme, sinon l'entrée est rejetée :

```
- claim_id: <id de l'affirmation>
  url: <URL qui résout réellement>
  extrait: "<verbatim exact, jamais paraphrasé>"
  tier: <niveau de fiabilité, cf. references/sources-par-domaine.md>
  date: <date de la source>
  angle: pour | contre | nuance
```

4. **Chercher le contre.** Demander explicitement une requête orientée contre-argument, en plus de la requête directe. *Pourquoi :* une recherche qui ne cherche que la confirmation la trouve toujours, et le verdict devient un reflet de la requête.
5. **Rejeter.** Pas d'URL qui résout, ou extrait paraphrasé, l'entrée est nulle. Ne pas la « réparer » en la reformulant, la supprimer et le signaler.

## Test

- Sur un échantillon d'entrées, l'URL résout réellement (récupérer la page) et l'`extrait` s'y retrouve mot pour mot.
- Chaque affirmation porte au moins une entrée `angle: contre` ou `angle: nuance`, ou la mention explicite « aucune source contradictoire trouvée ».
- Aucune entrée ne porte d'URL non résolue : le compte des entrées rejetées est rapporté, pas silencieux.
- Calibrage sur un cas positif fabriqué : soumettre une affirmation inventée sans source possible. Le retour doit être zéro entrée, jamais une entrée plausible.
