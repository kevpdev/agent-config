# Défauts proposés — Java / Spring Boot

Défauts d'un back Java ou Spring Boot, que l'étape « Proposer les défauts » du skill soumet à l'utilisateur.

N'y figurent que des choix perso. Ce qu'un modèle sait déjà (OWASP, codes HTTP, requêtes paramétrées) n'est pas répété.

## Architecture

- Un bounded context par microservice. Un module qui agrège plusieurs domaines appelle l'extraction du domaine en trop.
- Dans un module, organisation par couche (`controllers/`, `services/`, `repositories/`, `models/`), sans DDD tactique ni sous-packages par feature.

**POURQUOI** : la frontière utile est le bounded context, pas la feature interne. Le DDD tactique se paie sur des invariants métier riches, et l'imposer à du CRUD est de la sur-ingénierie.

## Erreurs et API

- Erreurs au format RFC 9457, en `ProblemDetail`, via un `@ControllerAdvice` qui étend `ResponseEntityExceptionHandler`.
- `@Valid` sur les corps de requête.
- Actuator : jamais `management.endpoints.web.exposure.include=*`.

## Tests

- JUnit et Mockito.
- Nom `should_<effet>_when_<condition>`, par exemple `should_throwNotFound_when_idUnknown`, en structure AAA (Arrange, Act, Assert).

## Nommage et documentation

- Suffixe par rôle : `XxxController`, `XxxService`, `XxxRepository`, `XxxDto`. Un type public par fichier.
- Javadoc complète sur tout public (`@param`, `@return`, `@throws`). Elle documente le pourquoi et les invariants, pas le nom.

## Contrôles

- Corriger la cause plutôt que poser un `@SuppressWarnings` ou un `// NOSONAR`. Sinon, commenter l'exception en une ligne.
