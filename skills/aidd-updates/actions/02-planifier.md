# 02 - Planifier l'adaptation

Traduit les changelogs des versions sautées en une liste de patchs prouvés par grep, et l'écrit sur
disque pour ne pas la reconstruire au prochain appel.

## Input

Le JSON de `--etat` rendu par l'action 01, dont `cle_installe`, `cle_upstream` et `cassant`.

## Output

Le corps du plan écrit dans le fichier d'état via `--marquer-planifie`, au format
`../assets/gabarit-plan.md`, et affiché à l'humain.

## Process

1. **Lire.** Pour chaque plugin en retard, récupérer son `CHANGELOG.md` upstream (URL dans
   `../references/detecteur.md`) et n'en garder que les sections entre la version installée et la
   version cible.
   - Lire aussi le changelog racine quand un changement ne se rattache à aucun plugin.
2. **Extraire les ruptures.** Relever les sections `### ⚠ BREAKING CHANGES`, et en déduire la liste
   des noms qui changent : skills renommés ou renumérotés, skills supprimés, agents renommés, chemins
   d'artefacts déplacés.
   - C'est de la prose, donc c'est un travail de lecture, pas d'expression régulière. Le script, lui,
     n'a comparé que des numéros de version.
3. **Prouver l'impact.** Pour chaque nom relevé, grep le repo. Les cibles habituelles sont les noms
   `plugin:NN-slug`, les noms d'agents, et les chemins `aidd_docs/`.
   - Aucune occurrence → la rupture ne nous touche pas, elle va en une ligne dans la section « monte
     sans nous toucher ».
   - Occurrences trouvées → une ligne de tableau par occurrence, avec fichier, ligne, valeur
     actuelle, valeur cible.
4. **Rédiger.** Remplir le gabarit. Les plugins cassants ouvrent le plan.
   - Ne pas recopier la prose upstream. Une ou deux phrases par rupture, en français.
   - Ne jamais écrire « à vérifier ». Une entrée non prouvée par grep n'est pas une entrée.
5. **Écrire.** Passer le corps rédigé sur stdin de `--marquer-planifie`.
   - Ne pas éditer le front-matter, ni le fichier d'état par un autre moyen.
6. **Rendre la main.** Afficher le plan, puis demander « on applique maintenant, ou plus tard ? ».
   - Plus tard → s'arrêter. Le plan reste en `statut: planifie`, et l'action 01 le ressortira intact.
   - Maintenant → action 03.

## Test

- Sur l'état réel de cette machine, le plan doit nommer `skills/aidd-pilot/actions/01-intake.md` et
  le passage de `aidd-refine:04-shadow-areas` à `aidd-refine:03-shadow-areas`. C'est la cible connue
  d'avance, donc le juge du plan.
- `grep -c '^| ' ` sur la section « ce qui casse » rend autant de lignes que
  `grep -rn '<ancien nom>'` trouve d'occurrences dans le repo. Un écart signale une entrée inventée
  ou une occurrence manquée.
- Après l'action, `--etat` rend `plan_a_refaire: false` et `corps_present: true`.
- Le plan ne contient ni « à vérifier », ni « probablement », ni section vide.
