# 02 - Vérifier

Contrôle un skill contre la convention. Deux passes : les `## Test` des actions (comme l'AIDD), puis le lint R1/R4/R6 (le trou que l'AIDD laisse ouvert).

## Input

Le chemin d'un skill (`~/.claude/skills/<nom>/` ou une cible perso). Un skill neuf sorti de `01-scaffold`, ou un skill existant à auditer.

## Output

Un rapport, une ligne par contrôle : `PASS` / `FAIL` + le fichier et la raison en cas d'échec. Verdict global en tête : prêt, ou liste des corrections à faire.

## Process

1. **Détecter la forme.** Présence d'un dossier `actions/` → skill routeur. Sinon → mono-fichier (exception R1). Toute la suite s'adapte à ce constat.
2. **Lint R5 — frontmatter.** `SKILL.md` porte un frontmatter avec `name` (égal au dossier) et `description`. Absence de l'un ou l'autre = `FAIL` dur : sans `description`, le harness déclenche mal le skill.
3. **Relancer les `## Test`.**
   - Routeur : pour chaque action, lire sa section `## Test` et exécuter réellement chaque vérif (commande, contrôle d'artefact, effet observable). Jamais un mock. Idéalement chaque action dans un contexte neuf, pour qu'un état partagé ne masque pas un manque.
   - Mono-fichier : exécuter le `## Test` de `SKILL.md` s'il existe. S'il n'y en a pas et que le skill produit un artefact vérifiable, signaler le manque (R8). Un skill purement conversationnel (persona) peut légitimement n'avoir aucun test.
4. **Lint R4 — taille.** Compter les lignes de `SKILL.md`. Au-delà de 500, signaler : le routeur doit dégraisser vers des références.
5. **Lint R1 — forme justifiée.**
   - Routeur : le corps ne porte que intro courte, flux, table d'actions, règles transverses avec pointeurs. Des étapes numérotées de logique métier, un `## Process`, ou du détail qui appartient à une action → dérive à signaler.
   - Mono-fichier : vérifier que l'inline est justifié (responsabilité unique, sous le seuil d'alerte ~150 lignes, aucune connaissance de référence qui devrait sortir en `references/` par R7). Sinon, proposer le découpage en actions.
6. **Lint R6 — doublon.** Chercher un même fait présent à deux endroits (une règle recopiée entre `SKILL.md` et une action, ou entre deux actions/références). Signaler chaque doublon avec ses deux emplacements. *Pourquoi : la copie stale survit et fait dériver le skill.*
7. **Lint R9 — pas de section vide.** Grep les placeholders type `→ Aucun` ou une section d'anatomie sans contenu dessous. Signaler.
8. **Rendre le verdict.** Si tout passe, dire prêt. Sinon, lister les corrections par fichier, la plus structurante d'abord (R5/R1/R6 avant la cosmétique).

## Test

- Lancé sur ce skill (`skill-craft` lui-même), le rapport sort avec un verdict global et au moins une ligne par action vérifiée.
- Lancé sur un skill mono-fichier (sans `actions/`), aucun `FAIL` fantôme pour « actions manquantes » ; la passe `## Test` cible `SKILL.md`.
- Lancé sur un skill sans `description` dans le frontmatter, le lint R5 remonte un `FAIL` dur.
- Lancé sur un skill où une règle du routeur est aussi recopiée dans une action, le lint R6 remonte le doublon avec ses deux emplacements.
- Lancé sur un `SKILL.md` de plus de 500 lignes, le lint R4 remonte un `FAIL`.
- Le rapport est en français, sauf les libellés `PASS`/`FAIL`.
