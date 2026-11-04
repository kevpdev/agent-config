# Références — les portes : où déranger l'humain, et sur quoi poser la garde

Doctrine à lire quand on pose, maintient ou retire une porte dans le harnais : un skill en appel manuel (`disable-model-invocation`), une question d'approbation prescrite par une règle ou un skill, un garde déterministe. La question posée en cours de session relève de `rules/intention.md`, pas d'ici.

## Le critère : l'équilibre, pas la porte par défaut

Le but est l'équilibre entre l'autonomie de l'agent et la boucle humaine. L'humain est dérangé quand sa décision change le résultat, jamais pour chaque petite action.

Une porte coûte à chaque usage, qu'elle serve ou non. Elle doit donc gagner sa place. Elle se pose sur l'acte et sa cible, jamais sur l'intention.

**Ce que ça garde de `ai-principles.md`** : « Garder l'humain dans la boucle d'approbation » reste vrai. L'humain approuve là où il endosse le résultat : merge, publication, choix d'une approche. Le merge et la publication gardent leur question par `intention.md`, sauf quand l'utilisateur a déjà nommé l'état visé. Le choix d'une approche garde la sienne par `plan-mode.md`. Ce qui sort de la boucle, ce sont les étapes réversibles entre deux de ces points. Elles se font, puis se listent dans le compte rendu.

## Trois entrées

| Entrée | Ce qu'elle pèse | Comment elle se lit |
|---|---|---|
| frottement | ce que la porte coûte à chaque usage | la part de « oui » nus, `tools/measure-approvals.py` |
| perte espérée | ce que coûte l'erreur quand elle arrive | la réversibilité : `git restore`, `git revert`, `reflog`, suppression d'un fichier neuf |
| sensibilité de la cible | ce que l'acte atteint | une cible déclarée : alias, nom de branche, préfixe de dépôt |

## Deux conditions, sans lesquelles le calcul ne vaut rien

- **Lisible sans le modèle.** La cible se reconnaît par une donnée, pas par un jugement. Si l'agent décide lui-même « ici c'est la prod », la porte repose sur celui qu'elle doit contenir.
- **Vivante.** Un garde signale qu'il ne protège aucune cible quand sa liste est vide ou ne correspond plus à rien. Une liste morte protège zéro cible et se lit comme une protection.

## Où chaque levier vaut

| Levier | Où il se pose mal | Où il vaut | Sa mesure |
|---|---|---|---|
| `disable-model-invocation` | sur le déclenchement | si l'effet reste irréversible après coup, ou si le moment du déclenchement doit rester à l'humain (second motif de R13) | l'éval de déclenchement |
| question d'approbation | sur l'intention | seulement si la perte n'est pas récupérable, ou si l'humain endosse le résultat | la part de « oui » nus |
| garde déterministe | sur un acte nu | sur l'acte et sa cible déclarée | l'incident qui l'a justifié |

L'appel manuel ne borne rien une fois le skill ouvert : il bloque le déclenchement légitime et laisse passer tout ce que le skill fait ensuite. Contre un acte dangereux, le garde sur l'acte et sa cible est le levier qui borne. R13 de `skills/skill-craft/references/skill-authoring-fr.md` applique ce critère aux skills.

## Les cas qui fondent la doctrine (2026-11-04, issue #90, proposition 5)

- **Un skill de création de projet (#93) livré en appel manuel.** Il ne partait donc pas sur « je veux créer un projet ». La raison invoquée était R13, appliquée à un `mkdir`, alors que supprimer un dossier neuf rattrape l'effet.
- **Un garde supposé.** Le même skill affirmait que `hooks/no_remote_write.py` gardait `gh repo create` et `git push`. Mesuré par `hooks/check.py --guard no_remote_write`, les deux passent avec un code retour 0. Dans la même mesure, un `docker compose down` par ssh vers un alias de la liste est refusé : ce garde vise les serveurs distants déclarés, pas les dépôts. Sa liste, écrite dans le code, ne visait plus aucune cible active. #98 l'a sortie vers `~/.config/agent-config/protected-hosts`, et la bascule signale désormais une liste vide ou morte.
- **Le défaut commun** : une porte posée sur l'intention au lieu de l'acte. La première bloque l'usage légitime. La seconde rassure sans rien couvrir.

## Signal de révision

Cette doctrine sert quand on pose ou retire une porte, un geste rare, d'où le rangement « à la demande » d'`audits/grille-harnais.md`. Trois sessions qui la chargent en un mois la font monter en règle permanente.

Le compteur : `python3 tools/measure-reference-loads.py --days 31 --ref ref-portes.md`. Il compte les appels `Read` des transcripts Claude Code, sous-agents compris, et écarte les sessions qui éditent la même référence. Il ne voit ni une lecture par `cat`, ni OpenCode. Calibré le 2026-11-04 sur 110 sessions et leurs sous-agents. Il trouve 8 lectures de références, toutes dans des sessions qui éditaient la référence lue, donc zéro lecture d'usage. Avant ce filtre, `ref-ci-github.md` aurait compté 3 lectures dans 2 sessions, toutes de maintenance.
