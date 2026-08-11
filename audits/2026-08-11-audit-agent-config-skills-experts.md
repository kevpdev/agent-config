# Audit `agent-config` — passe B : les 9 corps d'experts

**Grille** : `audits/grille-harnais.md` au commit `cf5877a`, arbre **propre** sur `audits/` (`git diff -- audits/grille-harnais.md` vide en ouverture comme en clôture de passe).
**Arbre de travail** : deux fichiers modifiés hors périmètre — `wrappers/claude/scripts/hooks/guard-no-claude-in-commit.sh` et son test. Travail en cours dans une session parallèle, **non lu, non jugé**.
**Date** : 2026-08-11.

---

## Contrat

**Périmètre** : les corps des 9 skills d'expertise — `security-reviewer`, `code-reviewer`, `frontend-expert`, `database-expert`, `backend-architect`, `brain-expert`, `agentic-architect`, `devops-expert`, `ai-engineering`. Soit `SKILL.md` + `references/` + `assets/` + `evals/`.

**Critères** : C1→C5 puis C7 par instruction, C8 par fichier. **C6 est hors périmètre** — la grille (l.93) pose que le corps d'un skill ne se charge qu'à l'invocation. Un relevé de contrôle figure en clôture, sans verdict.

**Exclusions**
- Les 9 `description` du frontmatter : **déjà jugées** en passe A (`2026-08-11-audit-agent-config-skills-descriptions.md`). Elles n'entrent ici que comme surface de comparaison pour C4.
- Les 17 autres skills : passes C et D.
- `skills/_shared/` : entre au titre de référence citée par deux experts, pas comme objet de passe.
- La conformité de construction contre la doc Anthropic : déléguée à la note de cadrage (grille l.198).

**Volumes mesurés**

| Couche | Mots | Part |
|---|---|---|
| `SKILL.md` (9) | 7 991 | 49 % |
| `references/` (19 fichiers) | 6 252 | 38 % |
| `assets/` (5 gabarits) | 1 009 | 6 % |
| `evals/` (9 + fixtures) | 1 008 | 6 % |
| **Total** | **16 260** | |

*L'écart avec les 15 252 mots du plan de campagne est l'inclusion des `evals/` (eval.json + fixtures `.java`/`.js`), que le `find -name '*.md'` du plan excluait. Les deux chiffres sont justes sur leur périmètre.*

---

## Le moule, et ce qu'il implique

Les 9 corps suivent une structure **strictement identique**, vérifiée par `grep '^#\+ '` sur les 9 fichiers :

```
## Rôle → ## Quand t'activer (+ Ne pas s'activer pour) → ## Avant
→ ## Pendant → ## Après → ## Règles strictes → patterns → ## Contrôle de sortie → ## Test
```

**Conséquence de méthode** : une instruction présente à l'identique dans les 9 fichiers n'est pas 9 instructions, c'est **une instruction en 9 copies** — c'est la définition même du défaut C4. La cascade ci-dessous se rend donc par *instruction du moule*, en nommant ses copies. Les instructions propres à un seul skill (les négations de domaine) sont jugées à part.

---

## Cascade par instruction

### Instructions du moule — présentes dans les 9

| # | Instruction | Sort | Action prescrite | Base |
|---|---|---|---|---|
| M1 | `## Rôle` — persona nommée (Riley, Sam, Jordan, Morgan, Alex) + posture | survit C1→C5 · **C7 red flag** | Voir « le prénom » ci-dessous | jugé sur pièce |
| M2 | `## Quand t'activer` — liste de déclencheurs positifs | **sort en C1** | **Supprimer** — arrive après la décision qu'elle prétend informer | mesuré |
| M3 | `**Ne pas s'activer pour :**` — redirections vers les frères | survit C1 · **sort en C4** | Une seule copie ; la clause du frontmatter est la surface qui route | mesuré |
| M4 | `## Avant` — étapes de préparation + chargement conditionnel des références | survit tout | **Garder tel quel** — c'est le cœur non inférable | jugé sur pièce |
| M5 | `## Pendant` — méthode d'analyse (catégories à parcourir) | survit tout | Garder | jugé sur pièce |
| M6 | `## Après` — renvoi au gabarit `assets/` ou format inline | survit tout | Garder | mesuré |
| M7 | `## Règles strictes` — négations + alternative + pourquoi | 40 instances, **jugées à part** | ci-dessous | mixte |
| M8 | patterns / blocs de savoir inline | 4 sortent en C4, le reste survit | ci-dessous | mesuré |
| M9 | `## Contrôle de sortie` — critères appliqués pendant l'exécution | survit tout · **C4 partiel** | 1 phrase à dédupliquer (5 copies) | mesuré |
| M10 | `## Test` — pointeur vers `evals/` | survit tout · **C3 niveau 2 plafonné** | ci-dessous | mesuré |

### M2 — `## Quand t'activer` : le constat central de la passe

**1 083 mots** répartis sur les 9, contre **678 mots** de descriptions. Le corps pèse **1,6×** ce que la surface de routage porte déjà.

| Skill | `description` | `Quand t'activer` + `Ne pas` | Ratio |
|---|---|---|---|
| security-reviewer | 61 | 158 | 2,6 |
| ai-engineering | 92 | 162 | 1,8 |
| backend-architect | 71 | 126 | 1,8 |
| devops-expert | 76 | 116 | 1,5 |
| frontend-expert | 66 | 93 | 1,4 |
| agentic-architect | 97 | 123 | 1,3 |
| brain-expert | 79 | 98 | 1,2 |
| database-expert | 74 | 84 | 1,1 |
| code-reviewer | 62 | 123 | 2,0 |
| **Total** | **678** | **1 083** | **1,6** |

**Le verdict ne repose pas sur le recouvrement lexical, et c'est délibéré.** J'ai construit un détecteur de recouvrement description↔corps ; il s'est révélé **aveugle** au calibrage. Exhibés à la main, un positif connu (`security-reviewer` : « Review PR contenant des changements dans `*Security*`, `*Auth*`, `crypto*`, `.env*` » — activation par glob de fichiers, absente de la description) et un négatif connu (`code-reviewer` : « "review ce code", "relis ce fichier", "valide cette PR" », dont la description porte littéralement `"review"`, `"relire"`, `"valide ce code"`) rendent **tous deux 0,50** de couverture. Le sac-de-mots bute sur la variation morphologique (`relis`/`relire`, `évaluer`/`évaluation`). Comptage abandonné : un instrument non calibré ne distingue pas l'absence du défaut de son incapacité à le voir.

**Ce qui fonde le verdict est temporel, et ne demande aucun comptage** : le `description` est la surface que le harnais lit pour **router**. Le corps se charge **après** que la décision d'activer est prise. Donc `## Quand t'activer`, quel que soit son contenu, arrive dans un contexte qui a déjà tranché ce qu'il prétend trancher. Il ne peut pas informer sa propre décision. C1 : l'information existe, elle vit dans la seule couche qui agit.

**Réserve honnête, portant sur la moitié du bloc** : `**Ne pas s'activer pour :**` n'a *pas* le même sort. Lu après chargement, il garde une fonction vivante — le désengagement en vol (« je suis chargé, mais je vois qu'il faut rediriger vers `code-reviewer` »). Il ne sort donc pas en C1 mais en **C4**, et c'est un doublon **volatil**, pas statique.

**Preuve de divergence déjà survenue** — 2/9, mesurée par comparaison des noms de frères cités dans chaque copie :

| Skill | Frère cité par le corps, absent de la clause `NE PAS` du frontmatter |
|---|---|
| `database-expert` | `code-reviewer` (corps l.33 : « Review de code Java/TypeScript ») |
| `ai-engineering` | `security-reviewer` (corps l.37 : « Vulnérabilités / OWASP ») |

Les deux vérifiés à la main dans les descriptions. La divergence va dans le mauvais sens : **le corps connaît une collision que la surface de routage ignore**, donc le routage ne peut pas la prévenir. C'est exactement le doublon volatil que C4 décrit — deux copies qui divergent au premier edit, et l'edit a déjà eu lieu.

### M7 — les 40 négations de `## Règles strictes`

Forme homogène sur les 40 : **négation + « à la place » + pourquoi**. La forme est conforme à la source normative de la grille (l.224, « dire quoi faire plutôt que quoi éviter ») et survit C7 : impératif + pourquoi en une ligne, aucune quatrième part.

Sortent de la cascade, **en C1** — savoir de manuel qu'un modèle applique sans qu'on le lui dise :

| Skill | Instruction | Pourquoi C1 |
|---|---|---|
| security-reviewer | « ne jamais suggérer de rouler son propre crypto » | consigne canonique, aucun modèle actuel ne recommande l'inverse |
| devops-expert | « ne jamais `latest` comme tag en prod » | idem, et déjà dans `references/kubernetes.md` **et** `references/cicd.md` → aussi C4 |
| devops-expert | « ne jamais lancer des containers en root » | idem, et déjà dans `references/docker.md` → aussi C4 |
| devops-expert | « ne jamais déployer sans health check » | idem, et déjà dans `references/kubernetes.md` → aussi C4 |
| devops-expert | « ne jamais mettre un secret dans un Dockerfile » | idem, et déjà dans `references/docker.md` + `cicd.md` → aussi C4 |
| frontend-expert | « ne jamais l'index comme clé de liste » | idiome React de base |

*Base : jugé sur pièce.* Le test C1 de la grille (sonder un contexte neuf, < 3 appels d'outil) **n'a pas été joué** — il demande un sous-agent, hors de ce qui m'était autorisé cette session. Les six verdicts ci-dessus sont donc à confirmer par sondage, et je les marque tels quels plutôt que de les présenter comme mesurés. À noter que les quatre de `devops-expert` sont **aussi** des C4 mesurés, eux : la référence du même skill porte déjà la consigne.

Survivent et méritent leur place — le gotcha non évident, celui qui achète un comportement :

- `database-expert` : « ne jamais créer un index sans `CONCURRENTLY` » (le lock TABLE est le piège que l'on oublie), « ne jamais diagnostiquer une perf sans EXPLAIN ANALYZE ».
- `backend-architect` : « ne jamais rendre une recommandation confiante quand aucune contrainte n'a été fournie », dont le pourquoi porte une précision qui ne se déduit pas — « remplir *Contexte assumé* après coup ne rachète pas un verdict déjà rendu ».
- `ai-engineering` : « ne jamais asserter l'égalité exacte d'un output LLM », « ne jamais valider une feature LLM parce que "ça a marché 3 fois" ».
- `brain-expert` : « ne jamais conclure avant de connaître la population visée », qui porte le mécanisme (« un raccourci qui sauve l'expert piège le novice »).

**Une seule sort en C3** : `security-reviewer`, « ne jamais crier au loup sur un POC interne sans risque réel ». Aucune condition de violation observable — « crier au loup » et « risque réel » sont tous deux à l'appréciation de celui qu'on juge. Niveau 4 du gradient. **Action** : reformuler en niveau 3, ou l'adosser au contrôle de sortie qui existe déjà (« chaque entrée critical cite son vecteur d'exploitation ») — lequel *est* la version falsifiable de la même intention.

### M8 — les blocs de savoir inline : 4 doublons mesurés

**D1 — le Cartesian check, en 4 copies dans cette passe et déjà présent en contexte permanent.**

| Emplacement | Mots |
|---|---|
| `rules/reasoning.md:52` — **contexte permanent, hérité des sous-agents** | (règle source) |
| `backend-architect/SKILL.md:51` | 50 |
| `frontend-expert/SKILL.md:49` | 50 |
| `agentic-architect/SKILL.md:100` | 49 |
| `database-expert/SKILL.md:49` | 45 |
| `_shared/llm-decision-grid.md` — « Red flag : … cohérent avec le reste → refaire l'analyse hors-contexte » | (6ᵉ formulation) |
| `aidd-pilot/SKILL.md` — 7ᵉ occurrence, **hors périmètre**, capturée | — |

Les 4 copies du périmètre reformulent la règle permanente, red flag « cohérence avec le reste » compris. **194 mots** qui redisent ce qui est déjà chargé dans chaque session. C4 : éliminer, ne pas hiérarchiser. Les 4 skills se contentent d'un pointeur — ou de rien, la règle étant permanente.

**D2 — `agentic-architect` pointe vers la référence partagée *et* réinline son contenu.** Ligne 43 : « Charge `../_shared/llm-decision-grid.md` : la décision déterministe / LLM borné / agent ». Lignes 47-56 : une table « Déterministe vs Probabiliste » sur la même décision, avec des axes **différents** de ceux de la grille partagée (la grille classe par *qui contrôle le flow*, la table inline par *critère de comportement*). Deux réponses à une même question dans un même fichier. C4 volatile, et le divergence est déjà là. **Action** : la table inline sort, le pointeur suffit — c'est le motif R6 que `skill-craft` prescrit déjà.

**D3 — le plafond de 300 mots, en 3 copies + 1 gabarit.** `code-reviewer:76`, `frontend-expert:75`, `backend-architect:74`, plus `code-reviewer/assets/review-template.md:49`. Trois formulations différentes du même seuil. Doublon **statique** (un chiffre ne dérive pas), donc bénin au sens de la grille — mais les trois libellés diffèrent déjà (« 300 mots de commentaire général » / « 300 mots » / « ~300 mots de prose »). À unifier au passage, pas un chantier en soi.

**D4 — la phrase « une section sans contenu se déclare vide (« Aucun ») »**, verbatim dans 5 `## Contrôle de sortie` (`security-reviewer`, `code-reviewer`, `frontend-expert`, `database-expert`, `backend-architect`). Elle appartient au gabarit qu'elle décrit, pas aux 5 skills. **Action** : la porter une fois dans chaque `assets/*-template.md`, la retirer des 5 corps.

### M8 (suite) — C1 sur les 19 références : aucune ne porte d'ancrage repo

Mesure exhaustive sur les 19 fichiers de `references/` du périmètre :

```
grep -cE '(\.\./|rules/|aidd_docs/|skills/|agent-config|Winggy|invoice-extractor)'
→ 0 sur 19/19
```

**Aucune des 19 références n'encode une décision projet, un chemin local ou une convention maison.** Ce sont 6 252 mots de savoir public reformulé — OWASP Top 10, Web Vitals, checklist a11y, anti-patterns K8s, multi-stage Docker, les 3 piliers de l'observabilité.

Ce constat ne prescrit pas leur suppression : la table C1 distingue « inférable, coût faible → supprimer » de « inférable, coût élevé, info stable → synthèse courte ». Une checklist curée a une valeur de rappel systématique qu'un modèle ne produit pas spontanément. Mais il place **les 19 en C1**, et il tranche le sous-cas volatile :

| Référence | Assertions périssables | Verdict C1 |
|---|---|---|
| `security-reviewer/references/owasp-2021.md` | 6 | **Info volatile → pointeur.** Le bloc « Algos recommandés (**2026**) » (`bcrypt cost ≥ 12`, `RSA-2048+`) est daté par construction et pourrit sans que rien ne le signale |
| `frontend-expert/references/a11y-checklist.md` | 3 | idem, à vérifier au cas par cas |
| `devops-expert/references/docker.md` | 2 | `node:20-alpine` — version épinglée dans un exemple |
| les 16 autres | 0 | **Info stable → synthèse courte** admissible ; à trancher par sondage C1 |

*Base : mesuré pour le comptage, jugé sur pièce pour le classement stable/volatile.*

### M10 — C3 : niveau 2 atteint sur les 9, et plafonné là

`ls skills/<skill>/evals/` → les 9 portent un `evals/eval.json`. Verdict mécanique : **niveau 2 du gradient** sur les 9.

Le contenu, lui, plafonne le niveau atteint :

| Skill | Scénarios | `trigger_markers` | `files` | `forbidden_tools` |
|---|---|---|---|---|
| security-reviewer | 1 | ✅ | ✅ | ✗ |
| code-reviewer | 1 | ✅ | ✅ | ✗ |
| frontend-expert | 1 | ✅ | ✅ | ✗ |
| database-expert | 1 | ✅ | ✗ | ✗ |
| backend-architect | 1 | ✅ | ✗ | ✗ |
| brain-expert | 1 | ✅ | ✗ | ✗ |
| agentic-architect | 1 | ✅ | ✗ | ✗ |
| devops-expert | 1 | ✅ | ✗ | ✗ |
| ai-engineering | 1 | ✅ | ✗ | ✗ |

**Un scénario par skill, les 9 positifs.** L'angle mort que la grille nomme explicitement (l.63 — « un scénario qui vérifie que le skill part ne vérifie pas qu'il ne part pas à tort ») couvre donc **100 % du corpus**, sans exception.

Et il tombe exactement sur le défaut que cette passe mesure par ailleurs : les redirections de M3 (« ne pas s'activer pour → frère ») sont **la moitié non falsifiée du contrat**, et c'est celle où la divergence de 2/9 s'est déjà produite. Les deux constats se tiennent : rien ne teste la clause que rien n'empêche de dériver.

Second angle mort, celui du faux négatif d'instrument : `devops-expert` **est** le cas mesuré le 2026-08-06 (marqueurs absents, comportement intégralement vert sur trois critères, gabarit à quatre champs libres). Son verdict de déclenchement ne doit pas se lire comme un non-déclenchement.

**Ce que les 9 `## Test` promettent, et qui n'est pas tenu.** Les 9 annoncent un cas précis — « ils portent les cas où le skill doit ne rien trouver », « où le skill doit refuser de conclure », « où le framework n'est pas déterminable ». Avec un seul scénario chacun, cette promesse est au mieux à moitié tenue. Le libellé de `## Test` décrit l'intention de conception, pas le contenu de `evals/eval.json`. **Action** : soit le scénario négatif existe, soit le `## Test` cesse de l'annoncer.

### M1 — C7 : le prénom des personas

`## Rôle` porte une identité nommée dans 5 des 9 : Riley (security), Sam (code), Jordan (frontend), Morgan (database), Alex (backend). Les 4 autres (`brain-expert`, `agentic-architect`, `devops-expert`, `ai-engineering`) ouvrent sur « Tu es un expert en… » sans prénom.

C7, cas « impératif plus court que le décoratif » : le prénom n'achète aucun comportement observable, et **l'incohérence 5/4 est un défaut C8 de groupe** — le moule prescrit une case que la moitié du corpus remplit. Le reste de `## Rôle` (la posture : « Pragmatique, orienté risques, empathique ») survit : elle calibre le ton, qui est un comportement.

**Action** : trancher dans un sens ou l'autre, et le porter dans la convention `skill-craft` pour que le 10ᵉ expert n'ait pas à re-trancher. *Base : jugé sur pièce — le test C7 (retirer la part, comparer le comportement d'un contexte neuf) n'a pas été joué.*

---

## Cohérence par fichier — C8

| Fichier | Verdict | Détail |
|---|---|---|
| `security-reviewer/SKILL.md` | **1 défaut** | La négation « ne jamais crier au loup » (C3 niveau 4) et le contrôle de sortie « chaque critical cite son vecteur » prescrivent la même chose, l'une invérifiable, l'autre falsifiable. Redondance interne → fusionner sur la falsifiable |
| `code-reviewer/SKILL.md` | **1 défaut** | Le plafond de 300 mots est dans le corps **et** dans `assets/review-template.md`, en deux libellés |
| `frontend-expert/SKILL.md` | cohérent | — |
| `database-expert/SKILL.md` | **1 défaut** | Corps et description ne citent pas les mêmes frères (`code-reviewer` manquant côté description) |
| `backend-architect/SKILL.md` | cohérent | Le seul dont `## Avant` cite une règle du repo (`../../rules/back-spring.md`) — et il précise le régime de chargement. Modèle à suivre |
| `brain-expert/SKILL.md` | **1 défaut** | `## Les 6 domaines cognitifs` (~330 mots inline) est le seul bloc de savoir de cette taille laissé dans un `SKILL.md` alors que 8 skills sur 9 sortent le leur en `references/`. Orpheline de forme, pas de fond |
| `agentic-architect/SKILL.md` | **2 défauts** | D2 (pointeur + contenu réinliné, axes divergents) ; et `## Les 4 décisions clés` (~430 mots) même défaut de forme que `brain-expert` |
| `devops-expert/SKILL.md` | **1 défaut** | Les 4 négations de `## Règles strictes` sont toutes déjà dans ses propres `references/` — le fichier se contredit sur son propre principe l.44 (« Charger la référence du domaine concerné — inutile de lire les autres ») en remontant leur contenu au niveau toujours-chargé |
| `ai-engineering/SKILL.md` | **2 défauts** | Corps et description divergent sur les frères (`security-reviewer`) ; et c'est le seul des 9 **sans aucune `references/`** — 1 108 mots dont `## Les décisions clés` (~450) tout inline, alors que le moule prescrit la sortie en référence |

---

## Captures hors grille

Notées, **non creusées**.

1. `aidd-pilot/SKILL.md` porte une 7ᵉ formulation du Cartesian check. Hors périmètre (passe C).
2. `security-reviewer/references/owasp-2021.md:62` déclare A06 « hors périmètre du skill » — une référence qui exclut une part d'elle-même. Question de conception, pas de grille.
3. Les `assets/*-template.md` (1 009 mots, 5 fichiers) n'ont été jugés que par ricochet (D4). Ils méritent leur propre crible : ce sont des gabarits injectés, régime différent d'une référence lue.
4. `_shared/llm-decision-grid.md` est cité par 2 experts avec un chemin relatif `../_shared/`. Aucun mécanisme ne vérifie que ce chemin résout depuis l'emplacement monté du skill.
5. `ai-engineering/SKILL.md:117` — « Panorama vérifié sur 9 sources » sans les nommer. Une traçabilité qui ne trace rien ; C3 hors du périmètre des instructions (c'est une section `## Sources`).

---

## À réviser entre deux audits

1. **Le test C1 de la grille est inapplicable en pratique cette session.** Il prescrit un sondage sous-agent ; la consigne de session l'interdisait. Résultat : 6 verdicts C1 marqués « jugé sur pièce » là où la grille attend « mesuré ». La grille devrait prévoir le repli explicitement — soit un critère sur pièce recevable et nommé, soit l'obligation de rendre ces instructions « non jugées » plutôt que jugées faiblement. En l'état, le protocole pousse au verdict faible sans le dire.

2. **C4 ne dit pas quoi faire d'un doublon dont les deux copies agissent à des moments différents.** M3 en est le cas : la clause du frontmatter agit au routage, celle du corps agit en vol. « Une instruction dupliquée s'élimine » ne tranche pas — éliminer laquelle ? La grille gagnerait la distinction *doublon de contenu à fonction unique* (éliminer) vs *à fonctions distinctes* (garder les deux, dériver l'une de l'autre, et le rendre vérifiable).

3. **C8 devrait porter un cas « défaut de groupe ».** Le prénom présent dans 5 corps sur 9, et la sortie en `references/` faite par 8 sur 9, sont des incohérences réelles qui ne vivent dans **aucun** fichier — elles vivent entre les fichiers d'un même moule. C8 se rend par fichier, C4 cherche des doublons : ni l'un ni l'autre n'attrape l'application partielle d'un moule. Cette passe a dû les rendre hors table.

4. **Le seuil C7 « contrat de routage ~130 mots » ne s'applique pas ici, et la grille ne le dit pas.** Les instructions de corps ne sont pas des contrats de routage ; le seuil de 60 mots (instruction rédigée) s'applique. Aucune des 40 négations ne le dépasse. Mais la table de la grille (l.142-145) laisse le lecteur choisir sa ligne : elle devrait dire que la nature se lit de l'**emplacement** (frontmatter = routage, corps = rédigée), pas du contenu.

5. **Aucun critère ne juge un `## Test` qui promet plus que son `evals/` ne contient.** Les 9 annoncent un scénario négatif ; les 9 n'en ont aucun. C3 valide la présence du fichier, C8 ne compare pas un fichier à son voisin. Le défaut est réel, mesuré, et sorti de la cascade par le bas.

---

## Report vers les chantiers de la note de cadrage

`0_INBOX/2026-08-10-cadrage-refonte-skills.md`, chantiers 0-8. Aucun plan parallèle créé.

| Chantier | Ce que la passe B y verse |
|---|---|
| **1 — bugs** | `database-expert` et `ai-engineering` : ajouter le frère manquant à la clause `NE PAS` de la description (`code-reviewer`, `security-reviewer`). Livrable immédiatement, indépendant de tout verdict |
| **Nouveau — dédoublonnage** | Retirer les 4 copies du Cartesian check (194 mots) ; sortir la table inline de `agentic-architect` (D2) ; unifier le plafond 300 mots (D3) ; déplacer la phrase « section vide » dans les 5 gabarits (D4) |
| **Nouveau — le moule** | Supprimer `## Quand t'activer` des 9 (1 083 mots) ; trancher `**Ne pas s'activer pour :**` — une copie, dérivée de l'autre ; trancher le prénom 5/9 ; sortir en `references/` les blocs inline de `brain-expert`, `agentic-architect`, `ai-engineering` |
| **Nouveau — évals** | Un scénario négatif par expert (9), ou retirer la promesse des 9 `## Test`. C'est le jalon « aucun scénario négatif » du plan de campagne, qui cesse d'être une hypothèse : il est mesuré sur 9/9 |
| **Chantier `skill-craft`** | Le moule des experts n'est décrit nulle part dans la convention. Les 9 l'appliquent, 5 le remplissent à moitié (prénom), 1 le contredit (`ai-engineering` sans `references/`). À écrire à la réécriture post-passe D, pas avant |
| **8 — renommage** | Inchangé, reste dernier |

**Ce qui ne descend pas dans la refonte** : les 19 références placées en C1. Leur sort demande le sondage qui n'a pas été joué, et supprimer 6 252 mots de savoir curé sur un verdict « jugé sur pièce » serait exactement l'erreur que la grille interdit.

---

## Relevé de contrôle — C6, hors périmètre

Lancé pour vérifier que la passe n'a rien déplacé dans le permanent :

- Règles + output style : **4 869 mots** (inchangé depuis `cf5877a`)
- Descriptions de skills : **2 206 mots** (inchangé — les descriptions n'ont pas été touchées)
- Total permanent : **7 075 mots**

Aucun verdict C6 rendu : les 16 260 mots de cette passe ne se chargent qu'à l'invocation.

**Effet attendu de la refonte sur C6** : nul. Les 1 083 mots de `## Quand t'activer` ne sont pas du permanent. Le gain est un gain de **contexte à l'invocation** et de cohérence, pas de budget de session. À dire, sinon le chiffre sera lu comme une économie qu'il n'est pas.
