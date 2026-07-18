# 02 — pipeline : plan → phases (implémenter/tester/commit/review)

Le cœur. Déroule le tunnel par **repo** puis par **phase**. Compose `/00-sdlc` sans le refaire, mais **possède** la validation (ladder) et la cadence commit/review.

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

1. **Plan.** `mode = complet` → générer via `aidd-dev:01-plan` (agent planner). `mode = implementation` → utiliser le plan humain fourni, **grounder ses prémisses** contre le vrai code avant de dérouler (directive prime).
   - Le master plan reste un **squelette** ; détailler la phase N, planifier N+1 après N (`feature-decomposition`, rolling-wave).

2. **Par phase :**
   a. **Implémenter** — agent `implementer` (`aidd-dev:02-implement`) sur la phase.
   b. **Valider** — lancer la **ladder** (`03-validate`). Boucle implémenter↔debug (`aidd-dev:08-debug`) **jusqu'aux critères d'acceptation** ET zéro régression.
   c. **Commit de phase** — `aidd-vcs:01-commit`, atomique, Conventional Commits EN, scope = la phase. Uniquement une fois la phase **validée**.
   d. **Review** — voir cadence ci-dessous.

## Cadence de review

- **Défaut** : `aidd-dev:05-review` sur le diff **après chaque commit de phase**. Findings → retour implémenter (boucle correctrice).
- **Exception** : phases **interdépendantes** (phase de préparation + phase qui en dépend) → review **différée en fin de bloc**, plus qualitative.
- **Phase « de préparation »** (vérifié : le format de plan n'a **pas** de tag prep ; le master-plan gère un gating séquentiel par checkbox, les child plans visent des phases indépendantes) : ne pas inventer de tag absent. Détecter l'interdépendance depuis la **structure du plan** — une phase est « de préparation » ⟺ une phase ultérieure dépend de sa sortie (fichiers/critères partagés, ou chaîne de gating master). Défaut = review par phase ; review différée uniquement sur dépendance dure avérée.

## Autonomie

Tout au long : le **gouverneur** (`references/governor.md`) décide seul sauf arbitrage lourd / prémisse non vérifiable → escalade.

## Handoff

Feature implémentée + committée par phases → `04-doc-ship`.
