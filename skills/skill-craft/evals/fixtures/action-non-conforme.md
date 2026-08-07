# 01 - Collecter

Rassemble les dépendances déclarées d'un projet et rend un inventaire.

## Input

Le chemin d'un projet contenant un manifeste de dépendances.

## Output

Un fichier `inventaire.json` : une entrée par dépendance, avec son nom, sa version déclarée et son
gestionnaire d'origine.

## Process

1. **Repérer.** Trouver le manifeste (`package.json`, `pom.xml`, `pyproject.toml`).
2. **Extraire.** Lire les dépendances déclarées, sans résoudre l'arbre transitif.
3. **Écrire.** Sérialiser l'inventaire, trié par nom.

## Test

- `inventaire.json` existe et parse.
- Chaque entrée porte `nom`, `version` et `gestionnaire` ; aucune valeur nulle.
- Le fichier est trié par nom : `python3 -c "…"` rend `True`.
- Lancé sur un projet sans manifeste, l'action s'arrête et le dit, au lieu de rendre un inventaire vide.
- Lancé sur un dépôt qui n'est pas un projet, l'action ne propose pas d'en créer un.
