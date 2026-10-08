# Références — contrat CI GitHub

La fiche complète derrière la section « CI GitHub » de `rules/aidd.md`. Jamais chargée automatiquement : la règle garde le déclencheur, cette page porte le contrat et sa preuve. Capitalisée le 2026-10-08 depuis `kevpdev/yt-transcriber` (issue #40), puis appliquée à `kevpdev/swapi`.

---

## Le contrat en une page

Le ruleset n'exige qu'**un** check : la porte `ci`. Elle attend tous les autres jobs de son workflow et échoue si l'un d'eux n'a pas réussi. Le reste se découpe au grain de la stack.

| Couche | Contenu |
|---|---|
| **Imposé partout** | la porte `ci`, Trivy dans le même workflow qu'elle, actions épinglées par SHA, permissions minimales, Dependabot |
| **Couvert, sans forme imposée** | format, lint, analyse statique, tous les niveaux de tests que le dépôt possède (unitaires, intégration, e2e), couverture avec seuil mesuré |
| **Libre, au grain de la stack** | le nombre de jobs et leur découpage. Maven peut garder un seul job `verify`, Node ou Gradle peuvent séparer `lint`, `unit-tests`, `build`, `e2e`. |

**Nommer un job par ce qu'il vérifie** (`lint`, `unit-tests`, `integration-tests`, `e2e`, `security`, `build`), jamais par l'outil (`ruff`, `pytest`). **Ne pas découper contre le grain de l'outil** : séparer des étapes que la stack enchaîne (le cycle de vie cumulatif de Maven) fait recompiler chaque job.

La porte, sous une forme minimale (validée le 2026-10-08 sur `yt-transcriber` : un test cassé rend `unit-tests` et `ci` rouges et la PR `BLOCKED`, kevpdev/yt-transcriber#45) :

```yaml
  ci:
    if: always()
    needs: [lint, unit-tests, security]   # tous les autres jobs du workflow
    runs-on: ubuntu-24.04
    steps:
      - run: test "${{ contains(needs.*.result, 'failure') || contains(needs.*.result, 'cancelled') }}" = false
```

- **`if: always()`** : GitHub compte un job sauté comme réussi. Sans lui, la porte est sautée dès qu'un job qu'elle attend échoue, et la fusion passe ([doc GitHub](https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/troubleshooting-required-status-checks)).
- **`needs` complet** : un job oublié dans `needs` ne bloque plus rien.
- **Trivy dans le même workflow** : `needs` ne voit que les jobs de son workflow.

Hors de la porte, un workflow peut exister sans être exigé. C'est le cas de `codeql.yml`.

**POURQUOI**, décidé le 2026-10-08 (issue `agent-config#8`) : les noms fixes `check`, `security`, `e2e` ne disaient pas ce qu'ils vérifiaient et imposaient le même découpage à toutes les stacks. La porte rend les noms libres, comme le « Pipelines must succeed » de GitLab, et réduit le ruleset à un nom.

## Règles de forme

- **Actions épinglées par SHA** de 40 caractères (`uses: actions/checkout@<sha> # v7.0.1`). Un tag ou une branche se déplace sans qu'on le voie. Le tag en commentaire sert à Dependabot et au lecteur, le script ne le contrôle pas.
- **Permissions minimales** : un bloc `permissions:` en tête de chaque workflow, qui ne contient que `read` ou `none`. Une permission d'écriture se pose sur le job qui en a besoin, jamais en tête.
- **Dependabot** sur l'écosystème `github-actions`, avec l'écosystème du langage en plus. Sans lui, les SHA épinglés ne montent jamais.
- **Maven : Failsafe pour les `*IT`.** Surefire (actif par défaut) ne lance que `*Test`, `*Tests` et leurs voisins. Une classe `FooIT` est ignorée sans erreur tant que `maven-failsafe-plugin` n'est pas déclaré dans le `pom.xml`, donc `verify` reste vert sans l'avoir lancée (mesuré le 2026-10-08 sur `swapi`). Avec le parent Spring Boot, la déclaration seule suffit : sa version et ses exécutions sont déjà gérées. Le script de conformité refuse un dépôt qui a des `*IT` sans Failsafe.
- **Parité locale** : un script versionné (`check.sh`, `mvnw verify`, `pnpm` script) enchaîne en local les mêmes étapes que les jobs. Un job n'a pas d'autre logique que d'en appeler une.

## Ce que la CI doit couvrir

La CI ne se limite pas à compiler et lancer les tests. Elle couvre quatre catégories, du plus déterministe au plus lent : **format, lint, analyse statique, couverture avec seuil**. Le script de conformité ne le mesure pas, il ne lit que les workflows.

**Ces quatre catégories valent pour tout langage. Les outils, non.** Avant d'appliquer une recette, constater le langage réel du dépôt (`src/main/java`, `src/main/kotlin`, `*.kt`, `pyproject.toml`). Si la ligne du langage est marquée « non mesuré », garder les quatre catégories, choisir l'outil équivalent, calibrer chaque outil par une violation plantée et écrire « non mesuré » dans la PR. Ne jamais recopier la table d'un autre langage.

| Stack | Statut | Outils |
|---|---|---|
| Python | mesuré (`yt-transcriber`) | ruff format, ruff check, pyright, pytest avec seuil de couverture, dans `scripts/check.sh` |
| Java + Maven | mesuré le 2026-10-08 (`swapi`) | table ci-dessous |
| Kotlin + Maven | **non mesuré** | pistes : Spotless avec `ktlint` ou `ktfmt` pour le format, detekt pour lint et analyse statique, JaCoCo inchangé. Checkstyle, PMD et SpotBugs ne lisent pas Kotlin. Les coordonnées Maven officielles de detekt ne sont pas vérifiées. |
| Node / TypeScript (backend) | mesuré le 2026-10-08 (`newsletter-automation`, pnpm) | jobs parallèles `lint` (Prettier `--check`, ESLint, `tsc --noEmit`), `unit-tests` (Vitest et `@vitest/coverage-v8`, `coverage.include` sur tout `src/` sinon seuls les fichiers importés comptent : 92,85 % affichés pour 58,7 % réels), `build` (`tsc`), `security` (`pnpm audit --audit-level=high` puis Trivy). Découper paie ici : 29 s pour le job le plus long contre 58 s en un seul job (kevpdev/newsletter-automation#5), chaque `pnpm install` en cache coûtant quelques secondes. Le framework (Express, Fastify, NestJS) ne change pas ces outils. |

**Évaluer la version avant de garder ou de choisir un outil.** Un outil peut être compromis sans devenir mauvais, la version épinglée est ce qui compte.

1. Lire les avis de sécurité de l'outil (GitHub Advisories, OSV) et comparer la version épinglée aux versions touchées.
2. Si la version est touchée, passer à la première version saine, sans changer d'outil.
3. Ne chercher un remplaçant que si le dépôt est archivé, si aucune version saine n'existe, ou si l'outil n'est plus compatible avec le JDK ou le parent Maven du projet.
4. Après tout changement d'outil ou de version : recalibrer par une violation plantée et remesurer le seuil de couverture. Le contrat ne bouge pas, il tient aux quatre catégories et à la porte `ci`.

**POURQUOI**, constaté le 2026-10-08 : le 19 mars 2026, 76 des 77 tags de `trivy-action` ont été repointés et le binaire v0.69.4 publié avec un code malveillant (sources divergentes sur les plages exactes, vérifier l'avis GHSA-69fq-xp46-6x23). `swapi` et `yt-transcriber` épinglent `trivy-action` par SHA sur un commit du 2026-04-22 (v0.36.0), et le log d'un run montre le binaire v0.70.0, hors des versions citées. Le SHA protège d'un tag repointé, pas d'une version touchée.

**POURQUOI**, constaté le 2026-10-08 : la recette n'a été mesurée que sur un projet Java, et son titre « Maven » laissait croire à une portée générale.

**Recette Java + Maven** (appliquée à `kevpdev/swapi` le 2026-10-08, tout lié à `verify`, donc `sh ./mvnw -B verify` suffit, **en un seul job**) :

| Phase | Plugin | Rôle |
|---|---|---|
| `validate` | Spotless (`googleJavaFormat`) | format |
| `validate` | Checkstyle (`google_checks.xml`) | style, avec un fichier de suppressions pour ce que le projet refuse |
| `process-classes` | PMD | mauvaises pratiques |
| `process-classes` | SpotBugs | bugs probables dans le bytecode |
| `verify` | JaCoCo (`report` puis `check`) | couverture, seuil fixé sur la valeur **mesurée** arrondie vers le bas |

- **Un seul job, mesuré le 2026-10-08** (kevpdev/swapi#7) : découpé en `lint` (`process-classes`) et `unit-tests` (`verify` avec les analyseurs en `skip`), le job le plus long passe de 47 s à 58 s pour un run complet identique (72 s). Maven charge encore les plugins sautés, environ 14 s. Appeler les goals un par un pour l'éviter sort du cycle de vie et oublie en silence un plugin ajouté plus tard au `pom.xml`.
- Le seuil JaCoCo ne se pose pas au hasard. Sur `swapi` la couverture de lignes mesurée était de 43 %, le seuil est de 40 %.
- Reformater tout le code avec Spotless se fait dans un commit à part, avant d'activer la porte `ci`.
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
| Poser le ruleset (un seul contexte, `ci`) | `bash wrappers/claude/scripts/apply-ci-ruleset.sh <owner/repo> [--dry-run]` |
| Calibrer le script de conformité | `python3 wrappers/claude/scripts/tests/test-check-ci-contract.py` |

Le script rend 0 si le dépôt est conforme, 1 s'il mesure un écart (une ligne par écart, `fichier:ligne`), 2 s'il ne peut pas conclure.

## L'ordre pour passer à la porte

Le contexte `ci` doit avoir rapporté avant que le ruleset l'exige. On pousse d'abord la porte, on attend qu'elle ait rapporté sur la PR, puis on applique le ruleset, puis on fusionne. L'ordre inverse bloque la fusion sur un contexte qui n'existe pas encore, puisque le ruleset n'a aucun acteur de contournement.

Une fois la porte en place, renommer ou découper les autres jobs ne touche plus le ruleset.

## Premier Trivy rouge sur un dépôt repris

Un dépôt ancien sort souvent rouge à son premier scan : des CVE connues dans des dépendances jamais montées. Deux sorties, à choisir CVE par CVE : monter la dépendance, ou ignorer la CVE avec la raison écrite dans la PR. Le contrat ne demande pas un dépôt sans CVE, il demande qu'aucune ne soit ignorée en silence.
