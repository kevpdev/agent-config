## Recall — une question de reprise de fil se répond sur le journal, jamais de mémoire

**CONDITION** : la règle ne vaut que si un home de session logs existe. Le vérifier factuellement et non au jugé, par `test -d "$OBSIDIAN_VAULT_PRO"` ou par la présence d'un journal équivalent dans le projet. Aucun des deux, répondre normalement sans invoquer cette règle.

**DÉCLENCHEUR** : l'utilisateur demande où on en était, le reste-à-faire d'une tâche, l'historique d'une décision, ou « reprends le fil sur X ». Toute question dont la réponse vit dans les session logs et non dans le code courant.

**À LA PLACE DE** répondre de mémoire → charger le journal d'abord (`/vault-load`, scopé sur l'id de task s'il est repérable, global sinon), puis répondre à partir du contexte chargé. Aucun push automatique n'existe : le contexte vault n'arrive que par `/vault-load`, donc par défaut aucune source n'est chargée et rien ne signale son absence.

**CAS VÉCU, 2026-08-05** : à la question « où en sommes-nous sur la config agentique », j'ai répondu de mémoire qu'aucune trace d'audit n'existait. L'audit était dans le log de session du 31 juillet, et il a fallu que l'utilisateur m'envoie le lire. Le déclencheur était littéral, la règle existait, et elle n'a pas suffi. Un `grep` sur le mauvais mot-clé avait rendu zéro, ce qui s'est lu comme une absence au lieu d'un instrument mal calibré (cf. `reasoning.md`).

**AVERTISSEMENT — un session log peut être périmé** : il fige l'état au moment où il a été écrit, et depuis, le code, les migrations ou la décision ont pu bouger. Il raconte ce qu'on pensait alors, pas forcément l'état actuel. Le marquer « d'après la session du {date}, à vérifier » et le confronter à la source qui fait autorité (git, `aidd_docs/`, le code) avant toute affirmation dont dépend une décision. Présenter un log périmé comme l'état courant propage une décision sur une base fausse, et le coût du raté est différé donc invisible.
