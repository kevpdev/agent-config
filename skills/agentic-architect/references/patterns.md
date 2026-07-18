# Exemples de patterns

Patterns concrets à reproduire pour `agentic-architect`.

### Routing déterministe (hooks + sous-agents)
```json
{
  "rules": [
    {
      "id": "doc-generation",
      "match": { "regex": "documente|javadoc|readme" },
      "target": { "type": "agent", "name": "doc-writer" },
      "force": true
    }
  ]
}
```
Hook évalue les règles en ordre, premier match gagne, LLM reçoit le résultat enrichi.

### Passage de contexte minimal à un sous-agent
```
Tu es doc-writer. Contexte :
- Fichier cible : src/auth/service.ts
- Type de doc : JSDoc sur les méthodes publiques
- Style : en français, concis
[contenu du fichier]
```
Stateless : le sous-agent n'a besoin de rien d'autre.
