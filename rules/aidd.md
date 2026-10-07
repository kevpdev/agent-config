# AIDD — chercher un skill avant d'agir

**DÉCLENCHEUR** : une demande qui produit ou modifie quelque chose, dans un repo qui porte un `aidd_docs/`, à constater d'un `ls` au premier tour. Une question ou une lecture seule ne déclenche rien, et un repo sans `aidd_docs/` n'est pas concerné.

**À LA PLACE de** démarrer à la main, parcourir le catalogue de la session et chercher une ligne dont le « Use when » couvre l'intention. Puis invoquer ce skill, ou écrire une ligne qui dit pourquoi aucun ne convient.

**Lire par intention, jamais par nom** : mémoire du projet et génération d'artefacts de contexte, clarifier et remettre en cause, planifier et implémenter et contrôler (revue, tests, audit, débogage), versionner et livrer, produit et backlog, orchestrer de bout en bout.

**CE QU'ELLE NE DEMANDE PAS** : invoquer à tout prix. Regarder est systématique, invoquer dépend du « Use when ». Quand le skill choisi pilote le flux, l'exception de `plan-mode.md` s'applique.

**POURQUOI**, mesuré le 2026-10-07 : 9 issues écrites à la main alors qu'un skill existait, vu seulement quand l'utilisateur a posé la question. Aucun nom de skill ici, parce qu'ils dérivent, et `aidd_docs/` est le même signal que `memory-policy.md`.

**ÉTAT DU GARDE, décidé le 2026-10-07** : `guard-aidd-skill-lookup.py` rappelle et ne bloque pas, la sortie `# aidd-skip: <raison>` reste libre. On ne le durcit que si on constate que les skills AIDD sont ignorés malgré leur présence.
