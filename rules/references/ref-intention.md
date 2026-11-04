# Référence — `intention.md`

## Le cas d'origine (2026-11-04, issue #90)

L'utilisateur écrit « oui, mergée, lance la bascule ». La PR #91 était encore en draft, pendant un incident GitHub sur les opérations Git. `bascule.sh` refuse parce que `main` n'a pas bougé. Je m'arrête et je demande : « Je passe la #91 en ready, je la merge, puis je lance la bascule ? ».

La réponse de l'utilisateur : « tu dois agir en respectant l'intention et non les règles littérales, sinon tu risques de bloquer et de m'attendre à chaque événement non mentionné littéralement ». Puis : « la lecture stricte est bien pour les tests ou les vérifications strictes », et « je dois savoir tout ce que tu as fait ».

La règle découle du principe « l'agent sert l'intention, pas la commande littérale » de `rules/ai-principles.md`. Elle dit où ce principe s'arrête.

## Pourquoi les bornes de la règle

- **« Hors de ma branche de travail » plutôt que « visible dehors »** : un push de branche est visible sur GitHub. Le mot « visible » seul aurait renversé la permission de `aidd.md`, ou n'aurait rien protégé.
- **« Contourner ne vise jamais un garde »** : un push refusé par un hook est un refus de garde. Sans cette phrase, « contourner un push refusé » pouvait se lire comme un `--no-verify`.
- **« Un état présenté comme acquis » borné à mon propre travail** : « mergée » décrit un fait que l'utilisateur croit vrai. Sur sa propre PR, le produire est ce qu'il veut. « C'est déployé » alors que rien ne l'est ne doit pas déclencher un déploiement en production.
- **Le choix d'approche reste à `plan-mode.md`** : sans cette exclusion, « corrige X » nomme l'état « X corrigé » et la règle aurait dit de faire, contre `plan-mode.md`. L'alignement de `plan-mode.md` se décide dans #90.
## Base de mesure (2026-11-04)

`python3 tools/measure-approvals.py --days 31` : 110 sessions Claude Code, 1 191 questions d'approbation en fin de tour, dont 324 « oui » nus (27 %). Le total vient de la ligne `bare yes total` de la sortie. Les colonnes par motif se recouvrent, une question pouvant relever de deux motifs, donc leur somme est plus grande.

Parts de « oui » nus par motif : push de branche ou PR draft 54 %, ménage après merge 52 %, bascule 50 %, push sur la branche par défaut 50 %, « je pars sur ça » 38 %, merge 37 %, commit 37 %, étape suivante d'un plan 37 %, lecture seule 27 %, création d'issue 14 %.

Si la règle tient, le nombre de questions par session et la part de « oui » nus doivent baisser. Rejouer la même commande quelques semaines après le merge.
