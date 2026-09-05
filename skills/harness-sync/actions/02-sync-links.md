# 02 - Réparer les symlinks du harnais

Répare les liens manquants entre le repo et `~/.claude`, et signale tout le reste sans y toucher.

## Output

Par cible (`rules`, `skills`, `agents`, `output-styles`, `scripts`) : « conforme », « réparé (N liens créés) », ou la liste des cas laissés en arbitrage.

## Process

1. **Déléguer `rules/`.** Lancer `bash wrappers/claude/scripts/sync-rules.sh`, sans `--fix` d'abord.
   - **Garde.** Code de sortie autre que 0 ou 1 → instrument hors service, pas un défaut du harnais : arrêter, remonter la cause brute.
   - Code 1 : lister les écarts qu'il rapporte (`ABSENT`, `PAS UN LIEN`, `MAUVAISE CIBLE`, `ORPHELIN`, `INTRUS`). Ne réparer que via son propre `--fix`, jamais en réimplémentant sa logique de diff (zéro doublon).
2. **Parcourir les cibles à liens multiples.** Pour `skills/`, `wrappers/claude/agents/`, `wrappers/claude/output-styles/` et `wrappers/claude/scripts/` (récursif sur ses sous-dossiers `hooks/` et `tests/`), comparer chaque entrée source à son homologue dans `~/.claude/<cible>/`.
   - Rien à l'emplacement cible → créer le symlink (`ln -s`). Seul cas d'écriture automatique de cette action.
   - Symlink présent mais pointant ailleurs que la source attendue → arrêter pour cette entrée, la lister « mauvaise cible », jamais recréée seule.
   - Chemin cible occupé par un fichier ou un dossier réel, pas un symlink → la lister « conflit non-lien », jamais écrasée.
   - Symlink dans `~/.claude/<cible>/` dont la source a disparu du repo → la lister « orphelin, arbitrage humain », jamais supprimée seule.
3. **Rendre le tableau.** Une ligne par cible : conforme, réparée (avec le compte), ou son nombre de cas laissés en arbitrage.

## Test

| Cas | Preuve |
| --- | --- |
| un skill présent dans `skills/` sans lien dans `~/.claude/skills/` | lien créé, `readlink` confirme qu'il pointe vers le dossier du repo |
| symlink orphelin déjà connu (`~/.claude/skills/aidd-pilot`, cible disparue du repo) | listé « orphelin, arbitrage humain », toujours présent après coup |
| `sync-rules.sh` renvoyant un code 3 (script de test substitué) | rendu « instrument hors service », aucune réparation tentée à la place |
| tout conforme (relance juste après une réparation) | « conforme » sur chaque cible, aucune écriture jouée |
