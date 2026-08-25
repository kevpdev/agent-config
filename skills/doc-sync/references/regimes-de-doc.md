# Régimes de doc — reflet contre décision

Qui fait foi selon la surface touchée, et où vivent les homes de doc quand le projet est un coordinateur. Chargée par les actions `02`, `04` et `07`, avant de classer ou de toucher une surface.

## Les deux régimes

Le mot « doc » recouvre deux choses d'autorité **opposée**. Confondre les deux fait écraser une décision d'équipe par du code, ou l'inverse. Toujours classer la surface (action `02`) avant de la toucher.

| Régime | Ce que c'est | Exemples | Autorité | doc-sync fait |
|---|---|---|---|---|
| **Reflet** | *décrit* ce que le code fait déjà | README, memory `codebase-map` / `api-docs` / `database` | **le CODE fait foi** | **réécrit** la doc pour matcher le code |
| **Décision** | *prescrit* ce qui a été décidé ou agréé | contrat partagé, ADR, memory `decisions` / `coding-assertions`, specs | **la DÉCISION fait foi** sur l'intention | **signale** l'écart code↔décision, **n'écrase jamais** seul |

Pourquoi ce garde-fou : quand le code s'écarte d'une décision, par exemple un champ `category` non prévu au contrat, doc-sync ne peut pas savoir si c'est une découverte à entériner ou une bavure à corriger. Réécrire la décision seul graverait peut-être un bug dans la loi. Le skill met donc l'écart devant l'humain, à qui revient l'arbitrage (action `07`).

## Le cas qui se classe mal au premier regard

`coding-assertions`. Que `./mvnw test` existe est un **fait**, donc du reflet. En faire une **porte** avant chaque commit est une politique, donc de la décision. C'est le second qui gouverne le fichier, il part en régime décision.

Un script `lint` ajouté à un enfant se **signale** (action `07`) : c'est à l'humain de dire s'il gate. Le fait brut, lui, a son propre home en reflet, `<enfant>/tooling.md`, écrit par `memory-bootstrap`.

## Topologie — autorité universelle, homes variables

L'autorité des deux régimes est **universelle**. Ce qui change d'un projet à l'autre, c'est seulement **où chercher le code** et **combien de homes de doc** existent, et c'est ce que l'action `01` détecte.

Code-home et doc-home peuvent être **dissociés**. En coordinateur centralisé, le code vit dans l'enfant mais sa memory de reflet vit dans le parent (`aidd_docs/memory/<enfant>/`). Le commit memory atterrit alors au parent, le commit README chez l'enfant.

En coordinateur, l'autorité s'établit **par fait** : le repo qui implémente fait foi. Le backend fait foi sur les endpoints, le schéma DB et les DTO. Le front fait foi sur les routes UI et le comportement consommé. Une divergence entre deux enfants se signale au lieu de se deviner (action `07`).
