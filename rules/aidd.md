# AIDD — règles communes aux repos du framework

Foyer des décisions qui valent pour tout repo portant un `aidd_docs/`. Une décision n'entre ici que si elle vaut pour tous ces repos et se tient en quelques lignes avec son pourquoi. Chaque section porte son propre déclencheur.

## Chercher un skill avant d'agir

**DÉCLENCHEUR** : une demande qui produit ou modifie quelque chose, dans un repo qui porte un `aidd_docs/`, à constater d'un `ls` au premier tour. Une question ou une lecture seule ne déclenche rien, et un repo sans `aidd_docs/` n'est pas concerné.

**À LA PLACE de** démarrer à la main, parcourir le catalogue de la session et chercher une ligne dont le « Use when » couvre l'intention. Puis invoquer ce skill, ou écrire une ligne qui dit pourquoi aucun ne convient.

**Lire par intention, jamais par nom** : mémoire du projet et génération d'artefacts de contexte, clarifier et remettre en cause, planifier et implémenter et contrôler (revue, tests, audit, débogage), versionner et livrer, produit et backlog, orchestrer de bout en bout.

**CE QU'ELLE NE DEMANDE PAS** : invoquer à tout prix. Regarder est systématique, invoquer dépend du « Use when ». Quand le skill choisi pilote le flux, l'exception de `plan-mode.md` s'applique.

**POURQUOI**, mesuré le 2026-10-07 : 9 issues écrites à la main alors qu'un skill existait, vu seulement quand l'utilisateur a posé la question. Aucun nom de skill ici, parce qu'ils dérivent, et `aidd_docs/` est le même signal que `memory-policy.md`.

**ÉTAT DU GARDE, décidé le 2026-10-07** : `guard-aidd-skill-lookup.py` rappelle et ne bloque pas, la sortie `# aidd-skip: <raison>` reste libre. On ne le durcit que si on constate que les skills AIDD sont ignorés malgré leur présence.

## Langue du code et des documents

**DÉCLENCHEUR** : j'écris ou modifie du code, un commentaire, un nom de test ou un document, dans un repo qui porte un `aidd_docs/`.

**À LA PLACE de** mélanger, tout ce qui est code est en **anglais** : identifiants, commentaires, docstrings, noms de test, scripts, Dockerfile. La documentation (README, `aidd_docs/`) est en français.

**Documents produits par un skill AIDD** (plan, spec, PRD, issue, mémoire projet) : le gabarit reste en anglais, c'est-à-dire les titres de section et les noms de champ. Le contenu est en **français**. Les skills AIDD rédigent en anglais par défaut, donc ne pas laisser ce défaut passer : écrire ou réécrire le contenu en français.

**HORS PÉRIMÈTRE** : les textes affichés à l'utilisateur final (messages d'erreur, interface), dont la langue relève du produit. C'est de la forme au sens de `autorite-des-conventions.md` : un repo qui déclare autre chose garde la priorité, et migrer l'existant est un `refactor` séparé.

**POURQUOI**, constaté le 2026-10-07 sur `yt-transcriber` : 14 fichiers de code mêlaient français et anglais, et le choix n'était écrit nulle part. Les titres de plan en anglais viennent du gabarit du skill, et le corps suit la langue de la conversation, sans règle qui les garantisse. Le contenu des documents est en français pour épargner au lecteur une traduction mentale, le gabarit reste en anglais parce que c'est le contrat du skill.

## Git pendant un run AIDD

**DÉCLENCHEUR** : l'utilisateur lance `aidd-orchestrator:01-sdlc` ou un `/aidd-dev:*`.

**PERMIS pour ce run** : commit, push de la branche de travail et PR **draft**, y compris si le repo écrit « never » (`vcs.md`, `CLAUDE.md`).

**HORS PÉRIMÈTRE** : push sur `main`, merge, force-push, tag, et toute action hors du run. `guard-no-claude-in-commit.sh` continue de s'appliquer.

**POURQUOI** : lancer le skill est l'accord durable sur ce run, et s'arrêter avant chaque commit contredit « decide and act without confirmation » (`plan-mode.md`).
