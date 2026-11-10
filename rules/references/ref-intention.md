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

## Une tâche confiée va jusqu'à la PR draft (2026-11-10, issue #90)

**La mesure qui l'a déclenchée.** `python3 tools/measure-approvals.py --days 6`, rejouée après les retraits de la #90 : 35 sessions, 243 questions, 78 « oui » nus (32 %), contre 27 % de base. « je pars sur ça » fait 21 questions à 47 % de « oui » nus. Les 20 questions « commit » à 60 % se décomposent à la lecture de `--detail` : environ 9 dans le vault, qui committe sur `main` et sort de la #91, environ 6 faux positifs du détecteur (le mot « commit » dans une question qui porte sur autre chose), et 3 vrais écarts à la #91 sur une branche de travail. Quelques sessions de la fenêtre datent d'avant les retraits, `--days` les compte par date de fichier.

**Ce qu'a dit l'utilisateur** (orthographe corrigée). « tu dois incarner un collègue assistant. Donc quand je te demande de faire une tâche, tu dois avoir un minimum d'autonomie et de libre arbitre, quitte à prendre le risque de faire quelques erreurs que tu peux corriger par itération. » Puis : « Le risque est le ratio temps/coût par rapport aux erreurs. D'où l'intérêt de demander avant de se lancer dans des travaux coûteux, comme un humain le ferait avec son référent. » Et sur le plan, sous forme de question : « La demande d'approbation avant un plan doit-elle être systématique ? Car c'est une étape importante qui conditionne l'implémentation. L'humain doit garder le contrôle je pense. » La validation systématique de tout plan a été proposée en réponse, puis acceptée par « oui ajoute-les et représente le plan ».

**Pourquoi tout plan se valide, et pas seulement les plans coûteux.** Un plan engage une direction, et refuser une direction après l'exécution jette tout. Le coût sert à décider si le travail mérite un plan. Il ne sert jamais à sauter la validation d'un plan écrit.

**Pourquoi annoncer sans attendre le peu coûteux.** Trois formes ont été proposées : rien avant et compte rendu à la fin, une ligne d'annonce sans attente, un plan court à valider. L'utilisateur a choisi l'annonce. Elle laisse l'interrompre tôt sans lui faire payer d'attente.

**Pourquoi la reco se prend seule quand le choix est peu coûteux.** Sur 31 jours, plusieurs réponses aux questions à options portaient une information que l'agent n'avait pas (« j'ai Brave installé et c'est mon navigateur principal », « pour l'instant j'ai juste besoin d'un HTML »). Le choix pris seul reste donc écrit en une ligne, pour que l'utilisateur le voie passer et corrige en une phrase. Le choix qui dépend d'une information que seul l'utilisateur a garde sa question.

**Pourquoi la borne quitte `aidd.md`.** Elle ne couvrait que la boucle executor et checker. Une correction menée à la main, un test rouge relancé, un build réessayé n'avaient aucune borne. Le chiffre vit désormais dans `intention.md`, chargé par tous les agents, et `aidd.md` y renvoie pour ne pas l'écrire deux fois.

**Ce que `/goal` de Claude Code a appris.** Lu le 2026-11-10 sur code.claude.com/docs/en/goal, et la commande présente dans le binaire 2.1.322. Il n'a aucune borne chiffrée par défaut : « *To bound how long a goal runs, include a turn or time clause in the condition, such as `or stop after 20 turns`* ». Un petit modèle séparé juge après chaque tour si la condition tient, ce qui sépare le juge du travailleur. Ses arrêts automatiques visent la condition jugée impossible, certaines erreurs, et l'agent qui répond plusieurs tours de suite sans appeler d'outil. Aucun ne vise l'agent qui réessaie la même correction en appelant des outils. D'où une borne chiffrée propre au harnais, et « fini » prouvé de dehors.

**Base de suivi.** Rejouer `python3 tools/measure-approvals.py --days 14` quelques semaines après le merge, et la comparer à la mesure ci-dessus.
