# Défauts proposés — design d'interface web

Défauts de design d'une interface web, que l'étape « Proposer les défauts » du skill soumet à l'utilisateur.

N'y figurent que des choix perso. Les bases d'accessibilité (WCAG AA, `alt`, `:focus-visible`) ne sont pas répétées.

## Outils

- Style en Tailwind CSS, avec ses breakpoints (`sm` 640, `md` 768, `lg` 1024, `xl` 1280).
- Tests end-to-end en Playwright.

## Mise en page

- Mobile-first, à partir de 320px.
- Espacements en multiples de 8px, 4px pour les micro-ajustements.
- Texte courant limité à `65ch`.

## Typographie

- Polices système, deux familles au plus.
  - Interface : `system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif`
  - Code : `ui-monospace, SFMono-Regular, Consolas, Menlo, monospace`
- Hiérarchie par la graisse (600 et 700) et la couleur plus que par la taille.
- Interligne de 1.2 à 1.3 pour les titres, de 1.5 à 1.65 pour le corps.

## Couleurs et mouvement

- 60 % de neutre pour les fonds, 30 % pour le texte et la structure, 10 % d'accent.
- Un seul accent, réservé aux actions principales, aux liens et aux états actifs.
- Transitions de 0.2s, sur `opacity` et `transform` seulement.
