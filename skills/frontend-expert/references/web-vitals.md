# Web Vitals — diagnostic et leviers

Référence de `frontend-expert`. Charger quand la question porte sur la performance perçue.

## Les 3 métriques qui comptent

| Métrique | Mesure | Bon | À corriger |
|---|---|---|---|
| **LCP** (Largest Contentful Paint) | temps d'affichage du plus gros élément visible | ≤ 2,5 s | > 4 s |
| **INP** (Interaction to Next Paint) | latence de réponse aux interactions, sur toute la visite | ≤ 200 ms | > 500 ms |
| **CLS** (Cumulative Layout Shift) | instabilité visuelle | ≤ 0,1 | > 0,25 |

INP a remplacé FID en mars 2024 : FID ne mesurait que le **premier** délai d'entrée, INP couvre toutes les interactions — beaucoup plus représentatif.

Les seuils s'évaluent au **75e centile** du trafic réel, pas sur une mesure locale. Un labo rapide masque les appareils bas de gamme.

## LCP — causes fréquentes

- **Réponse serveur lente** → cache, CDN, SSR/SSG plutôt que CSR pour le contenu au-dessus de la ligne de flottaison
- **Ressource bloquante** → différer le JS non critique, inliner le CSS critique
- **Image non optimisée** → format moderne, dimensions explicites, `priority` sur l'image LCP
- **Chargement paresseux mal placé** → ne jamais lazy-loader l'élément LCP, c'est l'anti-pattern classique

## INP — causes fréquentes

- **Tâches longues sur le thread principal** → découper, `startTransition` pour les mises à jour non urgentes
- **Re-render en cascade** → mémoïser, remonter l'état au bon niveau, éviter les contextes trop larges
- **Handler synchrone coûteux** → sortir le calcul du chemin d'interaction
- **Hydratation massive** → composants serveur, hydratation partielle ou différée

## CLS — causes fréquentes

- **Images ou vidéos sans dimensions** → toujours `width`/`height` ou un ratio réservé
- **Contenu injecté au-dessus de l'existant** → réserver l'espace avant l'insertion (bandeaux, pubs)
- **Police web qui change les métriques** → `font-display: optional` ou une police de repli aux métriques proches

## Méthode

**POURQUOI mesurer avant d'optimiser** : les leviers ci-dessus se contredisent — précharger améliore le LCP et dégrade l'INP en saturant le thread. Sans mesure, on déplace le problème au lieu de le résoudre.

1. Mesurer en **terrain réel** (RUM, données Chrome UX), pas seulement en labo
2. Identifier la métrique la plus loin de son seuil — une seule à la fois
3. Corriger la cause dominante, remesurer, s'arrêter dès que le seuil est atteint

**Ne jamais** optimiser un score de labo isolé → **à la place** viser le 75e centile du trafic réel. *Pourquoi* : un score parfait en local peut coexister avec une expérience dégradée sur mobile 4G, qui est le cas réel de la majorité des visiteurs.
