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
- `actions/NN-<slug>.md` — une par action, à l'anatomie, avec `## Test`.
- `references/` et `assets/` — seulement si une action en a besoin.

## Process

1. **Lire la convention.** Ouvrir `references/skill-authoring-fr.md` avant d'écrire quoi que ce soit. Toutes les règles citées plus bas (R1, R5, R8…) y sont définies. Je ne les recopie pas ici.
2. **Nommer et vérifier la collision.** Choisir le nom selon la section « Nommage » de la convention, puis appliquer son « Check de collision » avant de créer. *(Les deux vivent dans la convention, on ne les recopie pas ici — R6.)*
3. **Choisir la forme.** Responsabilité unique, pas de référence à différer → mono-fichier (`SKILL.md` seul, exception R1). Plusieurs actions distinctes ou de la connaissance à charger à la demande → routeur + `actions/`. Dans le doute, commencer mono-fichier ; on découpe quand ça déborde.
4. **Cadrer les actions** (si routeur). Découper le but en actions à responsabilité unique. Une action = une étape vérifiable. Numéroter (`01-`, `02-`…) seulement si l'ordre est strict.
5. **Écrire le `SKILL.md`.** Frontmatter (`name` égal au dossier, `description` en forme R5 « quoi + quand + NE PAS pour »). Puis le corps : routeur pur (intro, flux, table d'actions, règles transverses) si routeur ; méthode inline directe si mono-fichier. Pas de logique métier dans un routeur (R1).
6. **Écrire chaque action** (si routeur). Suivre l'anatomie de la convention : `# NN - Titre` + phrase, `## Input` (si utile), `## Output` (obligatoire), `## Process` (étapes numérotées, label gras d'un mot par étape), `## Test`. Une idée par phrase (R11). Toujours le pourquoi sur une règle (R12).
7. **Sortir les données lourdes.** Un gabarit à copier va dans `assets/`, une donnée à lire va dans `references/`. Une action cite le fichier, ne l'inline pas (R6/R7).
8. **Rédiger en français.** Tout le contenu en français, sauf les en-têtes d'anatomie. Si une source anglaise a servi, réécrire la prose en français (R10).
9. **Symlinker si perso.** Si le skill vit dans `claude-config-perso/skills/`, créer le lien `~/.claude/skills/<nom>` → la cible réelle, comme les autres skills perso.

## Test

- `SKILL.md` existe, avec un frontmatter portant `name` (égal au dossier) et `description`.
- Si le skill a des actions : chaque fichier `actions/*.md` porte une section `## Output` et une section `## Test` (grep les deux en-têtes, aucune action ne doit en manquer). En mono-fichier, ce check ne s'applique pas.
- Aucun fichier ne contient de placeholder vide type `## X → Aucun` (R9) : grep ne renvoie rien.
- Aucun en-tête d'anatomie autre que `Input`/`Output`/`Process`/`Test` ; le reste de la prose est en français.
- Enchaîner sur `02-validate` sur le skill fraîchement écrit : il doit passer.
