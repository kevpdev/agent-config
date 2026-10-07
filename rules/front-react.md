---
paths:
  - "**/*.{ts,tsx}"
---

# Conventions front — React / TypeScript

Défauts qui comblent les trous : une règle ne s'applique que si la convention du repo (config lint, `aidd_docs/`, code existant) ne couvre pas le sujet (`autorite-des-conventions.md`).

## Contrôles
- Lancer lint, typecheck et tests du projet (scripts de `package.json`), corriger jusqu'au vert : le CI et la review remontent ce que ces commandes détectent déjà.
- Corriger la cause plutôt que `eslint-disable` / `@ts-ignore`, sinon commenter l'exception en une ligne.

## Pièges lint et sécurité
- Hooks : règles des hooks respectées et dépendances d'`useEffect` complètes. Pas d'effet pour dériver une valeur calculable au rendu.
- Pas de `any` ni de `as` pour taire le compilateur : typer, ou `unknown` puis une garde.
- Pas de `dangerouslySetInnerHTML` ni d'URL construite depuis une entrée utilisateur. Si besoin, assainir d'abord.
- Aucun secret ni token dans le code ou dans les variables exposées au client (`VITE_*`, `NEXT_PUBLIC_*`).
- Listes avec une `key` stable, jamais l'index.
- Éléments sémantiques (`button`, `a`, `label`), pas de `div` cliquable.
- Pas de `catch` vide : afficher l'état d'erreur et de chargement.

## Nommage
- Composants : **PascalCase**, le fichier porte le nom du composant (`InvoiceCard.tsx`).
- Hooks : préfixe `use` (`useInvoiceList`). Utils/non-composants : **camelCase** (`formatAmount.ts`).
- Types/interfaces en PascalCase. Pas de préfixe `I`.

## Tests
- Vitest + React Testing Library, sauf runner existant.
- Tester le comportement. Requêtes par rôle/label avant `getByTestId`.
- Test colocalisé : `Xxx.test.tsx`.

## Documentation
- TSDoc sur tout export public. Props documentées via le type, pas en double.
