---
status: done
---

# Instruction: Installer AIDD global sous OpenCode et le documenter

## Architecture projection

```txt
.
├── README.md ✏️
└── audits/
    └── 2026-11-02-cadrage-workflow-coeur.md ✏️
```

## Test Scope

| Scenario | Action | Observable outcome | Actor |
| -------- | ------ | ------------------ | ----- |
| Setup | `python3 tools/install.py --agent opencode --target ~/.config/opencode --check` | « 23 liens et opencode.json, aucun écart », sha256 de `opencode.json` noté | cli |
| Happy path | `npx @ai-driven-dev/cli@5.7.0 setup --global --source remote --ide opencode --plugins aidd-context,aidd-dev,aidd-vcs,aidd-pm,aidd-orchestrator,aidd-refine --yes` | « Installed for every project on this machine » avec les 6 plugins | cli |
| Happy path | `opencode debug skill` lancé dans un dépôt sans `.opencode/` | les skills AIDD des 6 plugins sont listés, aucun nom en double | cli |
| Edge case | `install.py --check` relancé après l'installation | toujours aucun écart, sha256 de `opencode.json` identique | cli |
| Edge case | `npx @ai-driven-dev/cli@5.7.0 doctor --global` | « User-scope installation is healthy » | cli |

## Tasks to do

### `1)` Installer sur la machine

> Les 6 plugins de Claude, sur le vrai `~/.config/opencode`.

1. Noter le sha256 de `~/.config/opencode/opencode.json` et la sortie de `install.py --check`.
2. Lancer la commande `setup --global` du Test Scope, avec `npm_config_ignore_scripts=true`.
3. Rejouer `install.py --check`, `doctor --global` et `opencode debug skill`.

### `2)` Documenter dans le README

> Un lecteur sur une machine neuve installe AIDD sous OpenCode sans relire l'issue.

1. Dans la section « OpenCode », ajouter un paragraphe : la commande, l'obligation de `--source remote` en non interactif, la liste de plugins alignée sur Claude, le retrait par `clean --global --force`, et le fait qu'aucun conflit n'existe avec `install.py` (chemins disjoints).
2. Ne pas écrire de compte de skills.

### `3)` Avenant au cadrage

> Le cadrage du 2026-11-02 ne laisse plus croire que l'installation globale est impossible.

1. Sous la table « L'installation globale n'est pas supportée par AIDD », ajouter un avenant daté du 2026-11-23 qui renvoie à #122 et à la CLI 5.7.0, sans réécrire le texte existant.

## Test acceptance criteria

| Task | Acceptance criteria |
| ---- | ------------------- |
| 1 | `opencode debug skill` liste les skills AIDD dans un dépôt sans `.opencode/`, `install.py --check` reste sans écart et `opencode.json` garde son sha256 |
| 2 | `python3 tools/check-doc.py` reste vert, et la section « OpenCode » du README contient la commande avec `--source remote` |
| 3 | le cadrage porte un avenant daté qui cite #122, et `git diff` ne montre aucune ligne supprimée dans ce fichier |
