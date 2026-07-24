---
paths:
  - "**/*.java"
  - "**/pom.xml"
---

# Conventions back — Java / Spring Boot

## Documentation
- Toute classe et méthode **publique** → Javadoc complète : `@param`, `@return`, `@throws`.
- Pas de Javadoc qui paraphrase le nom (`/** Gets the name */`) — documenter le *pourquoi* / les invariants, pas l'évident.

**POURQUOI** : le public est le contrat — c'est ce que l'appelant ne peut pas déduire en lisant le corps. Une Javadoc qui paraphrase le nom coûte de la maintenance sans ajouter d'information, et devient fausse au premier renommage.

## Tests
- **Principe directeur** : tester le **comportement métier**, pas l'implémentation — robuste au refactor, maintenance réduite, le test sert de doc. Exception : cas critiques où l'implémentation *est* le contrat (algo de sécurité, calcul réglementaire).
- **Outside-in** : test d'acceptation (slice use-case / controller) d'abord, puis descente en unitaires sur le domaine (double boucle ATDD + TDD).
- JUnit 5 + Mockito. Un test = **AAA** (Arrange / Act / Assert), nom `should_<effet>_when_<condition>` (ex. `should_throwNotFound_when_idUnknown`).
- Mock **uniquement les I/O** (DB, API externe, LLM, fichiers) — jamais les collaborateurs internes : exercer le chemin métier complet avec les vrais objets.
- Peu de tests à forte valeur ; minimiser les tests d'intégration lents.

## Nommage
- Suffixe par rôle : `XxxController`, `XxxService`, `XxxRepository`, `XxxDto`.
- Un type public par fichier ; nom de fichier = nom du type.
- Packages en minuscules. Le découpage par domaine relève du **DDD stratégique** : un bounded context = un microservice. À l'intérieur d'un module, organisation **par couche** (`controllers/`, `services/`, `repositories/`, `models/`) — pas de DDD tactique (hexagonal, agrégats) tant que le domaine reste du CRUD auto-exposé. Ne pas subdiviser un domaine unique en sous-packages par feature, même s'il grossit ; un module qui grossit parce qu'il agrège plusieurs domaines → extraire le domaine surnuméraire dans son propre microservice.

**POURQUOI** : la frontière qui porte du sens est le bounded context, matérialisé par le microservice (DDD stratégique), pas la feature interne. Le suffixe de couche situe un type sans ouvrir le fichier. Le DDD tactique se paie sur des invariants métier riches ; l'imposer à du CRUD référentiel = sur-ingénierie. Le signal de séparation = la pluralité de domaines (un bloc consommé de façon autonome), jamais le seul nombre de classes.
