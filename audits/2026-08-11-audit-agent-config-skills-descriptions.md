# Audit harnais — agent-config, passe `skills/` A (les 26 descriptions) — 2026-08-11

Instantané immuable. Grille : `audits/grille-harnais.md` au commit **`1ad0dac`**, **arbre propre** (`git diff -- audits/grille-harnais.md` vide au cadrage et à la clôture) — verdicts rejouables.

Protocole : skill `audit-harnais` (01-cadrer → 02-cribler → 03-consolider). Rapport rendu après cascade complète sur 26 instructions.

**Verdict en une phrase** : les 26 descriptions survivent toutes à C1→C5 — aucune n'est inférable, aucune ne gagne à être scopée — mais elles pèsent **2 174 mots de contexte permanent que la cible C6 n'avait jamais comptés**, et leur falsifiabilité est inversement corrélée au risque : les 13 skills sans éval incluent **les 4 seuls qui écrivent, committent ou poussent**.

---

## Contrat

**Périmètre** : les 26 blocs `description` de `agent-config/skills/*/SKILL.md`. Une description = une instruction (le contrat de routage du skill). Justification du périmètre : c'est la seule couche de `skills/` qui entre dans chaque session — le corps ne se charge qu'à l'invocation (borne inscrite en C6 au commit `1ad0dac`).

**Critères** : cascade complète C1→C8 de la grille. C8 rendu par **famille** (les descriptions ne partagent pas de fichier ; la famille est l'unité de voisinage réelle).

**Hors crible, reporté** : corps de `SKILL.md`, `actions/`, `references/`, `evals/`, `assets/` → passes B/C/D. `skills/_shared/` (2 scripts + `llm-decision-grid.md`, aucun `SKILL.md`, donc non découvert comme skill — vérifié : `ls ~/.claude/skills/` rend 27 entrées dont `_shared`) → passe « scripts ».

**Exclusions** : les 22 skills vault pro et 13 vault perso (autres domaines). Les skills de plugin (`aidd-*`) et les skills livrés par Claude Code (`dataviz`, `artifact-*`, `code-review`…) — non versionnés dans ce repo, non modifiables ici.

**Entrées figées, non rejugées** : la note `myvaultobsidian/0_INBOX/2026-08-10-cadrage-refonte-skills.md` et son annexe `audits/2026-08-10-refonte-skills-constats.md` portent le volet **conformité de construction**, que la grille délègue explicitement à ses sources normatives (l.152-153). Les décisions humaines qu'elles actent (gérondif, groupement à plat, sous-dossiers écartés) entrent au contrat comme acquises.

**Extension du contrat, décidée par l'humain après le premier rendu** : la conformité de **structure** des descriptions à la doc Anthropic (personne grammaticale, forme quoi + quand, validité du frontmatter) avait été exclue ci-dessus au motif que la note du 2026-08-10 la portait. Elle n'avait pas été remesurée, ce que la grille exige pourtant de tout chiffre repris d'une note (section Méthode). L'humain a rouvert le contrat sur ce point ; l'agent ne l'a pas fait de lui-même. Résultats en section « Conformité de structure », dont un défaut absent de la note du 2026-08-10.

**État du dépôt au criblage** : `rules/reasoning.md`, `rules/workflow.md`, `wrappers/claude/scripts/sync-rules.sh` modifiés et `rules/references/` non suivi — travail d'application de la passe `rules/` en cours dans une autre session. Sans effet sur ce périmètre (aucune description touchée), mais les greps C4 contre `rules/` voient un état en mouvement : les verdicts C4 croisant `rules/` sont datés de ce criblage.

---

## Mesures d'ouverture

Toutes lancées avant le premier verdict.

| Mesure | Commande | Sortie |
|---|---|---|
| Poids des descriptions | `python3` + parseur YAML | **2 174 mots** / 15 370 car. sur 26 skills |
| Description la plus longue | idem | `memory-bootstrap`, 140 mots / 946 car. |
| Médiane | idem | **86 mots** (alerte C7 : ~60) |
| Frontmatter parsable par un YAML strict | `yaml.safe_load` sur les 26 | **25/26** — `skill-craft` échoue |
| Forme d'écriture du champ `description` | `grep` du 1er caractère | 23 en bloc `>-`, **3 en scalaire nu** |
| Personne grammaticale, hors phrases citées | script recalibré | **24/26** en 3e personne |
| Découpe quoi / quand / NE PAS | script, `scratchpad/mesure-descriptions.py` | 1 004 / 727 / 466 mots |
| Champs de frontmatter utilisés | `sed` + `uniq -c` sur les 26 | `name` ×26, `description` ×26, **rien d'autre** |
| Skills avec `evals/` | `ls skills/*/evals` | **13/26**, dont 12 avec `trigger_markers` |
| Sections « Quand t'activer » dans les corps | `awk` par section | **9/26**, **1 083 mots** |
| Arêtes de renvoi entre descriptions | script | 36 internes + 14 externes |
| Montage réel | `ls -ld ~/.claude/skills` | symlink → `agent-config/skills` |
| C6, permanent total | commande C6 de la grille | 5 161 (règles + output style) + 2 174 (descriptions) = **7 335 mots** |

**Référentiel doc, re-vérifié ce jour** (fetch `code.claude.com/docs/en/skills`, 2026-08-11) — trois faits qui pilotent des verdicts ci-dessous :

- **`paths:` existe pour un skill** : « Glob patterns that limit when this skill is activated. When set, Claude loads the skill automatically only when working with files matching the patterns. » C5 dispose donc bien de son mécanisme sur ce sous-domaine.
- **La description est plafonnée à 1 536 caractères dans le listing** (`description` + `when_to_use` cumulés), pas 1 024 — ce dernier est la limite de la spec API. Le chiffre de 1 024 repris de l'annexe du 2026-08-10 est corrigé ici. Max mesuré : 946 car., aucune troncature.
- **`disable-model-invocation: true`** « prevents Claude from automatically loading this skill » et « prevents the skill from being preloaded into subagents ».

**Calibrage des instruments — trois aveuglements corrigés, tous sur un positif exhibé à la main :**

1. **Effets de bord.** Le premier grep (`git add|commit|push|rm|mv`) ratait `vault-save`, positif connu et documenté (`skills/vault-save/SKILL.md:42-44`, `commit + push`). Recalibré, il le classe premier. Trois faux positifs subsistent dans l'extraction des renvois externes (`→ prompt direct`, `→ skill X`, `→ r`) — écartés à la main, non comptés.
2. **Personne grammaticale.** Le premier détecteur rendait 4 écarts, dont 3 faux : il comptait les « je » et « mes » **à l'intérieur des phrases utilisateur citées** (« "j'ai cloné un nouveau repo" »), qui sont l'usage correct. Et il ratait « te », donc `doc-sync` — positif connu de la note du 2026-08-10. Recalibré en excluant les segments entre guillemets et en couvrant les élidés, il retrouve les deux positifs connus et n'en ajoute aucun.
3. **Extraction du champ.** La première extraction, par expression régulière, incluait le marqueur de bloc `>-` et l'indentation YAML : elle rendait 2 197 mots / 15 734 car. Le comptage par parseur YAML rend **2 174 mots / 15 370 car.** — écart de 1 %, aucun verdict ne change, chiffre corrigé partout dans ce rapport.

---

## Cascade par instruction

Base : **M** = mesuré (commande citée), **P** = jugé sur pièce, **S** = supposé.

| # | Instruction | Sortie de cascade | Action prescrite | Base |
|---|---|---|---|---|
| 1 | `security-reviewer` (62 mots) | survit C1→C5, C7 OK | garder tel quel — sous l'alerte, éval présente | M |
| 2 | `code-reviewer` (63) | survit C1→C5, C7 OK | garder tel quel | M |
| 3 | `frontend-expert` (67) | survit C1→C5, **C7 alerte** (67 > 60) | jugé sur pièce : dépassement porté par 4 renvois frères, chacun une contrainte distincte → garder | M/P |
| 4 | `backend-architect` (72) | survit, **C7 alerte** | garder — 10 frères le désignent comme défaut, sa description porte le routage du groupe | M |
| 5 | `database-expert` (75) | survit, **C7 alerte** | garder | M/P |
| 6 | `devops-expert` (77) | survit, **C7 alerte** | garder | M/P |
| 7 | `brain-expert` (80) | survit, **C7 alerte** | garder | M/P |
| 8 | `ai-engineering` (93) | survit, **C7 alerte** | garder — 39 mots de « quand », couverts par éval | M |
| 9 | `agentic-architect` (98) | survit, **C7 alerte** | garder — idem | M |
| 10 | `vault-load` (46) | survit C1→C5, C7 OK | **C3 niveau 3** : aucune éval, mode `<task-id>` non falsifié | M |
| 11 | `vault-capture` (46) | survit, C7 OK | **C3 niveau 3** : aucune éval | M |
| 12 | `vault-slides` (48) | survit, C7 OK | **C3 niveau 3** : aucune éval | M |
| 13 | `vault-capture-projet` (54) | survit, C7 OK | **C3 niveau 3** ; écrit dans le vault (desc:0/corps:0 au grep, jugé sur pièce) | M/P |
| 14 | `vault-save` (57) | survit C1, **sort en C2** | **mécanisme déterministe disponible** : `disable-model-invocation: true`. Effet de bord le plus net du corpus (`git add -A` + commit + push, mesuré 7 corps / 3 desc). Le routage probabiliste est le mauvais mécanisme pour une action irréversible. | M |
| 15 | `vault-log-session` (59) | survit C1, **sort en C2** | idem — journalise et écrit dans le vault (3 corps / 2 desc) | M |
| 16 | `docs-check` (86) | survit, **C7 alerte** | garder — éval présente ; 14 mots de « quoi » seulement, structure la plus économe du corpus | M |
| 17 | `mermaid-craft` (88) | survit, **C7 alerte** | **C3 niveau 3** : aucune éval, alors que `rules/mermaid.md` délègue à ce skill en se déclarant partielle — le pointeur est permanent, sa cible non falsifiée | M |
| 18 | `vault-recap-raisonnement` (86) | survit, **C7 alerte** | **C8 — collision** : partage le terme déclencheur `"recap"` avec `vault-log-session` (mesuré) ; **C3 niveau 3** | M |
| 19 | `audit-harnais` (103) | survit, **C7 alerte** | garder — éval présente, 2 renvois externes tous deux résolubles | M |
| 20 | `test-runner` (106) | survit, **C7 alerte**, **défaut C1** | **2 pointeurs périmés** : `aidd-dev:02` et `aidd-dev:06` ne sont pas des noms invocables (réels : `02-implement`, `06-test`). Une copie tronquée n'est pas un pointeur. **C3 niveau 3** : aucune éval | M |
| 21 | `aidd-pilot` (111) | survit, **C7 alerte**, **défaut C1**, **sort en C2** | **2 pointeurs périmés** (`aidd-dev:05`, `aidd-vcs:01`) ; effet de bord fort (13 corps) → candidat `disable-model-invocation` ; **C3 niveau 3** | M |
| 22 | `mr-review` (114) | survit, **C7 alerte** | garder — éval présente ; renvoi externe résoluble | M |
| 23 | `skill-craft` (116) | survit, **C7 alerte**, **défaut de structure** | **Frontmatter refusé par un parseur YAML strict** : ` : ` dans un scalaire nu (« un skill existant **:** relance les… »). Claude Code l'accepte, la spec agentskills.io et l'API Skills le rejetteraient. Plus « Fabrique et vérifie **mes** skills perso » — 1re personne. Éval présente. | M |
| 24 | `fact-checker` (120) | survit, **C7 alerte** | **C3 niveau 3** : aucune éval, 30 mots de déclencheurs non falsifiés | M |
| 25 | `doc-sync` (130) | survit C1, **sort en C2**, **défaut de structure** | effet de bord le plus dense du corpus (14 corps / 3 desc) → `disable-model-invocation` ; **C3 niveau 3** : aucune éval ; 2e personne — « il signale l'écart et **te** laisse arbitrer » | M |
| 26 | `memory-bootstrap` (140) | survit, **C7 alerte** (la plus longue), **sort en C2** | écrit dans un index partagé → candidat ; **C3 niveau 3** ; 57 mots de « quoi » à eux seuls | M/P |

**Aucune instruction ne sort en C1, C4 ou C5.** Les motifs, mesurés :

- **C1** — une description est le contrat de routage : rien d'autre dans le repo ne le porte, donc rien à inférer. Les seuls défauts C1 sont les **4 pointeurs externes tronqués** (#20, #21), qui sont des copies périmées et non des pointeurs — exactement le cas que C1 proscrit pour l'info volatile.
- **C4** — les 36 renvois entre descriptions sont des contraintes de routage **distinctes**, pas des copies : « ne pas utiliser `code-reviewer` pour la sécurité » n'existe qu'une fois. Vérifié par grep du motif central. Le vrai doublon est **entre couches** et non dans celle-ci : les 9 sections « Quand t'activer » des corps (**1 083 mots**) reformulent la description qui les précède. La description est le foyer canonique — c'est elle qui route ; la section de corps est la copie à supprimer, en **passe B**.
- **C5** — `paths:` existe (doc vérifiée ce jour) mais **ne convient à aucune des 26**. Les 7 ponts vault se déclenchent sur une phrase, jamais sur un fichier ouvert ; les 9 experts répondent à des questions posées sans fichier courant. Poser `paths:` y **réduirait** l'activation au lieu de la scoper. Verdict : mécanisme disponible, gain nul sur ce corpus — et c'est un item de refonte à ne pas ouvrir.

---

## Conformité de structure (contrat étendu par l'humain)

Contre la doc officielle re-fetchée ce jour, pas contre la note du 2026-08-10.

| Attente | Mesuré le 2026-08-11 | Base |
|---|---|---|
| Forme « quoi + quand », avec termes déclencheurs | **26/26** — toutes portent un bloc `Utiliser quand` et des phrases citées (2 à 9, médiane 5) | M |
| 3e personne | **24/26** | M |
| Sous le plafond du listing (1 536 car.) | **26/26** — maximum 946 car., soit 62 % du plafond | M |
| Frontmatter valide pour un parseur YAML strict | **25/26** | M |

**Verdict : la structure est conforme.** Les descriptions font ce que la doc attend d'elles — une surface de correspondance, pas une notice. Trois écarts seulement, dont un neuf.

**Les deux écarts de personne** sont exactement ceux relevés le 2026-08-10, toujours présents : `skill-craft` (« Fabrique et vérifie **mes** skills perso ») et `doc-sync` (« il signale l'écart et **te** laisse arbitrer »). Confirmés par un détecteur calibré sur ces deux cas.

**L'écart neuf, absent de la note du 2026-08-10** : le frontmatter de `skill-craft` n'est pas du YAML valide au sens strict. Un ` : ` apparaît dans un scalaire non quoté ; un parseur y voit le début d'une nouvelle clé. Claude Code l'accepte — le skill est listé avec sa description entière, vérifié dans la session de cet audit — mais la spec agentskills.io et l'API Skills, qui valident strictement, le rejetteraient.

**Ce qui protège les 25 autres est une forme d'écriture, pas une vérification** : 23 descriptions sur 26 sont écrites en bloc `>-`, où un `:` est inoffensif. Trois sont en scalaire nu, donc exposées, et l'une des trois est déjà tombée. La note du 2026-08-10 annonçait « frontmatter valide (aucune clé inconnue) » : ce contrôle portait sur les **clés**, pas sur la **syntaxe** — il ne pouvait pas voir ce défaut.

---

## Verdicts par famille (C8)

| Famille | Verdict | Détail |
|---|---|---|
| **Experts (9)** | Cohérente | 36 arêtes de renvoi, aucun cycle contradictoire. `backend-architect` est cité par 10 frères : il joue le défaut du groupe, ce qui est explicite et assumé. Aucune orpheline. |
| **Ponts vault (7)** | **Un défaut** | Collision de déclencheur mesurée : `"recap"` route à la fois `vault-log-session` et `vault-recap-raisonnement`. Les deux descriptions le citent verbatim, aucune ne départage. À trancher au niveau du terme partagé, pas par un `NE PAS` de plus. |
| **Workflow / outillage (10)** | Cohérente, 2 pointeurs cassés | Les renvois internes (`aidd-pilot` ↔ `test-runner` ↔ `skill-craft`) s'articulent sans contradiction. Les 4 pointeurs externes tronqués (#20, #21) sont un défaut C1, pas C8. |

---

## C6 — le budget

Somme mesurée ce jour, commande de la grille :

| Couche | Mots | Compté dans la cible du 2026-08-10 ? |
|---|---|---|
| Règles non scopées (`rules/` + `wrappers/claude/rules/`) | 4 938 | oui |
| Output style actif (`chat-style.md`) | 223 | oui (hors cible) |
| **Descriptions des 26 skills** | **2 174** | **non** |
| `MEMORY.md` du projet courant | 0 (absent pour `agent-config`) | oui |
| **Total permanent réel** | **7 335** | — |

**Verdict** : le corpus n'est pas en dépassement, **la cible est sous-périmétrée**. Les ~3 950 mots visés ont été établis le 2026-08-10 sur les seules règles ; 30 % du permanent réel n'entrait pas dans le calcul. Conformément à la décision du 2026-08-10 inscrite en C6 — « on ne supprime pas une instruction survivante pour tenir un chiffre » — **aucune description n'est supprimée au titre du budget**. La révision de la cible part en section suivante.

Ce que C6 ne réclame pas mais que la mesure éclaire : **466 mots** (21 % de la couche) sont des blocs « NE PAS utiliser pour », et **727 mots** (33 %) des listes de phrases déclencheuses — 129 termes distincts. Les seconds sont des seuils au sens de C7 : porteurs **si mesurables**. Ils le sont pour les 13 skills à éval ; pour les 13 autres, **303 mots** de déclencheurs ne sont adossés à aucun test. C7 nomme ce cas : « sinon c'est un défaut C3 déguisé en précision ».

---

## Le constat qui domine la passe

**La falsifiabilité est inversement corrélée au risque.**

Les 13 skills qui portent une éval avec `trigger_markers` — donc dont le déclenchement se vérifie par une commande — sont `agentic-architect`, `ai-engineering`, `audit-harnais`, `backend-architect`, `brain-expert`, `code-reviewer`, `database-expert`, `devops-expert`, `docs-check`, `frontend-expert`, `mr-review`, `security-reviewer`, `skill-craft`. **Tous rendent un avis ou lisent.** Aucun n'écrit.

Les 13 sans éval incluent **les quatre seuls skills du corpus qui écrivent, committent ou poussent** : `vault-save` (`git add -A` + push), `doc-sync`, `aidd-pilot`, `vault-log-session`. Un faux déclenchement y coûte un commit non voulu ; un faux déclenchement sur `code-reviewer` coûte un paragraphe.

C'est une double panne qui se cumule, et c'est le même motif que celui documenté en C2 : là où le coût de l'erreur est le plus haut, on a le mécanisme le plus faible (routage probabiliste) **et** aucune mesure de sa fiabilité. Le mécanisme déterministe existe et n'est utilisé nulle part (`disable-model-invocation`, 0/26).

---

## Captures hors grille

Notées, non creusées.

- Le listing de skills injecté en session inclut aussi les skills de plugin et ceux livrés par Claude Code — hors périmètre de ce repo, mais ils pèsent sur le même budget de session. Aucun domaine de la grille ne les couvre.
- `skills/_shared/llm-decision-grid.md` (2 213 o.) n'est routé depuis aucun `SKILL.md` des 26 — annexe potentiellement orpheline, à vérifier en passe scripts.
- L'annexe du 2026-08-10 donne « descriptions ≤ 954 caractères » ; la mesure de ce jour rend 946 au maximum. Écart non creusé (corpus modifié depuis, ou méthode de comptage différente).
- `disallowed-tools`, `model`, `effort` figurent au frontmatter documenté et sont absents de la liste de champs de la note de cadrage du 2026-08-10.

---

## À réviser entre deux audits

1. **Cible C6 à re-poser sur le périmètre complet.** Elle vaut ~3 950 mots pour un permanent qui en fait 7 335. Soit la cible ne concerne que les règles et le dit, soit elle intègre les descriptions et se recalcule. En l'état elle se lit comme un plafond global qu'elle n'est pas.
2. **C5 est muet sur le cas « mécanisme disponible mais inadapté ».** Sa table ne propose que « domaine limité → `paths:` ». Les 26 verdicts de cette passe ont dû être rendus hors table. Un troisième cas — « global par nature, scoper nuirait » — éviterait que la prochaine passe le re-tranche.
3. **C3 gagnerait un niveau explicite pour l'éval.** Le gradient parle de « commande de vérification » ; sur ce sous-domaine la commande est un fichier d'éval avec `trigger_markers`. Le nommer rendrait le verdict mécanique au lieu d'interprétatif.
4. **C7 juge des instructions rédigées, pas des contrats de routage.** Sa quatrième part (preuve, cas vécu) n'existe pas dans une description : l'alerte à 60 mots a marqué 19 dépassements sur 26 sans jamais désigner de part compressible. Le seuil est probablement à recalibrer pour ce sous-domaine, ou C7 à déclarer partiellement inapplicable.

---

## Report vers les chantiers de la note de cadrage

Seul canal entre cette passe et le travail de refonte. Aucun plan parallèle n'est créé.

| Chantier | Ce que la passe y change |
|---|---|
| **0 — convention** | Corriger le plafond de description : **1 536 car.** dans le listing Claude Code, 1 024 étant la limite spec API. Ajouter `disallowed-tools`, `model`, `effort` à la liste des champs. **Écrire qu'une phrase déclencheuse sans éval est une assertion non testée** — c'est le levier qui manque au lint. **Exiger le bloc `>-`** pour le champ `description` : il rend un `:` inoffensif, là où le scalaire nu casse le parsing strict. **Étendre le lint** à un `yaml.safe_load` du frontmatter (le contrôle actuel porte sur les clés, pas sur la syntaxe) et à la 3e personne hors phrases citées. |
| **1 — bugs** | **Nouveau, mesuré** : 4 pointeurs externes tronqués et non invocables — `aidd-dev:05` et `aidd-vcs:01` dans `aidd-pilot`, `aidd-dev:02` et `aidd-dev:06` dans `test-runner`. Cibles réelles : `05-review`, `01-commit`, `02-implement`, `06-test`. **Neuf** : frontmatter de `skill-craft` non parsable en YAML strict (` : ` dans un scalaire nu) — accepté par Claude Code, rejeté par la spec et l'API. **Confirmés toujours présents** : 1re personne dans `skill-craft`, 2e personne dans `doc-sync`. |
| **2 — frontmatter** | **Confirmé et resserré** : `disable-model-invocation` sur `vault-save`, `doc-sync`, `aidd-pilot`, `vault-log-session` — les 4 sortis en C2, par effet de bord mesuré et non par appréciation. `memory-bootstrap`, `vault-capture-projet`, `vault-slides` restent des candidats jugés sur pièce. **`paths:` : ne pas ouvrir** — mécanisme disponible, gain nul sur ce corpus (verdict C5 mesuré). |
| **3 — dédupliquer** | **Chiffré** : les 9 sections « Quand t'activer » pèsent **1 083 mots** et reformulent la description. La description est le foyer canonique. Suppression en passe B. |
| **6 — boucles de validation** | **Priorité redéfinie par le risque** : écrire d'abord les évals des 4 skills à effet de bord, pas des skills de lecture. La liste actuelle du chantier 6 ne classe pas par risque. |
| **7 — collisions** | **Nouveau sur agent-config** (le chantier ne visait que les vaults) : `"recap"` route `vault-log-session` et `vault-recap-raisonnement`. |
| **8 — renommage** | Inchangé, reste dernier. |

---

## Suite

Passe B — les 9 corps d'experts (15 252 mots), où atterrit le doublon des 1 083 mots chiffré ci-dessus.
