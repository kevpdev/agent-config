# 01 — discover : reconstituer la recette de run

Premier pas. Produit la **recette** (comment démarrer + comment tester) sans rien démarrer. Les autres actions la consomment.

## Méthode

1. Balayer les sources dans l'**ordre fixe** (`references/discovery.md`) : fichiers env → config framework → docs run.
2. Pour chaque champ de la recette, appliquer l'échelle **découvrir → déduire → escalader** : un candidat qui sert la fonction est retenu même si son nom ne matche pas (déduction par finalité), et signalé.
3. Ne rien inventer : un champ ni trouvable ni déductible est marqué **non couvert**, pas rempli au jugé.

## Sortie

```
recipe = {
  startCmd   : commande + workdir (ou "non couvert")
  env[]      : { clé, source, déduit?: bool }   # déduit = signalé pour véto
  readyUrl   : URL + signal de disponibilité
  testCommand: { unit?, integration? }
  paidOps[]  : opérations payantes repérées
  gaps[]     : champs non couverts + pourquoi (remontés tels quels)
}
```

- Les `gaps` ne bloquent pas la découverte : ils bornent honnêtement ce que la validation pourra couvrir.
- Rien de spécifique à un projet n'est mis en dur ici : la recette est **recalculée** à chaque run (agnosticisme).
