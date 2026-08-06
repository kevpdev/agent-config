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

> **Spécifique au runtime** : le scoping par `paths:` est une syntaxe **Claude Code**. Un autre runtime (Cursor utilise `globs:`, etc.) ignore cette clé — la règle est alors chargée **inconditionnellement** (elle reste correcte, juste non scopée), ou pas du tout si ce runtime n'auto-découvre pas `rules/`. C'est le « indice, pas dépendance » de la règle de placement : `paths:` ne casse rien ailleurs, mais ne compte pas dessus pour tenir une règle hors contexte hors de Claude Code.

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

**`~/.claude/rules/` est le seul cas particulier.** Deux dossiers de ce repo s'y déversent, et un lien de dossier ne fusionne pas : il faut donc un lien **par fichier**. Un fichier de règle neuf reste donc inerte jusqu'à ce que son lien existe, sans qu'aucun signal ne le dise. Les cinq autres cibles sont des liens uniques et ne peuvent pas dériver.

```bash
bash wrappers/claude/scripts/sync-rules.sh          # vérifie, échoue sur tout écart
bash wrappers/claude/scripts/sync-rules.sh --fix    # crée, répare, retire les orphelins
```

À lancer après tout ajout, renommage ou suppression dans `rules/` ou `wrappers/claude/rules/`.

### Jouer les évals des skills

Un skill qui porte un `evals/eval.json` déclare des scénarios en données pures : une requête, le comportement attendu, et de quoi juger. L'exécuteur, lui, est spécifique à Claude Code — ouvrir une session neuve passe par `claude -p`.

```bash
python3 wrappers/claude/scripts/run-skill-evals.py --self-test        # calibre le juge, ne joue aucun scénario
python3 wrappers/claude/scripts/run-skill-evals.py                    # joue tout, rend un tableau de verdicts
python3 wrappers/claude/scripts/run-skill-evals.py --skill code-reviewer --force
```

Chaque scénario rend deux verdicts. Le **déclenchement** est déterministe : les `trigger_markers` du scénario apparaissent-ils dans la sortie ? Le **comportement** passe par un juge LLM confronté aux `expected_behavior`. `--force` préfixe la requête par `/<skill>` et isole donc le comportement du déclenchement.

**Le déclenchement dépend d'abord du modèle, pas du skill.** Mesuré le 2026-08-06 sur quatre skills en deux répétitions, à skills, requêtes et règles identiques : **7/8 sur `opus`, 0/8 sur `sonnet`**. Deux des quatre ne déclenchaient jamais sous Sonnet et déclenchent 2/2 sous Opus. D'où le `--model opus` par défaut : jouer les évals sur un modèle plus petit mesure un agent qu'on n'exécute pas, et fait passer pour un défaut de `description` ce qui n'en est pas un. Corollaire : un verdict de déclenchement rouge se réinterprète en changeant de modèle **avant** de réécrire quoi que ce soit.

**Une passe coûte de l'argent** — environ 0,51 $ par scénario joué sur `opus` plus 0,07 $ de juge, soit 5 à 6 $ pour les dix. Ce n'est pas un lint qu'on lance à chaque commit.

**Lancer `--self-test` avant de croire une passe.** Il confronte le juge à trois sorties fabriquées — conforme, vide, partielle — et exige les trois verdicts attendus. Sans lui, un juge aveugle qui répond toujours PASS est indiscernable d'un juge intact.

### `SKILLS_ROOT` — le contrat entre un skill et son agent

Plusieurs skills appellent un script partagé de `skills/_shared/`. Ils le désignent par `$SKILLS_ROOT/_shared/<script>.sh`, jamais par le chemin d'un agent précis. À déclarer dans le bloc `env` de `~/.claude/settings.local.json`, à côté de `OBSIDIAN_VAULT_PRO` :

```json
{
  "env": {
    "SKILLS_ROOT": "/chemin/absolu/vers/agent-config/skills"
  }
}
```

**Pourquoi une variable** : un `~/.claude/skills/…` écrit dans un skill le rend inutilisable sous un autre agent, alors que le script visé est au même endroit relatif partout. Le skill dit quoi appeler, le wrapper dit où. Sans la variable, l'appel échoue bruyamment — il ne dégrade pas en silence.

## Dépendance externe

`skills/aidd-pilot/` orchestre les plugins du framework [AI-Driven Dev](https://github.com/ai-driven-dev/framework) et ne fonctionne pas sans eux — voir `skills/aidd-pilot/README.md`. Les autres skills sont autonomes.

Les skills `vault-*` sont des passerelles vers un vault Obsidian : ils délèguent aux skills canoniques situés sous `$OBSIDIAN_VAULT_PRO/.agents/skills/`. Pour les activer, déclarer la variable dans le bloc `env` de `~/.claude/settings.local.json` (fichier local, non versionné) — Claude Code l'injecte alors dans chaque session, sans dépendre du shell de lancement :

```json
{
  "env": {
    "OBSIDIAN_VAULT_PRO": "/chemin/absolu/vers/le/vault"
  }
}
```

Sans cette variable, chaque `vault-*` dégrade sans casse (garde-fou en tête du SKILL.md : message « vault non configuré » puis arrêt, jamais d'écriture dans le repo courant).

## Reprendre ce repo

Un seul fichier n'est pas transposable : **`rules/profil.md`**. Il décrit la personne à qui l'agent s'adresse — niveau technique, contraintes cognitives, mode de compréhension — pour calibrer ton et profondeur. Le remplacer par le sien ; le format compte, pas le contenu.

Tout le reste s'applique tel quel.

## Conventions d'écriture

Toute règle énonce sa **raison**, pas seulement l'ordre — un LLM suit mieux un pourquoi qu'un impératif, et transfère au cas non prévu.

Préférer « négation + alternative » à l'interdit sec : *ne fais pas X — à la place, fais Y*. Énoncer une négation seule active le concept avant de le nier.

Les messages de commit suivent [Conventional Commits](rules/commit-convention.md), en anglais.
