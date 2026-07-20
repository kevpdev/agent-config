## Auto-memory ↔ AIDD / vault — couche projet (conditionnelle)

La **couche projet a deux homes dédiés**, selon la nature du fait :

- **Durable / tranché / reproductible** (ADR, doc technique, specs, état qui fait autorité) → **AIDD** du repo (`<repo>/aidd_docs/`), qui a son propre système de mémoire.
- **Récap multi-session, raisonnement, exploration, brainstorming** → **vault** (extension cognitive ; chargé sur demande via `/vault-load`, pas de push automatique).

**POURQUOI** : un même fait à deux endroits dérive (la copie stale survit jusqu'à ce qu'une session la corrige — l'auto-memory ne s'auto-purge pas). Tant que l'AIDD **ou** le vault couvre la couche projet, l'auto-memory n'a rien à y ajouter.

**RÈGLE D'ÉCRITURE — ne pas écrire de fait projet en auto-memory**
- Détection : `aidd_docs/` dans un repo du workspace (→ AIDD actif) **ou** présence d'un vault (→ vault actif). Si l'un des deux est présent, la couche projet est **suspendue** en auto-memory.
- **Fallback** : l'auto-memory ne reprend la couche projet **que si ni AIDD ni vault** n'assurent le récap/contexte.
- Le vrai risque visé = les **faits projet volatils** (config, clés, runs, état) — ils deviennent faux et ont un autre home. Ne pas les laisser entrer empêche le stock stale de se reconstituer (auto-géré, pas de purge récurrente manuelle).

**CE QUE L'AUTO-MEMORY GARDE** (parent-only, sans autre home) :
- Profil user (`user_*`), config dev / environnement perso et référence Claude (`reference_*`), feedback parent-only (`feedback_*`).

**RÈGLES ET FEEDBACK PERTINENTS EN CONTEXTE ISOLÉ** → `rules/` ou `CLAUDE.md` : les deux traversent un sous-agent (project rules doc-vérifié ; user rules **vérifié le 2026-07-20** — sondage d'un sous-agent general-purpose, 0 lecture disque : les rules user globales sont bien injectées, celles à frontmatter `paths:` suivent leur scope). Jamais dans le vault ni en auto-memory — un sous-agent ne lit ni l'un ni l'autre.

> Doublon de **règle statique** (style, méthodo) entre auto-memory et `rules/` = bénin (ne dérive pas) → ne pas imposer de purge. Seule la couche projet volatile justifie le garde-fou ci-dessus. Gating **probabiliste** (évalué par Claude, pas un hook) : coût d'un raté = une mémoire stale, faible et différé.

## Recall — question mémoire → charger les session logs

Ce qui précède concerne l'**écriture** ; ici, la **lecture**. Aucun push automatique n'existe : le contexte vault n'arrive **que** par `/vault-load`. Une question de reprise de contexte n'a donc, par défaut, aucune source de session log chargée.

**CONDITION — la règle ne s'applique que si un home de session logs existe.** Le vérifier **factuellement**, pas au jugé : `$OBSIDIAN_VAULT_PRO` pointe un dossier existant (`test -d "$OBSIDIAN_VAULT_PRO"`), ou un journal de session équivalent est présent dans le projet. Aucun des deux → répondre normalement, sans invoquer cette règle.

**RÈGLE — sur une question de reprise de fil, charger le journal avant de répondre**
- Déclencheur : l'utilisateur demande où on en était, le statut/reste-à-faire d'une tâche, l'historique d'une décision, ou « reprends le fil sur X » — une question dont la réponse vit dans les session logs, pas dans le code courant.
- Action : ne pas répondre de mémoire — à la place, charger le journal (`/vault-load`, scopé sur l'id de task si repérable, global sinon ; ou l'équivalent projet), puis répondre à partir du contexte chargé.

**AVERTISSEMENT — un session log peut être périmé**
- Il fige l'état **au moment où il a été écrit** : depuis, le code, les migrations, l'AIDD ou la décision ont pu bouger. Il raconte ce qu'on *pensait* alors, pas forcément l'état actuel.
- **POURQUOI** : présenter un log stale comme l'état courant propage une décision sur une base fausse (cf. `reasoning.md` — ne jamais affirmer sans vérifier). Le coût du raté est différé et invisible.
- **À LA PLACE de** restituer le journal comme vérité présente → le marquer « d'après la session du {date}, à vérifier » et confronter à la source qui fait autorité (git, `aidd_docs/`, le code) avant toute affirmation mécanique dont dépend une décision.
