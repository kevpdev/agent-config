# 03 — validate : la ladder de test

Décide si une phase est **validée** (donc committable). Une phase l'est quand le **signal le plus fort disponible** est vert **et** qu'il n'y a **aucune régression** (suite pertinente complète verte, pas seulement le nouveau test).

**Pourquoi une ladder** : `/00-sdlc` n'a **aucune étape de test** (ses 5 actions sont `spec|plan|implement|review|ship`) et le framework suppose l'app **déjà lancée** — `03-assert-frontend` : *« Never start or restart a server »*, `06-test:02-test-journey` : *« Assume every server is already running »*. Personne n'y démarre l'app. aidd-pilot **possède** donc la validation, via le testeur générique (`references/test-runner.md`).

**Un vert ne vaut que ce que vaut la suite.** Mesuré sur un run réel : un tunnel complet s'est terminé « 3/3 tests verts, plan `implemented` » alors qu'une mutation du code de prod (remettre l'ancien service en dur) laissait la suite **verte**. D'où le rung 2 (curl live), signal **indépendant du code testé** : c'est le seul rung qu'une suite complaisante ne peut pas faire mentir.

## Précondition — invoquer le testeur (skill), ne pas l'improviser

Le « testeur générique » **est le skill `test-runner`** : on l'**invoque** (outil Skill → `test-runner`), ce qui charge ses actions `01-discover` / `02-lifecycle` / `03-validate-live`. Toutes les notations `testeur.X()` de ce fichier (`start()`, `runTests()`, `exerciseApi()`, `costGuard()`) **mappent sur ces actions** — on les exécute **en invoquant le skill**, jamais en déroulant des commandes ad-hoc à la main.

**Pourquoi (écart réel du 1er run)** : discover/lifecycle/validate ont été faits en bash inline sans jamais appeler le skill → sa logique (déduction par finalité, garde-coût, honnêteté du « non couvert ») n'a pas tourné comme unité. Invoquer le skill garantit qu'elle s'applique.

- Instance nécessaire ? → le testeur la démarre AVANT la validation (`02-lifecycle` start), après `01-discover` de la recette. Pas d'adaptateur à résoudre : aidd-pilot compose toujours ce skill.
- **Locus** : invoqué **inline (parent)** quand un serveur doit persister dans la boucle debug ou qu'une confirmation coût est requise ; les ops bornées (runTests, exerciseApi) peuvent partir en **subagent qui invoque le skill** (table locus, `references/test-runner.md`).

## Rungs (du plus fort au fallback)

| Rung | Quand | Comment |
|---|---|---|
| 0 | tests UI/unitaires présents | `testeur.runTests()` — doivent passer |
| 1 | tests d'intégration présents | `testeur.runTests()` (intégration) |
| 2 | **pas de TI** pour la couche visée (backend) | `testeur.exerciseApi()` — **curl live** contre l'endpoint réel |
| 3 | validation UI / e2e | **`dev:06-test:02-test-journey`** pilote le navigateur sur l'URL lancée : un screenshot par étape, un verdict pass/fail par étape. Le testeur ne fournit que **l'URL** |

- On prend le rung disponible le plus fort pour la couche touchée ; on **descend** en fallback.
- « Sans régression » = rejouer la **suite pertinente complète**, pas juste le test neuf.

### Le rung 3 mesure, il ne répare pas

**Ne jamais utiliser `dev:03-assert` comme rung 3.** Sa facette `03-assert-frontend` est une **boucle de réparation** : *« Take a cause, apply a candidate fix, validate […] On failure, mark it and take the next »*, et la règle transversale du skill dit *« the coding and frontend facets **fix and re-run** until they pass »*. Il modifierait donc du code pendant la validation d'une phase, hors périmètre planifié et sans passer par la review.

`06-test:02-test-journey` est le thermomètre : *« Report actual behavior even when it differs from expected, **never silently fix or skip** »*.

`03-assert-frontend` garde sa place **dans la boucle debug** (`02-pipeline`, étape b), là où sa réparation est voulue et cadrée.

**Et ne jamais invoquer `dev:03-assert` nu** : *« Run every applicable facet by default »*, et la facette `01-assert` (assertions projet) *« always applies »* — on rejouerait la suite déjà passée aux rungs 0/1. Nommer l'action, toujours.

**L'outil de navigation appartient au projet**, pas au testeur : `03-assert` et `06-test` parlent du *« project's **configured** browser tool »*. `discover()` ne renvoie d'ailleurs aucun outil de navigation dans sa recette.

## Quand déclencher le rung 3 (e2e)

L'e2e est **découplé des repos planifiés** : le front est le point d'entrée métier, donc un critère peut exiger l'e2e même si aucun code front n'a changé. Le déclencheur n'est **pas** « quel repo j'ai touché » mais **un seul test** :

> **Le critère est-il prouvable à la frontière API ?** Oui → curl (rung 2) suffit. Non, il dépend du front → rung 3.

| Curl (rung 2) suffit | Rung 3 (e2e) nécessaire |
|---|---|
| critère sur la **donnée** : champ présent, valeur, forme, code HTTP | critère sur un **rendu front** : formatage, affichage conditionnel, i18n, dérivation réponse→pixels |
| logique **100% back** (calcul, validation, filtrage, erreur) | **câblage back↔front neuf** : champ nouvellement consommé — le contrat clé JSON ↔ binding n'a jamais fait feu ensemble avec une vraie valeur |

**Règle du doute (directive prime)** : la donnée présente dans le code front ne **prouve pas** que le câblage est bon (ex. back sérialise `unit_raw`, front lit `unitRaw` → curl vert, UI toujours `—`). Ne jamais supposer le câblage correct parce que le champ existe. **Dans le doute → e2e** (un screenshot coûte peu ; une supposition fausse coûte cher, différé).

- *Cas M5* : fix back-only, mais champ nouvellement câblé → **e2e**, non pas parce que « c'est visuel » mais parce que le contrat n'a jamais tourné ensemble.
- **« Couche visée » d'une phase** (vérifié : aucun tag couche dans les plans) : dérivée des **fichiers que la phase nomme** (section `## Architecture projection` du plan). Chemins back (`src/main/java`, controllers, DTO) → rungs backend ; chemins front (`.tsx`, `src/`) → rung 3. L'e2e reste découplé (front = entrée métier) selon la règle ci-dessus.
- **Détecter « pas de TI » / « pas d'outil e2e »** (vérifié : aucune convention aidd-dev, défère au projet) : rôle du **testeur générique** — il découvre le runner (plugin failsafe Maven, config vitest/playwright, dossiers de test) ; découvrable → l'utilise ; ambigu → **ne devine pas**, rapporte le rung comme non couvert (honnêteté remontée au verdict, `test-runner.md`).

## Coût

Un rung qui déclenche un appel payant (ex. extraction Mistral live) → **cost-guard** du testeur AVANT exécution (`testeur.costGuard()`), confirmation si au-dessus du seuil.

## Sortie

`{ validated: bool, evidence: [...] }` (chemins de captures, sorties curl, résultats de suite). L'évidence est jointe au contexte de phase (utile à la review).
