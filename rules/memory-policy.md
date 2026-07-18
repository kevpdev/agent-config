## Auto-memory ↔ AIDD / vault — couche projet (conditionnelle)

La **couche projet a deux homes dédiés**, selon la nature du fait :

- **Durable / tranché / reproductible** (ADR, doc technique, specs, état qui fait autorité) → **AIDD** du repo (`<repo>/aidd_docs/`), qui a son propre système de mémoire.
- **Récap multi-session, raisonnement, exploration, brainstorming** → **vault** (extension cognitive ; surfacé au parent par le hook `SessionStart`).

**POURQUOI** : un même fait à deux endroits dérive (la copie stale survit jusqu'à ce qu'une session la corrige — l'auto-memory ne s'auto-purge pas). Tant que l'AIDD **ou** le vault couvre la couche projet, l'auto-memory n'a rien à y ajouter.

**RÈGLE D'ÉCRITURE — ne pas écrire de fait projet en auto-memory**
- Détection : `aidd_docs/` dans un repo du workspace (→ AIDD actif) **ou** MOC vault / `_claudeTeam.vaultRoot` (→ vault actif). Si l'un des deux est présent, la couche projet est **suspendue** en auto-memory.
- **Fallback** : l'auto-memory ne reprend la couche projet **que si ni AIDD ni vault** n'assurent le récap/contexte.
- Le vrai risque visé = les **faits projet volatils** (config, clés, runs, état) — ils deviennent faux et ont un autre home. Ne pas les laisser entrer empêche le stock stale de se reconstituer (auto-géré, pas de purge récurrente manuelle).

**CE QUE L'AUTO-MEMORY GARDE** (parent-only, sans autre home) :
- Profil user (`user_*`), config dev / environnement perso et référence Claude (`reference_*`), feedback parent-only (`feedback_*`).

**RÈGLES ET FEEDBACK FORK-PERTINENTS** → `CLAUDE.md` (ou un de ses fichiers importés), seul store qui traverse un contexte isolé (sous-agent, skill `context: fork`). Jamais dans le vault : un fork ne le lit pas.

> Doublon de **règle statique** (style, méthodo) entre auto-memory et CLAUDE.md = bénin (ne dérive pas) → ne pas imposer de purge. Seule la couche projet volatile justifie le garde-fou ci-dessus. Gating **probabiliste** (évalué par Claude, pas un hook) : coût d'un raté = une mémoire stale, faible et différé.
