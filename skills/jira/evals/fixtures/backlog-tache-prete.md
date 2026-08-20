---
type: task
status: ready
source: aidd_docs/tasks/2000_01/2000_01_01_archivage-depots/cadrage.md
---

# Task: archiver les dépôts décommissionnés sans les supprimer

## Outcome

Les dépôts décommissionnés sont marqués archivés côté forge, en lecture seule, et ils n'apparaissent
plus dans les inventaires d'outillage.

## Scope

- Includes: la pose du drapeau d'archivage, et la mise à jour de l'inventaire qui les listait
- Excludes: la suppression d'un dépôt, et la migration de son historique

## Done When

- Un dépôt décommissionné refuse un push et reste clonable.
- L'inventaire d'outillage ne le compte plus parmi les dépôts actifs.

## Completion Evidence

- La sortie de l'inventaire avant et après, avec le décompte qui change.

## Cancellation

<why it is no longer pursued>
