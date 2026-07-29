---
name: doc-sync
description: >-
  Synchronise la doc avec l'état VALIDÉ du code (commité/mergé) quand elle a pris
  du retard. Deux régimes : les docs-REFLET (README, memory descriptive), dont le
  code fait foi et que le skill réécrit ; les docs-DÉCISION (contrat partagé, ADR,
  memory decisions), que le skill ne réécrit jamais seul — il signale l'écart
  code↔décision et te laisse arbitrer. Détecte la topologie (mono-repo ou repo
  coordinateur) et fait confirmer le scope avant d'éditer. Passe par /10-learn pour
  la memory AIDD, puis met les README à jour par repo. Utiliser quand l'utilisateur
  dit "sync la doc", "doc-sync", "clôture la feature", "resynchronise", "wrap-up",
  "/doc-sync", ou après une implémentation qui a touché
  entities/migrations/controllers/archi. NE PAS utiliser pour un fix sans impact
  doc, pour committer seul (→ aidd-vcs:01-commit), ni pour documenter du code non
  validé.
---

# doc-sync — synchroniser la doc avec le code validé

Après un dev qui change l'archi ou le schéma DB, la memory AIDD (`aidd_docs/memory/*`, relue par `/plan` et le brainstorming) et le README désynchronisent silencieusement. Enchaîner sans les remettre à jour → le planning repart d'une base fausse → erreurs en cascade sur les tâches dépendantes. Ce skill regroupe la sync derrière **un seul** point de décision. Périmètre : **memory AIDD + README** — pas de doc inline (Javadoc/JSDoc), pas de hook.

## Flux

`01-detect-scope` → `02-classify-impact` → puis, selon le régime de chaque cible :
- **reflet** (le code fait foi) → `03-sync-memory` → `04-sync-readme`
- **décision** (la décision fait foi) → `05-reconcile` (signaler, ne jamais écraser)

En coordinateur, le flux vaut **par repo** : chaque enfant traité comme un mono-repo (Boulot 1), plus le contrat partagé au parent traité en régime décision (Boulot 2, → `05`). Le home memory de l'enfant se résout à l'action `01` : **distribué** (memory chez l'enfant) ou **centralisé** (memory namespacée dans le parent `aidd_docs/memory/<enfant>/` — l'enfant reste code + README). Si `02` ne trouve aucune surface impactée, s'arrêter là.

## Actions

| # | Slug | Rôle | Input |
|---|---|---|---|
| 01 | `detect-scope` | Détecte topologie (mono/coordinateur) + propose et fait confirmer le scope de commits | CWD, opt-in WIP éventuel |
| 02 | `classify-impact` | Classe chaque fichier du scope en régime (reflet/décision) + cible doc | scope validé de 01 |
| 03 | `sync-memory` | MAJ memory AIDD reflet par repo, via `/10-learn` ou édition directe | cibles reflet memory de 02 |
| 04 | `sync-readme` | MAJ README reflet par repo (edits ciblés) + propose le commit doc | cibles reflet README de 02 |
| 05 | `reconcile` | Compare doc-vs-code à HEAD + signale les écarts des docs-décision | cibles décision de 02, ancre git non fiable |

## Régimes de doc — REFLET vs DÉCISION

Le mot « doc » recouvre deux choses d'autorité **opposée**. Confondre les deux fait écraser une décision d'équipe par du code, ou l'inverse. Toujours classer la surface (action 02) avant de la toucher.

| Régime | Ce que c'est | Exemples | Autorité | doc-sync fait |
|---|---|---|---|---|
| **Reflet** | *décrit* ce que le code fait déjà | README, memory `codebase-map` / `api-docs` / `database` | **le CODE fait foi** | **réécrit** la doc pour matcher le code |
| **Décision** | *prescrit* ce qui a été décidé/agréé | contrat partagé, ADR, memory `decisions` / `coding-assertions`, specs | **la DÉCISION fait foi** sur l'intention | **signale** l'écart code↔décision, **n'écrase jamais** seul |

Pourquoi ce garde-fou : quand le code s'écarte d'une décision (ex. un champ `category` non prévu au contrat), doc-sync ne peut pas savoir si c'est une découverte à entériner ou une bavure à corriger. Réécrire la décision seul graverait peut-être un bug dans la loi. Donc il met devant l'écart et **tu** tranches (action 05).

Cas qui se classe mal au premier regard — `coding-assertions` : que `./mvnw test` existe est un **fait**, donc du reflet ; en faire une **porte** avant chaque commit est une politique, donc de la décision. C'est le second qui gouverne le fichier, il part en régime décision. Un script `lint` ajouté à un enfant se **signale** (action 05) : c'est à l'humain de dire s'il gate. Le fait brut, lui, a son propre home en reflet (`<enfant>/tooling.md`, écrit par `memory-bootstrap`).

## La doc ne couvre que le VALIDÉ

La doc reflète l'état **commité / mergé**, jamais du code en vol : documenter du WIP = risque de décrire ce qui changera encore ou sera abandonné. Non négociable :
- **Défaut = commité only**, toujours.
- Scoper sur des **ranges de commits**, pas le working tree → le WIP sale d'une autre tâche est exclu sans effort (première barrière anti-contamination).
- **WIP non commité = opt-in explicite et averti**, réservé au cas rare où le code est figé mais pas encore commité.

## Topologie — autorité universelle, homes variables

L'autorité (régimes ci-dessus) est **universelle**. Ce qui change d'un projet à l'autre, c'est seulement **où chercher le code** et **combien de homes de doc** existent — c'est ce que l'action 01 détecte. Code-home et doc-home peuvent être **dissociés** : en coordinateur centralisé, le code vit dans l'enfant mais sa memory-reflet vit dans le parent (`aidd_docs/memory/<enfant>/`) — le commit memory atterrit alors au parent, le commit README chez l'enfant. En coordinateur, l'autorité s'établit **par fait** : le repo qui implémente fait foi (backend pour endpoints/DB/DTO, front pour routes UI/comportement consommé). Divergence entre enfants → signaler, pas deviner (action 05).

## Règle d'édition directe — lire la structure d'abord

Dès que le skill édite une surface doc **sans skill délégué qui en gouverne le style** (fallback memory en action 03, README en action 04), il doit **d'abord lire la structure/conventions existantes du fichier** (sections, format des tables, ton, niveaux de titre) et **s'y conformer**. Pourquoi : un skill délégué (`10-learn`) porte ses propres conventions ; en édition directe, rien ne gouverne le style — sans inspection préalable, on introduit une incohérence de forme qui dégrade la doc.

## Dependencies

- **`aidd-context:10-learn`** (plugin AIDD) — **optionnel**. Utilisé pour la memory AIDD (décisions durables). Si le framework est retiré, le skill **dégrade** : il édite `aidd_docs/memory/*` directement (action 03, cas B). Aucune autre dépendance externe.

## Pré-conditions

- Repo git, convention AIDD (`aidd_docs/memory/`) ET `README.md`. En coordinateur, le home memory de chaque enfant est **distribué** (chez l'enfant) ou **centralisé** (dans le parent, `aidd_docs/memory/<enfant>/`) : un enfant code-only **sans** `aidd_docs/` local n'est donc **pas** une anomalie si sa memory est centralisée au parent. Ne traiter comme « surface manquante » qu'un enfant qui n'a de memory **ni** locale **ni** centralisée.

## Garde-fous

- **Validé only** : jamais documenter du WIP hors opt-in averti.
- **Régime avant édition** : classer reflet vs décision. Les docs-décision se **signalent**, ne se réécrivent jamais seules.
- **Autorité = le code qui implémente** : pour un fait donné, le repo qui le code fait foi (backend pour l'API/DB, front pour l'UI). Divergence entre enfants → signaler, pas deviner.
- **Scope confirmé** : toujours montrer commits/fichiers (par repo) et laisser élaguer avant d'éditer. Ne pas deviner les frontières de tâche que git n'enregistre pas.
- **Édition ciblée only** : memory et README se patchent section par section ; une réécriture complète détruit le travail manuel et régresse en silence.
- **Vérifier avant d'affirmer** : ne pas écrire un comportement supposé — le confirmer dans le code d'abord.
- **S'arrêter si rien à faire** : diff sans impact doc → le dire, ne rien inventer.
- **Hors périmètre** : pas de doc inline (Javadoc/JSDoc/docstring), pas de hook. La doc inline est un **reflet** aussi, mais elle se rafraîchit **à chaud dans le flux de dev** (post-implémentation, contexte code déjà chargé, via l'agent `doc-writer`) — pas à froid ici, où la refaire imposerait un re-scan par-symbole coûteux et bruité. doc-sync = doc **à froid** (README/memory/contrat ↔ état validé) ; la doc inline = doc **à chaud**, ailleurs.
