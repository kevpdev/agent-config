---
paths:
  - "**/*.{ts,tsx}"
---

# Conventions front — React / TypeScript

## Documentation
- Tout export **public** (composant, hook, util) → bloc **TSDoc/JSDoc** : rôle + `@param` / `@returns` quand non trivial.
- Props d'un composant : documentées via le type/interface (commentaire au-dessus de chaque champ non évident), pas en double dans le TSDoc.

## Tests
- Vitest + React Testing Library. Tester le **comportement** (ce que voit l'utilisateur), pas l'implémentation.
- Requêtes par rôle/label (`getByRole`, `getByLabelText`) avant `getByTestId` (dernier recours).
- Fichier de test colocalisé : `Xxx.test.tsx` à côté du composant.

## Nommage
- Composants : **PascalCase**, fichier = nom du composant (`InvoiceCard.tsx`).
- Hooks : préfixe `use` (`useInvoiceList`). Utils/non-composants : **camelCase** (`formatAmount.ts`).
- Types/interfaces en PascalCase ; pas de préfixe `I`.
