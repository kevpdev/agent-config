# 02 - Vérifier

Contrôle un skill contre la convention : le lint mécanique d'abord, puis les trois choses qu'aucun script ne peut trancher.

## Input

Le nom d'un skill de `skills/`, ou le chemin d'une cible perso. Un skill neuf sorti de `01-scaffold`, ou un skill existant à auditer.

## Output

Un rapport en français, verdict global en tête puis une ligne par contrôle, `PASS` ou `FAIL` avec le fichier et la raison. Le verdict dit toujours si la passe d'évals a été jouée.

## Process

1. **Linter.** Lancer `python3 wrappers/claude/scripts/lint-skills.py --skill <nom>` et reporter sa sortie telle quelle, sans la réinterpréter. Elle couvre le frontmatter, le nom, la longueur de la description, la liste de sections, les placeholders et les liens morts.
   - **Garde.** Une sortie 2 n'est pas un défaut du skill mais un instrument hors service (gabarit absent, YAML illisible). S'arrêter là et remonter la cause : un lint qu'on ne peut pas croire ne rend pas de verdict.
2. **Relire R1.** Un routeur ne porte que portée, flux, table d'actions et règles transverses. Des étapes numérotées de logique métier, ou du détail qui appartient à une action, sont une dérive à signaler. En mono-fichier, vérifier que l'inline reste justifié : responsabilité unique, sous ~150 lignes, aucune référence qui devrait sortir.
3. **Relire R6.** Chercher un même fait présent à deux endroits, entre le routeur et une action, entre deux actions, ou entre une action et une référence. Signaler chaque doublon avec ses deux emplacements, la copie périmée étant ce qui fait dériver un skill.
4. **Relire R13.** Croiser deux signaux : le skill **exécute-t-il** un effet de bord, et porte-t-il `disable-model-invocation: true` ? Effet de bord sans le champ est un `FAIL` dur, le skill partant au flair sur une action irréversible. Champ présent avec une liste de phrases déclencheuses dans la description est un `FAIL` aussi, elle promet un déclenchement qui n'existe plus.
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
| le verdict final | dit explicitement que les évals n'ont pas été jouées, et rend la commande pour les jouer |
