---
name: jira
description: "Publie un brouillon de backlog AIDD vers Jira, et rattache la clé du ticket créé au fichier du dépôt. Délègue toute la rédaction aux skills aidd-pm du type visé, et ne porte que ce que le framework AIDD n'a pas : le champ qui pointe le ticket, le gel du brouillon à la publication, la mise en forme du texte envoyé, et la demande avant toute écriture. Invocation manuelle uniquement, par `/jira` : il écrit un fichier versionné et crée un ticket que personne ne pourra supprimer. NE PAS utiliser pour rédiger le brouillon lui-même (→ aidd-pm:10-task, 02-user-stories, 07-epic, 09-defect, 05-spike), ni pour piloter un backlog entier (→ aidd-orchestrator:02-backlog)."
disable-model-invocation: true
argument-hint: "[chemin du brouillon | besoin à cadrer]"
---

# jira

Fait le pont entre un artefact de backlog du dépôt et son ticket Jira. Le framework AIDD écrit le
brouillon, ce skill lui donne une clé de ticket et l'y envoie.

> [!important] Ce skill ne rédige rien
> Le brouillon appartient au skill `aidd-pm` de son type, qui porte son cycle de vie, ses relations et
> ses critères de maturité. *Pourquoi : réécrire cette logique ici la dédoublerait et perdrait une
> trentaine de fichiers de connaissance qu'aucun skill maison ne reproduit.*

## Le flux

```
besoin ou brouillon → 01-brouillon → 02-publier → ticket + clé rattachée
                            ↑              │
                            └──────────────┘  (brouillon à reprendre)
```

- **Brouillon déjà écrit** dans `aidd_docs/backlog/` : entrer direct dans `02-publier`.
- **Besoin encore informe** : passer par `01-brouillon`, qui délègue puis contrôle.

## Actions

| Étape | Fichier | Rôle |
|---|---|---|
| Brouillon | `actions/01-brouillon.md` | choisir le type, déléguer la rédaction au skill `aidd-pm`, contrôler l'artefact contre les conventions du dépôt |
| Publication | `actions/02-publier.md` | mettre en forme, demander, créer le ticket, rattacher la clé, geler le brouillon |

## Règles transverses

- **La mémoire du dépôt fait autorité sur tout ce qui est propre au projet.** Le site Jira, les clés
  de projet autorisées, la convention de scope, le banc d'essai : lus dans la mémoire, jamais codés
  ici. *Pourquoi : ce skill est partagé publiquement, donc aucune donnée d'un client n'y entre. Et
  c'est le mécanisme prévu par le framework, dont `01-ticket-info/references/tool-detection.md` place
  l'outil de ticketing dans la mémoire projet.*
- **Rien ne part vers Jira sans une demande explicite à l'humain**, nommant le ticket visé et ce que
  l'appel va écrire. *Pourquoi : un ticket créé ne se supprime pas forcément, le droit de suppression
  n'étant ni acquis pour l'humain ni exposé par le connecteur MCP. Une écriture est donc définitive.*
- **Un garde déterministe peut tenir la porte, et il a le dernier mot.** Si le dépôt en déclare un, son
  refus n'est pas un obstacle à contourner mais la réponse : demander à l'humain ce que le message du
  garde réclame. *Pourquoi : réessayer un appel refusé transforme un garde en ralentisseur.*
- **Jira fait foi après publication, le dépôt garde le raisonnement.** Le brouillon devient un
  instantané de ce qui a été soumis, jamais le miroir du ticket vivant. *Pourquoi : l'équipe corrige
  les tickets publiés, donc une copie dans le dépôt divergerait en silence.*
- **Aucune modification d'un ticket existant.** Ce skill crée, commente et relie. Éditer, transitionner
  ou pointer du temps appartient à l'humain. *Pourquoi : qui déplace un ticket en répond, et
  l'historique dit qui a décidé, pas quel outil a tapé.*
