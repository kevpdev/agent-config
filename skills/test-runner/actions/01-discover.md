# 01 - Découvrir la recette de run

Reconstitue comment démarrer et comment tester l'app, sans rien démarrer.

## Input

Le repo du projet à tester, et le changement à valider quand le caller le nomme.

## Output

La `recipe`, passée en contexte à `02-lifecycle` puis `03-validate-live`. Elle ne s'écrit dans aucun
fichier.

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

## Process

1. **Balayer.** Parcourir les sources dans l'ordre fixe de
   [`../references/discovery.md`](../references/discovery.md) : fichiers env, puis config framework,
   puis docs run.
2. **Remplir.** Pour chaque champ de la recette, descendre l'échelle découvrir, déduire, escalader.
   - Un candidat qui sert la fonction se retient même si son nom ne matche pas, et se signale pour
     véto humain via le drapeau `déduit`.
   - Un champ ni trouvable ni déductible se marque **non couvert** et part dans `gaps`.
3. **Repérer les ops payantes.** Lister dans `paidOps` tout ce qui coûte à l'appel, une extraction
   LLM live par exemple. C'est cette liste que le garde-coût de `03-validate-live` consomme.
4. **Rendre.** Passer la recette et ses `gaps` à `02-lifecycle`. Les `gaps` ne bloquent pas la
   découverte, ils bornent d'avance ce que la validation pourra couvrir.

## Test

| Cas | Preuve |
| --- | --- |
| lancer la découverte sur un repo sans aucun fichier env | `env[]` est vide et les champs manquants sont dans `gaps`, la découverte rend quand même sa recette |
| lancer la découverte sur un repo dont la clé porte un nom inattendu | le champ est rempli et son entrée porte `déduit: true` |
| comparer deux runs sur deux repos différents | aucune valeur du premier ne réapparaît dans le second |
| relire la recette rendue | aucun champ n'est rempli sans source nommée |
