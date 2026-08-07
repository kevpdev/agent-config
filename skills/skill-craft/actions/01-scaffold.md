# 01 - Échafauder

De l'intention à un skill au format routeur, prêt à vérifier. Applique la convention (`references/skill-authoring-fr.md`) à chaque fichier écrit.

## Input

L'intention du skill, en prose libre :

- Le but, en une phrase (ce qu'il fait, quand on l'appelle).
- Le domaine : outil (un nom, ex. `slack`) ou activité (un verbe, ex. `review`).
- Les actions pressenties, si je les ai déjà en tête. Sinon on les dégage à l'étape 2.

## Output

Une arborescence de skill sous `skills/<nom>/` :

- `SKILL.md` — routeur pur.
- `actions/NN-<slug>.md` — une par action, à l'anatomie : `## Contrôle de sortie` pour les critères qui s'appliquent en tournant, `## Test` réduit à un pointeur.
- `evals/eval.json` — les scénarios qui jugent si le skill marche, en données pures.
- `references/` et `assets/` — seulement si une action en a besoin.

## Process

1. **Lire la convention.** Ouvrir `references/skill-authoring-fr.md` avant d'écrire quoi que ce soit. Toutes les règles citées plus bas (R1, R5, R8…) y sont définies. Je ne les recopie pas ici.
2. **Nommer et vérifier la collision.** Choisir le nom selon la section « Nommage » de la convention, puis appliquer son « Check de collision » avant de créer. *(Les deux vivent dans la convention, on ne les recopie pas ici — R6.)*
3. **Choisir la forme.** Responsabilité unique, pas de référence à différer → mono-fichier (`SKILL.md` seul, exception R1). Plusieurs actions distinctes ou de la connaissance à charger à la demande → routeur + `actions/`. Dans le doute, commencer mono-fichier ; on découpe quand ça déborde.
4. **Cadrer les actions** (si routeur). Découper le but en actions à responsabilité unique. Une action = une étape vérifiable. Numéroter (`01-`, `02-`…) seulement si l'ordre est strict.
5. **Écrire le `SKILL.md`.** Frontmatter (`name` égal au dossier, `description` en forme R5 « quoi + quand + NE PAS pour »). Puis le corps : routeur pur (intro, flux, table d'actions, règles transverses) si routeur ; méthode inline directe si mono-fichier. Pas de logique métier dans un routeur (R1).
6. **Écrire chaque action** (si routeur). Suivre l'anatomie de la convention : `# NN - Titre` + phrase, `## Input` (si utile), `## Output` (obligatoire), `## Process` (étapes numérotées, label gras d'un mot par étape), `## Contrôle de sortie`, `## Test`. Une idée par phrase (R11). Toujours le pourquoi sur une règle (R12).
7. **Trier les critères de vérification par nature** — c'est le point où un skill part de travers, parce que les deux natures se ressemblent à l'écriture. Appliquer le sous-point de R8 :
   - Un critère que l'action applique **pendant** qu'elle travaille (l'artefact porte tel champ, la commande sort en zéro, la sortie cite une preuve) → `## Contrôle de sortie`. Il sert à chaque exécution, donc il reste inline.
   - Un scénario qui juge **si le skill marche** (il se déclenche sur telle requête, il s'arrête au lieu de continuer, il n'appelle pas tel outil) → `evals/eval.json`, et `## Test` n'en garde que le pointeur.
   - *Le test qui distingue les deux :* est-ce que ce critère peut s'évaluer **au milieu** d'une exécution, à partir de ce que l'action vient de produire ? Oui → contrôle de sortie. Non, il faut lancer une session neuve et regarder son comportement → éval.
8. **Écrire les évals.** Un `evals/eval.json` en données pures, aux champs définis par R7 — jamais un nom d'agent ni un appel d'outil. Un scénario par comportement qui doit tenir, en visant d'abord ceux qui *échouent ouvert* : le skill qui continue là où il devait s'arrêter, celui qui appelle un outil interdit. *Pourquoi ceux-là d'abord :* un skill qui rend un résultat plausible au lieu de refuser ne se voit dans aucun contrôle de sortie.
9. **Sortir les données lourdes.** Un gabarit à copier va dans `assets/`, une donnée à lire va dans `references/`. Une action cite le fichier, ne l'inline pas (R6/R7).
10. **Rédiger en français.** Tout le contenu en français, sauf les en-têtes d'anatomie anglais. Si une source anglaise a servi, réécrire la prose en français (R10).
11. **Emplacement.** Le skill vit dans `agent-config/skills/<nom>/`. Chaque agent l'expose depuis ce dossier via son propre wrapper, qui pose aussi `$SKILLS_ROOT` — aucun lien par skill à créer. *Pourquoi cette variable :* un skill qui code en dur le chemin d'un agent ne tourne plus sous un autre, alors que le script visé est au même endroit relatif partout.

## Contrôle de sortie

- `SKILL.md` existe, avec un frontmatter portant `name` (égal au dossier) et `description`.
- Si le skill a des actions : chaque fichier `actions/*.md` porte `## Output` et `## Contrôle de sortie` (grep les deux en-têtes, aucune action ne doit en manquer). En mono-fichier, ce check ne s'applique pas.
- Chaque `## Test` ne contient **qu'un pointeur** vers `evals/`, aucun critère exécutable. Un `## Test` qui porte une liste de vérifs est un tri de natures non fait (étape 7).
- `evals/eval.json` existe et parse, chaque scénario portant au moins `query` et `expected_behavior`. Un skill purement conversationnel peut légitimement n'en avoir aucun — alors le dossier est absent, pas vide.
- Aucun fichier ne contient de placeholder vide type `## X → Aucun` (R9) : grep ne renvoie rien.
- Aucun en-tête de section autre que `Input`/`Output`/`Process`/`Test` (anglais, R10) et `Contrôle de sortie` (français, seule exception) ; le reste de la prose est en français.
- Enchaîner sur `02-validate` sur le skill fraîchement écrit : il doit passer.

## Test

Scénarios dans `evals/eval.json`. Celui qui compte ici est l'échafaudage d'un skill neuf : il porte le cas du tri des natures, parce qu'un générateur qui produit un `## Test` rempli de vérifs exécutables fabrique en série des skills qui paient leurs évals en contexte à chaque invocation.
