# 03 - Rédiger

Écrit le fichier HTML à partir du gabarit et des faits réunis.

## Input

Le bloc d'entrées de `frame`, les sources et le fil conducteur de `research`. Au retour de `check`, son rapport.

## Output

Le fichier `<dossier>/<slug>.html` fixé par `frame`.

## Process

1. **Charger.** Lire [`../references/contrat-document.md`](../references/contrat-document.md) et [`../references/controles-redaction.md`](../references/controles-redaction.md) avant d'écrire.
2. **Copier.** Copier [`../assets/gabarit-document.html`](../assets/gabarit-document.html) vers le chemin de sortie, sans toucher au bloc `<style>` sauf pour ajouter une classe.
3. **Remplir.** Remplacer chaque zone « à remplir » en suivant l'ordre des 12 blocs du contrat.
   - Dupliquer la section numérotée autant de fois que le parcours a d'étapes, et reporter chaque ajout dans le sommaire.
   - Dessiner les 5 illustrations minimales selon la section « Illustrations » du contrat, chacune dans un `<div class="scroll">`.
   - Mesurer la largeur de chaque libellé SVG contre sa boîte, à 7 px par caractère environ, et agrandir la boîte plutôt que tronquer. *Pourquoi 7 : la règle `svg text` du gabarit pose une police condensée, qui fait environ une demi-taille par caractère. C'est une estimation, et le rendu PDF de `check` tranche.*
4. **Purger.** Vérifier par `grep -n "à remplir"` sur le fichier qu'aucune zone du gabarit ne survit.
   - **Garde.** Une zone restante bloque le passage à `check`. La remplir ou supprimer son bloc, jamais la laisser.
5. **Corriger**, au retour de `check` seulement. Appliquer chaque ligne du rapport, et ne rien réécrire d'autre.
   - Une ligne jugée à tort se garde telle quelle, avec sa raison en une ligne dans le compte rendu final.

## Test

| Cas | Preuve |
| --- | --- |
| `grep -c "à remplir"` sur le fichier livré | affiche 0 |
| `grep -c "<svg"` sur le fichier livré | rend 5 ou plus |
| `grep -c -e 'fill="#' -e 'stroke="#'` sur le fichier livré | affiche 0, toutes les couleurs passent par les classes |
