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

*Ce `## Test` n'a plus de cible à réponse connue : sa cible d'avance était un renommage réel du repo,
et il n'en reste aucun depuis l'archivage du 2026-08-24. Les lignes ci-dessous vérifient la cohérence
interne du plan, pas sa justesse. Rétablir une cible nommée au prochain renommage réel, au lieu d'en
fabriquer une. Un renommage inventé mesurerait le test.*

| Cas | Preuve |
| --- | --- |
| compter les lignes de tableau de la section « ce qui casse » | autant de lignes que `grep -rn '<ancien nom>'` trouve d'occurrences dans le repo, un écart signalant une entrée inventée ou une occurrence manquée |
| `--etat` relancé après l'action | rend `plan_a_refaire: false` et `corps_present: true` |
| relecture du plan écrit | il ne contient ni « à vérifier », ni « probablement », ni section vide |
