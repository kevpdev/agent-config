# Le détecteur — contrat de commandes et emplacement

> Table de référence des actions de `aidd-updates`. Elle porte la donnée consultée, la décision de
> flux reste dans les actions.

## Pourquoi ce fichier existe

Le détecteur (`tools/aidd-updates.py`) lit les plugins AIDD installés sous Claude Code et sous
OpenCode, et tient un seul fichier d'état pour les deux. Il est lié dans la config de chaque runtime.

**Le skill dit quoi appeler, cette référence dit où et avec quelle commande.** C'est le même partage que
`SKILLS_ROOT` dans le README du repo. Une commande propre à un runtime écrite dans une action rendrait
le skill inutilisable sous l'autre, alors qu'ici seul l'emplacement change, jamais le contrat.

## Emplacement, spécifique au runtime

| Runtime | Commande du détecteur |
|---|---|
| Claude Code | `python3 "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/scripts/aidd-updates.py"` |
| OpenCode | `python3 "${OPENCODE_CONFIG_DIR:-$HOME/.config/opencode}/scripts/aidd-updates.py"` |

Prendre la ligne du runtime de la session en cours. Les deux lancent le même script et lisent le même
fichier d'état.

## Commandes

| Commande | Effet | Quand |
|---|---|---|
| `--etat` | rend le front-matter en JSON sur stdout, plus les champs calculés `retards`, `plan_a_refaire`, `corps_present`, `fichier` | action 01, toujours en premier |
| `--refresh` | va chercher les tags upstream, recalcule les clés, préserve le plan si rien n'a bougé | action 01, seulement si `verifie_le` est vieux ou absent |
| `--marquer-planifie` | lit le corps du plan sur **stdin**, l'écrit sous le front-matter, pose `planifie_le` et `statut: planifie` | fin de l'action 02 |
| `--marquer-applique` | pose `statut: applique`, ce qui fait taire la notification jusqu'à la prochaine version | fin de l'action 03 |

Le script sort toujours en 0. Une panne se lit dans `derniere_erreur`, jamais dans le code de sortie.

## Champs de `--etat` qui portent une décision

| Champ | Lecture |
|---|---|
| `retards` | vide → rien à faire. Non vide → il y a de quoi planifier. |
| `plan_a_refaire` | `true` → aucun plan, ou plan invalidé par une nouvelle version. `false` → le plan sur disque tient. |
| `cassant` | liste des plugins qui changent de majeur. Non vide → le plan doit ouvrir par eux. |
| `derniere_erreur` | non nul → l'afficher **avant** toute autre sortie, l'état peut être partiel. |
| `fichier` | le chemin du plan, à lire pour en récupérer le corps. |
| `runtimes` | les runtimes où AIDD est installé (`claude`, `opencode`). La montée porte sur chacun, et sur eux seuls. Les versions de `cle_installe` sont les plus basses des runtimes listés. |

## Commandes de montée, par runtime

N'exécuter que les lignes des runtimes présents dans `runtimes`. Après la montée, relancer `--refresh`
puis `--etat` : `retards` doit être vide.

| Runtime | Commandes | Vérification |
|---|---|---|
| `claude` | `claude plugin marketplace update aidd-framework`, puis `claude plugin update <plugin>@aidd-framework` pour chaque plugin en retard | `claude plugin list --json` rend les versions cibles |
| `opencode` | `npx -y @ai-driven-dev/cli@5.7.0 clean --global --force`, puis `npm_config_ignore_scripts=true npx -y @ai-driven-dev/cli@5.7.0 setup --global --source remote --release vX.Y.Z --ide opencode --plugins <liste> --yes` | `npx -y @ai-driven-dev/cli@5.7.0 doctor --global` rend « User-scope installation is healthy » |

**Sous OpenCode, la montée réinstalle tout.** Ni `sync --global`, ni `plugin update --scope user`, ni
`framework update` ne font monter une installation globale, mesuré le 2026-11-23 avec la CLI 5.7.0
(#122). Seul `setup --global --release` le fait, et il laisse en place les fichiers que la nouvelle
version a retirés, d'où le `clean` avant.

- **`<liste>`** : tous les plugins installés sous OpenCode, pas seulement ceux en retard, parce que
  `clean` les retire tous. La relever **avant** le `clean`, dans le manifeste de la CLI :
  `python3 -c 'import json,os; p=os.path.join(os.environ.get("XDG_CONFIG_HOME") or os.path.expanduser("~/.config"),"aidd","manifest.json"); print(",".join(x["name"] for x in json.load(open(p))["tools"]["opencode"]["plugins"]))'`.
- **`vX.Y.Z`** : le dernier tag de release du framework, de la forme `vX.Y.Z`, dans le dépôt que le
  détecteur interroge (`git ls-remote --tags https://github.com/ai-driven-dev/framework.git`). Le
  détecteur, lui, compare les tags par plugin (`aidd-<plugin>-vX.Y.Z`) : la release retenue doit
  porter les versions de `cle_upstream`, ce que `--etat` confirme après la montée.

## Où lire les changelogs des versions sautées

Sans authentification, le dépôt étant public :

```
https://raw.githubusercontent.com/ai-driven-dev/framework/main/plugins/<plugin>/CHANGELOG.md
```

Le fichier est produit par release-please, donc chaque version y est une section `## [X.Y.Z]`, et un
majeur porte une section `### ⚠ BREAKING CHANGES` qui décrit le changement en prose.

**Lire aussi le changelog racine** (`CHANGELOG.md` à la racine du dépôt) quand un changement ne se
rattache à aucun plugin, par exemple un déplacement de l'arborescence `aidd_docs/`.
