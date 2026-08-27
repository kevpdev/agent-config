# 02 - Vérifier

Contrôle un skill contre la convention : le lint mécanique d'abord, puis les trois choses qu'aucun script ne peut trancher.

## Input

Le nom d'un skill de `skills/`. Un skill neuf sorti de `01-scaffold`, ou un skill existant à auditer. Le skill d'un autre repo se vise par le `--corpus` du lint, qui n'y joue alors que le fond.

## Output

Un rapport en français, verdict global en tête puis une ligne par contrôle, `PASS` ou `FAIL` avec le fichier et la raison. Le verdict dit toujours si la passe d'évals a été jouée.

## Process

1. **Linter.** Lancer `python3 wrappers/claude/scripts/lint-skills.py --skill <nom>` et reporter sa sortie telle quelle, sans la réinterpréter. Elle couvre le frontmatter, le nom, la longueur de la description, la liste de sections, les placeholders, les liens morts et la cohérence interne d'un skill déjà déclaré manuel.
   - **Garde.** Sur un corpus étranger, ajouter `--corpus <dossier>`. Le lint coupe alors la conformité au gabarit et `argument-hint`, et sa ligne de bilan dit combien de vérifications ont tourné. Ne pas lire son « 0 défaut » comme un skill conforme à la convention d'ici.
   - **Garde.** Une sortie 2 n'est pas un défaut du skill mais un instrument hors service (gabarit absent, YAML illisible). S'arrêter là et remonter la cause : un lint qu'on ne peut pas croire ne rend pas de verdict.
2. **Relire R1.** Un routeur ne porte que portée, flux, table d'actions et règles transverses. Des étapes numérotées de logique métier, ou du détail qui appartient à une action, sont une dérive à signaler. En mono-fichier, vérifier que l'inline reste justifié : responsabilité unique, sous ~150 lignes, aucune référence qui devrait sortir.
3. **Relire R6.** Chercher un même fait présent à deux endroits, entre le routeur et une action, entre deux actions, entre une action et une référence, ou **entre deux skills**. Signaler chaque doublon avec ses deux emplacements, la copie périmée étant ce qui fait dériver un skill.
   - **Le lieu inter-skills se mesure, il ne se juge pas.** `grep -rl "<une phrase du fait>" skills/` pour le texte repris tel quel, `md5sum` de bloc pour une section entière. Le home d'un fait partagé est `skills/_shared/`, R6 le dit.
4. **Relire R13.** Deux questions en cascade, qu'aucun script ne tranche. Le skill **exécute-t-il** un effet de bord ? Si oui, sa `description` nomme-t-elle un appelant autre que l'humain ? Le couple de réponses désigne la branche de R13, qui porte le verdict de chacune.
   - **La seconde question se lit dans la `description`**, à la recherche d'un orchestrateur ou d'un skill voisin qui ouvrirait celui-ci. Sur la branche du maillon de pipeline, le contrôle porte sur le garde déterministe nommé dans les règles transverses, jamais sur le champ.
   - **Garde.** Ne pas relire la cohérence d'un skill déjà déclaré manuel, description et évals comprises. La vérification 7 du lint la tranche, et l'étape 1 a déjà reporté son verdict.
   - **Garde.** Ne pas compter les mots-clés, lire ce que le skill fait. Mesuré le 2026-08-11, un comptage d'occurrences refusait `mr-review`, qui cite « commit » et « push » pour décrire ce qu'il relit et se déclare en lecture seule dès sa description.
5. **Contrôler le corpus d'évals.** Vérifier que `evals/eval.json` parse, puis que sa composition suit R7, **exception des skills à invocation manuelle comprise**. Un fichier d'évals cassé rend le même « rien à signaler » qu'un fichier absent.
   - **Garde.** Ne pas réénoncer la composition attendue ici. *Pourquoi : cette étape exigeait « au moins un cas positif » quand R7 dit qu'un skill manuel n'en écrit pas. Contradiction relevée le 2026-08-26 par un validateur externe sur `jira`, sur une copie partielle vieille de deux fichiers.*
   - **Garde.** Ne pas jouer les cas depuis ici. Rendre la commande de l'exécuteur externe et déclarer la passe non jouée : une éval jugée par le contexte qui vient d'écrire le skill n'est plus une évaluation externe.
6. **Rendre le verdict.** Tout au vert se dit « prêt », **en précisant que le comportement n'a pas été mesuré**, sinon « prêt » se lit comme « comportement vérifié ». Sinon, lister les corrections par fichier, la plus structurante d'abord.

## Test

| Cas | Preuve |
| --- | --- |
| lancé sur `skill-craft` lui-même | rapport avec un verdict global et le lint à 0 défaut |
| lancé sur un skill dont une action porte une section hors gabarit | le rapport nomme l'action et le home de remplacement |
| lancé sur un skill mono-fichier | aucun `FAIL` fantôme pour « actions manquantes » |
| lancé sur un skill dont le corpus d'évals n'a aucun cas négatif | le rapport nomme le frère qui n'a pas son cas |
| lancé sur un skill à effet de bord dont la description nomme un orchestrateur | le rapport contrôle le garde nommé, et ne réclame pas `disable-model-invocation` |
| le verdict final | dit explicitement que les évals n'ont pas été jouées, et rend la commande pour les jouer |
