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

### Les gardes déterministes

Trois hooks `PreToolUse` refusent à l'appel ce qu'une règle de prose ne tenait pas. Chacun est la couche déterministe d'une règle qui, du coup, ne répète pas ses critères.

| Garde | Refuse | Règle allégée | Batterie |
|---|---|---|---|
| `guard-bash-tooling.py` | `java`/`mvnw` hors `bash -lc 'sh ./mvnw …'`, heredoc imbriqué | `rules/tooling.md` | `tests/test-guard-bash-tooling.sh` |
| `guard-no-claude-in-commit.sh` | mention d'IA, format Conventional Commits | `rules/commit-convention.md` | `tests/test-guard-no-claude-in-commit.sh` |
| `guard-no-remote-write.py` | écritures de l'agent sur preprod/prod | — | *aucune* |

```bash
bash wrappers/claude/scripts/hooks/tests/test-guard-bash-tooling.sh
bash wrappers/claude/scripts/hooks/tests/test-guard-no-claude-in-commit.sh
```

**Une batterie pèse autant que son garde.** Un garde sans cible vivante se comporte exactement pareil qu'il soit cassé ou intact ; et un garde qui refuse du travail valide finit désactivé, donc ne protège plus rien. Chaque batterie porte les deux : des cas positifs **fabriqués à la main**, et les formes légitimes qui doivent passer. Toute forme de commande nouvellement rencontrée s'y ajoute *avant* d'être corrigée dans le garde.

**Calibrer sur du trafic réel, pas seulement sur ses propres cas.** `guard-bash-tooling.py` a été confronté aux 987 commandes du périmètre extraites des transcripts de sessions (`~/.claude/projects/*/*.jsonl`) : sa première conception, qui refusait tout ce qu'elle ne pouvait pas tokeniser, y produisait 5 faux positifs sur des `git commit` ordinaires. Une batterie écrite par l'auteur du garde ne les aurait jamais montrés.

### La veille des plugins AIDD

Claude Code sait appliquer une mise à jour de plugin, pas dire ce qu'elle va casser. Son auto-update
par marketplace applique dans les dix minutes qui suivent le démarrage, donc la casse arrive
décorrélée de sa cause. Or elle est **ici** : 16 noms de skills AIDD sont cités dans ce repo, et la
montée 1.x → 2.x en avait déjà renommé trois (cf. [`CHANGELOG-aidd.md`](CHANGELOG-aidd.md)). D'où
l'auto-update laissé désactivé pour `aidd-framework`, et ces quatre pièces.

| Pièce | Rôle |
|---|---|
| `wrappers/claude/scripts/aidd-updates.py` | compare les versions installées aux tags upstream, garde l'état |
| bloc `SessionStart` de `settings.json` | affiche une ligne au démarrage, une fois par jour au plus |
| `skills/aidd-updates/` | lit les changelogs, rédige le plan d'adaptation, l'applique sur accord |
| `wrappers/claude/scripts/tests/test-aidd-updates.sh` | la batterie du détecteur |

L'état vit **hors du repo**, dans `${XDG_STATE_HOME:-$HOME/.local/state}/aidd-updates/plan.md` : un
front-matter YAML pour la machine, le plan en markdown pour l'humain. C'est un état de machine, et
l'avertissement en tête de `CHANGELOG-aidd.md` interdit d'écrire ça dans le repo. Ce fichier est aussi
l'**interface** entre le wrapper qui produit et le skill qui consomme, ce qui garde le skill neutre :
changer de runtime ne réécrirait que le détecteur.

```bash
bash wrappers/claude/scripts/tests/test-aidd-updates.sh          # 28 cas, hors réseau
python3 wrappers/claude/scripts/aidd-updates.py --refresh        # force une vérification
python3 wrappers/claude/scripts/aidd-updates.py --etat           # ce que le skill lit
```

**Le chemin chaud ne touche jamais le réseau.** `--notify` lit le cache et détache un `--refresh`
quand celui-ci a plus de 24 h. Mesuré à 36 ms, contre 470 ms pour un `ls-remote`. Le découpage est
repris de la CLI AIDD elle-même, dont le commentaire dit « Hot path: print the update notice from
cached value only — fresh OR stale, never network ». Un `SessionStart` qui attend le réseau retarde
**chaque** ouverture de session, pour un service qui n'est que du confort.

**Écart assumé à l'échoue-fermé.** Ce script sort toujours en 0, contrairement aux gardes ci-dessus.
Un garde refuse une action, celui-ci ne fait qu'informer : échouer bruyamment polluerait chaque
session, et une machine hors réseau n'a rien fait de mal. À la place du code de sortie, toute panne
s'écrit dans `derniere_erreur`, que `/aidd-updates` affiche avant tout le reste. Rien n'est silencieux
pour de bon, rien ne bloque. C'est aussi pourquoi la batterie compte : le code de sortie ne disant
rien, un détecteur cassé se tait exactement comme un détecteur qui n'a rien trouvé. Son premier cas
est donc un retard **fabriqué à la main**, et elle s'arrête là s'il échoue plutôt que de rendre un vert
trompeur sur des silences.

### Linter les skills

Le lint lit les fichiers et n'exécute rien : sept vérifications mécaniques sur les 24 skills, en une seconde et sans appel LLM. Le frontmatter parse et porte ses trois clés, `name` égale le dossier, la `description` tient sous le plafond, les `##` correspondent à ceux du gabarit, aucun placeholder ne survit, aucun lien relatif n'est mort, et un skill qui porte `disable-model-invocation: true` ne promet de déclenchement nulle part ailleurs.

```bash
python3 wrappers/claude/scripts/lint-skills.py                      # tous les skills
python3 wrappers/claude/scripts/lint-skills.py --skill skill-craft   # un seul
python3 wrappers/claude/scripts/tests/test-lint-skills.py            # calibre les sept vérifications
```

**La liste des sections n'est pas dans le script.** Elle est dérivée des deux gabarits de `skills/skill-craft/assets/`, qui font foi pour l'humain comme pour le lint. Une liste décrite en prose et une liste vérifiée par un script divergent au premier edit de l'une des deux.

**Rien n'y grep ce que le skill fait.** Un comptage de « push » ou « commit » attrape `security-reviewer`, qui cite ces mots pour décrire du code qu'il relit sans rien exécuter. Ce qui demande de comprendre le skill reste à la relecture de `skill-craft:02-validate`.

C'est la moitié de R13 que la septième vérification laisse dehors. Elle ne sait pas dire qu'un skill qui écrit aurait dû porter le champ, seulement qu'un skill qui le porte se contredit ailleurs, dans sa description ou dans ses évals.

### Jouer les évals des skills

Un skill qui porte un `evals/eval.json` déclare ses cas en données pures : la requête, le déclenchement attendu, l'artefact attendu. Aucun nom d'outil, aucun nom d'agent — l'exécuteur est le seul à connaître Claude Code, ouvrir une session neuve passant par `claude -p`.

```bash
python3 wrappers/claude/scripts/tests/test-run-skill-evals.py   # calibre les verdicts, ne joue aucun cas
python3 wrappers/claude/scripts/run-skill-evals.py              # joue tout, rend un tableau de verdicts
python3 wrappers/claude/scripts/run-skill-evals.py --skill mr-review
```

Chaque cas rend deux verdicts, tous deux déterministes et sans juge LLM. Le **déclenchement** se lit au registre de la session : un appel à l'outil `Skill` nomme le skill ouvert, et sur un cas négatif le verdict s'inverse. L'**artefact** se contrôle par script : le fichier annoncé existe et porte les sections de son gabarit.

**Le champ `artifact` choisit le mode d'exécution.** Sans lui, le cas tourne `--tools "Skill"` : le skill peut s'ouvrir, rien d'autre ne peut s'exécuter, donc un skill à effet de bord se teste sans risque et sans worktree. Avec lui, le cas tourne outils ouverts dans un worktree jetable du repo. Couper **tous** les outils couperait aussi celui qui ouvre un skill, et l'instrument mesurerait sa propre censure (mesuré le 2026-08-24).

**Aucune `query` de cas positif ne commence par `/`, et l'exécuteur le refuse.** Mesuré deux fois le 2026-08-21 puis deux fois de plus le 2026-08-24, `claude -p "/<nom> …"` n'ouvre pas le skill : aucun appel à l'outil qui l'ouvre, aucune ligne du `SKILL.md` dans le transcript. Un cas positif préfixé mesurerait le harnais et non le skill. Conséquence : un skill à invocation manuelle n'a pas de cas positif, et `jira` ne porte que des cas négatifs — le contrat qui compte pour lui étant qu'il ne parte jamais tout seul. Le pourquoi n'est pas établi, `claude --help` annonçant l'inverse.

**Le déclenchement dépend d'abord du modèle, pas du skill.** Mesuré le 2026-08-06 sur quatre skills en deux répétitions, à skills, requêtes et règles identiques : **7/8 sur `opus`, 0/8 sur `sonnet`**. Deux des quatre ne déclenchaient jamais sous Sonnet et déclenchent 2/2 sous Opus. D'où le `--model opus` par défaut : jouer les évals sur un modèle plus petit mesure un agent qu'on n'exécute pas, et fait passer pour un défaut de `description` ce qui n'en est pas un. Corollaire : un verdict de déclenchement rouge se réinterprète en changeant de modèle **avant** de réécrire quoi que ce soit.

**Une passe coûte de l'argent** — 0,97 $ pour un cas de déclenchement joué sur `opus`, mesuré le 2026-08-24, soit une trentaine de dollars pour les 31 cas du corpus. Ce n'est pas un lint qu'on lance à chaque commit, et c'est pourquoi le lint existe à côté.

**Lancer la batterie avant de croire une passe.** Elle confronte les deux verdicts et la validation du corpus à 20 cas fabriqués à la main. Sans elle, un verdict aveugle qui répond toujours OK est indiscernable d'un verdict intact.

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
