# Grille d'audit du harnais

Crible d'admission au contexte permanent : chaque instruction du harnais y passe, une par une. L'objectif est la **stabilité**, pas la perfection — un harnais qui repose le moins possible sur la discipline du modèle dépend le moins possible du modèle.

**Source de vérité** : le harnais lui-même (ce repo). Le vault alimente et optimise, il ne fait pas foi. *(Décidé le 2026-08-10 — inverse l'en-tête actuel d'`ai-principles.md`, à corriger.)*

**Sources consolidées** : `0_INBOX/2026-08-10-refonte-harnais-agent-config.md` (vault pro), `rules/ai-principles.md`, `rules/ai-practices.md`, `rules/reasoning.md` (contrat de questions), `rules/workflow.md` (échec fermé).

---

## Méthode — un audit à la fois

- **Un audit = un domaine, contrat figé.** Les questions de l'audit sont les critères de cette grille, rien d'autre. Une découverte hors grille se capture en une ligne et ne se creuse pas. La grille se révise **entre** deux audits, jamais pendant.
- **Ordre** : `agent-config` (socle) → vault pro → vault perso → projets (qui héritent du socle). Dans chaque domaine, par sous-domaine : `rules/`, `skills/`, `scripts`/hooks, `CLAUDE.md`/output-styles, `settings.json` (bindings, permissions), memory auto.
- **Horodatage** : un rapport d'audit est un instantané immuable, nommé `audits/AAAA-MM-JJ-audit-<domaine>.md` ; l'audit suivant du même domaine est un nouveau fichier, jamais un edit. La grille, elle, est vivante et non horodatée — git porte son historique (`git log --oneline -- audits/grille-harnais.md`), pas de champ `version:` manuel qui divergerait au premier edit oublié. Chaque rapport cite en en-tête le commit de la grille contre laquelle il a tourné.
- **Traçabilité** : chaque constat du rapport cite sa mesure (commande + sortie) ou porte « supposé ». Un chiffre repris de la note d'inbox est un chiffre du 2026-08-10 : le remesurer avant de décider.

---

## Le crible — cascade de 6 critères

Chaque instruction descend la cascade ; elle sort au premier critère qui la disqualifie.

### C1 — Inférable ?

Un modèle sans cette instruction retrouverait-il l'information (dans le code, la config, la doc du repo) ?

| Cas | Action |
|---|---|
| Inférable, coût de découverte faible | **Supprimer** — laisser inférer |
| Inférable, coût élevé, info stable | Synthèse courte |
| Inférable, coût élevé, info volatile | **Pointeur** vers la source, jamais une copie |
| Non-inférable (décision, contrainte d'env, piège) | Garder → C2 |

**Test** : demander à un contexte neuf (sous-agent sans la règle) de retrouver l'info. S'il y arrive en < 3 appels d'outil, c'est inférable à coût faible *(seuil conventionnel, aucune source ne le porte — révisable entre deux audits)*.

### C2 — Déterminisable ?

Un mécanisme sans LLM (hook, CI, linter, script) peut-il porter l'invariant ?

| L'invariant porte sur | Couche déterministe | Sort de la règle prose |
|---|---|---|
| Un artefact versionné (message de commit, fichier) | hook git `core.hooksPath` + check CI | Réduite à un pointeur vers le garde |
| Une action éphémère de l'agent (commande tapée, écriture réseau) | hook harnais (`PreToolUse`) — **seul mécanisme possible** | Idem |
| Un raisonnement (pas d'appel d'outil observable) | Aucune — le hook ne voit que les tool calls | La prose reste, → C3 |

**Contraintes du mécanisme** (de `workflow.md`, non renégociables) : échoue fermé, aucun chemin absolu en dur, calibré sur un cas positif fabriqué à la main. **Séparation logique/binding** : la logique vit dans un script autonome testable hors agent (`checks/`), le binding propriétaire fait ≤ 10 lignes.

### C3 — Falsifiable ?

La règle gardée en prose porte-t-elle une condition de violation observable — au mieux, sa commande de vérification ?

**Gradient** (du plus sûr au plus faible) :
1. Hook/CI/linter — suivi garanti *(traité en C2)*
2. Règle falsifiable + commande de vérification
3. Impératif court non ambigu — suivi probabiliste
4. Prose vague ou de style — inutile même pour un bon modèle → **supprimer ou reformuler en 2/3**

**Exception assumée** : `ai-principles.md` ne prescrit rien donc n'est pas falsifiable, mais il est le repli quand une règle concrète est muette. Il se **réduit** (titres + une ligne de pourquoi), il ne se supprime pas.

### C4 — Unique ?

L'instruction existe-t-elle ailleurs (autre règle, skill, `CLAUDE.md`, memory) ?

Une instruction dupliquée s'**élimine**, elle ne se hiérarchise pas : une seule occurrence, et la couche permanente se déclare délibérément partielle (modèle : `mermaid.md` → skill `mermaid-craft`). Un doublon statique est bénin ; un doublon volatil diverge au premier edit.

**Test** : grep du motif central de l'instruction sur `rules/`, `skills/`, les `CLAUDE.md` du domaine.

### C5 — Scopée ?

L'instruction vaut-elle partout, ou pour un sous-ensemble de repos/chemins ?

Domaine limité → frontmatter `paths:` (modèle : `back-spring.md`, `front-react.md`). Une règle globale qui ne sert qu'un domaine fait payer son poids à toutes les sessions.

### C6 — Dans le budget ?

Le contexte permanent global tient-il sous le plafond ? Le périmètre est **tout ce qui entre dans chaque session** : les règles non scopées (`rules/` + `wrappers/claude/rules/`), l'output style actif, et l'index de memory auto du projet courant.

**Mesure** :

```bash
wc -w $(grep -L '^paths:' rules/*.md) wrappers/claude/rules/*.md \
      wrappers/claude/output-styles/chat-style.md
# + MEMORY.md de la memory auto du projet courant, variable par projet
```

**État au 2026-08-10 (remesuré)** : 5 830 mots — 5 607 de règles (dont `memory-policy.md`, 207) + 223 d'output style. ~40 % retirables côté règles (surtout `ai-practices.md` et les cas vécus de `reasoning.md`/`workflow.md`).
**Cible** : ≤ 3 500 mots hors output style — dérivée de la mesure « retirable », pas un dogme ; l'audit la révise.

Les **cas vécus** sortent du permanent vers un fichier de références chargé à la demande ; la règle garde le trigger et le pourquoi en une ligne.

---

## Sources normatives par sous-domaine

Contre quoi juger la **conformité de construction** d'un artefact (format, frontmatter, anatomie). On stocke le **pointeur**, jamais une copie (C1 : contenu volatil — la doc a déjà migré de domaine une fois).

**Standards ouverts multi-agents** — la couche portable, à préférer quand elle couvre la fonction :

| Mécanisme | Source | Vérifié |
|---|---|---|
| Skills | <https://agentskills.io/specification> + repo `anthropics/skills` | 2026-08-10, fetch |
| AGENTS.md | <https://agents.md> | supposé (standard connu, non re-fetché) |
| MCP | <https://modelcontextprotocol.io> | supposé |

**Propriétaire Claude Code** — le binding, confiné sous `wrappers/claude/` :

| Mécanisme | Source | Vérifié |
|---|---|---|
| Hooks | <https://code.claude.com/docs/en/hooks> | 2026-08-10, fetch |
| Output styles | <https://code.claude.com/docs/en/output-styles> | 2026-08-10, fetch |
| CLAUDE.md / memory | <https://code.claude.com/docs/en/memory> | 2026-08-10, via agent doc |
| Subagents | <https://code.claude.com/docs/en/sub-agents> | slug confirmé par liens |
| Scripts / checks | pas de doc — la norme est **ShellCheck** + contraintes `workflow.md` (échec fermé, calibrage) | — |
| Index complet | <https://code.claude.com/docs/llms.txt> | 2026-08-10 |

**Point tranché le 2026-08-10** (doc officielle, section AGENTS.md de la page memory) : Claude Code ne lit **pas** `AGENTS.md` nativement — seul `CLAUDE.md` est lu ; s'ils coexistent, `AGENTS.md` est ignoré. Deux ponts documentés : import `@AGENTS.md` en tête de `CLAUDE.md`, ou symlink. **Conséquence** : la couche standard reste possible — le contenu vit dans `AGENTS.md` (portable), `CLAUDE.md` se réduit à l'import. Même motif logique/binding que `checks/` + hook. **Portée** : ce pont ne vaut que pour les `CLAUDE.md` de projet ; les règles globales passent par les symlinks de `sync-rules.sh`, mécanisme distinct à auditer séparément.

---

## Mesures d'inventaire par domaine

À lancer en ouverture d'audit, avant tout jugement :

```bash
# Poids du contexte permanent → la commande de C6 (une seule définition)

# Couche déterministe réelle
ls checks/ 2>/dev/null; ls wrappers/claude/scripts/hooks/
git config core.hooksPath   # sur chaque repo du domaine

# Doublons inter-couches (par motif jugé, pas de regex unique)
# Symlinks de règles à jour
sh wrappers/claude/scripts/sync-rules.sh
```

---

## Écarts déjà identifiés (seed — à confirmer par l'audit, pas acquis)

D'après la note d'inbox du 2026-08-10 :

- [ ] `tooling.md` (449 mots) → migrer en hook `checks/guard-bash-tooling.sh` (C2 : ses deux interdits sont des motifs de chaîne sur une action éphémère)
- [ ] `ai-practices.md` (1 110) → sortir du contexte permanent (C6 : banc d'essai non validé qui dilue le validé)
- [ ] `reasoning.md` (1 100), `workflow.md` (1 055) → garder triggers et commandes, sortir les cas vécus (C3/C6)
- [ ] `ai-principles.md` (558) → réduire aux titres + une ligne (exception C3) ; corriger l'en-tête « le vault est la source »
- [ ] Gardes `guard-no-claude-in-commit.sh`, `guard-no-remote-write.py` → `git mv` vers `checks/` (séparation logique/binding)
- [ ] Couche 1 absente : 0 hook git sur 25 repos Winggy, 0 check CI de commits sur 19 (C2 : les deux gardes sont le seul filet)
