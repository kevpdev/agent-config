# Grille d'audit du harnais

Crible d'admission au contexte permanent : chaque instruction du harnais y passe, une par une. L'objectif est la **stabilité**, pas la perfection — un harnais qui repose le moins possible sur la discipline du modèle dépend le moins possible du modèle.

**Source de vérité** : le harnais lui-même (ce repo). Le vault alimente et optimise, il ne fait pas foi. *(Décidé le 2026-08-10 — inverse l'en-tête actuel d'`ai-principles.md`, à corriger.)*

**Sources consolidées** : `0_INBOX/2026-08-10-refonte-harnais-agent-config.md` (vault pro), `rules/ai-principles.md`, `rules/ai-practices.md`, `rules/reasoning.md` (contrat de questions), `rules/workflow.md` (échec fermé).

---

## Méthode — un audit à la fois

- **Un audit = un domaine, contrat figé.** Les questions de l'audit sont les critères de cette grille, rien d'autre. Une découverte hors grille se capture en une ligne et ne se creuse pas. La grille se révise **entre** deux audits, jamais pendant.
- **Ordre** : `agent-config` (socle) → vault pro → vault perso → projets (qui héritent du socle). Dans chaque domaine, par sous-domaine : `rules/`, `skills/`, `agents/`, `scripts`/hooks, `CLAUDE.md`/output-styles, `settings.json` (bindings, permissions), memory auto. Un sous-agent passe le même crible qu'un skill, pas celui d'un script : il porte de la prose normative et hérite du contexte permanent.
- **Une passe = un sous-domaine.** Le scope concentre le contexte (les fichiers d'un même sous-domaine se comparent entre eux) et borne le coût d'une session d'audit ; un domaine entier se couvre en plusieurs passes, jamais en une. Un hook n'est pas un sous-domaine à part : c'est un script (critères d'échec fermé de `workflow.md`) plus une ligne de trigger dans `settings.json`, chacun audité dans sa passe.
- **Horodatage** : un rapport d'audit est un instantané immuable, nommé `audits/AAAA-MM-JJ-audit-<domaine>.md` ; l'audit suivant du même domaine est un nouveau fichier, jamais un edit. La grille, elle, est vivante et non horodatée — git porte son historique (`git log --oneline -- audits/grille-harnais.md`), pas de champ `version:` manuel qui divergerait au premier edit oublié. Chaque rapport cite en en-tête le commit de la grille contre laquelle il a tourné.
- **Traçabilité** : chaque constat du rapport cite sa mesure (commande + sortie) ou porte « supposé ». Un chiffre repris de la note d'inbox est un chiffre du 2026-08-10 : le remesurer avant de décider.

---

## Le crible — cascade de 8 critères

Chaque instruction descend la cascade ; elle sort au premier critère qui la disqualifie. **C1→C5 et C7 se jugent par instruction**, **C8 par fichier** (une fois ses instructions criblées), **C6 est le seul critère global** (un budget est une somme, une instruction seule ne le viole jamais). C7 ne disqualifie pas une instruction, il disqualifie sa formulation.

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

Le contexte permanent global tient-il sous le plafond ? Le périmètre est **tout ce qui entre dans chaque session** : les règles non scopées (`rules/` + `wrappers/claude/rules/`), l'output style actif, les blocs `description` des skills montés, et l'index de memory auto du projet courant.

**Le corps d'un skill n'entre pas dans C6** — il ne se charge qu'à l'invocation. Il ne se juge donc que sur C1→C5, C7 et C8, dans sa propre passe. *Pourquoi le borner ici : sans ça, chaque passe de corps rejuge si le budget la concerne, et deux passes répondront différemment.*

**Mesure** :

```bash
wc -w $(grep -L '^paths:' rules/*.md) wrappers/claude/rules/*.md \
      wrappers/claude/output-styles/chat-style.md

# + les blocs `description` des skills montés (~/.claude/skills → skills/)
python3 -c "
import re,glob
t=0
for f in glob.glob('skills/*/SKILL.md'):
    fm=re.match(r'---\n(.*?)\n---\n',open(f).read(),re.S).group(1)
    t+=len(re.search(r'^description:\s*(.*?)(?=\n[a-z_-]+:|\Z)',fm,re.S|re.M).group(1).split())
print(t)"

# + MEMORY.md de la memory auto du projet courant, variable par projet
```

**État au 2026-08-11** : **7 358 mots** de permanent réel — 5 161 de règles + output style (la commande `wc -w` ci-dessus, en cours de baisse sous l'effet de la passe `rules/`) **+ 2 197 de descriptions de skills**, sur 26 skills `agent-config`. Cette seconde moitié n'avait jamais été comptée : elle pèse 30 % du permanent et aucune passe ne l'avait ouverte avant le cadrage `skills/` A.

**État au 2026-08-10 (remesuré)** : 5 830 mots — 5 607 de règles (dont `memory-policy.md`, 207) + 223 d'output style. L'estimation initiale « ~40 % retirables » ne s'est pas confirmée : la passe `rules/` du 2026-08-10 mesure ~1 650 mots retirés par la cascade (~30 %).
**Cible** : ~3 950 mots hors output style — plancher mesuré par la passe `rules/` du 2026-08-10 (rapport `2026-08-10-audit-agent-config-rules.md`), **pas un plafond obligatoire**. Décidé le 2026-08-10 : on ne supprime pas une instruction survivante pour tenir un chiffre ; le sort d'`ai-practices.md` se juge sur le fond, hors pression C6.

### C7 — Rentable ?

*Critère **par instruction**, appliqué à chaque survivante de C5, dans la même passe que C1→C5. C6 reste le seul critère global.*

L'instruction achète-t-elle son poids en mots ? C7 ne rejuge pas sa **présence** — C1→C5 l'ont tranchée — mais sa **formulation** : à couverture égale, combien de mots permanents elle coûte.

Décomposer l'instruction en quatre parts — **grille de lecture pour l'audit, jamais gabarit d'écriture** : on analyse une instruction existante avec, on n'impose aucun formulaire à la rédaction. *Pourquoi : la doc pose « Default assumption: Claude is already very smart » — sur-spécifier la forme ferme le modèle au lieu de le guider, et aucune source ne porte de budget par part.*

| Part | Statut |
|---|---|
| Impératif — le quoi, avec son alternative si c'est une négation | Porteur, irréductible |
| Pourquoi — une ligne (méta-règle de `reasoning.md`) | Porteur |
| Seuil / exception | Porteur **si mesurable** ; sinon c'est un défaut C3 déguisé en précision |
| Preuve, cas vécu, méta-commentaire, relance anti-complaisance | **Compressible** — sort vers un fichier de références chargé à la demande |

**Alerte** : ~60 mots par instruction — un déclencheur de test, pas un couperet. Le chiffre trie, le test tranche. *(Conventionnel : ~2× la médiane du harnais, 32 mots/bloc remesurée le 2026-08-10 sur 10 fichiers ; aucune source externe ne le porte, révisable entre deux audits.)*

| Cas | Action |
|---|---|
| Sous l'alerte, quatrième part absente | **Garder tel quel** |
| Dépassement porté par la quatrième part | **Extraire** la preuve vers les références ; l'instruction garde impératif + pourquoi + trigger |
| Dépassement porté par l'impératif | **Découper** — ce sont plusieurs instructions empilées, chacune repasse en C1 |
| Impératif plus court que pourquoi + preuve | **Red flag** — l'instruction argumente plus qu'elle ne prescrit ; réécrire avant de trancher |

**Test** — comportemental, pas un comptage : retirer la part jugée compressible, donner à un contexte neuf une tâche qui déclenche l'instruction, comparer le comportement. S'il change, la part était porteuse : la remettre et le noter. **Échantillonné** comme le sondage C1 — un test coûte une session, le réserver aux instructions au-dessus de l'alerte ; les autres verdicts C7 se marquent « jugé sur pièce ».

**Mesure** :

```bash
# Mots d'une instruction — plage de lignes issue du découpage du cadrage
sed -n '<début>,<fin>p' <fichier> | wc -w

# Médiane du harnais, pour recalibrer l'alerte
for f in $(grep -L '^paths:' rules/*.md) wrappers/claude/rules/*.md; do
  printf '%s\t%s\t' "$f" "$(grep -c '^\(- \|\*\*[A-ZÀ-Ü]\|#\+ \)' "$f")"; wc -w < "$f"
done
```

*Le compteur de blocs est une approximation (puces, titres, amorces en gras) : il calibre l'alerte, il ne découpe pas — le découpage qui fait foi est manuel.*

Les **cas vécus** sortent du permanent vers un fichier de références chargé à la demande ; la règle garde le trigger et le pourquoi en une ligne.

**POURQUOI ce critère** : le budget de C6 se satisfait en supprimant des instructions entières, donc en perdant de la couverture. C7 récupère les mêmes mots sans rien perdre — il ne coupe que ce qui n'achète aucun comportement. Et sans lui, une instruction bien placée (survivante de C1→C5) est réputée bien écrite : rien ne mesure sa formulation.

### C8 — Cohérent dans son fichier ?

*Critère **par fichier**, rendu une fois toutes ses instructions criblées.*

Les instructions survivantes d'un même fichier tiennent-elles ensemble ? Trois défauts que le verdict par instruction ne voit pas, parce qu'ils vivent **entre** les instructions :

| Défaut | Action |
|---|---|
| Deux instructions se contredisent, ou leurs exceptions se recouvrent en s'opposant | Trancher — une seule survit, ou l'articulation devient explicite |
| Redondance interne — deux instructions du fichier prescrivent la même chose autrement | Fusionner *(C4 ne l'attrape pas : son grep cherche ailleurs, pas entre voisines)* |
| Instruction orpheline — sans rapport avec le propos du fichier | Déplacer vers son vrai foyer |

**POURQUOI ce critère** : la cascade juge chaque instruction isolément ; un fichier peut être fait d'instructions toutes valides une à une et rester contradictoire — et c'est le fichier entier qu'une session charge, pas l'instruction.

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

**Rédaction d'instructions** — contre quoi juger C1 et C7, pour que la grille ne se valide pas contre la doctrine qu'elle audite :

| Sujet | Source | Vérifié |
|---|---|---|
| Rédaction de skills (« Does this paragraph justify its token cost? », degrees of freedom) | <https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices> | 2026-08-10, fetch |
| Rédaction de prompts/règles (motivation derrière l'instruction, dire quoi faire plutôt que quoi éviter) | <https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-4-best-practices> | 2026-08-10, fetch |
| CLAUDE.md (< 200 lignes, contexte = bien public) | <https://code.claude.com/docs/en/memory> | 2026-08-10, via agent doc |

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
# Symlinks de règles à jour (bash obligatoire : shebang bash, `set -o pipefail` casse sous dash)
bash wrappers/claude/scripts/sync-rules.sh
```

---

## Écarts déjà identifiés (seed — à confirmer par l'audit, pas acquis)

D'après la note d'inbox du 2026-08-10 :

- [x] `tooling.md` (449 mots) → migré le 2026-08-11 en `wrappers/claude/scripts/hooks/guard-bash-tooling.py` (**pas** `checks/`, cf. ligne ci-dessous), règle réduite à 120 mots. Câblé dans `settings.json`, batterie de 31 cas, calibré live et sur 987 commandes de transcripts.
- [ ] `ai-practices.md` (1 110) → sortir du contexte permanent (C6 : banc d'essai non validé qui dilue le validé)
- [ ] `reasoning.md` (1 100), `workflow.md` (1 055) → garder triggers et commandes, sortir les cas vécus (C3/C6)
- [ ] `ai-principles.md` (558) → réduire aux titres + une ligne (exception C3) ; corriger l'en-tête « le vault est la source »
- [ ] Gardes `guard-no-claude-in-commit.sh`, `guard-no-remote-write.py` → `git mv` vers `checks/` (séparation logique/binding). **Non fait, et le nouveau garde ne l'a pas anticipé** : `wrappers/claude/scripts/` est symlinké vers `~/.claude/scripts/`, donc `settings.json` y désigne ses hooks par `~/.claude/scripts/hooks/…`. Un `checks/` à la racine sortirait de l'arbre du symlink et imposerait un chemin absolu dans `settings.json`. Le déplacement reste défendable, mais il déplace les trois gardes **et** leur binding d'un coup — arbitrage à part.
- [ ] Couche 1 absente : 0 hook git sur 25 repos Winggy, 0 check CI de commits sur 19 (C2 : les deux gardes sont le seul filet)
