---
status: done
---

# Instruction: Rendre le skill agnostique

## Architecture projection

```txt
.
└── skills/
    └── aidd-updates/
        ├── SKILL.md ✏️
        ├── actions/
        │   ├── 01-lire-etat.md ✏️
        │   └── 03-appliquer.md ✏️
        ├── assets/
        │   └── gabarit-plan.md ✏️
        └── references/
            └── detecteur.md ✏️
```

## Test Scope

| Scenario | Action | Observable outcome | Actor |
| -------- | ------ | ------------------ | ----- |
| Setup | phase 2 livrée. `install.py --fix --repo <worktree>` sur une config OpenCode jetable (`OPENCODE_CONFIG_DIR`) et sur le banc Claude (`CLAUDE_CONFIG_DIR=~/.claude-bench`, `tools/bench.sh`), les liens réels visant encore le checkout principal jusqu'à la bascule | les deux configs jetables lient le skill et le détecteur du worktree, et `--etat` rend `runtimes: [claude, opencode]` | cli |
| Happy path | `grep -rn "claude plugin\|~/.claude\|wrappers/claude" skills/aidd-updates/actions skills/aidd-updates/assets` | aucune occurrence, les commandes propres à un runtime ne vivent que dans `references/detecteur.md` | cli |
| Happy path | `/aidd-updates` invoqué dans une session OpenCode sur la config jetable | le skill lance `--etat` par le chemin OpenCode et rend un verdict | cli |
| Happy path | `/aidd-updates` invoqué dans une session Claude Code sur le banc | même verdict qu'avant le plan | cli |
| Edge case | `runtimes` ne contient que `opencode` | l'action 03 ne propose aucune commande `claude` | cli |

## Tasks to do

### `1)` Une table par runtime dans la référence

> Le skill dit quoi appeler, la référence dit où et avec quelle commande, pour chaque runtime.

1. `references/detecteur.md` : emplacement du détecteur sous Claude (`~/.claude/scripts/aidd-updates.py`) et sous OpenCode (`~/.config/opencode/scripts/aidd-updates.py`).
2. Une table « commandes de montée » par runtime : `claude plugin marketplace update` puis `claude plugin update` pour Claude, la commande mesurée en phase 2 pour OpenCode.
3. Documenter le champ `runtimes` dans la table des champs de `--etat`.

### `2)` Des actions neutres

> Aucune action ni gabarit ne cite une commande propre à un runtime.

1. `01-lire-etat.md` : afficher `runtimes` avec le verdict.
2. `03-appliquer.md` : monter chaque runtime listé dans `runtimes`, par la table de la référence, et vérifier chacun après coup. Remplacer la ligne de Test `bash wrappers/claude/scripts/sync-rules.sh` (l. 45) par `bash tools/test-all.sh`, neutre.
3. `assets/gabarit-plan.md` : la section « Commandes de la montée » renvoie à la table de la référence pour les runtimes listés.
4. `SKILL.md` : neutraliser la ligne de Test « aucune commande `claude plugin update` » et l'introduction qui ne parle que de Claude Code. Garder la description sans chevrons.

### `3)` Vérifier l'invocation sous OpenCode

> Le skill est réellement joignable sous OpenCode malgré `disable-model-invocation: true`.

1. Mesurer comment OpenCode expose un skill non proposé au modèle, dans une vraie session sur la config jetable du Setup.
2. Si OpenCode ne le rend pas invocable, s'arrêter et rendre la décision à l'humain plutôt que retirer le drapeau.

### `4)` Vérifications du dépôt

> La suite complète du repo passe avant la PR.

1. `bash tools/test-all.sh`.
2. `python3 tools/lint-skills.py` sur `skills/aidd-updates`.
3. `grep -rn '^description:.*[<>]' --include=SKILL.md skills/aidd-updates`.

## Test acceptance criteria

| Task | Acceptance criteria |
| ---- | ------------------- |
| 1 | `references/detecteur.md` nomme les deux emplacements et une commande de montée par runtime, et documente `runtimes` |
| 2 | le grep du Test Scope ne rend aucune occurrence dans `actions/` ni `assets/` |
| 3 | dans une session OpenCode, `/aidd-updates` rend le verdict de `--etat` |
| 4 | `test-all.sh` et `lint-skills.py` sortent en 0, et le grep des chevrons ne rend rien |
