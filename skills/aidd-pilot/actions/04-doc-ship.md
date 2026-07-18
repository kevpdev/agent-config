# 04 — doc & ship

Post-implémentation : synchroniser la doc, puis clore. **Commit-only par défaut.**

## Doc — via doc-sync, routé par l'orchestrateur

On **n'appelle pas** `doc-sync` en le modifiant ; on lit sa sortie et on route selon la nature du doc. `doc-sync` reste source unique (non forké).

| Nature (classée par doc-sync) | aidd-pilot fait |
|---|---|
| **Doc-reflet** (README, memory descriptive) | réécrit + commit **en auto** |
| **Doc-décision bloquante** (contrat qui alimente un repo/phase **aval**) | **exécutée à la couture entre pipelines** (`02-pipeline`, F6), **pas à la clôture** : sync + verrou du contrat **avant** que le consommateur démarre ; pause arbitrage si choix lourd |
| **Doc-décision non-bloquante** (ADR qui acte une décision déjà prise, sans consommateur aval) | **accumulée** dans un lot « arbitrage à confirmer », surfacé en **fin de tunnel**, sans bloquer |

- Le tri bloquant/non-bloquant se fait sur un **fait vérifiable** : y a-t-il un consommateur aval dans le plan / la topologie ? (pas au jugé — directive prime).
- Passer aussi par `aidd-context:10-learn` pour la memory AIDD si des conventions/décisions durables ont émergé.
- **Lot « arbitrage à confirmer » (v1)** : liste compacte, un item = **décision actée** · **pourquoi non-bloquant** (pas de consommateur aval) · **ce qui reste à confirmer**. Rendu dans la section 5 du recap. À affiner après runs.

## Commit doc

`aidd-vcs:01-commit` — commit séparé pour la doc + le plan (`docs(...)`), après les commits de phase.

- **Branch-first ici aussi** : tout repo où l'on committe suit la règle VCS de `02-pipeline` (jamais la branche par défaut). Cas fréquent : le repo **coordinateur** ne porte que de la doc (contrat) et n'a pas traversé la boucle repo → le brancher (`docs/<slug>`) avant son commit de contrat.

## Clôture — recap storytelling dans le chat

Le tunnel **s'arrête aux commits locaux**. Pas de push, pas de MR : c'est le **point de contrôle humain**. On ne compose PAS `aidd-vcs:02-pull-request` (brique non adaptée, principe F3 — elle ouvre une vraie MR draft en ligne, ce qui n'est pas voulu). Le push et la MR restent **100% dans les mains de l'humain**.

**Pourquoi ce format** : Kevin (TDAH) garde la main pour repérer une incohérence avant tout push. Un recap structuré + storytelling porte l'info à charge cognitive minimale ; un dump brut la sature.

Le livrable final = un **recap dans le chat**, structuré ainsi (verdict en tête, voix directe, phases lisibles dans le désordre) :

1. **Le fil** — ce que la feature voulait, en une phrase.
2. **Par phase, avant → après** — ce qui a changé concrètement (fichiers / comportement), pas le détail technique brut.
3. **Preuves de validation** — tests verts, captures e2e, sorties curl (l'évidence de la ladder, `03-validate`).
4. **Les commits posés** — liste (hash + message), pour inspection **avant** tout push.
5. **En attente / à trancher** — arbitrages doc-décision non-bloquants accumulés, TODO, ambiguïtés.
6. **La main te revient** — push et MR = décision humaine ; rappeler d'arrêter l'instance (`stop()` du testeur) si elle ne sert plus.

- **Gabarit recap (v1)** : les 6 blocs ci-dessus, verdict en tête, **1 ligne par phase** (charge cognitive minimale), commits en liste hash+message. Longueur cible : tient en un écran. À affiner après quelques runs.
