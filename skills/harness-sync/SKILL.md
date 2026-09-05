---
name: harness-sync
description: "Diagnostique et répare l'écart entre ce repo et le harnais Claude Code déployé sur ce poste (~/.claude) — retard du dépôt local sur origin, symlinks manquants ou orphelins des skills/agents/output-styles/scripts, dérive de settings.json. S'invoque par /harness-sync, jamais automatiquement. NE PAS utiliser pour ajouter une permission, un hook ou une variable d'environnement (→ update-config), pour committer ou pousser du code applicatif (→ aidd-vcs:01-commit), ni pour synchroniser une documentation projet (→ doc-sync)."
argument-hint: rien à apporter, ou le nom d'une action (sync-git, sync-links, check-settings) pour ne jouer qu'elle
disable-model-invocation: true
---

# harness-sync

Vérifie et répare l'écart entre ce repo et le harnais réellement déployé dans `~/.claude`, en s'arrêtant sur toute couche qui demande un arbitrage humain plutôt que d'improviser une réparation.

```mermaid
flowchart TD
  entree[/harness-sync] --> git[sync-git]
  git -- ok --> links[sync-links]
  git -- bloqué : réseau, working tree, divergence --> kogit([KO git, raison rendue])
  kogit --> links
  links -- ok --> settings[check-settings]
  links -- orphelin ou conflit --> koliens([KO liens, arbitrage listé])
  koliens --> settings
  settings -- conforme --> pret([harnais synchronisé])
  settings -- écart --> kosettings([KO settings, diff rendu])
```

## Actions

Dérouler le flux dans l'ordre. Ne lire que la prochaine action.

| Action | Fait |
| --- | --- |
| sync-git | aligner la branche locale sur origin, fast-forward seulement |
| sync-links | réparer les symlinks manquants entre le repo et ~/.claude |
| check-settings | diagnostiquer l'écart de settings.json face au repo, sans jamais écrire |

## Transversal rules

- Chaque couche joue même si la précédente s'est arrêtée sur un cas bloquant : elles sont indépendantes, un blocage git ne dit rien de l'état des symlinks.
- Aucune couche n'écrit hors de son propre domaine : `sync-git` ne touche pas aux symlinks, `sync-links` ne touche pas à `settings.json`.
- Le rapport final rend une ligne par couche — OK, ou KO avec sa raison et l'arbitrage attendu — jamais un verdict global unique qui écraserait le détail.
- Tout blocage se résout par un arrêt et un rapport écrit, jamais par une question interactive en cours de route. C'est la convention déjà en usage dans `doc-sync`, `skill-craft` et `test-runner`.
- `wrappers/claude/` est aujourd'hui tout le harnais : aucun autre wrapper de runtime n'existe dans ce repo, le périmètre s'arrête à lui et à `~/.claude/`.

## Test

Jouable seul, sans session neuve : les trois actions tranchent sans jugement LLM.

| Cas | Preuve |
| --- | --- |
| dépôt et harnais déjà synchronisés | les trois couches rendent « conforme », aucune écriture |
| `python3 wrappers/claude/scripts/lint-skills.py --skill harness-sync` | rend 0 |
