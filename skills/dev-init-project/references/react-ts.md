# Défauts proposés — React / TypeScript

Défauts d'un front React ou TypeScript, que l'étape « Proposer les défauts » du skill soumet à l'utilisateur.

N'y figurent que des choix perso. Ce que le lint et le compilateur attrapent déjà n'est pas répété, ni le PascalCase des composants et le préfixe `use` des hooks, que React impose.

## Tests

- Vitest et React Testing Library.
- Test colocalisé : `Xxx.test.tsx` à côté de `Xxx.tsx`.

## Nommage

- Le fichier d'un composant porte son nom (`InvoiceCard.tsx`). Le reste en camelCase (`formatAmount.ts`).
- Types et interfaces en PascalCase, sans préfixe `I`.

## Documentation

- TSDoc sur tout export public. Les props se documentent par leur type, pas en double.

## Contrôles

- Corriger la cause plutôt que poser un `eslint-disable` ou un `@ts-ignore`. Sinon, commenter l'exception en une ligne.
