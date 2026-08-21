# 04 - Livrer la mémoire

Écrit le plan cadré en action 03, par repo, en déléguant à `/10-learn` si disponible, sinon en édition
directe.

## Input

Le **plan de mémoire** de l'action 03 : par candidat, son verdict (garder / pointeur / sortir) et sa
réconciliation. Plus les cibles de régime **reflet** de l'action 02 et le contexte du scope validé.
En coordinateur : chaque enfant, plus le contrat au parent (traité en 07, pas ici). Le **home memory**
de chaque enfant vient de l'action 01 : `<enfant>/aidd_docs/memory/` (distribué) ou
`aidd_docs/memory/<enfant>/` au parent (centralisé).

## Output

La memory AIDD des repos concernés mise à jour (via `/10-learn` ou édition directe ciblée), memory
d'abord car c'est la source relue par `/plan`.

## Process

1. **Vérifier.** Contrôler si `10-learn` est disponible (skill `aidd-context:10-learn` listé /
   framework AIDD présent), **et** le home memory de la cible (action 01).
   - **Garde-fou home centralisé** : `10-learn` écrit **à plat** dans `aidd_docs/memory/` (il ne cible
     pas de sous-dossier `<enfant>/`). Donc pour une memory **centralisée**
     (`aidd_docs/memory/<enfant>/`), ne PAS déléguer à `10-learn` — il écrirait au mauvais endroit
     (top-level parent). Basculer directement en **cas B** (édition directe dans le sous-dossier de
     l'enfant). La délégation `10-learn` (cas A) ne vaut que pour une memory **à plat** : mono-repo, ou
     enfant **distribué** (invoqué dans le CWD de l'enfant).
2. **Déléguer (cas A — nominal, home à plat).** Si `10-learn` est disponible **et** la cible est à
   plat, l'invoquer (`/10-learn`) avec le contexte du scope, les catégories de l'action 02, **et les
   verdicts de l'action 03**.
   - Pourquoi déléguer : `10-learn` a déjà son pipeline scope → write → sync (gate d'approbation +
     refresh du bloc `<aidd_project_memory>`) et porte ses propres conventions. Le réécrire =
     divergence garantie.
   - **Pourquoi lui passer les verdicts** : son scoring note quatre poids qui ignorent si le fait est
     reconstructible. Sans les verdicts de 03, un fait inférable et volatil repasse la porte.
   - Si `10-learn` ne voit aucune décision/convention durable, la memory descriptive (reflet :
     `codebase-map`, `api-docs`, `database`) peut quand même nécessiter une MAJ factuelle → basculer
     sur le cas B pour ces fichiers.
3. **Éditer en direct (cas B — fallback, MAJ descriptive, ou home centralisé).** Si `10-learn` est
   absent, pour une MAJ descriptive directe, ou pour une memory **centralisée**, éditer les fichiers
   **de régime reflet** concernés dans **leur home résolu**.
   - Appliquer la **règle d'édition directe** (routeur) : lire d'abord la structure/conventions
     existantes du fichier et s'y conformer.
   - Appliquer [memory-criteria.md](../references/memory-criteria.md) à chaque ligne écrite. Un verdict
     « pointeur » s'écrit comme un chemin, jamais comme un résumé du contenu pointé.
   - Édition ciblée, jamais de réécriture complète.
4. **Déporter avant de supprimer.** Un verdict « pointeur » qui déplace un fait vérifie que le fait
   **existe au home destinataire** avant de retirer la copie. Si le home ne le porte pas encore, l'y
   écrire d'abord.
   - *Pourquoi cet ordre : l'inverse perd le fait entre les deux edits, et rien ne le signale.*
5. **Rejouer ce qui descendait de la prémisse.** Quand une correction change un fait dont d'autres
   affirmations dépendent, relancer les **mesures** qui les fondaient — pas seulement réécrire la phrase
   qui les énonçait. Le geste est mécanique : grep le fait corrigé dans le home, et pour chaque
   occurrence trouvée, rejouer la commande qui l'avait établie.
   - *Pourquoi mécanique et non au jugement : décider « celle-là dépend-elle de ma correction ? » est un
     jugement, donc il se trompe, et il se trompe **en silence** — la phrase réécrite a l'air juste. Un
     grep sur le fait corrigé ne demande aucun jugement.*
   - **NE PAS remplacer un décompte par une explication qu'on n'a pas mesurée.** Un verdict « pointeur »
     s'écrit comme un chemin, jamais comme un résumé de ce qui s'y trouve. *Pourquoi le redire ici alors
     que l'étape 3 le porte déjà : une reformulation contourne la règle sans la contredire. Elle ne
     recopie rien, donc le refus dur ne mord pas, et elle affirme quand même.*
   - **Mesuré le 2026-08-21**, trois cas d'une même passe : une correction a écrit partout que les
     bibliothèques internes étaient désormais clonées, en laissant debout les deux affirmations que ce
     clone rendait fausses (« aucun `pom.xml` ne déclare de starter AMQP », et un comptage scopé sur
     deux dépôts écrit comme un « **que** dans celui-ci »). Une autre a remplacé un décompte par une
     explication inventée, fausse dans ses deux moitiés. Trois des treize faits faux du contrôle, et
     deux étaient des régressions créées par la passe elle-même.
6. **Différer les décisions.** Les docs-décision (memory `decisions`, contrat partagé) ne s'éditent
   **pas** ici en autonomie → régime décision, action 07.
   - **Exception cadrée, la prose de détail d'un index de portes.** Sur une surface classée décision
     parce qu'elle **prescrit** (l'index `coding-assertions`), le critère de la coupe est : *si
     l'édition ne change aucune commande de porte ni aucun prérequis bloquant, c'est du reflet*. La
     prose de détail déjà présente dans la fiche d'un enfant sort donc vers son home et laisse un
     pointeur. La table des commandes, ses prérequis, et le recensement des repos sans porte ne
     bougent pas. *Pourquoi : déplacer une explication ne change pas ce qui gate, donc ça n'arbitre
     aucune décision.*

## Test

- La memory de chaque repo concerné est mise à jour avant son README (ordre memory → README respecté).
- Chaque édition trace son verdict de l'action 03. Une ligne écrite sans candidat correspondant au plan
  est une dérive : la signaler, pas l'écrire.
- Si `10-learn` est disponible **et la cible est à plat**, le chemin nominal passe par son invocation,
  pas par une réécriture maison de son pipeline, **et** le prompt qui l'invoque porte les verdicts.
- Une memory **centralisée** (`aidd_docs/memory/<enfant>/`) est éditée en direct (cas B), jamais
  déléguée à `10-learn` (qui écrirait à plat au top-level parent).
- Un fait déporté est retrouvable au home destinataire **avant** que la copie soit retirée.
- **Toute affirmation qui citait un fait corrigé a été rejouée**, ou porte la mention « supposé ». Une
  phrase réécrite sans que sa mesure soit relancée est une régression, pas une correction.
- **Aucun décompte retiré n'a été remplacé par une explication.** Si le chiffre sort, ce qui le remplace
  est un chemin.
- Aucune édition sur une memory de régime décision (`decisions`) ni sur le contrat partagé. Sur un
  index de portes, aucune commande ni prérequis modifié — seule la prose de détail a bougé.
- En édition directe (cas B), la structure existante du fichier a été lue avant toute modification, et
  l'édition est ciblée (pas de fichier réécrit en entier).
