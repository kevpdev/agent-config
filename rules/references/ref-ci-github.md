# Références — contrat CI GitHub

La fiche complète derrière la section « CI GitHub » de `rules/aidd.md`. Jamais chargée automatiquement : la règle garde le déclencheur, cette page porte le contrat et sa preuve. Capitalisée le 2026-10-08 depuis `kevpdev/yt-transcriber` (issue #40), puis appliquée à `kevpdev/swapi`.

---

## Le contrat en une page

Trois jobs, dont le nom ne dépend jamais de la stack. Le nom d'un job est le contexte que le ruleset exige, donc un nom qui cite un outil (`check (ruff, pyright, pytest)`) oblige à réécrire le ruleset à chaque changement d'outil.

| Job | Rôle | Obligatoire |
|---|---|---|
| `check` | format, lint, types, tests unitaires. Un seul job, chaque outil est une étape ou un groupe de logs (`::group::`) | toujours |
| `security` | scan de dépendances (Trivy). Rien d'autre dans ce job | toujours |
| `e2e` | tests navigateur sur l'application réelle ou simulée | seulement si le dépôt porte un dossier `e2e/` |

Hors de ces trois noms, un workflow peut exister mais le ruleset ne l'exige pas. C'est le cas de `codeql.yml`.

## Règles de forme

- **Actions épinglées par SHA** de 40 caractères (`uses: actions/checkout@<sha> # v7.0.1`). Un tag ou une branche se déplace sans qu'on le voie. Le tag en commentaire sert à Dependabot et au lecteur, le script ne le contrôle pas.
- **Permissions minimales** : un bloc `permissions:` en tête de chaque workflow, qui ne contient que `read` ou `none`. Une permission d'écriture se pose sur le job qui en a besoin, jamais en tête.
- **Dependabot** sur l'écosystème `github-actions`, avec l'écosystème du langage en plus. Sans lui, les SHA épinglés ne montent jamais.
- **Maven : Failsafe pour les `*IT`.** Surefire (actif par défaut) ne lance que `*Test`, `*Tests` et leurs voisins. Une classe `FooIT` est ignorée sans erreur tant que `maven-failsafe-plugin` n'est pas déclaré dans le `pom.xml`, donc `verify` reste vert sans l'avoir lancée (mesuré le 2026-10-08 sur `swapi`). Avec le parent Spring Boot, la déclaration seule suffit : sa version et ses exécutions sont déjà gérées. Le script de conformité refuse un dépôt qui a des `*IT` sans Failsafe.
- **`check.sh` ou équivalent** : un script versionné que la CI et le poste local lancent à l'identique. Le workflow n'a pas d'autre logique que de l'appeler.

## Ce que `check` doit couvrir

Le job `check` ne se limite pas à compiler et lancer les tests. Il couvre le format, le lint, l'analyse statique et un seuil de couverture, du plus déterministe au plus lent, et s'arrête au premier échec. Le script de conformité ne le mesure pas, il ne lit que les workflows.

**Recette Maven** (appliquée à `kevpdev/swapi` le 2026-10-08, tout lié à `verify`, donc `sh ./mvnw -B verify` suffit en CI) :

| Phase | Plugin | Rôle |
|---|---|---|
| `validate` | Spotless (`googleJavaFormat`) | format |
| `validate` | Checkstyle (`google_checks.xml`) | style, avec un fichier de suppressions pour ce que le projet refuse |
| `process-classes` | PMD | mauvaises pratiques |
| `process-classes` | SpotBugs | bugs probables dans le bytecode |
| `verify` | JaCoCo (`report` puis `check`) | couverture, seuil fixé sur la valeur **mesurée** arrondie vers le bas |

- Le seuil JaCoCo ne se pose pas au hasard. Sur `swapi` la couverture de lignes mesurée était de 43 %, le seuil est de 40 %.
- Reformater tout le code avec Spotless se fait dans un commit à part, avant d'activer `check`.
- Un outil qui rend zéro violation ne prouve rien tant qu'il n'a pas détecté une violation plantée. PMD a été calibré ainsi sur `swapi` (un champ privé inutilisé et un `catch` vide détectés).
- Les règles Javadoc de `google_checks.xml` (49 des 103 premières violations de `swapi`) se suppriment par `suppressionsLocation`, le reste se corrige.

## CodeQL

- `codeql.yml` à part, un job par langage, **non requis** par le ruleset tant que sa stabilité n'est pas mesurée.
- Gratuit en dépôt public. En dépôt privé il demande GitHub Code Security (doc GitHub, vérifié le 2026-10-07).
- Langages : ceux du dépôt, plus `actions` pour analyser les workflows eux-mêmes.

## Ce que le contrat ne couvre pas

- Les workflows partagés entre dépôts : les comptes perso et pro sont séparés.
- Les templates copiés par stack.
- Le déploiement. Il s'ajoutera plus tard dans un workflow séparé (par exemple `deploy.yml`), déclenché après la fusion et non sur une pull request.

## Mesurer et appliquer

| Geste | Commande |
|---|---|
| Mesurer qu'un dépôt respecte le contrat | `python3 wrappers/claude/scripts/check-ci-contract.py <dépôt>` |
| Poser le ruleset (trois contextes, `e2e` en option) | `bash wrappers/claude/scripts/apply-ci-ruleset.sh <owner/repo> [--e2e] [--dry-run]` |
| Calibrer le script de conformité | `python3 wrappers/claude/scripts/tests/test-check-ci-contract.py` |

Le script rend 0 si le dépôt est conforme, 1 s'il mesure un écart (une ligne par écart, `fichier:ligne`), 2 s'il ne peut pas conclure.

## L'ordre pour changer des noms de job

Les noms de job sont aussi les contextes du ruleset. Pour renommer sans bloquer la pull request qui renomme, on pousse d'abord les nouveaux noms, on attend qu'ils aient rapporté sur la PR, puis on applique le ruleset, puis on fusionne. Appliquer le ruleset avant que les nouveaux noms aient rapporté bloque la fusion sur des contextes qui n'existent pas encore.

## Premier Trivy rouge sur un dépôt repris

Un dépôt ancien sort souvent rouge à son premier scan : des CVE connues dans des dépendances jamais montées. Deux sorties, à choisir CVE par CVE : monter la dépendance, ou ignorer la CVE avec la raison écrite dans la PR. Le contrat ne demande pas un dépôt sans CVE, il demande qu'aucune ne soit ignorée en silence.
