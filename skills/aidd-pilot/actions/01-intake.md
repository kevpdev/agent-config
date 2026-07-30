# 01 — intake : normaliser, classer, router

Premier pas systématique. Transforme une entrée brute en un contexte de run décidé : quoi, quelle taille, quelle topologie, quel mode, faut-il affiner.

## Entrées — 2 modes

1. **Externe** : `request` = `$ARGUMENTS` — texte du besoin collé, **ou** url/chemin (note vault Obsidian, fichier système, peu importe le stockage), **ou** chemin d'un plan AIDD déjà rédigé. Le skill n'a **aucune** connaissance du vault : l'humain fournit le pointeur.
2. **In-session** : le besoin a été cadré dans la conversation en cours (via `/01-brainstorm` ou non) et **validé par l'humain** ; l'orchestrateur transmet ce besoin cadré directement, sans paramètre (il est déjà en contexte).

- Le mode in-session arrive **pré-validé côté métier** : la gate de clarté ne rouvre pas le cadrage produit (cf. étape 3), elle grounde quand même les prémisses techniques.
- CWD = repo (mono) ou racine de coordination (multi).

## Sorties (contexte de run)

```
mode          : complet | implementation
size          : small | medium | large
topology      : mono | coordinator+children
repos[]       : { name, path, role: contract|back|front }
plan_path?    : si fourni ou à générer
needs_refine  : bool
entry_artifact: le brief normalisé (objectif + critères d'acceptation)
```

## Étapes

1. **Détecter un plan fourni.** Si `request` pointe un plan AIDD validé → `mode = implementation`, on saute l'affinage et le plan ; grounder le plan (ne PAS régénérer) et aller au pipeline.
   - **Reconnaissance « plan AIDD »** (vérifié, aidd-dev 2.x) : un **dossier de feature** `aidd_docs/tasks/<yyyy_mm>/<yyyy_mm_dd>_<slug>/` contenant `plan.md` (frontmatter `objective:` + `status:`) et un `phase-<n>.md` par phase (frontmatter `status:` seul). Vocabulaire de statut **en anglais** : plan `pending|in-progress|implemented|reviewed|blocked`, phase `pending|in-progress|done`. **Pas** de `status: ready` (n'existe pas — ne pas s'appuyer dessus).
   - **Les suffixes `-master` / `-part-N` n'existent plus** : un plan multi-parties est un `plan.md` + N `phase-<n>.md` dans le même dossier. Un plan **plat** hérité (`<yyyy_mm_dd>-<slug>.md` à la racine du mois, séparateur `-`, statuts en français) reste lisible en `mode=implementation` — le grounder tel quel, ne pas le migrer sans demander.

2. **Détecter la topologie ET les projets concernés (F5).** Mono-projet vs coordinateur + projets enfants + contrat partagé. Puis **déterminer quels repos la feature touche réellement** (passe Explore / grounding du brief) et ne retenir que ceux-là dans `repos[]` — on ne planifie **que** les repos concernés. Un repo « touché mais rien à coder » (ex. M5 : front déjà prêt) est **exclu du plan**, pas planifié à vide — **mais pas exclu de la validation** : s'il porte un critère non prouvable à la frontière API (rendu front, ou câblage back↔front neuf), il reste dans le périmètre e2e (`03-validate`, rung 3). L'e2e est découplé des repos planifiés.
   - **Détection topologie** : appeler le script partagé, **ne pas réimplémenter**.
     ```
     bash "$HOME/.claude/skills/_shared/detect-children.sh" --long
     ```
     Un script n'est pas un skill : l'appeler n'invoque **pas** `doc-sync` et n'hérite d'aucune gate de confirmation. L'invocation lourde de `doc-sync` reste réservée à `04-doc-ship`.
     - *Pourquoi un home unique :* la règle a été recopiée à l'identique dans trois skills, et elle a dérivé — la copie locale cherchait un `.git` sur deux niveaux, donc voyait **0** enfant sur un monorepo (mesuré) et ratait un enfant rangé à `apps/backend/svc/`. La règle, ses contre-exemples mesurés et le `basename` du home memory vivent désormais dans les commentaires du script (R6 : un fait, un seul home).
     - **Ce que la sortie change pour `repos[]`** : la colonne `BUILD` nomme le manifeste, donc l'existence d'une porte de test dans cet enfant ; un enfant à `BUILD = aucun` (dépôt de doc ou de config) est un enfant légitime, sans porte. La colonne `VCS` dit s'il peut porter sa propre branche — en monorepo (`parent`), **un seul repo git** : ne pas promettre un commit ou une branche par enfant, et ne pas déduire « mono-projet » de l'absence de `.git` dans les enfants.
   - **Contrat partagé** : candidat `aidd_docs/memory/*.md` (top-level) **à confirmer**, aucun nom figé.
   - **« Repo réellement modifié »** (vérifié : aucun tag repo/couche dans les plans) : passe de grounding (Explore) qui mappe chaque critère d'acceptation à des fichiers concrets par repo. Repo concerné ⟺ le grounding nomme ≥1 fichier à créer/modifier dedans. Un consommateur runtime seul (front qui rend déjà) n'est **pas** concerné pour le plan mais reste dans le périmètre validation (règle e2e découplée ci-dessous + `03-validate`). Mapping vérifié contre le vrai code, pas supposé.
   - **Pas de résolution d'adaptateur.** aidd-pilot compose **toujours** le testeur générique de son workflow (`references/test-runner.md`) ; rien à déclarer ni à demander en intake. Le testeur découvre la recette de run au moment de valider (`03-validate`).

3. **Gate de clarté — grounder les prémisses, PAS le besoin métier.** Le besoin métier (« afficher le filename ») n'est **jamais** rechallengé : arbitrage humain, validé (in-session) ou posé par l'humain (externe). Ce que la gate vérifie = **les détails techniques qui remplissent les conditions du contrat** (le champ existe dans le DTO ? l'endpoint le renvoie ? le chemin est bon ?), contre le **vrai code**. Une validation métier ≠ prémisses vérifiées (directive prime).
   - **Spec-skip (garde-fou dur)** : on n'annule la génération de spec **que si** le brief d'entrée porte un **cadrage fiable des critères d'acceptance** (quelle que soit sa forme : note groundée, plan, brief in-session validé). Défaut = spec générée ; sauter = l'exception **qui doit se prouver**.
   - Cadrage incomplet/ambigu → `needs_refine = true` → affinage **non-interactif** auto : `aidd-refine:04-shadow-areas` + `aidd-refine:02-challenge`. Le vrai `aidd-refine:01-brainstorm` (Q&A) reste un pré-pas que l'humain lance lui-même.
   - **Heuristique « cadrage fiable des critères »** (checklist, pas au jugé) : fiable ⟺ pour chaque critère on peut nommer (a) l'observable (endpoint/champ/élément UI) et (b) la condition de succès, ET le grounding confirme que la surface de code référencée existe. Un seul critère non rattachable à un observable vérifiable → **non fiable → spec générée**.

4. **Classer la taille** → `small | medium | large`.
   - **Signaux de taille** : `small` = 1 projet, contrat déjà stable, peu de fichiers, prémisses sûres. `medium` = 1–2 projets ou 1 nouveau champ de contrat mais borné. `large` = plusieurs projets à contrat instable, nombreuses phases/couches, ou prémisses exigeant le rolling-wave (`feature-decomposition`). `large` sans plan humain → STOP (étape 5).
     - *L'unité est le **projet**, pas le repo git.* Deux projets dans un même repo posent le même problème de contrat instable que deux repos — c'est la frontière de stack et de porte de test qui coûte, pas la frontière de versionnement. Compter les repos ferait passer un monorepo back+front pour `small` et sauterait le STOP.

5. **Router selon taille + plan.**
   - `large` **sans** plan humain → **STOP** : renvoyer l'humain planifier (`aidd-dev:01-plan` en mode assisté), ne pas planifier une grosse feature en autonomie. *(Limite dure, cf. SKILL.md.)*
   - sinon → `mode = complet`, continuer.

6. **Normaliser le brief** (si pas déjà un plan) : collecter les sources (request + note/url + conversation), déléguer à `aidd-pm:04-spec` pour produire objectif + critères → `entry_artifact`. **Skip uniquement si le spec-skip de l'étape 3 est satisfait** (cadrage fiable des critères déjà présent).

## Handoff

Passer le contexte de run à `02-pipeline`.
