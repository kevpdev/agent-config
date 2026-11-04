# Tests — le fond, quelle que soit la stack

**DÉCLENCHEUR** : j'écris ou je modifie un test, dans n'importe quel langage.

- Tester le comportement, pas l'implémentation. Seule exception, l'implémentation qui **est** le contrat : un algorithme de sécurité, un calcul réglementaire.
- Partir de l'extérieur (*outside-in*) : le test d'acceptation sur le cas d'usage ou le point d'entrée d'abord, puis les unitaires sur le domaine.
- Ne mocker que les I/O (base, API externe, LLM, fichiers), jamais un collaborateur interne.
- Peu de tests, à forte valeur. Les tests d'intégration lents restent rares.

Ces quatre lignes sont du **fond** au sens de `autorite-des-conventions.md` : elles l'emportent sur la convention du repo. La forme des tests (nom, outil, emplacement) suit la hiérarchie de ce même fichier.
