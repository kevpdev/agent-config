# AIDD — le workflow de tout dépôt git

AIDD est le workflow unique de tout travail qui produit dans un dépôt git, à profondeur selon la taille. Récits datés et sources → `rules/references/ref-aidd.md`.

## Chercher un skill avant d'agir

**DÉCLENCHEUR** : une demande qui produit ou modifie quelque chose dans un dépôt git, qu'il porte un `aidd_docs/` ou non. Une question ou une lecture seule ne déclenche rien.

**À LA PLACE de** démarrer à la main, parcourir le catalogue, par intention et jamais par nom, et chercher une ligne dont le « Use when » la couvre. Puis l'invoquer, ou écrire une ligne qui dit pourquoi aucun ne convient.

**CE QU'ELLE NE DEMANDE PAS** : invoquer à tout prix, seul regarder est systématique. Quand le skill choisi pilote le flux, l'exception de `plan-mode.md` s'applique. Sans AIDD installé (OpenCode sans installation projet), le parcours reste le même, mené sans ses skills.

**POURQUOI** : 9 issues ont été écrites à la main alors qu'un skill existait. Le garde `guard-aidd-skill-lookup.py` tient cette section, sortie `# aidd-skip: <raison>`.

## Profondeur selon la taille

| Taille | Parcours |
|---|---|
| Petit (un script, un template) | implémenter, puis relecture à contexte neuf (`aidd-dev:checker` ou `aidd-dev:05-review`) |
| Moyen (un skill, plusieurs fichiers) | `aidd-dev:01-plan`, puis implémenter, puis relire |
| Grand (une feature de bout en bout) | `aidd-orchestrator:01-sdlc` |

## Rôles et boucle de correction

**La session principale orchestre.** Sous Claude Code, `aidd-dev:executor` implémente dans le worktree, `aidd-dev:checker` relit, et chaque correction repasse par le checker jusqu'au verdict « prêt ». Ailleurs, ces agents ne sont pas garantis : relire à contexte neuf par le moyen disponible.

**BORNE, dans tous les modes, SDLC compris** : la borne d'`intention.md` s'applique aux verdicts « à corriger » sur un même travail. Une fois atteinte, l'orchestrateur ne relance pas l'executor. Il revient au cadrage ou au plan, rapporte les écarts récurrents et rend la décision à l'humain.

**ROUTAGE hors SDLC**, d'après le sujet du finding :

| Le finding porte sur | Il repart vers |
|---|---|
| le besoin ou le contrat, dont un finding `fit` du `05-review` | le cadrage |
| l'implémentation, corrections dépendantes | le plan puis l'exécution, d'un seul tenant |
| l'implémentation, corrections indépendantes | l'exécution, parallèle possible (`aidd-dev:10-batch`) |

## Où vit la mémoire

| Rang | Condition | Où |
|---|---|---|
| 1 | le dépôt porte un `aidd_docs/` | `aidd_docs/memory/` |
| 2 | le vault | `AGENTS.md` et `decisions/` |
| 3 | sinon | le `CLAUDE.md` ou l'`AGENTS.md` du projet |

Le fichier du rang 3 se crée au premier fait projet, pas d'avance. **Dans le vault, ne pas lancer `aidd-context:02-project-memory`** : il doublerait `AGENTS.md` et `decisions/`.

## Langue du code et des documents

**DÉCLENCHEUR** : j'écris du code, un commentaire, un nom de test ou un document dans un dépôt git.

**À LA PLACE de** mélanger, tout ce qui est code est en **anglais** : identifiants, commentaires, docstrings, noms de test, scripts, Dockerfile. La documentation (README, `aidd_docs/`) est en français.

**Documents produits par un skill AIDD** (plan, spec, PRD, issue, mémoire projet) : le gabarit, titres de section et noms de champ, reste en anglais. Le contenu est en **français**, même quand le skill rédige en anglais par défaut.

**HORS PÉRIMÈTRE** : les textes affichés à l'utilisateur final, qui relèvent du produit. Forme au sens de `autorite-des-conventions.md` : un repo qui déclare autre chose garde la priorité, et migrer l'existant est un `refactor` séparé.

**POURQUOI** : sans choix écrit, le code mêle les deux langues. Le français épargne au lecteur une traduction mentale, le gabarit est le contrat du skill.

## Git sur une branche de travail

**DÉCLENCHEUR** : je m'apprête à commiter, pousser ou ouvrir une PR draft.

**PERMIS sans question** : commit, push et PR **draft** sur la branche que j'ai créée pour ce travail (`worktrees.md`).
- **Pendant un run AIDD** (`aidd-orchestrator:01-sdlc`, `/aidd-dev:*`) : à chaque étape, même si le repo écrit « never » (`vcs.md`, `CLAUDE.md`). Lancer le skill vaut accord sur le run.
- **Hors run** : une fois le travail validé (tests verts ou checker « prêt »). Un « never » du repo garde sa question.

**Les autres gestes git** (merge, force-push, tag, branche par défaut ou d'autrui) ne sont pas réglés ici : `intention.md` dit quand ils se font sans question et quand ils gardent la leur.

**POURQUOI hors run (issue #90)** : un « oui » nu à 54 % des questions push ou PR draft et 36 % des questions commit. Aucune autre réponse push ou PR draft ne refusait le geste.

## Issue et PR draft sans validation

**DÉCLENCHEUR** : je crée une issue ou une PR draft à la demande de l'utilisateur.

**À LA PLACE de** montrer le brouillon et attendre l'accord, créer, puis donner le lien, même si le skill dit d'attendre.

**POURQUOI** : les deux se modifient ou se suppriment en un geste, et les brouillons montrés ont été validés tels quels.

## CI GitHub

**DÉCLENCHEUR** : je crée ou modifie un fichier de `.github/workflows/`, `.github/dependabot.yml` ou le ruleset d'un dépôt.

**À LA PLACE de** composer la CI de mémoire, lire `rules/references/ref-ci-github.md`, appliquer son contrat, puis lancer `tools/check-ci-contract.py` sur le dépôt avant de pousser.

**Après le changement** : corriger ce que la CI ou les commandes de build rendent faux dans le README et la mémoire du projet, avec `sh ./mvnw` dans les commandes Maven. Constater le langage avant d'appliquer la fiche : une stack « non mesurée » ne reçoit pas la table d'une autre.

**POURQUOI** : des jobs nommés d'après leurs outils font changer le ruleset avec chaque stack, alors que le contrat fixe les noms.
