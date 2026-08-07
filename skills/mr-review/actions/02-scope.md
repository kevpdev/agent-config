# 02 - Cadrer

Fixe l'ancrage et le périmètre de lecture, puis fait confirmer. Seul arrêt humain du flux.

## Input

La fiche de `01-prep`, et l'accès au ticket référencé par la MR quand il existe.

## Output

Une phrase d'ancrage, un tableau de tri des commits, et la liste des fichiers de documentation
touchés. Le tout soumis à l'humain en une seule question.

## Process

1. **Ancrer.** Écrire en une phrase ce que la MR doit livrer, depuis le ticket et la description de la
   MR — pas depuis le code.
   - Si la phrase ne se forme pas, **s'arrêter** et demander à l'auteur. Ne pas ouvrir le diff avant :
     sans ancrage, chaque fichier lu devient une digression et le fil se perd.
   - Cas intermédiaire, fréquent : la phrase se forme depuis la description de la MR, mais la
     **référence d'acceptation est inaccessible** — ticket sans description, spec en pièce jointe
     illisible. Alors continuer, et marquer l'ancrage comme reconstitué en nommant la source réellement
     utilisée. La conformité au besoin devient une question pour `04-route`, adressée au propriétaire de
     la spec. *Pourquoi ne pas s'arrêter là :* les contrôles structurels ne dépendent pas de la spec, et
     s'arrêter ne rendrait rien alors qu'ils sont livrables.
   - Cette phrase est le point de retour. On y revient au lieu de relire, chaque fois qu'on décroche.
2. **Trier.** D'abord établir **l'ensemble des tickets voulus** — le titre et la description d'une MR en
   nomment souvent plusieurs (`feat/X et fix/Y`). Puis grouper les commits par identifiant de ticket
   porté par leur message.
   - Un commit dont le ticket est dans cet ensemble est du **périmètre voulu**, quelle que soit la façon
     dont il est arrivé — y compris par un merge.
   - Un commit dont le ticket n'y est pas est un **passager**, quelle que soit la façon dont il est
     arrivé — y compris s'il ouvre la ligne de branche au lieu d'y avoir été mergé.
   - *Pourquoi le critère est le ticket et non le mode d'arrivée :* un correctif nommé dans le titre de
     la MR est du travail assumé même s'il vient d'un merge, et le premier commit d'une branche peut
     appartenir à un tout autre ticket. Trier sur « arrivé par un merge » classe les deux à l'envers.
3. **Classer.** Étiqueter chaque commit selon la nature dominante de **son propre diff** :
   `feature`, `correctif`, `refactor`, `test`, `doc`, `passager`. Un commit, une étiquette.
   - Les **commits de merge se comptent à part**, sans étiquette. Un merge n'a pas de nature propre : il
     transporte. Relever seulement son diff combiné (`git diff-tree --cc`), qui n'est pas vide quand une
     résolution de conflit a été écrite à la main — c'est du code que personne n'a relu.
   - Un commit qui fait visiblement **plusieurs choses** garde une étiquette (la dominante) et se
     marque d'un `+` : c'est lui-même un signal de non-relisibilité, pas un cas à trancher finement.
   - Le décompte des étiquettes dit déjà si la MR fait une chose ou plusieurs, avant toute lecture de
     code. C'est le premier signal de non-relisibilité.
   - *Pourquoi `test` et `doc` méritent leur étiquette :* sans elles, un commit de test seul ou de doc
     seule se range en `correctif` par défaut, ce qui gonfle le décompte des correctifs et fait
     conclure à une MR plus mêlée qu'elle n'est. Le décompte est justement ce sur quoi `04-route`
     appuie sa demande de découpe — le bruiter affaiblit le seul retour qui ne demande aucune expertise.
4. **Lire la doc d'abord.** Sortir le diff des fichiers de documentation, et le lire avant le code.
   C'est là que l'auteur écrit ses *raisons*, dans ses mots, et le ratio information/lignes y est le
   meilleur de la MR.
   - Si le repo ne documente pas ses raisons, remplacer cette étape par une demande de walkthrough à
     l'auteur. Reconstituer l'intention depuis le code seul coûte plus que de la demander.
5. **Confirmer.** Rendre l'ancrage et le tri, puis poser **une seule question, celle qui change la suite
   du travail** : sur quel périmètre lancer les contrôles. Les autres éléments s'affirment au lieu de se
   demander — l'humain corrigera ce qui est faux sans qu'on le lui demande. Puis s'arrêter et attendre.
   - *Pourquoi une seule décision :* deux questions ouvertes dans le même message bloquent au lieu de
     faire avancer, et l'ancrage n'a pas besoin d'un accord explicite pour être corrigeable.

## Contrôle de sortie

- Une phrase d'ancrage existe, formulée en termes de résultat attendu et non de fichiers, et elle nomme
  sa source quand la référence d'acceptation était inaccessible.
- Chaque commit non-merge porte exactement une étiquette ; aucun n'est non classé. Les merges sont
  comptés à part, sans étiquette.
- Le décompte par étiquette est rendu, et l'ensemble des tickets voulus est explicité.
- Le message se termine sur **une** question, pas deux.

## Test

Scénarios dans `evals/eval.json`. Ils portent le cas de l'arrêt : qu'une seule question soit écrite se
lit dans la sortie, mais que l'action **s'arrête vraiment** au lieu d'enchaîner sur les contrôles ne se
juge qu'en session neuve — et c'est le seul arrêt humain du flux.
