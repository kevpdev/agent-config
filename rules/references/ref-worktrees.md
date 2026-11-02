# Références — `rules/worktrees.md`

Ce qui sert à qui édite la règle, pas à qui l'applique. Jamais chargé automatiquement. Sortis de la règle le 2026-10-28, texte d'origine.

---

## Pourquoi les commandes Orca ne sont pas dans la règle

**Les commandes ne sont pas recopiées ici** : le CLI change avec les versions d'Orca. Depuis le 2026-11-02 (issue #76), elles vivent dans `tools/worktree.sh`, que sa batterie `tools/tests/test-worktree.sh` couvre.

## Pourquoi un routeur et non « créer par Orca » (2026-11-02)

L'ancienne section « Dans Orca » disait de créer par Orca dès que `ORCA_WORKTREE_ID` était défini, décision de l'utilisateur du 2026-10-28. Son pourquoi, mesuré le même jour : 2 dépôts sur 3 enregistrés dans Orca cachaient les worktrees créés hors d'Orca (`externalWorktreeVisibility: hide`). Le 2026-11-02, les trois dépôts sont passés à `show`, et le choix entre Orca et git est passé dans le script, pour que le harnais marche aussi sans Orca (cadrage `audits/2026-11-02-cadrage-workflow-coeur.md`, Q3).

## Le worktree hors d'agent-config

Ailleurs, le worktree évite le `stash` et le fichier oublié au changement de branche.

## Ce qu'Orca apporte en plus

Un worktree Orca rattache aussi l'issue et lance un agent avec son brief en une seule commande.

## Pourquoi un agent dédié implémente et un autre relit (2026-11-02)

Décision de l'utilisateur du 2026-11-02. La session principale garde le contexte de l'ensemble. Un relecteur qui n'a pas écrit le code n'hérite pas de ses angles morts.
