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
   - **Si aucun ne se défend, s'arrêter et le dire.** Un besoin sans livrable identifiable n'est pas un
     artefact de backlog mal typé, c'est un besoin qui n'en est pas un. **À LA PLACE de** le forcer dans
     le type le moins faux, rendre ce qui a été observé et rien d'autre.
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
   - *Pourquoi la délégation est stricte :* ce skill-là porte la maturité, l'ordonnancement et les
     relations du type. Les court-circuiter produit un artefact que le reste du framework refusera.
4. **Contrôler le frontmatter** contre le `relations.md` du type. Chaque type verrouille sa liste de
   champs par une clause « carries no other field ». Un champ hors liste doit être une extension
   déclarée par le dépôt, sinon c'est un défaut.
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

## Contrôle de sortie

- **Sur refus de typage**, aucun fichier n'a été écrit, aucun skill `aidd-pm` n'a été ouvert, et la
  sortie donne la mesure qui a établi l'absence de livrable. Les contrôles suivants ne s'appliquent pas.
- Le fichier existe sous `aidd_docs/backlog/<type>/<slug>.md`, le slug en kebab-case.
- Le `type` du frontmatter correspond au dossier qui le contient.
- Le `status` appartient à l'énumération du cycle de vie du type, et il n'est pas traduit.
- Tout champ de frontmatter hors du `relations.md` du type est soit l'extension déclarée par le dépôt,
  soit signalé comme défaut dans la sortie.
- La clé du ticket est **absente** du frontmatter à ce stade.
- La sortie nomme le skill `aidd-pm` qui a réellement écrit le fichier, pas seulement le type.
- La sortie porte le titre littéral `## Contrôle du brouillon`, sous lequel vivent le chemin écrit, le
  type retenu et les écarts constatés. *Pourquoi un intitulé imposé : c'est le seul signal qui permette
  de distinguer, depuis l'extérieur, une action qui a tourné d'une réponse plausible écrite sans elle.*

## Test

Scénarios dans [`evals/eval.json`](../evals/eval.json).
