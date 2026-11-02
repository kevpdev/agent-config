# Cadrage : le workflow cœur du harnais, agnostique et routé

Analyse menée le 2026-11-02 sous Claude Code, dans Orca. Elle fixe comment le harnais articule la méthode de travail, AIDD, git, les worktrees et Orca, pour Claude Code et OpenCode. Les seuls fichiers écrits sont ce cadrage et un worktree Orca créé pour l'héberger, qui sert aussi de mesure (Q3).

Marquage : **mesuré** (commande lancée ce jour), **doc-vérifié** (fichier ou doc lu ce jour), **supposé**.

| Nom court | Source |
|---|---|
| Brief | brief vidéo « Non, le top 1 % n'a pas refait son setup Claude Code », F. Utzmann, vault `6 ATTACHMENTS/html/video-brief/aenixZ4LuF0-…html` |
| Kit | `~/Developpement/Workspaces/_vrac/kit-setup-claude-code`, le setup présenté dans la vidéo |
| Article | Anthropic, *Building agents: When to fold subagents into your main agent loop*, 22/10/2026, cité par le Kit (`AUDITE-TON-SETUP.md`) et non relu ici |
| SDLC | `aidd-orchestrator` 2.4.0, `skills/01-sdlc/` (SKILL et `references/`) |
| DEV | `aidd-dev` 2.7.1, `skills/01-plan`, `skills/10-batch`, `agents/executor.md` |
| Suivi | `audits/suivi-refonte-agnostique.md` |
| #61 | issue « Revoir AIDD avec Orca : délégation, compatibilité multi-agents et choix du modèle » |

---

## Q0 — Le problème

**Verdict : le harnais n'a pas de workflow cœur. Il a un workflow conditionnel, et la condition se paie en attention.**

- `rules/aidd.md` ne s'applique qu'aux dépôts qui portent un `aidd_docs/`. Un projet sans ce dossier, le vault compris, n'a aucun parcours défini pour créer ou modifier un script, un skill ou un template.
- Avant chaque travail, il faut donc se demander quel régime s'applique. C'est une décision de plus pour un lecteur dont l'attention est la ressource rare (`rules/profil.md`).
- Les setups publiés, celui du Kit compris, appliquent un seul workflow à tous les projets. C'est leur force, pas leur outillage.
- Une contrainte s'ajoute : Orca est l'IDE de travail, mais le harnais ne doit pas casser sans lui. Il doit fonctionner dans un terminal nu, sous Claude Code comme sous OpenCode.

## Q1 — La méthode

**Verdict : planifier, exécuter, vérifier, valider. C'est l'invariant, et rien d'autre dans ce cadrage ne l'est.**

Le Brief et le Kit défendent la même thèse : le *quoi* ne change pas d'un modèle à l'autre, seul le *comment* change. Les couches suivantes sont toutes des *comment*, donc remplaçables une par une.

## Q2 — Le workflow : AIDD partout

**Verdict : AIDD devient le workflow unique, à profondeur variable selon la taille du travail. On ne construit pas de workflow maison.**

Ce qui tranche, c'est qu'AIDD couvre déjà les quatre étapes de la méthode : `01-plan`, `02-implement`, `checker` et `05-review`, puis la PR draft. Un workflow maison remplacerait un outil maintenu par un pari à maintenir seul.

| Taille du travail | Parcours |
|---|---|
| Petit (un script, un template) | implémenter, puis relecture à contexte neuf (`aidd-dev:checker` ou `05-review`) |
| Moyen (un skill, plusieurs fichiers) | `01-plan`, puis implémenter, puis relire |
| Grand (une feature de bout en bout) | `aidd-orchestrator:01-sdlc` |

### Où tourne chaque étape (doc-vérifié, SDLC et DEV)

| Étape | Où | Parallèle |
|---|---|---|
| Frame : ticket, brainstorm, spec | session courante | non |
| Plan, `01-plan` | session courante, puis un sous-agent lecture seule qui vérifie le plan contre `plan-checks` | non |
| Implémentation | un seul agent `aidd-dev:executor` reçoit tout le plan | non |
| Revue, `05-review` puis `02-challenge` | un agent `aidd-dev:checker` neuf | non |
| Correctifs indépendants | `aidd-dev:10-batch`, un `executor` par tâche, lancés dans un même message | oui |
| PR draft | session courante | non |

AIDD respecte déjà le crible de l'Article : il ne lance un sous-agent que pour isoler l'exécution ou pour relire avec un regard neuf, et ne parallélise que les correctifs. Le Kit, lui, lance jusqu'à 4 dev-agents en parallèle, un par ticket.

**AIDD ne dit rien des worktrees** (mesuré : `grep -ri worktree` sur les 7 plugins AIDD du cache ne rend rien). `01-sdlc` dit seulement « Spawn specialized agents… Parallelize independent work when it is faster ». Le harnais peut donc décider seul de l'isolation sans modifier AIDD.

### Le trou de l'agnosticisme

- Sous Claude Code, AIDD est un plugin global (mesuré : 7 plugins `aidd-*` installés et activés dans `settings.json`).
- Sous OpenCode, il s'installe projet par projet (Suivi, tâche 12) : `npx @ai-driven-dev/cli@5.5.0 setup --ai opencode` pose 467 fichiers dans `.opencode/`, soit 51 skills au nom aplati.
- `~/.config/opencode/skills/` ne contient aucun skill `aidd-*` (mesuré). Un projet OpenCode sans installation n'a donc aucun workflow.

Deux options restent ouvertes, à trancher dans #61 chantier C :

| Option | Pour | Contre |
|---|---|---|
| Installation par projet | supportée par AIDD, mesurée | 467 fichiers par dépôt, à mettre à jour un par un |
| Lien global depuis `agent-config`, comme les autres skills | une seule copie, servie par `install.py` | non supporté par AIDD (supposé). Les noms aplatis pourraient entrer en collision avec d'autres skills |

## Q3 — L'isolation : worktree git, routé

**Verdict : un worktree par travail, créé par un script de routage unique. Le script prend l'outil le plus riche disponible, et chaque rang produit le même résultat sur disque.**

### Ce qu'est un worktree Orca (mesuré)

Un worktree Orca est un worktree git avec une couche de métadonnées. Le worktree qui héberge ce cadrage le montre :

| Champ | Valeur |
|---|---|
| Commande | `orca-ide worktree create --repo name:agent-config --name docs-cadrage-workflow-coeur --no-parent` |
| Chemin | `~/orca/workspaces/agent-config/docs-cadrage-workflow-coeur` |
| Branche | `kevpdev/docs-cadrage-workflow-coeur`, soit `<gitUsername>/<nom>` |
| Base | `88829f6`, la tête de `main` |
| Vu par git | oui, `git worktree list` le liste |

L'aide de la CLI confirme la double nature : `worktree rm` se décrit comme « Remove a worktree from Orca and git ».

| Couche | Contenu | Survit sans Orca |
|---|---|---|
| git | dossier, branche, commits | oui |
| Métadonnées Orca | parent et enfants, issue ou PR liée, commentaire, agent lancé | non, sans rien casser |
| Orchestration Orca | tâches, `dispatch`, messages `ask` et `reply` | non, c'est la seule vraie dépendance |

### La visibilité, réglée par dépôt (mesuré)

Orca masque les worktrees créés hors de lui selon `externalWorktreeVisibility` :

| Dépôt | Réglage |
|---|---|
| agent-config | `show` |
| MyObsidianVault | `hide` |
| yt-transcriber | `hide` |

Le réglage se change par `orca-ide repo set --repo <sélecteur> --external-worktree-visibility show`. Avec `show` partout, un worktree créé par git reste visible et reprenable dans Orca.

### Le routeur

Une commande, par exemple `tools/worktree create <nom>`, que Claude et OpenCode appellent de la même façon. Les conditions se testent dans l'ordre :

| Rang | Condition | Mécanisme |
|---|---|---|
| 1 | `ORCA_WORKTREE_ID` défini et `orca-ide status` répond | `orca-ide worktree create`, avec toutes les métadonnées |
| 2 | `orca-ide` installé, mais hors terminal Orca ou runtime injoignable | `git worktree add` au chemin et sous le nom de branche d'Orca, avec un avertissement |
| 3 | pas d'Orca | `git worktree add`, même chemin, même branche |

Le chemin `~/orca/workspaces/<dépôt>/<nom>` est hors de `~/Developpement/Workspaces/`. Il ne heurte donc pas `rules/workspaces.md`, et un worktree n'y est pas un projet (`rules/worktrees.md`).

Le routeur sort les commandes Orca des règles. `rules/worktrees.md` se réduit alors à une consigne : créer le worktree par `tools/worktree`. Les commandes vivent dans le script, qui suit les versions d'Orca.

## Q4 — L'exécution parallèle

**Verdict : même modèle de routage que Q3, mais en dernier. Il dépend de Q2 et de Q3, et de la façon dont Orca coordonne ses ouvriers.**

| Rang | Condition | Mécanisme |
|---|---|---|
| 1 | dans Orca | un ouvrier Orca par tâche, dans un worktree enfant, piloté par `orchestration task-create` puis `dispatch` (doc-vérifié : `orca-ide --help`) |
| 2 | ailleurs | sous-agent natif : outil `Agent` sous Claude, agent OpenCode équivalent |

- Le seul point d'AIDD qui écrit en parallèle est `10-batch`. Ses `executor` partagent aujourd'hui le même dossier. Qu'ils se gênent réellement reste supposé.
- Le skill `orchestration` d'Orca interdit tout autre outil de sous-agent que le sien (#61). Il entre donc en conflit avec le `checker` lancé par `Agent`. Il faut décider si la contrainte vise le coordinateur entier ou seulement ses ouvriers.
- Ce chantier est le D de #61.

## Q5 — Les garde-fous

**Verdict : rien à refaire. Le modèle du cœur plus un adaptateur par agent est déjà en place et mesuré.**

- Le cœur des gardes vit dans `hooks/`. Claude l'appelle par `wrappers/claude/hooks/`, OpenCode par le plugin `harness-guards` (Suivi, tâches 5 et 6).
- La parité de l'adaptateur Claude est mesurée sur 963 commandes réelles rejouées : 0 écart, 35 refus identiques (Suivi, tâche 5).
- Le routeur de Q3 suit le même modèle : la décision dans un script neutre, l'appel dans l'adaptateur.

Candidat annexe : le Kit refuse les commandes destructives locales (`git reset --hard`, `rm -rf`, `DROP TABLE`). Le harnais n'en parle que dans `hooks/no_sensitive_write.py`, limité aux fichiers sensibles. L'absence de garde général est supposée.

## Q6 — La mémoire projet

**Verdict : le workflow est le même partout. Seul l'endroit où vivent les décisions change, selon une hiérarchie.**

| Rang | Condition | Où vit la mémoire |
|---|---|---|
| 1 | le dépôt porte un `aidd_docs/` | `aidd_docs/memory/` |
| 2 | le vault | `AGENTS.md` et `decisions/` (fiches datées depuis le 2026-04-24) |
| 3 | sinon | le `CLAUDE.md` ou l'`AGENTS.md` du projet |

Dans le vault, `aidd-context:02-project-memory` doublerait `AGENTS.md` et `decisions/`, donc on ne l'y lance pas. `aidd-dev:01-plan` n'exige pas de mémoire AIDD : il écrit son plan dans `aidd_docs/tasks/` « or in the source's own folder » (DEV, `actions/03-conclude.md`).

## Les principes qui tiennent l'ensemble

| Principe | Ce qu'il impose ici |
|---|---|
| Le déterministe d'abord | tout routage est un script testable, jamais une règle que le modèle interprète |
| Une hiérarchie du plus riche au plus simple | on prend l'outil le plus riche disponible, et chaque rang produit le même résultat sur disque |
| L'agnosticisme | règles et scripts neutres. Ce qui est propre à un agent ou à un outil vit dans un adaptateur |
| Combiner plutôt que remplacer | AIDD, git et Orca restent tels quels, le harnais les relie |
| Le crible de l'Article | un sous-agent seulement pour le parallèle ou pour une relecture à contexte neuf |

## Crible des alternatives

Chaque couche contre son alternative la plus simple, prise isolément :

| Couche | Choix | Alternative la plus simple | Écartée parce que |
|---|---|---|---|
| Méthode | planifier, exécuter, vérifier, valider | aucune méthode écrite | c'est l'invariant que toutes les sources partagent |
| Workflow | AIDD partout | workflow maison, comme le Kit | il faudrait réécrire et maintenir seul ce qu'AIDD fait |
| Isolation | routeur de worktrees | `git worktree add` seul | Orca perdrait ses métadonnées sur chaque worktree |
| Parallèle | routeur d'exécution | sous-agent natif seul | les ouvriers resteraient invisibles dans Orca |
| Garde-fous | cœur plus adaptateurs | règles seules | une règle conseille, un garde refuse |
| Mémoire | hiérarchie à trois rangs | un format unique | il casserait `decisions/` et `AGENTS.md` du vault |

## Non établi

- **`orca-ide worktree set` sur un worktree créé par git** : on ne sait pas s'il rattache après coup les métadonnées Orca.
- **AIDD dans un ouvrier Orca** : sous Claude, les plugins globaux devraient suffire (supposé). Sous OpenCode, non, faute d'installation globale.
- **Lien global d'AIDD sous OpenCode** : jamais essayé.
- **Collisions de `10-batch`** : jamais observées.
- **Le rang 2 du routeur** : on ne sait pas si un worktree créé par git au chemin d'Orca, dans un dépôt réglé sur `show`, se comporte dans Orca comme un worktree natif.

---

## Découpage en tâches ordonnées

L'ordre suit une contrainte : chaque tâche est utile seule, et la dernière dépend des trois autres.

| # | Tâche | Effet vérifiable |
|---|---|---|
| 1 | Routeur `tools/worktree`, trois rangs, puis `rules/worktrees.md` réduit à son appel. `externalWorktreeVisibility: show` sur tous les dépôts | une batterie simule les trois environnements et vérifie le rang choisi. Un worktree créé au rang 3 apparaît dans `orca-ide worktree list` |
| 2 | AIDD disponible partout sous OpenCode (#61 C) | une session OpenCode dans un dépôt sans installation locale voit `01-plan` |
| 3 | `rules/aidd.md` réécrit : AIDD comme workflow unique, profondeur selon la taille, déclencheur « tout travail qui produit », mémoire selon Q6 | `guard-aidd-skill-lookup.py` rappelle aussi hors d'un dépôt `aidd_docs/`, et sa batterie le couvre |
| 4 | Routeur d'exécution parallèle (#61 D) | un `10-batch` lancé dans Orca crée un ouvrier et un worktree enfant par tâche. Hors d'Orca, il retombe sur des sous-agents natifs |

Candidats annexes, indépendants de l'ordre ci-dessus :

| Candidat | Origine |
|---|---|
| Passer le crible de l'Article sur `wrappers/claude/agents/doc-writer.md`, le seul agent maison | le Kit classe son writer-agent comme « candidat parfait pour devenir un skill » |
| Une routine d'audit à chaque nouveau modèle : relire les sessions ratées par `aidd-refine:05-improve`, retirer un seul élément à la fois | Brief, méthode d'audit de l'auteur (17 contradictions, 2 plugins utilisés sur plusieurs dizaines) |
| Un garde des commandes destructives locales | Kit, `block-dangerous.mjs` |

Chaque tâche peut devenir une issue par `aidd-vcs:04-issue-create`.

## Provenance

- Discussion du 2026-11-02, partie du brief de la vidéo publié en artifact (`claude.ai/artifact/EDgctNGeUg8Hj8dECyf4o9`).
- Le Kit a été lu en entier, ses fichiers n'ont pas été exécutés.
- Seuls fichiers écrits : ce cadrage et le worktree Orca `docs-cadrage-workflow-coeur` qui l'héberge.
