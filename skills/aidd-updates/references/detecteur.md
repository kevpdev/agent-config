# Le détecteur — contrat de commandes et emplacement

> Table de référence des actions de `aidd-updates`. Elle porte la donnée consultée, la décision de
> flux reste dans les actions.

## Pourquoi ce fichier existe

Le détecteur lit `~/.claude/plugins/installed_plugins.json`, un fichier de Claude Code. Il vit donc
dans le wrapper du runtime, pas en zone neutre. Le skill, lui, doit rester portable.

**Le skill dit quoi appeler, cette référence dit où.** C'est le même partage que `SKILLS_ROOT` dans le
README du repo. Un chemin `~/.claude/…` écrit dans une action rendrait le skill inutilisable sous un
autre agent, alors qu'ici seul l'emplacement change, jamais le contrat.

## Emplacement, spécifique au runtime

Sous **Claude Code** : `python3 ~/.claude/scripts/aidd-updates.py`.

Sous un autre runtime, le producteur d'état est à réécrire, mais les commandes ci-dessous et le
format du fichier d'état sont le contrat à respecter.

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

## Où lire les changelogs des versions sautées

Sans authentification, le dépôt étant public :

```
https://raw.githubusercontent.com/ai-driven-dev/framework/main/plugins/<plugin>/CHANGELOG.md
```

Le fichier est produit par release-please, donc chaque version y est une section `## [X.Y.Z]`, et un
majeur porte une section `### ⚠ BREAKING CHANGES` qui décrit le changement en prose.

**Lire aussi le changelog racine** (`CHANGELOG.md` à la racine du dépôt) quand un changement ne se
rattache à aucun plugin, par exemple un déplacement de l'arborescence `aidd_docs/`.
