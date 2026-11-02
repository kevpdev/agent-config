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

## Un worktree créé par git apparaît dans Orca (mesuré le 2026-11-02)

Le dépôt `agent-config` est réglé sur `externalWorktreeVisibility: show`. Un worktree créé par `tools/worktree.sh` au rang 3, puis un autre au rang 2, apparaissent tous deux dans `orca-ide worktree list --json`, au chemin d'Orca et sous leur branche.

Ils diffèrent d'un worktree natif par leurs métadonnées. `creatorProvenance`, `cliProvenance` et `baseRef` y valent `null`. Le nom affiché est la branche (`kevpdev/essai-rang3-76`, mode `automatic`) au lieu du nom court (mode `fixed`).

`orca-ide worktree rm` les retire comme un natif, branche locale comprise. Cette mesure tranche le point « non établi » de l'issue #76 sur le rang 2, pour l'affichage et le retrait. Le rattachement après coup par `orca-ide worktree set` n'a pas été mesuré.

## Pourquoi le retrait passe par `remove` (2026-11-02)

Constaté le 2026-11-02 sur les PR #72 et #77. Un `git branch -D` lancé juste après `orca-ide worktree rm` a échoué, parce que le retrait par Orca n'était pas fini. Un peu plus tard, la branche avait disparu, supprimée par Orca lui-même.

Le ménage à la main tenait donc mal l'ordre et l'outil. Depuis l'issue #80, `tools/worktree.sh remove <nom>` s'en charge. Ses étapes et ses refus sont dans l'en-tête du script, section REMOVE.
