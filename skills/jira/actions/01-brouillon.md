# 01 - Brouillon

Amène un besoin à l'état de brouillon de backlog publiable, en déléguant la rédaction et en contrôlant
le résultat.

## Input

Un besoin en prose, ou le chemin d'un brouillon déjà écrit sous `aidd_docs/backlog/`.

## Output

Un fichier `aidd_docs/backlog/<type>/<slug>.md` qui existe, dont le frontmatter est conforme au type,
et dont l'écart éventuel avec les conventions du dépôt est nommé plutôt que corrigé en silence.

## Process

1. **Lire la mémoire avant tout.** Ouvrir la mémoire projet pour y trouver le support qui fait
   autorité, la convention de nommage et les extensions de frontmatter que le dépôt déclare. Sans
   cette lecture, l'action inventerait des conventions que le dépôt contredit.
2. **Trancher le type.** Un besoin porte de la valeur utilisateur observable → story. Un travail borné
   sans valeur propre → task. Un regroupement → epic. Un dysfonctionnement → defect. Une question dont
   la réponse est une connaissance → spike.
   - Si deux types se défendent, demander. Le type décide du cycle de vie et des relations, donc se
     tromper coûte une réécriture entière.
   - **Garde.** Si aucun type ne se défend, s'arrêter et le dire, sans écrire de fichier et sans
     ouvrir aucun skill `aidd-pm`. Un besoin sans livrable identifiable n'est pas un artefact de
     backlog mal typé, c'est un besoin qui n'en est pas un. **À LA PLACE de** le forcer dans le type
     le moins faux, rendre ce qui a été observé et rien d'autre.
   - **Chercher d'abord la mesure qui tuerait le sujet**, avant de choisir le type et avant de poser la
     question. Une commande qui prouve l'absence de livrable épargne toute la chaîne. *Mesuré le
     2026-08-20 : un besoin de repointage de connecteur MCP est tombé sur un `grep` montrant que la
     cible n'existait sur aucun fichier de la machine, donc qu'aucun livrable local n'était possible.*
     Le type n'avait plus à être tranché.
   - *Pourquoi cette branche est nommée explicitement :* les skills `aidd-pm` portent chacun leur propre
     qualification et refuseront le besoin de toute façon. Mais ils refusent **après** avoir été
     ouverts, donc après avoir payé le cadrage. Refuser ici coûte une commande.
3. **Déléguer la rédaction** au skill `aidd-pm` du type retenu, et le laisser aller jusqu'à sa
   persistance. Ne pas rédiger le contenu ici, ni pré-remplir son gabarit.
   - Le fichier écrit vit sous `aidd_docs/backlog/<type>/<slug>.md`, le slug en kebab-case, et son
     `type` de frontmatter correspond au dossier qui le contient.
   - *Pourquoi la délégation est stricte :* ce skill-là porte la maturité, l'ordonnancement et les
     relations du type. Les court-circuiter produit un artefact que le reste du framework refusera.
4. **Contrôler le frontmatter** contre le `relations.md` du type. Chaque type verrouille sa liste de
   champs par une clause « carries no other field ». Un champ hors liste doit être une extension
   déclarée par le dépôt, sinon c'est un défaut.
   - Le `status` appartient à l'énumération du cycle de vie du type, et il n'est pas traduit.
   - Le champ qui porte la clé du ticket est une extension de ce genre. Sa forme et sa raison vivent
     dans [extension-frontmatter](../references/extension-frontmatter.md).
5. **Ne pas renseigner la clé du ticket maintenant.** Elle s'écrit à la publication, et elle seule
   marque le passage à l'état gelé. Un champ posé vide mentirait sur l'état du brouillon.
6. **Rattacher le raisonnement.** Le brouillon garde un lien vers le dossier de cadrage qui porte les
   mesures et les alternatives écartées, par le champ prévu à cet effet par le type.
   - *Pourquoi ce lien est le seul qui compte :* le raisonnement du découpage est la seule matière que
     le tracker ne portera jamais.
7. **Rendre l'écart, ne pas le réparer.** Si l'artefact dévie d'une convention du dépôt, le dire en
   nommant la convention et le chemin. La correction est une décision de l'humain.
8. **Rendre la sortie sous le titre littéral `## Contrôle du brouillon`**, portant le chemin écrit, le
   type retenu, le skill `aidd-pm` qui a réellement écrit le fichier, et les écarts constatés.
   - *Pourquoi un intitulé imposé :* c'est le seul signal qui permette de distinguer, depuis
     l'extérieur, une action qui a tourné d'une réponse plausible écrite sans elle.

## Test

| Cas | Preuve |
| --- | --- |
| un besoin de valeur utilisateur passé à l'action | un fichier existe sous `aidd_docs/backlog/story/`, le slug en kebab-case, le `type` du frontmatter égal au dossier |
| le frontmatter du fichier écrit | son `status` est une valeur de l'énumération du type, non traduite, et tout champ hors du `relations.md` du type est l'extension déclarée par le dépôt ou signalé comme défaut |
| le frontmatter du fichier écrit | la clé du ticket y est absente |
| un besoin sans livrable identifiable | aucun fichier écrit, aucun skill `aidd-pm` ouvert, et la sortie donne la mesure qui a établi l'absence de livrable |
| la sortie de l'action | elle porte le titre `## Contrôle du brouillon`, et nomme le skill `aidd-pm` qui a écrit, pas seulement le type |
