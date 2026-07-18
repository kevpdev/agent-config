# Découverte de la recette de run

Le testeur reconstitue **seul** comment démarrer et tester l'app. Il ne sollicite l'humain qu'en dernier recours (barreau 3 ci-dessous). C'est le cœur de son autonomie et de son agnosticisme.

## La recette (ce qu'il doit reconstituer, par appli)

- comment démarrer (commande + dossier de travail) ;
- secrets / env requis (compte BDD, clés API, chemins) ;
- signal « prête » + URL/port ;
- commande de test (suites existantes) ;
- ops payantes (garde-coût).

## Où il cherche — ordre fixe, du plus fiable au moins

| Source | Ce qu'il y prend |
|---|---|
| Fichiers env (`.env`, `.env.local`) | secrets, compte BDD, clés API, chemins |
| Config framework (`application.yml/.properties`, `vite.config`, `package.json`) | ports, commande de démarrage, profils |
| Docs run (README, `aidd_docs/testing.md`, `deployment.md`) | la recette officielle si elle existe |

## Déduire, pas inventer (clé de l'autonomie)

**Déduire par correspondance sémantique ou de finalité = autorisé et attendu.** Ce n'est PAS de la supposition hypothétique : une valeur qui **existe** et dont le sens **colle par preuve** est utilisable, même si son nom ne matche pas au mot près.

*Exemple* : `SPIKE_INVOICE_DIR` est nommé pour le spike, mais c'est un dossier de factures → utilisable pour **tout** test qui a besoin de factures (curl `/analyse` classique compris). On cherche la **fonction** (« un dossier de factures »), pas un nom exact (« INVOICE_DIR »).

**Inventer = interdit** : fabriquer une valeur absente, ou supposer un fait invérifiable.

L'échelle :

1. nom explicite → utilise.
2. pas de nom exact mais un candidat sert clairement la fonction → **utilise et le signale** (véto humain possible), ne bloque pas.
3. rien, ou plusieurs candidats ambigus → **escalade**.

Le « je n'ai pas trouvé » ne tombe qu'au barreau 3, jamais parce qu'un nom précis manque. Ce qu'il ne peut ni découvrir ni déduire, il le **déclare non couvert** — l'honnêteté remonte au verdict de validation.
