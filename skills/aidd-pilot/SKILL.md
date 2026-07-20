---
name: aidd-pilot
description: Orchestrateur autonome du workflow AIDD calé sur l'usage de Kevin. Prend une expression de besoin (story, note de cadrage, texte brut) ou un plan AIDD déjà rédigé, et déroule le tunnel besoin→analyse→plan→implémentation+test→review→commit→doc en semi-auto (ne sollicite l'humain que sur un arbitrage lourd). Compose /00-sdlc pour le cœur dev, un testeur générique pour la validation live/e2e, et doc-sync pour la doc. Utiliser quand l'utilisateur dit "automatise cette feature", "déroule le tunnel", "fais cette feature en autonome", "pilote AIDD", ou "/aidd-pilot". NE PAS utiliser pour un simple commit (→ aidd-vcs:01), une review isolée (→ aidd-dev:05), ou lancer/tester une instance sans développer (→ test-runner).
---

# aidd-pilot

Orchestrateur **autonome** du workflow AIDD. Il ne réinvente rien : il **compose** les briques existantes (`aidd-*`, `doc-sync`) et un **testeur générique** de validation, en ajoutant ce que `/00-sdlc` seul ne fait pas : garantir le test e2e réel, gérer le multi-repo, et une autonomie *sélective*.

> [!note] Logique fermée — gabarits v1
> Flux et décisions arrêtés (F1–F6 + testeur générique + validation e2e découplée, ancrés sur le comportement réel des plugins AIDD). Restent des **gabarits v1** (recap, escalade, lot arbitrage) à affiner après quelques vrais runs, et le testeur générique à créer.

## Portée

- **Scopé AIDD** : suppose le workflow et les plugins AIDD (`aidd-dev`, `aidd-pm`, `aidd-vcs`, `aidd-refine`, `aidd-context`) installés. Pas de routage haut-niveau générique (décision explicite).
- **Validation par un testeur générique** : démarrer l'app, tester en live, découvrir secrets/chemins, garde-coût — tout ça vit dans un **testeur générique** composé par le workflow, qui **découvre** la recette de run par projet (`references/test-runner.md`). Pas d'adaptateur à déclarer.
- **N'intégrer que les briques adaptées (F3)** : un skill AIDD composé n'est retenu que s'il **sert le besoin**. Un skill non adapté (ex. `ship`/MR quand on ne veut pas de MR) est **retiré, jamais forcé** ; ce qu'aucune brique ne couvre → on écrit une nouvelle action/instruction. *(Cartesian check : chaque brique survit à son challenge d'adéquation isolé, sinon dehors.)*

## Principe d'exécution

Le skill **vit inline dans la session parente** : c'est le chef d'orchestre. Il **délègue** le travail borné à des sous-agents (implementer, reviewer, scans), mais garde inline : les décisions, les gates d'arbitrage, et le testeur quand un serveur doit survivre à une boucle debug ou qu'un dialogue interactif est requis.

**Pourquoi** : un serveur ou un dialogue de confirmation ne peut pas vivre dans un subagent (le serveur meurt avec lui, l'interactif est impossible) ; une tâche bornée qui rend un résultat sature au contraire le fil parent si elle tourne inline. Règle : borné et sans interaction humaine → subagent ; persistant ou interactif → parent.

## Directive prime — PAS DE SUPPOSITION

Toute affirmation mécanique (comportement d'un test, forme d'un DTO, état d'un service) est **vérifiée contre la source** avant d'agir. Face à l'incertitude non levable → **escalade humaine**, jamais deviner. C'est la règle qui arme le gouverneur ci-dessous. Détail : `references/governor.md`.

## Gouverneur d'autonomie — semi-auto

Autonome partout où il peut vérifier. **Sollicite l'humain sur exactement 2 cas** :
1. **Arbitrage lourd** — choix produit/archi qui appartient à l'humain (ex. le libellé M2 : note périmée vs code).
2. **Prémisse non vérifiable de façon fiable** — la directive prime interdit de deviner.

Tout le reste (petites recos, choix mécaniques vérifiables) → décidé seul.

**Le lancement vaut consentement.** Lancer `/aidd-pilot` autorise tout le tunnel (implémenter **et** committer par phase) : l'autonomie du gouverneur **écrase in-scope** les gates globales « demander avant d'implémenter / committer ». Le skill ne re-demande pas à chaque phase — il ne s'arrête que sur les 2 cas ci-dessus **et** la frontière push/MR (100 % humaine). Détail et pourquoi : `references/governor.md`.

## Le tunnel nominal (happy path)

```
besoin → [affinage?] → plan → { implémenter → tester(ladder) → boucler jusqu'aux critères } → review → commit(phase) → doc-sync → commit(doc)
```

- **Affinage/spec conditionnels (garde-fou dur)** : on ne les saute **que si** le brief porte un cadrage fiable des critères d'acceptance ; défaut = on les fait (`01-intake`).
- **Commit par phase validée** ; **review par phase**, différée en fin de bloc si phases interdépendantes (`02-pipeline`).
- **Fin = commit-only + recap storytelling dans le chat** ; **jamais de MR**, le push reste une décision humaine (`04-doc-ship`).

## Les 2 modes selon la taille

| Mode | Déclencheur | Périmètre du skill |
|---|---|---|
| **Complet** | petite/moyenne feature | tout le tunnel, du besoin au commit doc |
| **Implémentation** | grosse feature | entrée = **plan AIDD écrit par l'humain** ; démarre à *implémenter*, va jusqu'au commit doc |

**Limite dure** : grosse feature **sans** plan humain → le skill **ne planifie pas seul**, il renvoie planifier d'abord (`01-intake`). *(Raison : un plan détaillé de grosse feature repose sur des prémisses ; les figer en autonomie fait cascader une erreur — cf. `feature-decomposition`.)*

## Multi-repo

Chaque repo concerné = **pipeline séparé avec son plan autonome** (implémentable sans repo frère) ; l'orchestrateur ne porte que la spec si besoin. L'ordre **dépend des dépendances de contrat** : séquentiel dès qu'un repo consomme un contrat pas encore figé (défaut), parallèle seulement si vraiment indépendants (à challenger). Repos concernés + topologie détectés en `01-intake` (F5) ; ordonnancement en `02-pipeline`.

## Actions

| Étape | Fichier | Rôle |
|---|---|---|
| Intake | `actions/01-intake.md` | normalise l'entrée, gate de clarté (affinage ?), classe taille, détecte topologie + mode |
| Pipeline | `actions/02-pipeline.md` | boucle par repo/phase : compose `/00-sdlc`, injecte la ladder, commit + review par phase |
| Validation | `actions/03-validate.md` | la ladder de test (UI → intégration → curl → e2e via `dev:03-assert`), app tenue par le testeur générique |
| Doc & clôture | `actions/04-doc-ship.md` | routage `doc-sync` (reflet/décision) + commit-only + recap storytelling (pas de MR) |

Références : `references/test-runner.md`, `references/governor.md`.
