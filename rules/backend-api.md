---
paths:
  - "**/*.java"
  - "**/pom.xml"
  - "**/application*.{yml,yaml,properties}"
---

# Backend — bases API et sécurité par défaut

Défauts qui comblent les trous : une règle ne s'applique que si la convention du repo ne couvre pas le sujet (`autorite-des-conventions.md`).

## Sécurité (OWASP API Top 10 2023)
- Autorisation vérifiée côté serveur à chaque accès par identifiant et à chaque fonction sensible (API1, API5).
- DTO en entrée et en sortie, jamais l'entité exposée (API3).
- Pagination et taille des requêtes bornées (API4).
- Aucun appel vers une URL fournie par l'utilisateur sans liste blanche (API7).
- Requêtes paramétrées, jamais de SQL concaténé. Entrées validées en liste blanche.
- Aucun secret dans le code ni le dépôt : variables d'environnement.
- Aucune stack trace ni message interne côté client. Aucune donnée sensible dans les logs.

## API
- Codes HTTP exacts (201, 204, 400, 401, 403, 404, 409).
- Erreurs au format RFC 9457 (`application/problem+json`).
