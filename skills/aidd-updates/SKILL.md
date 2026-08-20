---
name: aidd-updates
description: >-
  Veille des plugins du framework AIDD : lit le changelog des versions en attente, en déduit ce qui
  casse dans les skills de ce repo, rédige un plan d'adaptation gardé sur disque, puis applique la
  montée de version et les patchs au moment choisi. Invocation manuelle uniquement, par
  `/aidd-updates` : le skill met à jour des plugins et patche des fichiers versionnés, deux effets de
  bord qu'un déclenchement probabiliste ne doit pas pouvoir provoquer.
disable-model-invocation: true
---

# aidd-updates — décider d'une montée de version AIDD en connaissance de cause

Claude Code sait appliquer une mise à jour de plugin, pas te dire ce qu'elle va casser. Le risque
n'est pas la montée elle-même, c'est que 16 noms de skills AIDD soient cités dans ce repo et qu'un
renommage upstream les rende muets sans erreur visible. Ce skill produit la décision, pas la mise à
jour.

## Actions

| # | Action | Rôle | Input |
|---|---|---|---|
| 01 | `actions/01-lire-etat.md` | lire l'état du détecteur, et brancher : plan valide, plan à refaire, ou rien à faire | aucun |
| 02 | `actions/02-planifier.md` | lire les changelogs des versions sautées, en déduire les patchs à faire ici, écrire le plan | l'état rendu par 01 |
| 03 | `actions/03-appliquer.md` | monter les plugins, appliquer les patchs, proposer l'entrée de `CHANGELOG-aidd.md` | un plan validé par l'humain |

## Flux

01 est toujours le point d'entrée. Il branche ensuite.

- Aucun retard → dire « à jour », s'arrêter. Ne pas dérouler 02.
- Plan déjà écrit et encore valide → le rendre tel quel, puis proposer 03. **Ne pas replanifier.**
- Retard sans plan, ou plan invalidé par une nouvelle version → 02, puis demander « maintenant ou
  plus tard ». Plus tard veut dire s'arrêter là, le plan reste sur disque.

## Règles transverses

- **Ne jamais écrire le front-matter du fichier d'état à la main.** Passer par les commandes du
  détecteur (`references/detecteur.md`).
  Pourquoi : un front-matter cassé par une édition libre rend le même symptôme qu'un plan absent, et
  le skill replanifierait à chaque appel sans que rien ne dise pourquoi.
- **Ne jamais lancer la montée de version sans un plan validé par l'humain**, même quand le changelog
  paraît anodin.
  Pourquoi : c'est exactement le comportement de l'auto-update, que ce montage existe pour remplacer.
- **Un renommage se prouve par un grep, pas par une lecture de changelog.** Citer le fichier et la
  ligne, jamais « il faudra vérifier les appels ».
  Pourquoi : un plan qui dit « vérifier » renvoie le travail à l'humain, alors qu'il déléguait pour
  s'en débarrasser.
- **Ce qui n'est pas cité dans ce repo ne va pas au plan.** Une nouveauté upstream sans impact ici se
  résume en une ligne, sans devenir une tâche.
  Pourquoi : 16 versions de changelog produisent des dizaines de changements, dont une poignée nous
  concerne. Tout lister noie la seule ligne qui compte.
