# 02 - Vérifier

Contrôle un skill contre la convention. Deux passes : les `## Contrôle de sortie` des actions, puis le lint R1/R4/R6/R8 (le trou que l'AIDD laisse ouvert).

## Input

Le chemin d'un skill (`$SKILLS_ROOT/<nom>/` ou une cible perso). Un skill neuf sorti de `01-scaffold`, ou un skill existant à auditer.

## Output

Un rapport, une ligne par contrôle : `PASS` / `FAIL` + le fichier et la raison en cas d'échec. Verdict global en tête : prêt, ou liste des corrections à faire.

## Process

1. **Détecter la forme.** Présence d'un dossier `actions/` → skill routeur. Sinon → mono-fichier (exception R1). Toute la suite s'adapte à ce constat.
2. **Lint R5 — frontmatter.** `SKILL.md` porte un frontmatter avec `name` (égal au dossier) et `description`. Absence de l'un ou l'autre = `FAIL` dur : sans `description`, le harness déclenche mal le skill.
3. **Relancer les `## Contrôle de sortie`.**
   - Routeur : pour chaque action, lire sa section et exécuter réellement chaque vérif (commande, contrôle d'artefact, effet observable). Jamais un mock. Idéalement chaque action dans un contexte neuf, pour qu'un état partagé ne masque pas un manque.
   - Mono-fichier : exécuter celui de `SKILL.md` s'il existe. S'il n'y en a pas et que le skill produit un artefact vérifiable, signaler le manque (R8). Un skill purement conversationnel (persona) peut légitimement n'en avoir aucun.
4. **Lint R8 — le tri des natures, et ne pas jouer les évals ici.** Un `## Test` qui contient des vérifs exécutables au lieu d'un pointeur vers `evals/` = `FAIL` : les deux natures sont mélangées, et l'éval se paie en contexte à chaque invocation du skill. Inversement, un critère rangé en `evals/` qui s'évalue depuis l'artefact que l'action vient de produire appartient au contrôle de sortie.
   - **Ne pas exécuter les scénarios d'`evals/`.** Ils demandent une session neuve, donc un exécuteur externe. Rendre la commande à lancer (voir le `README.md` du repo) et signaler la passe comme non jouée. *Pourquoi ne pas les jouer d'ici : une éval jugée par le contexte qui vient d'écrire le skill n'est plus une évaluation externe — c'est le skill qui se note lui-même, et il se donne toujours la moyenne.*
   - Vérifier quand même que `evals/eval.json` parse et que chaque scénario porte `query` et `expected_behavior`. Un fichier d'évals cassé rend le même « rien à signaler » qu'un fichier absent.
5. **Lint R4 — taille.** Compter les lignes de `SKILL.md`. Au-delà de 500, signaler : le routeur doit dégraisser vers des références.
6. **Lint R1 — forme justifiée.**
   - Routeur : le corps ne porte que intro courte, flux, table d'actions, règles transverses avec pointeurs. Des étapes numérotées de logique métier, un `## Process`, ou du détail qui appartient à une action → dérive à signaler.
   - Mono-fichier : vérifier que l'inline est justifié (responsabilité unique, sous le seuil d'alerte ~150 lignes, aucune connaissance de référence qui devrait sortir en `references/` par R7). Sinon, proposer le découpage en actions.
7. **Lint R6 — doublon.** Chercher un même fait présent à deux endroits (une règle recopiée entre `SKILL.md` et une action, ou entre deux actions/références). Signaler chaque doublon avec ses deux emplacements. *Pourquoi : la copie stale survit et fait dériver le skill.*
8. **Lint R9 — pas de section vide.** Grep les placeholders type `→ Aucun` ou une section d'anatomie sans contenu dessous. Signaler.
9. **Rendre le verdict.** Si tout passe, dire prêt — **en précisant que la passe d'évals n'a pas été jouée**, sinon « prêt » se lit comme « comportement vérifié ». Sinon, lister les corrections par fichier, la plus structurante d'abord (R5/R1/R8/R6 avant la cosmétique).

## Contrôle de sortie

- Lancé sur ce skill (`skill-craft` lui-même), le rapport sort avec un verdict global et au moins une ligne par action vérifiée.
- Lancé sur un skill mono-fichier (sans `actions/`), aucun `FAIL` fantôme pour « actions manquantes » ; la passe de contrôle cible `SKILL.md`.
- Lancé sur un skill sans `description` dans le frontmatter, le lint R5 remonte un `FAIL` dur.
- Lancé sur un skill dont une action porte un `## Test` rempli de vérifs exécutables, le lint R8 remonte un `FAIL` en nommant l'action.
- Lancé sur un skill où une règle du routeur est aussi recopiée dans une action, le lint R6 remonte le doublon avec ses deux emplacements.
- Lancé sur un `SKILL.md` de plus de 500 lignes, le lint R4 remonte un `FAIL`.
- Le verdict global dit explicitement que les évals n'ont pas été jouées, et rend la commande pour les jouer.
- Le rapport est en français, sauf les libellés `PASS`/`FAIL`.

## Test

Scénarios dans `evals/eval.json`. Ils portent le cas du verdict honnête — un validateur qui rend « prêt » sans dire que la passe comportementale n'a pas tourné inspire exactement la confiance qu'il n'a pas méritée.
