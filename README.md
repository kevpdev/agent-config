# agent-config

Configuration centralisée pour agents de code : règles de comportement, skills experts, et le câblage propre à chaque runtime.

Pas d'outils, pas de CLI — de l'instruction en markdown.

## Structure

```
rules/              règles chargées en contexte — neutres
skills/             expertises chargées à la demande — neutres
  _shared/          références partagées entre plusieurs skills
wrappers/
  claude/           tout ce qui ne fonctionne que sous Claude Code
```

## La règle de placement

Un fichier va dans `wrappers/<runtime>/` si et seulement si **il cesse de fonctionner sans ce runtime**.

| | Exemple | Où |
|---|---|---|
| **Dépendance** | un hook qui parse le JSON d'événement de Claude Code | wrapper |
| **Indice** | un frontmatter `paths:` qu'un autre runtime ignorera sans dommage | zone neutre |

Le critère n'est pas « mentionne Claude » — une règle qui interdit de citer un assistant dans un message de commit reste universelle. Le critère est : **ça échoue, ou ça dégrade sans casse ?**

## `rules/` ou `skills/` ?

| | `rules/` | `skills/` |
|---|---|---|
| Découverte | automatique, récursive | automatique, via la `description` |
| Chargement | **en contexte** — toujours, ou sur match `paths:` | **à la demande** — quand jugé pertinent |
| Coût | permanent | nul tant qu'inutilisé |

Ce qui doit être vrai en permanence est une règle. Ce qui ne sert que sur une tâche précise est un skill.

Une règle peut se restreindre à certains fichiers via son frontmatter — `back-spring.md` ne se charge que sur du Java :

```yaml
---
paths:
  - "**/*.java"
  - "**/pom.xml"
---
```

Un skill se déclenche sur sa `description` : la soigner, c'est tout ce qui décide s'il sera choisi ou ignoré.

## Utilisation avec Claude Code

Claude Code découvre ces dossiers automatiquement, sans rien déclarer. Aucun `CLAUDE.md` global n'est nécessaire.

| Ce repo | Emplacement attendu |
|---|---|
| `rules/` | `~/.claude/rules/` |
| `skills/` | `~/.claude/skills/` |
| `wrappers/claude/agents/` | `~/.claude/agents/` |
| `wrappers/claude/output-styles/` | `~/.claude/output-styles/` |
| `wrappers/claude/rules/` | `~/.claude/rules/` |
| `wrappers/claude/scripts/` | `~/.claude/scripts/` |
| `wrappers/claude/settings.json` | `~/.claude/settings.json` |

Les symlinks sont supportés — lier plutôt que copier garde le repo comme source unique.

## Dépendance externe

`skills/aidd-pilot/` orchestre les plugins du framework [AI-Driven Dev](https://github.com/ai-driven-dev/framework) et ne fonctionne pas sans eux — voir `skills/aidd-pilot/README.md`. Les autres skills sont autonomes.

Les skills `vault-*` sont des passerelles vers un vault Obsidian : ils délèguent aux skills canoniques situés sous `$OBSIDIAN_VAULT_PRO/agent/skills/`. Pour les activer, exporter la variable dans son shell :

```bash
export OBSIDIAN_VAULT_PRO="/chemin/absolu/vers/le/vault"
```

Sans cette variable, chaque `vault-*` dégrade sans casse (garde-fou en tête du SKILL.md : message « vault non configuré » puis arrêt, jamais d'écriture dans le repo courant).

## Reprendre ce repo

Un seul fichier n'est pas transposable : **`rules/profil.md`**. Il décrit la personne à qui l'agent s'adresse — niveau technique, contraintes cognitives, mode de compréhension — pour calibrer ton et profondeur. Le remplacer par le sien ; le format compte, pas le contenu.

Tout le reste s'applique tel quel.

## Conventions d'écriture

Toute règle énonce sa **raison**, pas seulement l'ordre — un LLM suit mieux un pourquoi qu'un impératif, et transfère au cas non prévu.

Préférer « négation + alternative » à l'interdit sec : *ne fais pas X — à la place, fais Y*. Énoncer une négation seule active le concept avant de le nier.

Les messages de commit suivent [Conventional Commits](rules/commit-convention.md), en anglais.
