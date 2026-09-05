# 03 - Diagnostiquer l'écart de settings.json

Compare `wrappers/claude/settings.json` (le repo) à `~/.claude/settings.json` (le fichier vivant), sans jamais y écrire.

## Output

Un diff textuel des hooks et des clés partagées, ou « conforme » si rien ne diverge.

## Process

1. **Lire les deux fichiers.** Parser `wrappers/claude/settings.json` et `~/.claude/settings.json` en JSON.
   - **Garde.** L'un des deux ne parse pas → arrêter, rendre KO « JSON invalide », nommer le fichier fautif.
2. **Comparer les hooks.** Pour chaque hook déclaré côté repo, vérifier sa présence côté vivant, puis si le script qu'il référence existe dans `~/.claude/scripts/`.
   - Hook absent côté vivant → le lister, jamais ajouté seul.
   - Hook présent mais script cible absent de `~/.claude/scripts/` → le lister à part comme incohérence : le hook est inatteignable, et corriger est ambigu entre lier le script manquant ou retirer le hook — décision humaine.
3. **Comparer les clés partagées.** Pour toute clé présente des deux côtés (`statusLine` compris), lister celles dont la valeur diffère.
   - Ne jamais lister comme écart une clé qui n'existe que côté vivant : les préférences personnelles (`permissions`, `voice`, `tui`, `language`, etc.) ne sont pas censées venir du repo.
4. **Rendre le diff.** Hooks manquants, incohérences de script, valeurs différentes — cette action ne modifie jamais `~/.claude/settings.json`.

## Test

| Cas | Preuve |
| --- | --- |
| état actuel du poste (hooks manquants et `statusLine` divergent, déjà constatés) | le diff les cite tous, `~/.claude/settings.json` identique avant et après (`diff` sur une copie) |
| deux fichiers strictement alignés (copie de test) | rendu « conforme », rien à arbitrer |
| `~/.claude/settings.json` rendu invalide (copie de test tronquée) | KO « JSON invalide », nomme le fichier |
