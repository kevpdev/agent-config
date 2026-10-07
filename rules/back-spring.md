---
paths:
  - "**/*.java"
  - "**/pom.xml"
---

# Conventions back — Java / Spring Boot

Défauts qui comblent les trous : une règle ne s'applique que si la convention du repo (`aidd_docs/`, code existant) ne couvre pas le sujet (`autorite-des-conventions.md`).

## Contrôles
- Lancer build et tests du projet (`mvnw verify`, cf. `tooling.md`), corriger jusqu'au vert : le CI et la review remontent ce que ces commandes détectent déjà.
- Corriger la cause plutôt que `@SuppressWarnings` / `// NOSONAR`, sinon commenter l'exception en une ligne.

## Erreurs et API
- Erreurs en `ProblemDetail` via un `@ControllerAdvice` qui étend `ResponseEntityExceptionHandler`.
- `@Valid` sur les corps de requête.
- Actuator : jamais `management.endpoints.web.exposure.include=*`.

## Tests
- Tester le **comportement métier**, pas l'implémentation. Exception : quand l'implémentation *est* le contrat (algo de sécurité, calcul réglementaire).
- **Outside-in** : test d'acceptation (use-case ou controller) d'abord, puis unitaires sur le domaine.
- JUnit + Mockito. Structure AAA, nom `should_<effet>_when_<condition>` (`should_throwNotFound_when_idUnknown`).
- Mock **uniquement les I/O** (DB, API externe, LLM, fichiers), jamais les collaborateurs internes.
- Peu de tests à forte valeur. Minimiser les tests d'intégration lents.

## Nommage
- Suffixe par rôle : `XxxController`, `XxxService`, `XxxRepository`, `XxxDto`. Un type public par fichier.
- Un bounded context correspond à un microservice (DDD stratégique). Dans un module, organisation par couche (`controllers/`, `services/`, `repositories/`, `models/`), sans DDD tactique ni sous-packages par feature.
- Un module qui agrège plusieurs domaines appelle l'extraction du domaine surnuméraire dans son propre microservice.

**POURQUOI** : la frontière utile est le bounded context, pas la feature interne. Le DDD tactique se paie sur des invariants métier riches, et l'imposer à du CRUD est de la sur-ingénierie.

## Documentation
- Javadoc complète sur tout public (`@param`, `@return`, `@throws`), qui documente le pourquoi et les invariants, pas le nom.
