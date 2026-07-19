# Conventional Commits — Référence détaillée

Document chargé à la demande par le skill `commit` lorsque la convention exacte est nécessaire.

## Format complet

```
<type>(<scope>): <description>

[body optionnel — explique le POURQUOI, pas le quoi]

[footer optionnel — BREAKING CHANGE, refs, co-auteurs externes]
```

## Types autorisés

| Type | Usage | Exemple description |
|---|---|---|
| `feat` | Nouvelle fonctionnalité | `add OAuth2 login flow` |
| `fix` | Correction de bug | `handle empty response from API` |
| `docs` | Documentation uniquement | `update README install steps` |
| `style` | Formatage, pas de logique | `apply prettier on src/` |
| `refactor` | Refacto sans feat ni fix | `extract validation into service` |
| `test` | Ajout ou modif de tests | `add integration tests for auth` |
| `chore` | Maintenance, build, config | `update dependencies to latest` |
| `perf` | Amélioration de performance | `cache user lookup in middleware` |
| `ci` | Changements CI/CD | `add e2e job to GitHub Actions` |
| `revert` | Revert d'un commit précédent | `revert "feat(auth): add OAuth2"` |

## Règles de rédaction

- **Description** : minuscules, sans point final, ≤ 72 caractères, à l'impératif présent
  - ✅ `add user pagination`
  - ❌ `Added user pagination.` / `adds user pagination`
- **Scope** : optionnel mais recommandé. Module, package ou feature concernée.
  - ✅ `feat(auth):`, `fix(api/users):`
- **Body** : optionnel. Sépare avec une ligne vide. Explique **pourquoi** ce changement existe (contrainte, incident, motivation produit).
- **Footer** : refs d'issues, breaking changes, autres metadata.
- **Aucun** `Co-Authored-By: Claude` ni mention que le code a été généré par une IA.

## Breaking changes

Deux notations valides, **les deux à utiliser ensemble** :

1. Ajouter `!` après le type/scope :
   ```
   feat(config)!: rename db_host to database.host
   ```
2. Ajouter un footer `BREAKING CHANGE:` avec l'explication :
   ```
   BREAKING CHANGE: `db_host` renamed to `database.host`. Migration:
   update your config files and re-deploy with the new schema.
   ```

## Exemples canoniques

### Feature simple
```
feat(auth): add OAuth2 login flow
```

### Fix avec contexte
```
fix(api): handle empty response from external service

Inventory API returns 204 instead of 200+empty body since v2.3.
Without this guard, the parser throws on null and crashes the worker.
```

### Refacto sans body (le quoi est évident)
```
refactor(users): extract email validation helper
```

### Chore avec scope omis
```
chore: bump TypeScript to 5.6
```

### Breaking change complet
```
feat(api)!: drop support for v1 endpoints

BREAKING CHANGE: All `/api/v1/*` endpoints removed. Clients must
migrate to `/api/v2/*`. Migration guide: docs/migration-v2.md.
```

## Anti-patterns à proscrire

| ❌ À éviter | ✅ Préférer |
|---|---|
| `update stuff` | `chore: bump deps to latest minor` |
| `Fix bug` | `fix(payment): handle 3DS timeout` |
| `WIP` | Ne pas committer un WIP — créer une branche locale |
| `feat: add login.` | `feat: add login` (pas de point final) |
| `feat(Auth): Add Login` | `feat(auth): add login` (minuscules) |
