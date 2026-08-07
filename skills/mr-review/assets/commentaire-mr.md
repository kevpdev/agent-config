# Gabarit — commentaire de revue de MR

À copier puis remplir. Les intitulés sont fixes ; retirer une section vide plutôt que d'y écrire
« néant » — sauf `Non couvert`, qui est toujours présente.

Si la MR mêle plusieurs natures de commit, plusieurs repos ou plusieurs tickets, le bloc
`Relisibilité` passe en tête, avant `Périmètre relu`.

---

**Périmètre relu** — `<base_sha>`..`<head_sha>`, <N> commits, <N> fichiers.
Suite de tests : <N> tests, <N> échecs, <N> erreurs.

**Ce que je comprends de l'attendu** — <la phrase d'ancrage, en une ligne. Si la référence
d'acceptation était inaccessible, dire d'où vient cette phrase.>

**Relisibilité** *(si la MR mêle plusieurs choses)*
<ce que la MR contient : X commits de feature, Y de correctif, Z de refactor, T de test, D de doc,
W passagers, M merges ; N repos ; N tickets. Puis la demande de découpe, et selon quelle ligne
découper.>
<Si la MR est déjà mergée : le dire ici, requalifier la demande en rétrospective, et renvoyer vers
les défauts encore actifs sur la branche déployée.>

**Défauts** *(du plus coûteux si laissé passer au moins coûteux)*

| # | Ticket | Constat | Preuve | Pourquoi ça compte |
|---|---|---|---|---|
| 1 | `<VW3-xxxx>` | <une phrase> | `<chemin:ligne>` ou `<commande>` | <le coût si on laisse> |

La colonne `Ticket` dit de quel ticket vient le défaut, sur une MR qui en mêle plusieurs — pour que
l'auteur sache ce qu'il défend lui-même et ce qui vient d'ailleurs. La retirer si la MR n'en porte qu'un.

Un défaut argumenté mais non mesuré se marque comme tel, dans ses propres mots (« hypothèse à
confirmer », « question à l'auteur ») — jamais présenté comme un constat.

**<Nom de l'axe délégué>** *(axe délégué à `<destinataire>`, rendu — verdict « <son verdict> »)*
<le résumé de son retour, sans le rejuger. Une seule section par axe rendu. Omettre si aucun retour
n'est arrivé — dans ce cas l'axe est nommé dans `Non couvert`.>

**Questions qui ne sont pas de mon ressort** *(valeur métier — je n'ai pas de moyen de trancher)*

| Question | Qui peut répondre |
|---|---|
| <la question, telle qu'on peut y répondre par oui/non ou par une valeur> | <rôle ou nom> |

**Non couvert**
<les axes délégués dont le retour n'est pas arrivé ; ce que je n'ai pas su juger et pourquoi ; les
repos voisins dont seule la présence d'un pendant a été mesurée, sans relire leur diff ; les contrôles
passés sans trouvaille, pour mémoire.>
