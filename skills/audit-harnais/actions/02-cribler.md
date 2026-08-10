# 02 - Cribler

Fait descendre chaque instruction du cadrage dans la cascade C1→C5 puis C7, et rend le verdict de cohérence C8 par fichier. Mesures d'abord, verdicts ensuite.

## Input

La liste d'instructions et le contrat rendus par `01-cadrer`.

## Output

Un verdict de cascade par instruction : critère de sortie (ou « survit jusqu'à C6 »), verdict C7 avec son comptage de mots, action prescrite par la grille, base du verdict (« mesuré » / « jugé sur pièce » / « supposé »). Plus un verdict C8 par fichier du cadrage.

## Process

1. **Trier.** Séparer les critères en deux natures. Exécutables : sondage C1, grep C4 (un motif central par instruction), `head` des frontmatters C5, comptage de mots par instruction C7. Jugements : C1 par nature (décision, piège, préférence), verdict C2, gradient C3. Les exécutables se batchent avant tout verdict (« mesurer avant de juger », règle transverse du routeur).
2. **Batcher.** Lancer tous les greps C4 et les `head` C5 en lots, sur `rules/`, `skills/`, `wrappers/`, les `CLAUDE.md` du domaine. Exclure les fichiers que le contrat interdit de lire. Consigner chaque sortie brute avant interprétation.
3. **Sonder (C1).** Réserver le sondage sous-agent aux instructions suspectes d'inférabilité — pas systématique, un sondage coûte une session. Protocole : sous-agent sommé d'ignorer les règles injectées dans son contexte, interdit de lire la règle testée et le dossier `audits/`, qui compte ses appels d'outil et cite sa source. Marquer le résultat « approximé » : les règles globales sont injectées aux sous-agents (vérifié le 2026-07-20, cf. `wrappers/claude/rules/memory-policy.md`), le contexte n'est donc jamais vraiment neuf.
4. **Descendre.** Pour chaque instruction, dérouler C1→C5 dans l'ordre de la grille et sortir au premier critère disqualifiant, puis passer **C7** sur chaque survivante — il juge la formulation, pas la présence, donc il ne fait jamais sortir de la cascade et se rend même quand l'instruction survit tout. Les définitions et les actions prescrites (supprimer, synthèse, pointeur, hook…) se lisent dans la grille au moment du verdict — ne pas les recopier ni les paraphraser de mémoire. C6 ne se juge pas ici : un budget est une somme, une instruction seule ne le viole jamais (→ `03-consolider`).
5. **Recouper (C8).** Une fois toutes les instructions d'un fichier criblées, rendre son verdict de cohérence (contradictions, redondance interne, orphelines — définitions dans la grille). *Pourquoi après la cascade : C8 se juge sur les survivantes, pas sur ce que C1→C5 va de toute façon retirer.*
6. **Remesurer.** Un chiffre repris d'une note, d'un rapport antérieur ou du seed de la grille se remesure avant d'entrer dans un verdict — c'est une exigence de la grille (section Méthode), pas une option.
7. **Capturer.** Une découverte hors contrat (défaut C2 croisé pendant une passe C4, incohérence de la grille, doc contradictoire) se note en une ligne dans une liste « captures » et ne se creuse pas — y compris quand elle touche la grille (règle transverse du routeur : la grille ne se touche pas pendant l'audit).

## Si ça casse

- **Une mesure échoue** (commande en erreur, outil absent) → le verdict se rend « supposé » avec l'erreur consignée ; ne jamais inventer ni reconstituer la sortie.
- **Un sondage C1 ou un test C7 est infaisable** (pas de sous-agent, budget de session) → verdict « jugé sur pièce », dit tel quel.
- **La grille change pendant la passe** (`git diff -- audits/grille-harnais.md` non vide) → stop, contrat cassé : rendre le partiel et remonter à l'utilisateur.
- **La session s'épuise avant la fin** → rendre les verdicts déjà rendus et la liste des instructions non criblées ; un partiel tracé se reprend, un criblage bâclé se refait.

## Contrôle de sortie

- Chaque instruction du cadrage porte un verdict avec son critère de sortie et sa base ; aucune n'est absente ni jugée « en bloc » avec ses voisines de fichier.
- Chaque fichier du cadrage porte un verdict C8.
- Chaque verdict « mesuré » cite sa commande ou sa sortie ; chaque « supposé » est marqué tel quel.
- Les sondages C1 portent la mention « approximé ».
- La liste des captures hors contrat existe (éventuellement vide) et aucune capture n'a été creusée.

## Test

Scénarios dans `evals/eval.json` — notamment la capture sans creusage d'une découverte hors grille.
