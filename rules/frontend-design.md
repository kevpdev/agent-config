---
paths:
  - "**/*.{css,scss,html,vue,svelte,tsx,jsx}"
  - "**/*.spec.ts"
  - "**/{tailwind,playwright}.config.*"
---

# Frontend — bases de design par défaut

Ces règles comblent les trous. Une règle ne s'applique que si le design system ou la convention du repo ne couvre pas le sujet, et seulement si elle n'entre pas en conflit avec lui (`autorite-des-conventions.md`). Avant de choisir une stack ou une valeur, lire `package.json`, les fichiers de config et le design system existant. Agnostique du framework et de la méthode de style.

## Stack par défaut
- Style : Tailwind CSS, sauf si le projet définit déjà un framework CSS. Ses breakpoints (`sm` 640, `md` 768, `lg` 1024, `xl` 1280) sont ceux de la section suivante.
- E2E : Playwright, sauf si le projet a déjà un outil e2e.

## Responsive
- Mobile-first : coder pour 320px, élargir avec des media queries en `rem`.
- Zéro défilement horizontal.
- Breakpoints : 640 / 768 / 1024 / 1280px.
- Cible tactile d'au moins 44×44px.
- Champs de formulaire à 16px minimum (évite le zoom auto d'iOS).

## Espacements et mise en page
- Espacements en multiples de 8px (4px pour les micro-ajustements).
- Texte courant limité à `65ch`.
- Flexbox et Grid. Pas de largeur fixe : `width: 100%; max-width: 300px`.

## Typographie
- Polices système, pas de police web tierce. Deux familles maximum.
  - Interface : `system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif`
  - Code : `ui-monospace, SFMono-Regular, Consolas, Menlo, monospace`
- Hiérarchie par graisse (600/700) et couleur plus que par la taille.
- Interligne : titres 1.2 à 1.3, corps 1.5 à 1.65.

## Couleurs
- 60 % neutre (fonds), 30 % texte et structure, 10 % accent.
- Un seul accent, réservé aux actions principales, liens et états actifs.
- Contraste WCAG AA : 4.5:1 pour le texte, 3:1 pour le grand texte.

## Interactions et accessibilité
- Bouton principal en accent, secondaires discrets.
- États visibles : `:hover` (pas sur tactile), `:active`, `:focus-visible`, `disabled`.
- Jamais de `outline: none` sans équivalent visible.
- Toute image porte un `alt` (vide si décorative).
- Transitions de 0.2s sur `opacity` et `transform` seulement, pas `all`.
