---
name: docs-check
description: >
  Récupère la documentation à jour d'une librairie/framework via Context7 v2 (HTTP, sans MCP).
  Utiliser quand l'utilisateur demande "comment faire X avec la lib Y", "quelle est la signature de",
  "cette API a-t-elle changé", "version récente de", "doc à jour de", ou en cas de doute sur une
  API/version/breaking change d'une dépendance précise. NE PAS utiliser pour les libs stables et
  bien connues (Spring core, React hooks classiques) → répondre directement ; ni pour les décisions
  d'architecture (→ backend-architect / frontend-expert), ni la review (→ code-reviewer).
---

# Skill — Docs Check

## Rôle

Récupérer de la doc de librairie **à jour et ciblée**, au moindre coût en tokens, via l'API HTTP Context7 v2.

## Méthode

Suivre la recette partagée : `~/.claude/skills/_shared/context7-fetch.md`.

En résumé :
1. Vérifier d'abord si l'abstention est justifiée (lib stable connue → réponse directe, pas d'appel).
2. Sinon : `searchLibrary` → `getContext?type=json` (2 appels WebFetch max).
3. Citer les sources renvoyées.
4. Fallback `llms.txt` / web si Context7 échoue, en signalant la source utilisée.

## Sortie

- Réponse centrée sur le besoin (signature, exemple, config), pas de blabla
- Bloc code si pertinent
- Liste des sources (URLs Context7 ou doc officielle)
