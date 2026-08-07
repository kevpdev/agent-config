# 04 - Restituer

Sépare ce qui est un défaut de ce qui est une question, et rend un commentaire prêt à coller.

## Input

Les findings de `03-check`, les questions métier écartées, et la fiche de `01-prep`.

## Output

Un commentaire rédigé depuis `assets/commentaire-mr.md`, rendu en texte dans la conversation. Jamais
publié.

## Process

1. **Trancher la taille d'abord.** Si la MR mêle plusieurs natures de commit, plusieurs repos ou
   plusieurs tickets, le premier paragraphe est « découpe cette MR », avant tout finding. Dire selon
   quelle ligne découper, sinon la demande n'est pas actionnable.
   - *Pourquoi en premier :* une MR non relisible par construction rend les findings secondaires, et
     ce retour ne demande aucune expertise domaine — il est donc toujours légitime à faire.
   - **Si la MR est déjà mergée** (l'état relevé en `01-prep`) : garder ce paragraphe mais le
     **requalifier en rétrospective** — la découpe n'est plus demandable, elle documente ce qui a rendu
     la revue difficile. Puis **déplacer l'urgence** sur les findings encore actionnables, en disant
     lesquels sont actifs sur la branche déployée en ce moment. *Pourquoi ne pas la supprimer :* la
     leçon de découpe vaut pour la MR suivante, alors qu'exiger une découpe impossible fait passer tout
     le reste du retour pour hors-sol.
2. **Séparer.** Deux listes distinctes, jamais mélangées : les défauts structurels d'un côté, les
   questions de valeur métier de l'autre.
   - *Pourquoi :* mélangées, les questions se lisent comme des reproches, et l'auteur passe son temps
     à défendre des choix qui ne lui appartiennent pas.
3. **Adresser.** Chaque question métier nomme qui peut y répondre : le propriétaire de la spec,
   l'auteur du besoin, le référent du domaine. Une question sans destinataire ne reçoit pas de réponse.
4. **Graduer.** Classer les findings par ce qu'ils coûtent si on les laisse passer, pas par l'effort de
   correction. Un défaut à symptôme différé passe devant un défaut visible immédiatement.
5. **Dire ce qui n'a pas été regardé.** Nommer le périmètre non couvert, et les axes délégués **dont le
   retour n'est pas arrivé**.
   - Un axe délégué **dont le retour est arrivé** ne va pas là : il prend sa propre section, étiquetée du
     nom du destinataire, et reste résumé sans être rejugé. *Pourquoi une section à lui : rangé en « non
     couvert » il disparaît alors qu'il a été couvert ; fondu dans les défauts, il devient un jugement
     qu'on s'attribue et qui échappe à la règle de délégation.*
   - *Pourquoi cette section existe :* un retour silencieux sur ses angles morts se lit comme une revue
     complète, et personne ne repasse derrière.
6. **Rendre, ne pas publier.** Sortir le texte dans la conversation, et s'arrêter là.

## Contrôle de sortie

- Le commentaire porte toutes les sections du gabarit, dans son ordre.
- Défauts et questions métier sont dans deux listes séparées ; chaque question porte un destinataire.
- Sur une MR mergée, le premier paragraphe est requalifié en rétrospective et ne demande pas une découpe
  devenue impossible ; les findings encore actifs sur la branche déployée sont désignés comme tels.
- Chaque axe délégué dont le retour est arrivé a sa propre section, nommée de son destinataire, et n'est
  pas rejugé. Ceux dont le retour manque sont dans `Non couvert`, pas ailleurs.
- Un finding argumenté mais non mesuré est marqué comme tel, jamais rendu comme un constat.
- Une section dit explicitement ce qui n'a pas été couvert.

## Test

Scénarios dans `evals/eval.json`. Ils portent le cas de la lecture seule sous pression — un utilisateur
qui demande de publier le commentaire. C'est le seul endroit où le skill peut causer un dégât réel, et
aucun contrôle de sortie ne le voit : le commentaire produit est identique qu'il ait été posté ou non.
