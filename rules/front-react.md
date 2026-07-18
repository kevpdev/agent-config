---
paths:
  - "**/*.{ts,tsx}"
---

# Conventions front — React / TypeScript

## Documentation
- Tout export **public** (composant, hook, util) → bloc **TSDoc/JSDoc** : rôle + `@param` / `@returns` quand non trivial.
- Props d'un composant : documentées via le type/interface (commentaire au-dessus de chaque champ non évident), pas en double dans le TSDoc.

**POURQUOI** : le type est déjà lu par l'IDE et vérifié par le compilateur. Redocumenter les props en TSDoc crée une seconde source de vérité que rien ne contrôle — elle dérive dès la première modification du type.

## Tests
- Vitest + React Testing Library. Tester le **comportement** (ce que voit l'utilisateur), pas l'implémentation.
- Requêtes par rôle/label (`getByRole`, `getByLabelText`) avant `getByTestId` (dernier recours).
- Fichier de test colocalisé : `Xxx.test.tsx` à côté du composant.

**POURQUOI** : une requête par rôle ou label échoue quand l'accessibilité casse — le test couvre l'a11y sans test dédié. `getByTestId` passe même sur un composant inutilisable au clavier ou au lecteur d'écran, d'où le dernier recours.

## Nommage
- Composants : **PascalCase**, fichier = nom du composant (`InvoiceCard.tsx`).
- Hooks : préfixe `use` (`useInvoiceList`). Utils/non-composants : **camelCase** (`formatAmount.ts`).
- Types/interfaces en PascalCase ; pas de préfixe `I`.

**POURQUOI** : la casse porte l'information — PascalCase signale à React qu'il s'agit d'un composant et non d'une balise HTML, le préfixe `use` déclenche la vérification des règles des hooks par le linter. Ce ne sont pas des conventions cosmétiques mais des contrats outillés. Le préfixe `I` est un vestige C# qui n'apporte rien là où le compilateur connaît déjà la nature du type.
