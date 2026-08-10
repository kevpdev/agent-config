# 02 - Cribler

Fait descendre chaque instruction du cadrage dans la cascade C1→C5, mesures d'abord, verdicts ensuite.

## Input

La liste d'instructions et le contrat rendus par `01-cadrer`.

## Output

Un verdict de cascade par instruction : critère de sortie (ou « survit jusqu'à C6 »), action prescrite par la grille, base du verdict (« mesuré » / « jugé sur pièce » / « supposé »).

## Process

1. **Trier.** Séparer les critères en deux natures. Exécutables : sondage C1, grep C4 (un motif central par instruction), `head` des frontmatters C5. Jugements : C1 par nature (décision, piège, préférence), verdict C2, gradient C3. Les exécutables se batchent avant tout verdict (« mesurer avant de juger », règle transverse du routeur).
2. **Batcher.** Lancer tous les greps C4 et les `head` C5 en lots, sur `rules/`, `skills/`, `wrappers/`, les `CLAUDE.md` du domaine. Exclure les fichiers que le contrat interdit de lire. Consigner chaque sortie brute avant interprétation.
3. **Sonder (C1).** Réserver le sondage sous-agent aux instructions suspectes d'inférabilité — pas systématique, un sondage coûte une session. Protocole : sous-agent sommé d'ignorer les règles injectées dans son contexte, interdit de lire la règle testée et le dossier `audits/`, qui compte ses appels d'outil et cite sa source. Marquer le résultat « approximé » : les règles globales sont injectées aux sous-agents (vérifié le 2026-07-20, cf. `wrappers/claude/rules/memory-policy.md`), le contexte n'est donc jamais vraiment neuf.
4. **Descendre.** Pour chaque instruction, dérouler C1→C5 dans l'ordre de la grille et sortir au premier critère disqualifiant. Les définitions et les actions prescrites (supprimer, synthèse, pointeur, hook…) se lisent dans la grille au moment du verdict — ne pas les recopier ni les paraphraser de mémoire. C6 ne se juge pas ici : un budget est une somme, une instruction seule ne le viole jamais (→ `03-consolider`).
5. **Remesurer.** Un chiffre repris d'une note, d'un rapport antérieur ou du seed de la grille se remesure avant d'entrer dans un verdict — c'est une exigence de la grille (section Méthode), pas une option.
6. **Capturer.** Une découverte hors contrat (défaut C2 croisé pendant une passe C4, incohérence de la grille, doc contradictoire) se note en une ligne dans une liste « captures » et ne se creuse pas — y compris quand elle touche la grille (règle transverse du routeur : la grille ne se touche pas pendant l'audit).

## Contrôle de sortie

- Chaque instruction du cadrage porte un verdict avec son critère de sortie et sa base ; aucune n'est absente ni jugée « en bloc » avec ses voisines de fichier.
- Chaque verdict « mesuré » cite sa commande ou sa sortie ; chaque « supposé » est marqué tel quel.
- Les sondages C1 portent la mention « approximé ».
- La liste des captures hors contrat existe (éventuellement vide) et aucune capture n'a été creusée.

## Test

Scénarios dans `evals/eval.json` — notamment la capture sans creusage d'une découverte hors grille.
