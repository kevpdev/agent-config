# Références — `rules/mermaid.md`

La raison du découpage entre la règle et le skill `mermaid-craft`. Jamais chargé automatiquement. Sortis de la règle le 2026-10-28 (issue #66), texte d'origine.

---

## Le renvoi au skill, version d'origine

**Ces deux critères ne suffisent pas, et ne prétendent pas suffire** — ils ne sont que l'alerte, et ignorent tout le craft propre à chaque type de diagramme. **Charger le skill `mermaid-craft` avant d'écrire un bloc `mermaid` non trivial** — il fait foi, et ne pas le sauter sous prétexte que cette règle a l'air complète.

## Pourquoi ce découpage

**POURQUOI ce découpage** : un diagramme surgit souvent dans une réponse sans qu'aucun skill soit invoqué, donc ces deux critères doivent être présents en permanence. Le détail, lui, ne sert qu'au moment de dessiner : le charger en continu ferait payer à chaque session un contexte utilisé quelques fois par mois.
