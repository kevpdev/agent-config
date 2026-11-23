---
objective: "AIDD est installé globalement pour OpenCode sur la machine, documenté, et /aidd-updates détecte, planifie et applique les montées AIDD aussi bien sous OpenCode que sous Claude Code."
status: done
---

# Plan: AIDD global sous OpenCode, et /aidd-updates agnostique

Source: issue kevpdev/agent-config#122, élargie par l'utilisateur le 2026-11-23 (« j'aimerais que le skill soit agnostique donc doit fonctionner aussi pour opencode »).

## Phases

| #   | Phase | File | Depends on |
| --- | ----- | ---- | ---------- |
| 1   | Installer AIDD global sous OpenCode et le documenter | [`phase-1.md`](./phase-1.md) | none |
| 2   | Rendre le détecteur agnostique | [`phase-2.md`](./phase-2.md) | 1 |
| 3   | Rendre le skill agnostique | [`phase-3.md`](./phase-3.md) | 2 |

## External sources

| URL | What it settled |
| --- | --------------- |
| https://github.com/ai-driven-dev/framework/blob/main/docs/INSTALL.md | `setup --global` couvre `opencode` depuis la CLI 5.7.0. Table « Update » : `sync --global` pour une installation globale par la CLI |
| https://github.com/ai-driven-dev/framework/blob/main/cli/README.md#scope | pour `opencode`, `setup --global` copie skills et agents dans `~/.config/opencode/` |
| https://github.com/ai-driven-dev/framework/blob/main/cli/CHANGELOG.md | `setup --global` arrive en 5.7.0 (2026-11-13, framework#1142) |

## Impact

| Category | Verdict and evidence | Handled in |
| -------- | -------------------- | ---------- |
| runtime | Mesuré le 2026-11-23 sur un HOME jetable rempli par le vrai `install.py` puis la vraie CLI 5.7.0 : 55 skills sous `skills/aidd-*/`, 4 agents sous `agents/`, état dans `~/.config/aidd/manifest.json` (`.tools.opencode.plugins[].name/version`). `opencode.json` inchangé (même sha256). `install.py --check` sans écart dans les deux sens. Non vérifié : le refus de la CLI sur un fichier dont elle n'a pas la propriété ne s'est jamais déclenché, parce que les chemins des deux outils sont disjoints (`skills/aidd-*/`, `agents/` contre les liens `skills/<nom>`). `opencode debug skill` voit les 55 skills dans un dépôt sans `.opencode/`. La CLI exige `--source remote` en mode non interactif, absent de la doc | 1 |
| runtime | Mesuré le 2026-11-23 sur un HOME jetable, CLI 5.7.0, installation `setup --global --release v5.10.0` (`aidd-dev` 2.5.0, `aidd-refine` 3.0.1). Ni `sync --global --force`, ni `sync --scope user --tool opencode --force`, ni `plugin update --scope user --tool opencode` (« All plugins are up to date », même après `marketplace refresh --force`), ni `framework update --tool opencode --force` ne changent `.tools.opencode.plugins[].version`. La marketplace reste épinglée sur `ref: v5.10.0` dans `aidd/marketplaces.json`. Seul `setup --global --release v5.14.0` fait monter (`aidd-dev` 2.8.0, `aidd-refine` 3.2.0), mais il laisse les fichiers disparus de la nouvelle version (skills `aidd-dev/10-todo` et `aidd-dev/11-browser-qa`, actions de `01-plan`, dossier `agents/`), et `sync --global` ne les retire pas. **Commande retenue** : `clean --global --force`, puis `setup --global --source remote --release vX.Y.Z --ide opencode --plugins aidd-context,aidd-dev,aidd-vcs,aidd-pm,aidd-orchestrator,aidd-refine`. Mesuré avec `aidd-dev,aidd-refine` : `diff -r` entre le `.config/opencode` obtenu ainsi et celui d'une installation neuve en `--release v5.14.0` sur un autre HOME jetable ne rend aucune différence, alors que le même `diff -r` après `setup --release` seul liste les fichiers restés. Sans `--release`, `setup` interroge l'API des releases GitHub, qui a rendu des 504 pendant la mesure, d'où un tag explicite | 2, 3 |
| runtime | Mesuré le 2026-11-23, `HOME=A` et `XDG_CONFIG_HOME=B` disjoints : le manifeste va dans `B/aidd/manifest.json`, les fichiers OpenCode dans `A/.config/opencode/`. Le détecteur lit donc `${XDG_CONFIG_HOME:-~/.config}/aidd/manifest.json` | 2 |
| runtime | Non vérifié : comment invoquer à la main sous OpenCode un skill `disable-model-invocation: true` | 3 |
| regression | `wrappers/claude/scripts/tests/test-aidd-updates.sh` (devenu `tools/tests/test-aidd-updates.sh` en phase 2) couvre le détecteur (calibrage, notify, plan gardé ou invalidé). Risque moyen : le déplacement du script change la source d'un lien de `~/.claude/scripts/aidd-updates.py`, appelé par le `SessionStart` de `wrappers/claude/settings.json:41`. Pas de phase filet, la batterie existante sert de filet et doit rester verte à chaque phase | 2 |
| architecture | Le détecteur vit dans `wrappers/claude/scripts/`, propre à Claude. Il passe dans `tools/`, zone neutre comme `tools/worktree.sh`, lié dans les deux manifestes d'`install.py` | 2 |
| documentation | README, sections « OpenCode » (installation AIDD) et « La veille des plugins AIDD » (chemins, runtimes). Avenant daté à `audits/2026-11-02-cadrage-workflow-coeur.md`. `skills/aidd-updates/references/detecteur.md` | 1, 2, 3 |

## Rules

| Rule | Why it applies |
| ---- | -------------- |
| `rules/reasoning.md`, substrat de vérification | la montée et l'invocation sous OpenCode se mesurent contre le vrai, le jetable ne sert que là où le vrai est partagé par les sessions ouvertes |
| `rules/redaction.md`, pas d'inventaire qui bouge | le README renvoie à la commande, pas à une liste de plugins ou de skills comptés |
| `rules/aidd.md`, langue | code et commentaires en anglais, README et plan en français |
| `rules/worktrees.md`, harnais dont `~/.claude` pointe vers le checkout | après le merge, `tools/bascule.sh` repose les liens dont la source a bougé |
| `rules/skill-description.md` | toute modification de `skills/aidd-updates/SKILL.md` garde une description sans chevrons |

## Decisions

| Decision | Why |
| -------- | --- |
| Un seul détecteur neutre qui lit tous les runtimes présents, plutôt qu'un détecteur par wrapper | un seul fichier d'état et un seul écrivain du front-matter. Deux détecteurs écriraient le même `plan.md` |
| Version installée d'un plugin : la plus basse parmi les runtimes qui l'ont, plus un champ `runtimes` qui liste les runtimes détectés | le plan porte sur le retard le plus grand, et l'action 03 monte chaque runtime listé. Les deux runtimes montent vers la même dernière version upstream |
| Installation AIDD à la main et documentée dans le README, ni pilotée par `install.py` ni par `tools/bascule.sh` (étape 3 de l'issue) | une commande lancée une fois par machine, et réversible par `clean --global --force`. La faire porter par `install.py` ajouterait une dépendance réseau à npm dans un outil que toutes les sessions chargent, et la montée passe par `/aidd-updates` |
| Les 6 plugins installés sous Claude, pas `--plugins all` | `all` ajoute `aidd-ui` (alpha), `aidd-telemetry` et `aidd-qa`, absents sous Claude |
| La notification de démarrage sous OpenCode reste hors de ce plan | le skill fonctionne sans elle, par invocation manuelle. La brancher touche le plugin `harness-guards`, un autre chantier |
