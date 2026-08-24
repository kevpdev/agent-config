# <NN - Titre de l'action>

<Une phrase : ce que fait cette action.>

## Input

<OPTIONNEL. Ce que l'action consomme. Omis quand elle ne consomme rien.>

## Output

<OBLIGATOIRE. Une ligne nommant ce qui est produit, avec son chemin d'écriture si c'est un fichier.>

## Process

<OBLIGATOIRE. Un numéro est toujours une étape jouée dans l'ordre. Un cas, une branche, une garde ou un retour de boucle est une sous-puce, jamais un numéro.>

1. **<Label>.** <Étape impérative, une phrase.>
   - <la garde, la branche ou la boucle qui appartient à cette étape>
2. **<Label>.** <Étape suivante.>

## Test

<OBLIGATOIRE. Une ligne par vérification observable par exécution réelle, jamais un mock.>

| Cas | Preuve |
| --- | --- |
| <ce qui est lancé> | <le résultat observable qu'il rend> |

> Remplir chaque `<...>` et supprimer cette ligne. Un chevron resté dans le fichier écrit est un bug.
