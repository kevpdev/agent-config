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
- Packages en minuscules, par feature avant par couche si le module grossit.

**POURQUOI** : le suffixe encode la couche dans le nom — on situe un type sans ouvrir le fichier ni remonter les imports. Le découpage par feature garde ensemble ce qui change ensemble ; par couche, une seule fonctionnalité se disperse dans tout le module.
