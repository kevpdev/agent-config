# Testeur générique — ce qu'aidd-pilot en attend (interface)

aidd-pilot **invoque** (outil Skill → `test-runner`) **toujours** le skill `test-runner` pour la validation live/e2e — jamais en dérouler les étapes en bash inline (écart du 1er run). Pas d'adaptateur par projet à déclarer, pas de résolution, pas de question à l'humain en intake.

**Source de vérité = le skill `test-runner`** (skill voisin `test-runner`). Son comportement (découverte de la recette, déduction par finalité, garde-coût, hors-scope auth front) y vit et ne doit **pas** être recopié ici — juste consommé. Ce fichier ne fixe que l'interface sur laquelle aidd-pilot s'appuie.

## Pourquoi ce modèle

Une déclaration `test_adapter` en mémoire = bricolage, friction, casse l'autonomie. Un skill par projet (ex. dev-pilot) est trop large et collé à un projet. On veut un seul testeur spécialisé, réutilisable, qui **découvre**.

## Ce que le testeur NE fait pas (délégations — F3)

Il ne double aucun skill AIDD :

- **e2e / validation UI** → `dev:06-test:02-test-journey` (mesure pure : un screenshot par étape, jamais de correction). Le testeur fournit **l'URL** ; il ne conduit pas le navigateur, et l'outil de navigation est celui **configuré par le projet**. *Pas* `dev:03-assert` : sa facette frontend répare le code au lieu de le mesurer (cf. `actions/03-validate.md`).
- **réparation UI en boucle debug** → `dev:03-assert` (facette `03-assert-frontend` nommée explicitement, jamais le skill nu).
- **écrire des tests** → `dev:06-test`.
- **planifier** → `dev:01-plan`.

## Interface consommée par la ladder (`03-validate`)

```
discover()     → recette de run { startCmd, env[], readyUrl, testCommand, paidOps[], gaps[] }
start/status/stop → cycle de vie de l'app, idempotent
runTests(kind) → suite EXISTANTE (unit|integration), pass/fail + régressions
exerciseApi()  → curl live d'un endpoint réel
costGuard(op)  → confirmation côté parent avant une op payante
```

## Locus — qui exécute quoi

Règle : **parent** = décisions + ce qui parle à l'humain ; **subagent** = boulot borné qui rend un résultat.

| Op | Locus | Pourquoi |
|---|---|---|
| `start`/`status`/`stop` | **parent** si l'app doit persister dans une boucle debug ; sinon **subagent** one-shot | un process orphelin doit être tué explicitement |
| `runTests` / `exerciseApi` | **subagent** | borné, rend un rapport |
| e2e via `dev:06-test:02-test-journey` | **subagent** | le navigateur est tenu par le serveur MCP |
| `costGuard` | **parent** | un subagent ne peut pas demander une confirmation humaine |

- TODO: figer la signature exacte au 1er run réel du testeur.
