---
name: mr-review
description: >
  Assistant de revue d'une merge request GitLab avec `glab` en lecture seule : met la MR en état
  d'être relue, cadre le périmètre, passe les contrôles structurels indépendants du métier, et rend
  un commentaire prêt à coller. Utiliser quand l'utilisateur dit "je dois reviewer une MR",
  "revue de MR", "aide-moi sur cette MR", "grosse MR", "je ne connais pas le contexte de cette MR",
  quand il donne un numéro ou une URL de merge request, ou "/mr-review".
  NE PAS utiliser pour juger la qualité du code lui-même (→ code-reviewer, ou aidd-dev:05-review
  quand un plan existe — ce skill les appelle), pour un audit sécurité (→ security-reviewer),
  ni pour créer une MR (→ aidd-vcs:02-pull-request).
---

# mr-review

Reviewer une grosse MR sans maîtriser le domaine métier. Le skill fait le travail mécanique que
personne ne fait à la main sans se tromper — retrouver le vrai périmètre du diff — puis borne la
revue à ce qui est jugeable sans contexte, et route le reste.

> [!note] Pourquoi ce skill n'est pas un skill de revue
> `code-reviewer` et `aidd-dev:05-review` jugent déjà du code. Ce qui manquait est en amont : une MR
> de plusieurs milliers de lignes n'est pas relisible tant que son périmètre exact n'est pas établi,
> et un reviewer sans le métier se perd faute d'ancrage, pas faute de compétence.

## Le flux

```
numéro ou URL de MR
   → 01-prep     récupérer, LIRE la base (jamais la dériver), prouver le périmètre, tester
   → 02-scope    ancrage + tri des commits ───── seul arrêt humain
   → 03-check    contrôles structurels ───────── délègue la qualité de code
   → 04-route    findings + questions métier → commentaire à coller
```

Séquence stricte : chaque étape consomme la sortie de la précédente. Entrer directement dans
`03-check` est possible sur une branche déjà préparée à la main, mais alors le périmètre du diff
n'est pas prouvé — le dire avant de rendre les findings.

## Actions

| Étape | Fichier | Rôle | Input |
|---|---|---|---|
| Préparation | `actions/01-prep.md` | MR → branche locale, base du diff prouvée, tests lancés | numéro ou URL de MR |
| Cadrage | `actions/02-scope.md` | phrase d'ancrage + tri des commits, confirmés | la sortie de 01 |
| Contrôles | `actions/03-check.md` | les contrôles qui ne demandent aucun contexte métier | le périmètre confirmé |
| Restitution | `actions/04-route.md` | deux listes séparées + commentaire prêt à coller | les findings de 03 |

## Règles transverses

- **Lecture seule de bout en bout.** Aucune écriture sur la MR, aucun `push`, aucun commentaire
  publié. La sortie finale est un texte à coller. *Pourquoi : le token `glab` est en lecture seule,
  et la relecture avant publication est la bonne place de l'humain dans la boucle.*
- **Un problème d'accès arrête le flux, il ne se contourne pas.** Token expiré ou révoqué, hôte
  injoignable, projet interdit, `iid` inexistant : le skill s'arrête, dit laquelle des quatre causes
  s'applique et la commande qui l'a révélée. Jamais de repli sur une dérivation locale.
  *Pourquoi : le repli produit une base plausible mais fausse, donc une revue confiante sur le
  mauvais diff — exactement la panne silencieuse que le contrôle de périmètre existe pour éviter.*
  - **Mais nommer la cause avant de s'arrêter**, et d'abord écarter celles qui ne sont pas des
    problèmes d'accès — un `glab api` lancé hors du clone rend `404` avec un accès parfaitement
    intact (voir la référence). *Pourquoi : échouer fermé sur la mauvaise cause envoie corriger un
    accès qui marche, ce qui coûte autant qu'échouer ouvert et se voit moins.*
- **Le périmètre du diff se prouve, il ne se devine pas.** Une base fausse fait relire le mauvais
  diff sans que rien ne le signale. *Pourquoi : c'est une panne silencieuse — le reviewer rend une
  revue confiante sur des lignes qui ne sont pas celles de la MR.*
- **La qualité de code est déléguée, jamais réécrite ici.** *Pourquoi : deux skills la couvrent
  déjà, et un troisième jeu de critères divergerait du leur au premier edit.*
- **Un seul arrêt humain, à l'étape 2.** Le reste s'enchaîne. *Pourquoi : empiler les questions
  ouvertes bloque au lieu de faire avancer ; une décision à la fois.*
- **Ne jamais trancher la valeur métier.** « Ce chiffre est-il le bon », « cette liste est-elle
  complète » se routent au propriétaire de la spec. *Pourquoi : les confondre avec de la revue de
  code coûte des heures et ne produit aucun retour livrable.*
- **Un retour partiel livré vaut mieux qu'une revue complète jamais rendue.** Si une étape bloque,
  rendre ce qui est acquis et dire ce qui manque. *Pourquoi : sur une MR de cette taille, la revue
  exhaustive n'arrive jamais, donc l'exiger revient à ne rien rendre.*

## Références

- `references/glab-et-base-du-diff.md` : les commandes `glab`/`git`, et pourquoi les deux façons
  évidentes de trouver la base du diff donnent un faux résultat.
- `references/controles-structurels.md` : les contrôles de `03-check`, un exemple concret chacun.

## Assets

- `assets/commentaire-mr.md` : le gabarit du commentaire rendu par `04-route`.
