---
name: doc-sync
disable-model-invocation: true
description: >-
  Synchronise la doc avec l'état VALIDÉ du code (commité/mergé) quand elle a pris
  du retard. Deux régimes : les docs-REFLET (README, memory descriptive), dont le
  code fait foi et que le skill réécrit ; les docs-DÉCISION (contrat partagé, ADR,
  memory decisions), que le skill ne réécrit jamais seul — il signale l'écart
  code↔décision et laisse l'utilisateur arbitrer. Détecte la topologie (mono-repo ou repo
  coordinateur) et fait confirmer le scope avant d'éditer. Côté memory, enchaîne
  cadrage (ce qui mérite d'exister), livraison via /10-learn, puis contrôle par un checker
  indépendant ; met ensuite les README à jour par repo. Invocation manuelle uniquement, par `/doc-sync` :
  le skill réécrit des fichiers versionnés, il ne se déclenche pas au fil de la conversation.
  NE PAS utiliser pour un fix sans impact doc, pour committer seul (→ aidd-vcs:01-commit), ni pour
  documenter du code non validé.
---

# doc-sync — synchroniser la doc avec le code validé

Après un dev qui change l'archi ou le schéma DB, la memory AIDD (`aidd_docs/memory/*`, relue par `/plan` et le brainstorming) et le README désynchronisent silencieusement. Enchaîner sans les remettre à jour → le planning repart d'une base fausse → erreurs en cascade sur les tâches dépendantes. Ce skill regroupe la sync derrière **un seul** point de décision. Périmètre : **memory AIDD + README** — pas de doc inline (Javadoc/JSDoc), pas de hook.

## Flux

`01-detect-scope` → `02-classify-impact` → puis, selon le régime de chaque cible :
- **reflet** (le code fait foi) → `03-frame-memory` → `04-deliver-memory` → `05-check-memory` → `06-sync-readme`
- **décision** (la décision fait foi) → `07-reconcile` (signaler, ne jamais écraser)

Le triptyque memory reprend les mots de `aidd-orchestrator:01-sdlc` — **frame** décide ce qui mérite d'exister, **deliver** écrit, **check** fait juger par un agent qui n'a pas écrit. *Pourquoi trois étapes et non une : sans cadrage, la mémoire grossit à chaque passe puisque rien ne dit ce qui n'a pas à y entrer ; sans contrôle indépendant, c'est celui qui a écrit qui juge son intention au lieu de son résultat.* `05-check-memory` route ses constats vers l'étape qui les répare, il ne corrige rien lui-même.

**Le cycle est borné à deux retours**, donc trois contrôles au plus, et il s'arrête plus tôt si un constat déjà déclaré réparé revient ou si le lot ne rétrécit pas. À la borne, le skill **échoue fermé** : il ne déclare pas le banc à jour, il rend l'état intermédiaire à l'humain. *Pourquoi une borne et non la convergence : au-delà de quelques passes, un modèle dégrade sa propre pertinence et se met à réparer ce qu'il vient d'écrire. Sans compteur, le cercle vicieux n'a pas de condition d'arrêt, et il coûte d'autant plus qu'il a l'air productif.*

En coordinateur, le flux vaut **par repo** : chaque enfant traité comme un mono-repo (Boulot 1), plus le contrat partagé au parent traité en régime décision (Boulot 2, → `07`). Le home memory de l'enfant se résout à l'action `01` : **distribué** (memory chez l'enfant) ou **centralisé** (memory namespacée dans le parent `aidd_docs/memory/<enfant>/` — l'enfant reste code + README). Si `02` ne trouve aucune surface impactée, s'arrêter là.

## Actions

| # | Slug | Rôle | Input |
|---|---|---|---|
| 01 | `detect-scope` | Détecte topologie (mono/coordinateur) + propose et fait confirmer le scope de commits | CWD, opt-in WIP éventuel |
| 02 | `classify-impact` | Classe chaque fichier du scope en régime (reflet/décision) + cible doc | scope validé de 01 |
| 03 | `frame-memory` | Décide ce qui mérite d'exister : garder / pointeur / sortir, sans rien écrire | cibles reflet memory de 02 + état du banc |
| 04 | `deliver-memory` | Écrit le plan cadré, via `/10-learn` ou édition directe | plan de 03 |
| 05 | `check-memory` | Fait juger par `@aidd-dev:checker` et route les constats | fichiers touchés par 04 + plan de 03 |
| 06 | `sync-readme` | MAJ README reflet par repo (edits ciblés) + propose le commit doc | cibles reflet README de 02 |
| 07 | `reconcile` | Compare doc-vs-code à HEAD + signale les écarts des docs-décision | cibles décision de 02, ancre git non fiable |

## Régimes de doc — REFLET vs DÉCISION

Le mot « doc » recouvre deux choses d'autorité **opposée**. Confondre les deux fait écraser une décision d'équipe par du code, ou l'inverse. Toujours classer la surface (action 02) avant de la toucher.

| Régime | Ce que c'est | Exemples | Autorité | doc-sync fait |
|---|---|---|---|---|
| **Reflet** | *décrit* ce que le code fait déjà | README, memory `codebase-map` / `api-docs` / `database` | **le CODE fait foi** | **réécrit** la doc pour matcher le code |
| **Décision** | *prescrit* ce qui a été décidé/agréé | contrat partagé, ADR, memory `decisions` / `coding-assertions`, specs | **la DÉCISION fait foi** sur l'intention | **signale** l'écart code↔décision, **n'écrase jamais** seul |

Pourquoi ce garde-fou : quand le code s'écarte d'une décision (ex. un champ `category` non prévu au contrat), doc-sync ne peut pas savoir si c'est une découverte à entériner ou une bavure à corriger. Réécrire la décision seul graverait peut-être un bug dans la loi. Donc il met devant l'écart et **tu** tranches (action 07).

Cas qui se classe mal au premier regard — `coding-assertions` : que `./mvnw test` existe est un **fait**, donc du reflet ; en faire une **porte** avant chaque commit est une politique, donc de la décision. C'est le second qui gouverne le fichier, il part en régime décision. Un script `lint` ajouté à un enfant se **signale** (action 07) : c'est à l'humain de dire s'il gate. Le fait brut, lui, a son propre home en reflet (`<enfant>/tooling.md`, écrit par `memory-bootstrap`).

**Où passe la coupe à l'intérieur d'une telle surface** : *si l'édition ne change aucune commande de porte ni aucun prérequis bloquant, c'est du reflet*. La table des commandes, ses prérequis et le recensement des repos sans porte ne bougent donc pas. La prose de détail qui vit déjà dans la fiche d'un enfant, elle, sort vers son home et laisse un pointeur. *Pourquoi : déplacer une explication n'arbitre aucune décision, puisque ça ne change pas ce qui gate. Sans cette coupe, un index de portes grossit indéfiniment — le régime décision le protège aussi de son propre ménage.*

## La doc ne couvre que le VALIDÉ

La doc reflète l'état **commité / mergé**, jamais du code en vol : documenter du WIP = risque de décrire ce qui changera encore ou sera abandonné. Non négociable :
- **Défaut = commité only**, toujours.
- Scoper sur des **ranges de commits**, pas le working tree → le WIP sale d'une autre tâche est exclu sans effort (première barrière anti-contamination).
- **WIP non commité = opt-in explicite et averti**, réservé au cas rare où le code est figé mais pas encore commité.

## Topologie — autorité universelle, homes variables

L'autorité (régimes ci-dessus) est **universelle**. Ce qui change d'un projet à l'autre, c'est seulement **où chercher le code** et **combien de homes de doc** existent — c'est ce que l'action 01 détecte. Code-home et doc-home peuvent être **dissociés** : en coordinateur centralisé, le code vit dans l'enfant mais sa memory-reflet vit dans le parent (`aidd_docs/memory/<enfant>/`) — le commit memory atterrit alors au parent, le commit README chez l'enfant. En coordinateur, l'autorité s'établit **par fait** : le repo qui implémente fait foi (backend pour endpoints/DB/DTO, front pour routes UI/comportement consommé). Divergence entre enfants → signaler, pas deviner (action 07).

## Règle d'édition directe — lire la structure d'abord

Dès que le skill édite une surface doc **sans skill délégué qui en gouverne le style** (fallback memory en action 04, README en action 06), il doit **d'abord lire la structure/conventions existantes du fichier** (sections, format des tables, ton, niveaux de titre) et **s'y conformer**. Pourquoi : un skill délégué (`10-learn`) porte ses propres conventions ; en édition directe, rien ne gouverne le style — sans inspection préalable, on introduit une incohérence de forme qui dégrade la doc.

## Dependencies

- **`aidd-context:10-learn`** (plugin AIDD) — **optionnel**. Utilisé pour la memory AIDD (décisions durables). Si le framework est retiré, le skill **dégrade** : il édite `aidd_docs/memory/*` directement (action 04, cas B). Aucune autre dépendance externe.

## Pré-conditions

- Repo git, convention AIDD (`aidd_docs/memory/`) ET `README.md`. En coordinateur, le home memory de chaque enfant est **distribué** (chez l'enfant) ou **centralisé** (dans le parent, `aidd_docs/memory/<enfant>/`) : un enfant code-only **sans** `aidd_docs/` local n'est donc **pas** une anomalie si sa memory est centralisée au parent. Ne traiter comme « surface manquante » qu'un enfant qui n'a de memory **ni** locale **ni** centralisée.

## Garde-fous

- **Validé only** : jamais documenter du WIP hors opt-in averti.
- **Régime avant édition** : classer reflet vs décision. Les docs-décision se **signalent**, ne se réécrivent jamais seules.
- **Autorité = le code qui implémente** : pour un fait donné, le repo qui le code fait foi (backend pour l'API/DB, front pour l'UI). Divergence entre enfants → signaler, pas deviner.
- **Scope confirmé** : toujours montrer commits/fichiers (par repo) et laisser élaguer avant d'éditer. Ne pas deviner les frontières de tâche que git n'enregistre pas.
- **Édition ciblée only** : memory et README se patchent section par section ; une réécriture complète détruit le travail manuel et régresse en silence.
- **Une entrée qui recopie un fichier du disque n'entre pas** : ni arbre de fichiers, ni schéma, ni liste de scripts, ni extrait de config — un **pointeur de chemin** la remplace. Le critère complet vit dans `references/memory-criteria.md`, ce garde-fou est le seul volet qui doit être connu **avant** de charger quoi que ce soit. *Pourquoi : la copie et sa source ne divergent pas au même rythme, donc la copie devient un piège au lieu d'un raccourci.*
- **Vérifier avant d'affirmer** : ne pas écrire un comportement supposé — le confirmer dans le code d'abord.
- **S'arrêter si rien à faire** : diff sans impact doc → le dire, ne rien inventer.
- **Hors périmètre** : pas de doc inline (Javadoc/JSDoc/docstring), pas de hook. La doc inline est un **reflet** aussi, mais elle se rafraîchit **à chaud dans le flux de dev** (post-implémentation, contexte code déjà chargé, via l'agent `doc-writer`) — pas à froid ici, où la refaire imposerait un re-scan par-symbole coûteux et bruité. doc-sync = doc **à froid** (README/memory/contrat ↔ état validé) ; la doc inline = doc **à chaud**, ailleurs.
