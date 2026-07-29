# 02 — pipeline : plan → phases (implémenter/tester/commit/review)

Le cœur. Déroule le tunnel par **repo** puis par **phase**. Pilote `aidd-dev:01-plan` / `02-implement` / `05-review` **directement** — pas via `/00-sdlc` —, et **possède** la validation (ladder) et la cadence commit/review.

**Pourquoi pas `/00-sdlc`** : il spawne un **unique** `executor` pour *toutes* les phases puis review le tout d'un bloc (`00-sdlc/actions/03-implement.md`). Le composer supprimerait la cadence par phase, qui est la raison d'être de cette action.

## Entrées

Le contexte de run de `01-intake` (`mode`, `repos[]`, `plan_path?`, `entry_artifact`).

## Ordonnancement multi-repo

Si `topology = coordinator+children` et la feature touche plusieurs repos (déterminés en `01-intake`, F5) → **un pipeline par repo concerné**. Chaque pipeline enfant produit un **plan dédié, implémentable de façon autonome** sans dépendre d'un repo frère. Le repo orchestrateur ne porte **que la spec** si besoin (pas de plan-code).

**Ordre = fonction des dépendances, pas figé** :
- **Séquentiel par défaut dès qu'une dépendance de contrat existe** : si le front consomme un champ back pas encore verrouillé (ex. M1, nouveau champ DTO), le back se fige avant que le front l'affiche.
- **Parallèle** seulement si les repos sont *vraiment* indépendants (contrat déjà figé des deux côtés) — l'exception, **à challenger** pour la pertinence, jamais la règle d'une feature coordonnée.
- Un handoff cross-repo (nouveau champ DTO) déclenche la **couture verrou-contrat** ci-dessous (F6).

## Couture entre pipelines — verrou-contrat (F6)

**Où ça se joue** : entre le pipeline **producteur** (back, qui fige le champ) et le pipeline **consommateur** (front, qui l'affiche) — **à mi-parcours**, PAS à la clôture. C'est le point que `04-doc-ship` nomme « pause arbitrage avant handoff back→front » ; il est **exécuté ici**.

Dès qu'un producteur a fini (implémenté + validé + committé) et qu'un consommateur dépend de son contrat :

1. **Synchroniser le contrat** — mettre `shared-contract.md` (parent) en phase avec la réalité **déjà committée** du producteur (branche doc-décision bloquante de `doc-sync`, cf. `04-doc-ship`). Commit doc dédié.
2. **Arbitrage si besoin** — gate humaine (gouverneur) **seulement** si un choix lourd émerge ; sinon décider seul après vérification.
3. **Verrouiller** — le contrat figé devient la source des prémisses du consommateur.
4. **Grounder le consommateur** — les prémisses du plan front sont groundées **contre le contrat verrouillé**, pas contre une hypothèse. Alors seulement le pipeline consommateur démarre.

**Pourquoi mi-parcours** : si le contrat se fige à la fin, le front aurait déjà été planifié/implémenté contre un contrat non verrouillé → prémisse fausse en cascade (directive prime). Le verrou avant le consommateur garde l'erreur locale.

## Préparation VCS — brancher avant le 1er commit (par repo)

**Ne jamais committer sur la branche par défaut.** Avant le premier commit de phase d'un repo :

1. **Détecter** la branche par défaut réelle du repo (`git symbolic-ref refs/remotes/origin/HEAD`, ou la branche de suivi) — ne pas supposer `main` (directive prime).
2. Si HEAD est déjà sur une feature branch dédiée (fournie par l'humain, ou plan `mode=implementation`) → l'utiliser telle quelle.
3. Sinon, si HEAD == branche par défaut → **créer `feat/<slug-feature>`** et s'y placer **avant** tout `add`/`commit`. Un repo doc-seul (coordinateur) → `docs/<slug>`.
4. **Multi-repo** : chaque repo concerné a **sa** branche, **même slug** pour la lisibilité cross-repo.

La branche porte tous les commits de phase **et** le commit doc (`04-doc-ship`). Merge / push / suppression de branche restent **100 % humains** — même frontière que le push (cf. `04-doc-ship`, clôture).

**Pourquoi** : committer sur la branche par défaut mêle du travail non mergé à la ligne de base ; l'humain doit garder une branche isolée à inspecter avant tout merge. *(Écart réel du 1er run : 2 commits posés sur `main`, corrigés à la main — d'où cette règle.)*

## Boucle par repo

1. **Plan.** `mode = complet` → dérouler `aidd-dev:01-plan` **inline, dans le contexte de l'orchestrateur** — jamais via un sous-agent. `mode = implementation` → utiliser le plan humain fourni, **grounder ses prémisses** contre le vrai code avant de dérouler (directive prime).
   - **Pourquoi inline** : le plan est le **contrat** que l'`executor` n'a pas le droit de réécrire (`00-sdlc/actions/02-plan.md` : *« You own the plan […] so you write it, never a worker »*). Un worker qui rédige le contrat peut l'arranger à sa convenance. L'agent `planner` de la 1.x a d'ailleurs été supprimé pour cette raison.
   - **Forme de sortie (aidd-dev 2.x)** : un **dossier de feature** `aidd_docs/tasks/<yyyy_mm>/<yyyy_mm_dd>_<slug>/` contenant `plan.md` (squelette : objectif, table des phases, décisions) et un `phase-<n>.md` par phase. La notion `-master` / `-part-N` **n'existe plus**.
   - Le `plan.md` reste un **squelette** ; détailler la phase N, planifier N+1 après N (`feature-decomposition`, rolling-wave). Écart assumé avec `01-plan`, qui écrit toutes les phases d'un coup depuis une projection unique — c'est précisément ce que la rolling-wave évite (une découverte en phase 2 ne périme pas les phases 3..N).

2. **Par phase :**
   a. **Implémenter** — agent `executor` (`aidd-dev:02-implement`) sur la phase. Il porte **aussi le commit de la phase** (code + `status: done` dans le même commit, cf. `02-implement`).
   b. **Valider** — lancer la **ladder** (`03-validate`). Boucle implémenter↔debug (`aidd-dev:08-debug`) **jusqu'aux critères d'acceptation** ET zéro régression.
   c. **Review** — agent `checker` (`aidd-dev:05-review`), voir cadence ci-dessous.

### Réception d'une dérive (`replan needed`)

L'`executor` s'arrête et remonte `replan needed: <raison>` dès qu'il constate un écart avec le plan — il ne réécrit jamais le plan. **Personne ne consomme ce signal dans aidd-dev** (`00-sdlc/actions/03-implement.md` ne connaît que `implemented` et `blocked`) : c'est donc **ici** qu'il se traite.

1. **Exiger la preuve.** Une dérive sans **la constatation de code qui la fonde** (`fichier:ligne`) est renvoyée à l'`executor` pour être étayée. Sans elle, replanifier est un pari — directive prime.
2. **Filtrer** :
   - **Triviale** (un port, un nom de paramètre, une signature, un header) → l'`executor` corrige dans le périmètre de la phase et le **note** dans son retour. Pas de replan.
   - **Substantielle** (la projection ou un critère d'acceptation est faux) → replan des **phases aval**, pas seulement la phase courante. C'est le point que le format 1.x ratait : l'amendement local laissait les parts suivantes périmées en silence.
3. **Replanifier inline**, comme au point 1. `aidd-dev:01-plan` n'a **aucune action d'amendement** (ses 4 actions : `gather`/`explore`/`wireframe`/`plan`) — une régénération complète écraserait les phases déjà `done` et committées. Réécrire donc **les fichiers `phase-<n>.md` aval uniquement**, en laissant intacts ceux marqués `done`.
4. **Reprendre** en spawnant un `executor` neuf. Il saute les phases `status: done` (mesuré) ; ne pas relancer sans avoir corrigé — le même plan produit le même arrêt.

## Cadence de review

- **Défaut** : `aidd-dev:05-review` sur le diff **après chaque commit de phase**. Findings → retour implémenter (boucle correctrice).
- **Exception** : phases **interdépendantes** (phase de préparation + phase qui en dépend) → review **différée en fin de bloc**, plus qualitative.
- **Phase « de préparation »** (vérifié : le format de plan n'a **pas** de tag prep ; les `phase-<n>.md` d'un même dossier de feature n'expriment aucune dépendance explicite) : ne pas inventer de tag absent. Détecter l'interdépendance depuis la **structure du plan** — une phase est « de préparation » ⟺ une phase ultérieure dépend de sa sortie (fichiers ou critères partagés, lus dans les sections `## Architecture projection`). Défaut = review par phase ; review différée uniquement sur dépendance dure avérée.

### Quels axes, quand

`05-review` a **trois** axes et les lance **tous par défaut**. Toujours **nommer** l'axe voulu, sinon on paie les trois.

| Axe | Juge | Cadence |
|---|---|---|
| `review-code` | qualité clean-code sur les lignes changées | **par phase** |
| `review-functional` | le diff contre les phases du plan et leurs critères | **par phase** |
| `review-relevancy` | `fit` / `conform` / `rot` — le changement a-t-il sa place | **une fois, en fin de feature** |

**Pourquoi `relevancy` en fin seulement** : sa lentille `fit` demande *« does the change serve the real intent **end to end** »*, et son diff par défaut est celui contre la branche par défaut — donc la feature entière. Le lancer sur la phase 1 d'un plan à 4 phases produit des faux positifs mécaniques : un morceau ne sert évidemment pas encore le besoin complet.

**Un seul `review.md` par dossier de feature, écrasé à chaque run** (*« a later review of the same work replaces the earlier one »*). La review de la phase 3 efface donc celle de la phase 2 — c'est **accepté** : la trace d'un finding résolu, ce sont les commits de correction, pas le rapport.

### Sortie de la boucle correctrice — par sévérité, pas par compteur

La rubrique de `05-review` rend `changes-requested` dès **un simple 🟡 warning** ; il n'existe pas d'« approuvé avec réserves ». Boucler sur le verdict seul ne converge donc pas.

- **🔴 critical** → on boucle, sans plafond. Rien ne passe avec un critical ouvert.
- **🟡 warning** → **deux tours maximum**. Au-delà : lister les warnings restants et **passer**, ou escalader si l'un porte sur un choix d'archi (arbitrage lourd du gouverneur).
- **🟢 minor** → jamais bloquant, on note et on avance.
- **Garde-fou de non-progression** : si le score de qualité du `checker` **ne monte pas** d'un tour au suivant, arrêter la boucle et escalader. *(Mesuré sur un run `auto` réel : deux tours consécutifs de `changes-requested`, qualité 72 → 68. Boucler davantage dégradait au lieu de corriger.)*

## Autonomie

Tout au long : le **gouverneur** (`references/governor.md`) décide seul sauf arbitrage lourd / prémisse non vérifiable → escalade.

## Handoff

Feature implémentée + committée par phases → `04-doc-ship`.
