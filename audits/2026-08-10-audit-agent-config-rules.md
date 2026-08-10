# Audit harnais — agent-config, passe `rules/` — 2026-08-10

Instantané immuable. Grille : `audits/grille-harnais.md` au commit **`5327bdd`**, **arbre propre** (`git diff --stat` vide au cadrage et à la clôture) — verdicts rejouables.

Protocole : skill `audit-harnais` (01-cadrer → 02-cribler → 03-consolider). Rapport rendu après cascade complète sur 56 instructions.

## Contrat

- **Domaine / passe** : `agent-config`, sous-domaine `rules/` — les 11 fichiers de `rules/` **plus** `wrappers/claude/rules/memory-policy.md` (membre du set de 12 lié par `sync-rules.sh` et du périmètre C6 ; le laisser à la passe « wrappers » l'aurait fait échapper aux deux passes).
- **Critères** : C1→C5 et C7 par instruction, C8 par fichier, C6 en une somme globale (ici, section Budget). Rien d'autre.
- **Exclusions** : les rapports `2026-08-10-audit-agent-config.md` et `-c1-c4.md` non lus pendant le criblage (pas d'ancrage) ; le seed « Écarts déjà identifiés » de la grille traité en hypothèses remesurées.
- **Découpage** : 56 instructions, validé par l'humain avant criblage. `back-spring.md`/`front-react.md` découpés par section (les puces d'une section partagent leur pourquoi).

### Mesures d'inventaire (ouverture)

- `sync-rules.sh` : `✓ 12 règles, 12 liens, aucun écart`.
- `checks/` : absent. Gardes : `wrappers/claude/scripts/hooks/{guard-no-claude-in-commit.sh, guard-no-remote-write.py}`. `git config core.hooksPath` : non défini (exit 1).
- Scoping C5 : `grep -L/-l '^paths:' rules/*.md` → 9 fichiers non scopés + `memory-policy.md` ; scopés : `back-spring.md`, `front-react.md`.
- Sondage C1 (sous-agent aveugle, interdit de lire `rules/` et `audits/`, sommé d'ignorer les règles injectées — résultat **approximé** : les règles globales sont injectées aux sous-agents, le contexte n'est jamais vraiment neuf) : reconstruction quasi complète de la convention de commit en **11 appels d'outil**, sources = `git log`, `settings.json`, le garde lui-même, `aidd_docs/memory/vcs.md` (Winggy), `CLAUDE.md`. Non déductibles : la langue anglaise, la portée exacte de l'interdit IA, la convention vault.

## Cascade par instruction

Mots (C7) : `sed -n '<plage>p' | wc -w`, mesurés en lot le 2026-08-10. C4 : grep du motif central sur `rules/`, `wrappers/`, `skills/`, `README.md` (hors `audits/`), sorties consignées en session. Alerte C7 : ~60 mots (grille). Base : **M** = mesuré, **JP** = jugé sur pièce, **S** = supposé.

### `rules/profil.md` — 277 mots

| Instr | Plage | Mots | Sortie de cascade | Action | Base |
|---|---|---|---|---|---|
| P1 niveau technique | 7-11 | 43 | survit tout | garder tel quel | M (mots, grep) + JP |
| P2 contraintes cognitives | 13-21 | 118 | survit ; C7 : 4ᵉ part | extraire ~40 mots d'apartés d'articulation (« le protocole vit dans l'output style », « ne la re-argumentent pas ») | M + JP |
| P3 compréhension par le concret | 23-27 | 32 | survit tout | garder | M + JP |
| P4 incrément visible | 29-33 | 37 | survit tout | garder | M + JP |

**C8** : cohérent — quatre facettes orthogonales du même lecteur. (JP)

### `rules/style.md` — 296 mots

| Instr | Plage | Mots | Sortie | Action | Base |
|---|---|---|---|---|---|
| S1 verdict d'abord | 5 | 57 | survit tout | garder | M + JP |
| S2 une reco | 7 | 58 | survit tout | garder ; déclinaison dans `backend-architect` = application, pas copie (capture 6) | M + JP |
| S3 concret | 9 | 50 | survit tout | garder | M + JP |
| S4 densité | 11 | 49 | survit tout | garder | M + JP |
| S5 marquer l'incertain | 13 | 25 | survit tout | garder | M + JP |

**C8** : cohérent, cinq règles orthogonales, densité exemplaire (25-58 mots). (JP)

### `rules/reasoning.md` — 1 100 mots

| Instr | Plage | Mots | Sortie | Action | Base |
|---|---|---|---|---|---|
| R1 ne jamais affirmer sans vérifier | 1-19 | 388 | survit C1-C5 (non inférable, non hookable : raisonnement — ligne 3 du tableau C2 ; falsifiable gradient 2) ; C7 : dépassement porté par la 4ᵉ part | extraire « PAS DE SECOND RANG » + « CE QUE TUE UNE MESURE » (~120 mots, preuve VW3-3256) vers un fichier de références | M + JP |
| R2 trigger échec CI | 21 | 54 | survit tout | garder | M + JP |
| R3 trigger comptage zéro | 23-28 | 195 | survit ; C7 : 4ᵉ part | extraire le cas vécu « 1 019 occurrences » (~55 mots) ; les deux raisons structurées restent | M + JP |
| R4 trigger session log | 30 | 78 | survit ; C7 : léger dépassement, aucune 4ᵉ part | garder (test comportemental non joué — au-dessus de l'alerte mais sans part détachable) | M + JP |
| R5 contrat de questions | 32-42 | 249 | survit ; C7 | comprimer le POURQUOI (~50 mots d'argumentation sur la récursion) | M + JP |
| R6 toujours le pourquoi | 44-50 | 78 | survit ; C4 : doublon **statique** verbatim dans `skills/skill-craft/references/skill-authoring-fr.md:39-40` (bénin per grille) | garder ; capture 5 | M + JP |
| R7 cartesian check | 52-61 | 58 | survit ; C4 : recopié dans 4 `SKILL.md` (statique) | garder ; capture 4 | M + JP |

**C8** : cohérent — noyau + triggers concrets explicitement articulés, pas de contradiction ni redondance non déclarée. (JP)

### `rules/workflow.md` — 1 055 mots

| Instr | Plage | Mots | Sortie | Action | Base |
|---|---|---|---|---|---|
| W1 demander avant d'implémenter | 1-7 | 44 | survit (C2 non : « go reçu » est un état conversationnel invisible d'un hook) | garder | M + JP |
| W2 pré-vol | 9-23 | 262 | survit ; C7 : 4ᵉ part | extraire le cas vécu « trois valeurs fausses » (~45 mots) ; `mr-review/actions/01-prep.md:41` duplique le geste (statique, capture 6) | M + JP |
| W3 suite complète après build | 25-30 | 82 | survit ; C7 : **red flag** — impératif (~35) plus court que pourquoi (~45) | resserrer le pourquoi | M + JP |
| W4 échec fermé | 32-46 | 392 | survit (les scripts la **citent** — `sync-rules.sh:18`, `run-skill-evals.py:26`, `check-vault-bridge.sh:8` : pointeurs, pas doublons) ; C7 : 4ᵉ part | extraire les deux cas vécus (~180 mots : jq/VAULT_ROOT, garde supprimé) | M + JP |
| W5 déléguer par défaut | 48-62 | 219 | survit ; C7 : dépassement porté par l'**impératif** | découper en 2 instructions (déléguer par défaut / traduire au retour + test du dump) — chacune repasse C1 et survit (stratégies décidées, non inférables) | M + JP |
| W6 pas de liste figée | 64-68 | 56 | survit tout | garder | M + JP |

**C8** : cohérent. (JP)

### `rules/tooling.md` — 449 mots (seed remesuré : ✓)

| Instr | Plage | Mots | Sortie | Action | Base |
|---|---|---|---|---|---|
| T1 `bash -lc` + `sh ./mvnw` | 1-9 | 187 | **sort en C2** — l'interdit est un motif de chaîne sur une action éphémère (commande Bash) : hook `PreToolUse`, seul mécanisme possible | migrer en `checks/guard-bash-tooling.sh` (échec fermé, calibré sur cas positif fabriqué) ; la règle devient un pointeur | M (motif) + JP (faisabilité) |
| T2 heredoc imbriqué | 11-24 | 262 | **sort en C2** — motif détectable : `bash -lc` contenant `<<` | même garde ; la nuance « heredoc 1ᵉʳ niveau autorisé » descend dans la logique du script et ses tests | M + JP |

**C8** : cohérent ; après migration le fichier devient deux pointeurs. (JP)

### `rules/mermaid.md` — 235 mots

| Instr | Plage | Mots | Sortie | Action | Base |
|---|---|---|---|---|---|
| M1 vertical par défaut | 5-6 | 36 | survit ; C4 : doublon avec `mermaid-craft` **déclaré et assumé** — le modèle deux-couches que la grille C4 cite en exemple | garder | M + JP |
| M2 zéro croisement | 7-8 | 45 | survit (idem) | garder | M + JP |
| M3 charger `mermaid-craft` | 10-12 | 135 | survit ; C7 | comprimer l'énumération-teaser de ce que rate un diagramme (~40 mots) — elle vit déjà dans le skill | M + JP |

**C8** : cohérent — fichier modèle du découpage permanent/à-la-demande. (JP)

### `rules/commit-convention.md` — 320 mots

| Instr | Plage | Mots | Sortie | Action | Base |
|---|---|---|---|---|---|
| CC1 format CC anglais | 3-16 + 22 | 79 | **sort en C1+C2** — sondage : inférable en 11 appels (coût élevé, info volatile : le garde évolue et `vcs.md` a déjà divergé → **pointeur, jamais copie**) ; format déjà déterminisé (`guard-no-claude-in-commit.sh:226-236`) | réduire au pointeur vers le garde + les seules décisions non observables (anglais, imperative) | M (sondage approximé + grep) |
| CC2 zéro mention IA | 18 | 35 | **sort en C2** — bloqué mécaniquement (`guard:95-96`, mesuré) | pointeur + une ligne de pourquoi (accountability) | M |
| CC3 exception vault | 20 | 57 | **sort en C2** — le garde la connaît (`guard:228`, mesuré) | pointeur | M |
| CC4 état d'enforcement | 24-30 | 142 | **sort en C1/C4** — copie **volatile** du comportement du garde ; le texte avoue le double emploi (« same type list … added in both places ») | réduire à un pointeur ; la liste des non-vérifiés se lit dans le script | M + JP |

**C8** : le fichier entier double la couche déterministe — redondance structurelle. Cible : décisions non enforçables + pointeur (~80-120 mots). (JP)

### `rules/ai-principles.md` — 558 mots

Exception C3 de la grille : ne prescrit rien, se **réduit** (titre + une ligne de pourquoi), ne se supprime pas.

| Instr | Plage | Mots | Sortie | Action | Base |
|---|---|---|---|---|---|
| AP1→AP10 | 11-49 | 31-72 chacun | survivent (doctrine non inférable ; C3 couvert par l'exception) | réduction « titre + une ligne » ≈ −150 mots sur le fichier ; AP4 (72 mots, le plus long) perd son aparté « Prolonge… » | M + JP |

**C8** : AP3 (adapter le médium) et AP4 (servir l'intention) se recouvrent — AP4 le déclare lui-même → candidats à fusion. En-tête « le vault reste la source » contredit la décision du 2026-08-10 portée par la grille (capture 7, seed confirmé). (JP)

### `rules/ai-practices.md` — 1 110 mots (seed remesuré : ✓)

| Instr | Plage | Mots | Sortie | Action | Base |
|---|---|---|---|---|---|
| PR1 incréments vérifiés | 9-17 | 118 | survit ; C7 | extraire « EN TEST DEPUIS » (~25 mots) vers un registre | M + JP |
| PR2 contexte est du code | 21-33 | 232 | survit ; C7 | extraire EN TEST (~15), comprimer « ce que testé veut dire » | M + JP |
| PR3 capitaliser la leçon | 37-47 | 149 | survit ; C7 | extraire EN TEST | M + JP |
| PR4 dupliquée s'élimine | 51-61 | 151 | survit ; C7 | extraire le n=1 (~45) | M + JP |
| PR5 charger le journal | 63-73 | 187 | survit ; C7 | extraire l'échec n=1 (~60) | M + JP |
| PR6 écartées du banc | 75-81 | 105 | **sort en C3** — registre non prescriptif, gradient 4 (rien à falsifier) | déplacer vers le MOC du vault, où la promotion se décide | M + JP |
| PR7 budget 150 lignes | 83-87 | 87 | survit (falsifiable : `wc -l`) | garder | M + JP |

**C8** : cohérent. Tension C6 portée en Budget : le seed propose de sortir le fichier entier du permanent, mais sa raison d'être est d'être chargé (« une pratique jamais chargée n'est jamais exercée ») — arbitrage humain, pas verdict de cascade. (JP)

### `wrappers/claude/rules/memory-policy.md` — 207 mots

| Instr | Plage | Mots | Sortie | Action | Base |
|---|---|---|---|---|---|
| MP1 pas de fait projet en auto-memory | 3-7 | 145 | survit (le cœur — classer la **nature** d'un fait — n'est pas hookable) ; C7 | comprimer le POURQUOI (~40 mots) | M + JP |
| MP2 ce qui traverse un sous-agent | 9 | 54 | survit ; C4 : même fait dans `ai-principles.md:5` (« un sous-agent ne lit pas le vault ») | dédupliquer — MP2 garde le foyer (preuve datée 2026-07-20), `ai-principles.md:5` se réduit | M + JP |

**C8** : cohérent. (JP)

### `rules/back-spring.md` — scopé `paths:` (C5 réglé au frontmatter)

| Instr | Plage | Mots | Sortie | Action | Base |
|---|---|---|---|---|---|
| B1 Javadoc publique | 9-13 | 76 | survit ; C2 **partiel** : la présence est lintable (checkstyle en CI), le jugement (« pas de paraphrase ») reste prose | proposer le linter ; en attendant, garder | M + JP (S sur la dispo checkstyle dans les CI Winggy — non vérifiée) |
| B2 tests comportement métier | 15-20 | 115 | survit ; C7 : puces solidaires du principe directeur | garder | M + JP |
| B3 nommage / DDD stratégique | 22-27 | 174 | survit ; C7 | comprimer le POURQUOI (~40 mots) | M + JP |

**C8** : cohérent. (JP)

### `rules/front-react.md` — scopé `paths:` (C5 réglé)

| Instr | Plage | Mots | Sortie | Action | Base |
|---|---|---|---|---|---|
| F1 TSDoc exports publics | 8-12 | 81 | survit | garder | M + JP |
| F2 Testing Library, rôle avant testId | 14-19 | 75 | survit ; C2 partiel : `eslint-plugin-testing-library` couvrirait « testId dernier recours » | proposer le plugin (**supposé** — existence connue, installation non vérifiée) | M + JP + S |
| F3 nommage PascalCase/use | 21-26 | 95 | survit ; C2 partiel : règles eslint de nommage | proposer ; garder en attendant | M + JP |

**C8** : cohérent. (JP)

## Budget (C6) — une somme, à la consolidation

Commande de la grille exécutée le 2026-08-10 : **5 830 mots** au total — 5 607 de règles + 223 d'output style (identique au seed, remesuré). Cible grille : ≤ 3 500 hors output style.

Projection des actions ci-dessus (approximations à ±10 %) :

| Fichier | Actuel | Après actions | Gain |
|---|---|---|---|
| `tooling.md` → pointeurs (hook) | 449 | ~40 | −409 |
| `commit-convention.md` → pointeur + décisions | 320 | ~120 | −200 |
| `reasoning.md` (extractions) | 1 100 | ~875 | −225 |
| `workflow.md` (extractions + resserrage) | 1 055 | ~790 | −265 |
| `ai-principles.md` (réduction) | 558 | ~410 | −150 |
| `ai-practices.md` (EN TEST + PR6, **sans** sortir le fichier) | 1 110 | ~860 | −250 |
| `memory-policy.md` | 207 | ~127 | −80 |
| `mermaid.md` | 235 | ~195 | −40 |
| `profil.md` | 277 | ~237 | −40 |
| **Total règles non scopées** | **5 607** | **~3 950** | **−1 657** |

**Verdict C6 : la cible 3 500 n'est pas atteignable par les seules actions de cascade.** Le solde (~450 mots) impose l'arbitrage `ai-practices.md` : sortie du permanent (−860 restants → ~3 100 ✓) contre sa fonction déclarée de banc d'essai chargé en continu. Décision humaine, remontée telle quelle.

## Captures hors grille

Notées en une ligne, non creusées (contrat de questions) :

1. `audit-harnais/actions/01-cadrer.md` cite « `workflow.md` en donne cinq » — le comptage manuel en donne 6 : l'exemple du skill a dérivé.
2. **Divergence avérée doc↔garde** (sondage) : `aidd_docs/memory/vcs.md` (Winggy) documente `style` et `revert`, la regex du garde les refuse ; `style(audit-item-card)` existe dans `interface_v3`. Quelle liste fait foi ?
3. Angle mort du garde (sondage) : `git commit --amend`/éditeur et corps multi-heredoc échappent au contrôle — précise le périmètre déjà avoué par CC4.
4. Cartesian check recopié dans 4 `SKILL.md` (backend-architect, frontend-expert, database-expert, agentic-architect) — doublon statique multiple, divergera au premier edit de la définition.
5. R6 (« toujours le pourquoi ») dupliqué quasi verbatim dans `skill-craft/references/skill-authoring-fr.md` (R12).
6. Fragments de `style.md`/`profil.md` déclinés dans `mr-review`, `backend-architect`, `fact-checker` — applications contextuelles, statiques, bénignes.
7. En-tête d'`ai-principles.md` (« le vault reste la source d'écriture ») contredit la décision du 2026-08-10 inscrite dans la grille (seed confirmé à la lecture).
8. MP2 et `ai-principles.md:5` portent le même fait harnais (injection des rules aux sous-agents) en deux fichiers.

## À réviser entre deux audits

Propositions pour la grille — rien n'y a été touché pendant la passe (`git diff -- audits/grille-harnais.md` vide) :

- **Seuil C1 « < 3 appels »** : le sondage a coûté 11 appels et a pourtant reconstruit ~90 % de la convention. Le seuil binaire ne capte pas « inférable mais dispersé sur plusieurs sources » ; envisager un barème appels × complétude.
- **C6** : la cible 3 500 s'est révélée inatteignable par cascade seule — soit la réviser, soit acter que l'arbitrage `ai-practices.md` en fait partie.
- **Foyer de la convention de commit** : trois occurrences volatiles aujourd'hui (règle, garde, `vcs.md` Winggy) dont deux divergent déjà — la grille pourrait exiger un foyer unique désigné pour toute convention outillée.
