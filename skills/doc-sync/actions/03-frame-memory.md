# 03 - Cadrer la mémoire

Décide, pour chaque fait candidat, s'il reste en mémoire, devient un pointeur ou sort. N'écrit rien.

## Input

Les lignes de régime mémoire AIDD de `scope.md`, et le banc de mémoire à son home. Sur un retour de `check-memory`, les seuls constats routés ici.

## Output

Un plan de mémoire montré à l'humain, une ligne par candidat : le fait, le fichier qui le rend inférable ou « aucun », le verdict, et sa réconciliation.

## Process

1. **Charger.** Lire [`../references/memory-criteria.md`](../references/memory-criteria.md), puis les quatre poids d'AIDD dans `aidd-context/skills/10-learn/references/assessment.md`, qui font foi sur les quatre.
2. **Lister les candidats.** D'abord les faits neufs du diff, puis les faits déjà en place dans les fichiers que la passe touche. En `--audit`, seulement les seconds, sur tout le scope.
   - Sur un retour de `check-memory`, ne pas relister : le périmètre est les constats routés.
3. **Mesurer.** Pour chaque candidat, ouvrir le fichier qui le porte dans le code ou la config. Un candidat dont la source n'a pas été ouverte se marque « supposé ».
4. **Regrouper par cause.** `grep` chaque fait dans le home. Plus d'un fichier touché signale un symptôme, et on cherche le fichier qui produit le fait.
   - Le lot reçoit un « garder » chez la cause et un « sortir » par symptôme. Tout groupement cite la commande qui l'a établi.
5. **Trancher et réconcilier.** Appliquer le verdict en trois issues du critère, puis sa réconciliation `10-learn`. Un `covered` ne descend pas.
6. **Rendre le plan** avec le coût que demande le critère, plus le nombre de symptômes supprimés.
   - **Garde.** Retirer une phrase écrite à la main est une décision : ce verdict se soumet, il ne s'applique pas seul.

## Test

| Cas | Preuve |
| --- | --- |
| chaque ligne du plan | nomme un fichier source ou « aucun », et porte un verdict |
| un groupement de candidats | cite le `grep` qui l'a établi |
| `git status --porcelain aidd_docs/memory/` avant et après | même sortie |
