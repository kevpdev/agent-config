# 02 - Classer les documents

Donne à chaque document du scope un type et un régime, puis route chacun vers l'action qui le traite.

## Input

L'en-tête de `scope.md`, écrit par `detect-scope`.

## Output

Dans `scope.md`, une ligne par document : chemin, type, régime, action suivante, et la raison en quelques mots. Ou un arrêt annoncé.

## Process

1. **Lister les documents.** En diff, les documents qui décrivent ce que les fichiers changés touchent : le README du repo, celui de l'enfant en coordinateur, la mémoire si `aidd_docs/` existe, les décisions qui le prescrivent. En `--audit`, les fichiers du scope eux-mêmes.
2. **Typer.** Un README prend le type `readme`, dont les règles vivent dans [`../references/types/readme.md`](../references/types/readme.md). Un autre document n'a pas de type pour l'instant et ne reçoit que des edits ciblés.
3. **Donner le régime** selon [`../references/regimes.md`](../references/regimes.md).
4. **Arrêter si vide.** En diff, un fix pur, un test ou une refacto interne ne touche aucun document : le dire et s'arrêter.
   - **Garde.** Jamais en `--audit`, où le scope est la doc elle-même et chaque fichier ressort classé.
5. **Router.** Mémoire AIDD vers `frame-memory`, reflet vers `sync-doc`, décision vers `reconcile`. Quand un repo a les deux, la mémoire passe avant le README.

## Test

| Cas | Preuve |
| --- | --- |
| un repo sans `aidd_docs/` | aucune ligne de `scope.md` ne porte le régime mémoire AIDD |
| un diff qui ne touche que des tests | l'action s'arrête en le disant, `scope.md` ne liste aucun document |
| un run `--audit` | chaque fichier du scope porte un régime, aucun n'est écarté |
