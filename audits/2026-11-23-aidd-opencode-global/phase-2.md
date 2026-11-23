---
status: pending
---

# Instruction: Rendre le détecteur agnostique

## Architecture projection

```txt
.
├── README.md ✏️
├── skills/
│   └── aidd-updates/
│       ├── SKILL.md ✏️
│       └── actions/
│           └── 01-lire-etat.md ✏️
├── tools/
│   ├── aidd-updates.py ✅
│   ├── manifests/
│   │   ├── claude.json ✏️
│   │   └── opencode.json ✏️
│   └── tests/
│       └── test-aidd-updates.sh ✅
└── wrappers/
    └── claude/
        └── scripts/
            ├── aidd-updates.py ❌
            └── tests/
                └── test-aidd-updates.sh ❌
```

## Test Scope

| Scenario | Action | Observable outcome | Actor |
| -------- | ------ | ------------------ | ----- |
| Setup | la batterie fabrique un `installed_plugins.json`, un manifeste AIDD et une liste de tags dans un dossier jetable | fixtures prêtes, aucun accès à `~/.claude`, `~/.config` ni au réseau | system |
| Happy path | calibrage Claude seul : `aidd-dev` 2.7.0 installé, tag 2.8.0 | `--etat` rend `retards.aidd-dev` de 2.7.0 vers 2.8.0 et `runtimes: [claude]` | cli |
| Happy path | calibrage OpenCode seul : manifeste AIDD avec `aidd-dev` 2.7.0, pas de `installed_plugins.json` | même retard, `runtimes: [opencode]` | cli |
| Edge case | les deux runtimes, Claude à 2.8.0 et OpenCode à 2.7.0 | `cle_installe.aidd-dev` vaut 2.7.0, `runtimes: [claude, opencode]` | cli |
| Edge case | aucun des deux fichiers | `derniere_erreur` non nul, sortie 0, aucune trace | cli |
| Edge case | manifeste AIDD illisible, Claude lisible | le retard Claude est rendu, `derniere_erreur` nomme le manifeste | cli |
| Teardown | fin de la batterie | le dossier jetable est supprimé | system |

## Tasks to do

### `1)` Déplacer le détecteur en zone neutre

> Un seul détecteur, lié dans les deux configs.

1. `git mv` du script vers `tools/aidd-updates.py` et de la batterie vers `tools/tests/test-aidd-updates.sh`. Le chemin `SCRIPT` de la batterie (`$ICI/../aidd-updates.py`) reste juste, seule sa ligne `Usage` change.
2. Remplacer l'ancien chemin de la batterie dans `skills/aidd-updates/SKILL.md:73` et `skills/aidd-updates/actions/01-lire-etat.md:36`.
3. `tools/manifests/claude.json` : sources des liens `scripts/aidd-updates.py` et `scripts/tests/test-aidd-updates.sh` vers les nouveaux chemins, cibles inchangées, donc `wrappers/claude/settings.json:41` ne bouge pas.
4. `tools/manifests/opencode.json` : ajouter le lien `scripts/aidd-updates.py`.

### `2)` Lire tous les runtimes présents

> Le détecteur voit les plugins installés sous Claude, sous OpenCode, ou les deux.

1. Ajouter la lecture du manifeste AIDD global (`~/.config/aidd/manifest.json`, clé `.tools.opencode.plugins`), avec la surcharge `AIDD_UPDATES_AIDD_MANIFEST` pour la batterie. Trancher par une mesure la prise en compte de `XDG_CONFIG_HOME`.
2. Retenir par plugin la version la plus basse, et écrire un champ `runtimes` dans le front-matter et dans `--etat`.
3. Un runtime absent n'est pas une panne. Aucun runtime lisible en est une, écrite dans `derniere_erreur`. Un fichier présent mais illisible s'y écrit aussi, sans masquer l'autre runtime.
4. Garder le contrat existant : sortie 0, pas de réseau sur `--notify`, un seul écrivain du front-matter.

### `3)` Mesurer la commande de montée OpenCode

> L'action 03 lancera une commande prouvée, pas supposée.

1. Sur un HOME jetable, installer une version antérieure du framework par la CLI, puis essayer `sync --global`, `plugin update --scope user --tool opencode` et `framework update`, et noter laquelle fait monter `.tools.opencode.plugins[].version`.
2. Remplacer la ligne « non vérifié » de la commande de montée dans la table Impact de `plan.md` par la commande retenue et sa mesure, que la phase 3 reprend.

### `4)` Étendre la batterie

> Chaque cas du Test Scope est un cas de la batterie, calibrage d'abord.

1. Un calibrage par runtime, en tête, qui arrête la batterie s'il échoue.
2. Les cas « deux runtimes », « aucun runtime » et « manifeste illisible ».

### `5)` Mettre le README à jour

> La section « La veille des plugins AIDD » décrit le détecteur tel qu'il est.

1. Nouveaux chemins des commandes, lecture des deux runtimes, champ `runtimes`.

## Test acceptance criteria

| Task | Acceptance criteria |
| ---- | ------------------- |
| 1 | `grep -rn "wrappers/claude/scripts/aidd-updates\|wrappers/claude/scripts/tests/test-aidd-updates" .` ne rend rien hors `audits/`, et `install.py --check` des deux agents, lancé sur une cible jetable avec `--fix`, rend aucun écart, et `~/.claude/scripts/aidd-updates.py` y pointe vers `tools/aidd-updates.py` |
| 2 | `--etat` rend le retard et `runtimes` attendus pour chacun des trois cas Claude seul, OpenCode seul et les deux |
| 3 | la commande retenue fait passer la version d'un plugin du manifeste jetable de l'ancienne à la nouvelle |
| 4 | `bash tools/tests/test-aidd-updates.sh` sort en 0, et un calibrage cassé à la main la fait sortir en 1 |
| 5 | `python3 tools/check-doc.py` reste vert, et aucun chemin `wrappers/claude/scripts/aidd-updates.py` ne subsiste dans le README |
