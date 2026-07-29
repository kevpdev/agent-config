# Changelog du framework AIDD

Ce que change chaque montée de version du marketplace [`ai-driven-dev/framework`](https://github.com/ai-driven-dev/framework), et ce que ça impose aux skills de ce repo.

**Ce fichier décrit des transitions, pas un état.** Il est vrai sur toutes les machines et pour toujours : « la 1.x nommait `implementer`, la 2.x nomme `executor` » ne périme jamais. Ce qui varie d'une machine à l'autre, c'est où elle en est dans la transition.

> **État installé sur *cette* machine** : `claude plugin list`. Ne jamais le recopier ici — une version écrite dans un fichier est fausse dès la mise à jour suivante, et personne ne la corrige.

**Le « pourquoi » des choix de nos skills n'est pas ici.** Il vit inline dans le skill qu'il justifie (`skills/aidd-pilot/actions/02-pipeline.md`, `03-validate.md`, `references/governor.md`). Ce fichier ne porte que le delta upstream.

Montée de version, sur une machine en retard :

```
claude plugin marketplace update aidd-framework
claude plugin update <plugin>@aidd-framework   # pour chacun
# puis redémarrer la session : les skills et agents ne sont pas rechargés à chaud
```

---

## 1.x → 2.x

*Constaté le 2026-07-29, en montant de `3f63ae2` (16/06) à `be83f25` (marketplace v5.5.6) — 131 commits.*

Transitions de version : `aidd-context` 1.1.2 → 2.4.1 · `aidd-dev` 1.2.1 → 2.3.1 · `aidd-vcs` 1.0.2 → 2.2.1 · `aidd-pm` 1.0.2 → 2.2.1 · `aidd-refine` 1.1.2 → 2.2.1.

### Renommages — cassants

| 1.x | 2.x |
| --- | --- |
| agents `implementer` / `reviewer` | `executor` (sonnet) / `checker` (opus) |
| agent `planner` | **supprimé**, sans équivalent — la planification revient à l'appelant |
| `aidd-context:02-project-init` | `aidd-context:02-project-memory` |
| `aidd-context:11-discovery` | `aidd-context:11-explore` |
| `aidd-pm:02-user-stories-create` | `aidd-pm:02-user-stories` |

### Layout des artefacts — fichiers plats → dossier de feature

```
1.x : aidd_docs/tasks/<yyyy_mm>/<yyyy_mm_dd>-<slug>.md          (+ -master, -part-N, -spec)
2.x : aidd_docs/tasks/<yyyy_mm>/<yyyy_mm_dd>_<slug>/
        plan.md  phase-1.md  phase-2.md  spec.md  review.md
```

Le séparateur après la date passe de `-` à `_`. La notion **master-plan / part-N disparaît** (`master-plan-template.md` et `tech-choice-template.md` supprimés, `phase-template.md` ajouté) : un plan = `plan.md` + N `phase-<n>.md` frères. Les plans plats hérités restent lisibles, mais hors convention.

**Le squelette de ces fichiers est apparié à l'identique** — frontmatter, valeurs de `status`, titres de section — par les templates (*« never add, rename, or reorder one »*) et par `05-review/assets/review-validator.yml` (*« Any other is invalid »*). Traduire un titre ou un statut casse l'appariement.

### Changements de comportement

**Boucle de dérive.** L'`executor` s'arrête sur tout écart avec le plan et remonte `replan needed: <raison>` sans jamais réécrire le plan. La soupape 1.x était l'inverse (*« amend the plan directly »*, marqué 🤖), qui rapiéçait la phase courante en laissant les suivantes périmées en silence. **Aucun skill ne consomme ce signal** : `00-sdlc/actions/03-implement.md` ne connaît que `implemented` et `blocked`. C'est à l'appelant de le traiter.

**`01-plan` n'a aucune action d'amendement** (ses 4 actions : `gather`, `explore`, `wireframe`, `plan`). Amender un plan en cours d'exécution est hors framework — une régénération écraserait les phases déjà `done`.

**`05-review` gagne un 3ᵉ axe** `review-relevancy` (`fit` / `conform` / `rot`), et lance **les trois par défaut**. Sortie disque obligatoire : un `review.md` unique par dossier de feature, **écrasé** à chaque run (pas d'historique). Sections fermées par un validator. Verdict = le plus strict des axes lancés, et un simple 🟡 warning suffit à interdire l'`approve`.

**`03-assert` répare, il ne mesure pas.** Sa facette `03-assert-frontend` applique des correctifs candidats en boucle (*« fix and re-run until they pass »*). Le thermomètre pur est `06-test:02-test-journey`, qui *« never silently fix or skip »* et rend un screenshot par étape. Il n'existe **aucune fonction d'enregistrement vidéo** dans le framework, seulement des captures.

**`00-sdlc` n'a aucune étape de test** (`spec | plan | implement | review | ship`) et le framework suppose l'app **déjà démarrée** : `03-assert-frontend` dit *« Never start or restart a server »*, `06-test:02-test-journey` dit *« Assume every server is already running »*. Personne n'y démarre l'app.

**`00-sdlc` garde le plan inline** — *« You own the plan: it is the contract the executor may not rewrite, so you write it, never a worker »* — et son mode par défaut s'inverse : `interactive` en 2.x, `auto` en 1.x.

**Hook `update_memory.js` (SessionStart)** : scanne désormais `aidd_docs/memory/` sur deux tiers — les `.md` racine en `@`-références auto-chargées, puis `internal/` et `external/` **récursivement**, listés en chemins nus « read on demand ». Les autres sous-dossiers ne sont pas scannés. Il fait un `git add` silencieux du fichier de contexte qu'il modifie.

**Supprimé en v5.0.0** : le système d'evals, l'auto-routing prompt→skill (les skills deviennent invoke-only), le `.mcp.json` livré.

### Nouveautés

Skills : `aidd-context:12-cook` (fiches recette, 4 actions `list`/`upsert`/`research`/`apply` + 5 recettes livrées) et `aidd-vcs:00-repo-init`. Tous deux absents de `aidd-context` 1.1.2 et `aidd-vcs` 1.0.2 — vérifié par `ls` du cache des deux versions. Plugins non installés par défaut : `aidd-orchestrator` (issues GitHub labellisées → PR), `aidd-ui` (embryon, un seul skill).

**`aidd-dev:10-todo` n'est pas une nouveauté** — il existait en 1.2.1, cette ligne le comptait à tort. Son delta 2.x est mineur : l'agent spawné passe de `implementer` à `executor`, et l'étape d'affinage se détend (la 1.x exigeait de découvrir un skill de refine, la 2.x accepte de reformuler inline, avec la consigne *« Never block on the user »*). Le principe est inchangé : un `executor` par todo en parallèle, aucune coordination entre eux, une table en sortie.

### Vérifié empiriquement

Trois simulations sur un dépôt jetable, avec un plan volontairement faux (une décision affirmant qu'un renommage vit dans le mauvais module) :

- **La détection de dérive est fiable** (2/2) : arrêt sur la phase fautive, plan jamais réécrit, phases aval jamais ouvertes, pas de confusion avec `blocked`. Diagnostic riche — les deux runs ont repéré que les critères de la phase étaient *déjà vrais*, donc la phase sans scope exécutable.
- **La reprise est sûre mais non spécifiée** : aucune règle n'ordonne de sauter les phases `status: done` ; un `executor` neuf les a pourtant re-vérifiées sans les refaire. C'est de l'inférence, pas du contrat.
- **La sortie de dérive laisse un état d'arbre indéfini** : un run a remis le marqueur de phase à `pending`, l'autre l'a laissé `in-progress` non committé — ce qui viole le propre test de `02-execute` (*« no dangling phase edits »*). L'étape Guard spécifie le nettoyage pour `blocked`, rien pour la dérive.
- **En `auto`, pas de boucle infinie** : l'orchestrateur improvise une arête retour `03 → 02`, amende le plan lui-même et termine. Mais il n'a pu replanifier que parce que le rapport de dérive **contenait déjà la constatation de code**. Un signal plus pauvre rendrait l'improvisation aveugle.
- **Le vrai risque de boucle est la review, pas la dérive** : `04 = iterate → 03` n'a aucun compteur d'itérations, et deux tours consécutifs ont fait *baisser* la qualité (72 → 68).
- **Un tunnel peut finir vert et faux** : plan `implemented`, 3/3 tests verts, arbre propre — alors qu'une mutation du code de prod (remettre l'ancien service en dur) laissait la suite verte. Un `runTests()` vert ne prouve rien sans signal indépendant du code testé.

### Impact sur les skills de ce repo

`skills/aidd-pilot/` patché sur 11 points : agents renommés, plan rédigé inline, layout en dossier de feature (y compris la reconnaissance d'un plan en `01-intake`), pilotage direct de `01-plan`/`02-implement`/`05-review` au lieu de composer `00-sdlc`, réception de `replan needed` avec filtre trivial/substantiel, matrice axes de review × cadence, sortie de boucle par sévérité, et rung 3 basculé de `03-assert` vers `06-test:02-test-journey`.

`skills/doc-sync/` inchangé : son garde-fou « `10-learn` écrit à plat dans `aidd_docs/memory/`, donc une memory centralisée passe en édition directe » reste valide en 2.4.1.
