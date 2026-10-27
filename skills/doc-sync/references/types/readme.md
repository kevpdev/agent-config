---
type: readme
sections:
  démarrer: [démarrage, démarrer, installation, installer, quickstart, getting started]
  comprendre: [comment, fonctionnement, architecture, concepts, comprendre, configure]
  changer: [changement, changer, modifier, développer, développement]
  consulter: [référence, reference, consulter, outillage]
  contribuer: [contribuer, contribution, contributing]
counted_nouns: [skills, règles, hooks, gardes, scripts, agents, actions, fichiers, commandes, batteries, dépôts, repos, services, outils, serveurs, plugins, endpoints, modules, tests, cas, vérifications, pièces]
inventory_min_items: 5
---

# Type README — ce qu'un README doit être

Les règles qu'un README suit, lues par l'agent avant de le réécrire. Le frontmatter est lu par `tools/check-doc.py`. Un repo les surcharge par `.doc-rules/readme.md` à sa racine, clé par clé, et le repo gagne sur la forme (`rules/autorite-des-conventions.md`).

## Un guide, pas un catalogue

Le README se lit dans l'ordre où le lecteur en a besoin. Ce fil a cinq étapes : démarrer, comprendre, changer, consulter, contribuer. Les titres varient d'un repo à l'autre, et `check-doc.py` reconnaît chaque étape par les mots-clés du frontmatter.

- **Une table d'entrée** sous le titre envoie vers les sections selon ce que le lecteur veut faire. Elle se relit à la main, aucun script ne juge qu'elle sert.
- **Le stable d'abord** : ce que fait le repo et pourquoi, puis comment s'en servir. L'état du jour (avancement, chiffres) sort vers le fichier qui en a la charge.

## Renvoyer, ne pas lister

- **Pas d'inventaire qui bouge.** Ni liste de skills, de règles ou de hooks, ni table de N gardes. Renvoyer à la source qui liste : un dossier, un manifeste, une commande.
- **Pas de compte d'éléments qui bougent** (« les 24 skills »). Aucun test ne signale qu'un chiffre écrit à la main est devenu faux.
- **Une mesure datée reste.** « Mesuré le 2026-08-27, 3 dépôts sur 33 » décrit un fait passé, donc il ne périme pas. `check-doc.py` laisse passer un compte quand sa ligne porte une date `AAAA-MM-JJ`.
- *Pourquoi, constaté le 2026-10-26 : le README d'`agent-config` portait six inventaires et comptes, dont un tableau de cinq gardes (PR #53).*

## Ce que la réécriture garde

- Les passages qui portent un piège vécu ou une mesure : ils se déplacent, ils ne se coupent pas.
- La langue et le ton du repo. Un README en anglais reste en anglais.
