# Grille de décision — Déterministe / LLM / Agent

> Référence partagée. Citée par `ai-engineering` (fiabilité d'une app LLM) et `agentic-architect` (orchestration). Décision d'entrée commune avant toute conception d'une feature qui utilise un LLM.

## La grille

Décomposer la tâche en étapes ; classer **chaque étape isolément** (Cartesian) :

| Étape | Critère | Choix |
|---|---|---|
| **Code / outil déterministe** | exprimable en code *et assez bon* (pas juste « possible ») | code, regex, fonction, requête SQL |
| **Un appel LLM borné** | demande du jugement flou, mais reste un **slot dans une séquence figée** | 1 appel LLM (ce n'est **pas** un agent) |
| **Agent** | une étape doit **piloter le flow au runtime** : choisir/enchaîner ses actions, s'adapter, boucler | agent (Task, tool-use en boucle) |

**Ordre par défaut** : déterministe d'abord → LLM borné si jugement requis → agent **seulement** si flow piloté au runtime.

## Le discriminant agent vs workflow

**Qui contrôle le flow ?**
- Le **code** décide les étapes, le LLM remplit un slot → **workflow** (LLM-augmenté).
- Le **LLM** décide la prochaine action et s'adapte → **agent**.

**Ne pas confondre avec l'agence** :
- *« Je ne détaille pas le process / boîte noire »* ≠ agentique — un endpoint qui cache un pipeline figé reste un workflow. L'encapsulation n'est pas l'agence.
- *Modèle local vs API* = axe **infra/déploiement**, orthogonal à l'agence. Un agent peut tourner sur API, un simple appel en local.

## Pourquoi cet ordre (coût)

Un agent paie **tokens + latence + garde-fous à chaque exécution** ; un workflow paie **une fois au design**. Réserver l'agent aux cas où l'intelligence au runtime est *vraiment* nécessaire.

## Insight de convergence

Un agent qu'on **fiabilise** en empilant des étapes de validation **converge vers un workflow** : les garde-fous qui le rendent fiable *sont* le pipeline déterministe. Partir de l'agent pour une tâche à procédure connue = chemin long pour réatterrir sur le workflow.

**Red flag** : choisir « agent » parce que c'est moderne / cohérent avec le reste → refaire l'analyse étape par étape hors-contexte.
