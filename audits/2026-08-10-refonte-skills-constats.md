# Constats — scan des 61 skills contre la source officielle (2026-08-10)

Annexe du cadrage porté par la note vault pro `0_INBOX/2026-08-10-cadrage-refonte-skills.md`. Référentiel : doc officielle Claude Code skills (code.claude.com/docs/en/skills) + best practices Anthropic (platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices), consultées le 2026-08-10.

Chaque constat cite `fichier:ligne` d'après la lecture du jour — à revérifier au moment de l'édition, le corpus bouge.

## Mesures mécaniques (script, vérifié)

- 61 skills : 26 `agent-config/skills/`, 22 `myvaultobsidian/.agents/skills/`, 13 `Obsidian perso/MyObsidianVault/.agents/skills/`.
- **Conformité totale sur les contraintes dures** : frontmatter valide (aucune clé inconnue), descriptions ≤ 954 caractères (limite 1024), corps ≤ 140 lignes (limite recommandée 500).
- **Frontmatter réduit à `name` + `description` sur les 61 skills.** Aucun usage de `disable-model-invocation`, `user-invocable`, `argument-hint`, `arguments`, `context: fork`, `allowed-tools`, `when_to_use`, `paths`. Un seul `$ARGUMENTS` dans tout le corpus (`myvaultobsidian/.agents/skills/convention-check`).
- 4 fichiers annexes > 100 lignes, tous sans table des matières (exigée par la doc officielle au-delà de 100 lignes) : `security-reviewer/references/fix-patterns.md` (203), `mr-review/references/controles-structurels.md` (141), `aidd-pilot/actions/02-pipeline.md` (105), `mr-review/references/glab-et-base-du-diff.md` (102).

## Référentiel officiel — ce que la doc exige/recommande

- `name` ≤ 64 car., minuscules/chiffres/tirets ; `description` non vide ≤ 1024 car., 3e personne, quoi + quand avec termes déclencheurs.
- Corps ≤ 500 lignes ; références à un seul niveau depuis SKILL.md ; TOC pour toute référence > 100 lignes ; fichiers annexes nommés par contenu.
- Workflows multi-étapes : étapes numérotées + checklist copiable ; boucle valider→corriger→répéter quand la qualité compte.
- Un défaut + échappatoire plutôt qu'un menu d'options ; terminologie unique ; zéro info périmable (ou en section « old patterns ») ; intent exécuter vs lire explicite pour chaque script.
- Champs Claude Code : `disable-model-invocation: true` pour les workflows à effets de bord déclenchés par l'humain (/commit, /deploy) ; `context: fork` (+ `agent`) pour les déroulés autonomes ; `argument-hint`/`$ARGUMENTS` pour les arguments ; `allowed-tools` pour pré-approuver les outils d'un tour.
- Évals : ≥ 3 scénarios par skill, construits avant la doc, testés sur les modèles réellement utilisés.

## Corpus agent-config (26 skills)

### Écarts par skill

- **agentic-architect** — persona + « Quand t'activer » (`SKILL.md:18-36`) recopie la description ; `:85-93` savoir générique ; candidat `context: fork`.
- **ai-engineering** — « Quand t'activer » (`:22-39`) duplique la description ; `:117` « panorama vérifié sur 9 sources » invérifiable, seuils chiffrés non sourcés (`:54-55`). Point fort : `:90` interdit les benchmarks mémorisés.
- **aidd-pilot** — info déjà fausse (`:14` « testeur générique à créer » alors que `test-runner` existe) ; citations verbatim des internals AIDD 2.x qui casseront (`actions/02-pipeline.md:64,88`) ; 3 termes pour la même brique ; annexe→annexe (`references/governor.md:18`, `references/test-runner.md:15`) ; les 4 actions sans `## Contrôle de sortie` ni `## Test` ; candidat fort `disable-model-invocation` (committe par phase) ; argument attendu non déclaré.
- **audit-harnais** — anecdotes datées dans le corps normatif (`SKILL.md:19`, `actions/02-cribler.md:17`) ; candidat `context: fork` ; `argument-hint` manquant (`rejoue sur <domaine>`).
- **backend-architect / brain-expert / code-reviewer / database-expert / devops-expert / frontend-expert / security-reviewer** — même pattern : persona nommé + « Quand t'activer » redondant avec la description ; blocs de savoir standard (brain-expert `:44-80`, database-expert `:70-106` dupliqué avec sa référence, frontend-expert `:79-85`).
  - code-reviewer : `references/testing.md` **orphelin** (jamais routé) ; candidat fork.
  - database-expert : point fort `:113` (« sans plan d'exécution, la section se titre Hypothèses »).
  - frontend-expert : versions figées `:51` (React 19, Next 15, Vue 3.5).
  - security-reviewer : `references/fix-patterns.md` 203 l. sans TOC ; OWASP millésime 2021 figé ; candidat fork.
- **doc-sync** — 2e personne dans la description (`:8-9`) ; critères sous `## Test` sans boucle de correction ; matrice à 4 axes ; candidat `disable-model-invocation`.
- **docs-check** — contradiction interne : « API HTTP Context7 v2 » (`:4,16`) vs « recherche web » (`:20`) ; « v2 » figé ; intent d'exécution flou sur `searchLibrary`/`getContext`.
- **fact-checker** — `assets/rapport-fact-check.md` atteignable seulement au 2e niveau ; pas de boucle de correction ; candidat fork.
- **memory-bootstrap** — 3 couplages périmables au plugin AIDD (`:21,27`, `actions/02-attach.md`) ; pas de boucle ; candidat `disable-model-invocation`.
- **mermaid-craft** — vraie boucle de correction (`:52`), mais auto-déclaration fausse : `SKILL.md:23` promet « ne pas redire » les deux non-négociables de `rules/mermaid.md`, or `:33` redit le `TD` et `:42` les redit tous les deux. Doublon statique (bénin au sens C4) ; à réaligner sur la clause `:23` pendant la refonte. *(mesuré le 2026-08-10, greps — constat issu de la passe d'audit sur `rules/mermaid.md`, hors scan doc officielle)*
- **mr-review** — 2 références > 100 l. sans TOC ; référence datée sur version d'outil (`glab 1.112`) ; candidat fork (post-scope) ; argument MR non déclaré.
- **skill-craft** — 1re personne dans la description (`:3`) ; annexe→annexe (`references/skill-authoring-fr.md:12,88` → `../actions/02-validate.md`) ; argument non déclaré.
- **test-runner** — les 3 actions sans anatomie, sans `## Contrôle de sortie` ni `## Test` ; « pour l'instant » gravé (`:38`).
- **vault-capture, vault-recap-raisonnement, vault-slides** — OK.
- **vault-capture-projet** — triple échappatoire au prompt de validation ; « Notes » redondantes (`:77-79`).
- **vault-load** — mode `<task-id>` sans `argument-hint`.
- **vault-log-session** — candidat `disable-model-invocation` (écrit dans le vault).
- **vault-save** — candidat `disable-model-invocation` **le plus net** : `git add -A` + commit + push, la description dit elle-même « à lancer délibérément ».

### Patterns du corpus

1. Redondance description ↔ corps sur les 9 « experts » (persona + « Quand t'activer ») : ~15-20 lignes payées deux fois, zéro contrainte de comportement.
2. Boucle de validation à deux vitesses : bonne en mono-fichier, absente d'aidd-pilot et test-runner, déclarative (sans correction) dans doc-sync / fact-checker / memory-bootstrap.
3. Péremption concentrée sur les couplages externes (plugins AIDD 2.x, hooks tiers, versions d'outils), pas sur la connaissance métier.
4. Deux annexes orphelines, trois chaînes annexe→annexe : disclosure bonne au 1er niveau, poreuse au 2e.

## Corpus vault pro (22 skills)

### Écarts par skill (saillants)

- **Références cassées ou non résolubles** : `doctor:24` nomme la racine `MyObsidianProVault/` (le vault s'appelle `myvaultobsidian/`) ; `product-framing:82` renvoie au namespace mort `/vaultx:save` ; `save:25` cite `commit-convention.md` qui vit dans agent-config, pas dans le vault ; `sync-to-template:34` chemin absolu vers un répertoire inexistant ; `journal:43-44` cite des « règles vault #2/#3 » jamais pointées ; `query:26-28` exclut `.claude`/`agent` alors que les skills vivent dans `.agents/`.
- **Prose déjà fausse** : `log-session:22` liste 4 sous-scripts de `regen-all.sh`, le script en lance 6 (`scripts/regen-all.sh:47-52`).
- **convention-check** — le corps affirme « fonctionne en fork » (`:15`) mais le frontmatter ne porte pas `context: fork` ; l'étape 7 corrige sans rejouer l'étage 1.
- **Candidats `disable-model-invocation`** : `save` (add -A + push), `sync-to-template` (commit dans un dépôt tiers), `archive`, `log-session`, `sync-refs-perso-to-pro`.
- **Candidats `context: fork`** : `doctor`, `review`, `sync-refs-perso-to-pro`, `sync-to-template`, `slides` (dont le corps décrit lui-même le besoin de délégation `:25`), `convention-check`.
- **`## Test` absent** de `load`, `lint`, `query`, `review`, `standup`, `doctor` — précisément les skills de lecture/synthèse.
- **stats** — OK.

### Patterns du corpus

1. Frontmatter amputé : ~12 skills documentent leurs arguments en `## Usage` au lieu d'`argument-hint`.
2. Collisions de déclencheurs non arbitrées : « daily » (journal ↔ standup), « recap » (log-session ↔ recap-raisonnement), « bilan sprint » (retro ↔ review).
3. Sections « Ce que le script fait » qui dupliquent le shell (archive, journal, new-project) — dérive déjà consommée sur log-session.
4. Racine du vault désignée de quatre manières (nom faux, chemin absolu en dur, `$OBSIDIAN_VAULT_PRO`, implicite).
5. Domaine diagnostic éclaté en quatre skills gigognes (`stats` ⊂ `lint` ⊂ `doctor`, + `convention-check`), tenus séparés par des `NE PAS` croisés.

## Corpus vault perso (13 skills)

### Écarts par skill (saillants)

- **capture-video** — liens cassés post-migration : `capture.md` et `triage.md` n'existent pas (cibles réelles `<dossier>/SKILL.md`) ; `CONVENTIONS-STYLE.md` vidé au profit de `.agents/rules/` ; table de destination dupliquée avec `triage` ; candidat fork net (ingère un transcript entier) ; candidat `disable-model-invocation` (supprime le fichier INBOX).
- **prime / save** — réimplémentent en prose ce que `scripts/prime.sh` et `scripts/save.sh` font déjà ; `save` porte une contradiction interne (« proposer un commit » vs « exécuter sans demander ») et est le candidat `disable-model-invocation` le plus évident du corpus.
- **archive** — double log (prose + script, libellés différents) ; candidat `disable-model-invocation` (mv irréversible).
- **triage** — renvoie vers une commande de traitement qui n'existe pas (`:105`) ; `evergreen` désigne à la fois un type et un statut ; candidats `disable-model-invocation` + fork.
- **clean / garden / query** — label « (script) » sur des `grep` inline : l'intent exécuter/lire n'est plus lisible.
- **stats** — OK.

### Patterns du corpus

1. Doublon SKILL.md ↔ `scripts/` (4 skills avec « Ce que le script fait »).
2. 8 skills sur 13 attendent un argument décrit en prose, zéro `argument-hint`.
3. Tables et seuils dupliqués (destinations IPCRA triage↔capture-video, seuil INBOX>5 prime↔lint, champs de tâche new-task↔template).
4. Garde-fous en prose (« Ne jamais… ») qui répètent les règles absolues d'`AGENTS.md` déjà en contexte permanent.

## Convention locale vs source officielle

`skill-craft/references/skill-authoring-fr.md` est déjà aligné sur l'essentiel (500 lignes, description quoi+quand 3e personne ≤ 1024, références à un niveau, un défaut + échappatoire). Ses trous vis-à-vis de l'officiel :

- Aucune couverture des champs frontmatter Claude Code (`disable-model-invocation`, `user-invocable`, `argument-hint`/`arguments`, `context: fork` + `agent`, `allowed-tools`, `when_to_use`, `paths`).
- Pas d'exigence de TOC pour les références > 100 lignes.
- Pas de pattern « checklist copiable + boucle valider→corriger » pour les workflows.
- Divergence **assumée** à confirmer : la convention refuse le gérondif que la doc recommande (choix délibéré, pas un écart).
- La convention elle-même viole R3 : elle renvoie vers `../actions/02-validate.md` (annexe→annexe).
