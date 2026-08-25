# 03 - Consolider

Juge C6 sur la somme des survivantes et fige le tout dans un rapport horodaté immuable.

## Input

Les verdicts de cascade et les captures rendus par `02-cribler`.

## Output

Un fichier `audits/AAAA-MM-JJ-audit-<domaine>.md` (nommage et invariants : la grille, section Méthode), rendu à l'utilisateur avec son verdict en une phrase.

## Process

1. **Sommer (C6).** Lancer la commande C6 de la grille (section C6 — une seule définition, ne pas la recopier) et comparer à la cible courante. En dépassement, désigner les contributeurs : `wc -w` par fichier des instructions survivantes, triés. *Pourquoi ici : C6 est le seul critère global de la cascade — jugé par instruction il ne disqualifie jamais rien.*
2. **Rédiger.** Le rapport selon les invariants de la grille : commit de la grille en en-tête (avec son état de travail), contrat et exclusions, puis ces sections aux intitulés imposés — `## Contrat`, `## Cascade par instruction` (tableau instruction × critère de sortie × action × base), `## Captures hors grille`, `## À réviser entre deux audits`, `## Ce que la passe apprend au protocole`. *Pourquoi des intitulés imposés : c'est le seul signal mesurable qu'un rapport vient de ce protocole.*
   - Les deux dernières ne visent pas le même objet. `## À réviser entre deux audits` vise la **grille**, ce qu'un audit mesure. `## Ce que la passe apprend au protocole` vise ce **skill**, l'instrument qui mesure. **Rendre la seconde même vide**, en le disant. *Pourquoi imposer la section plutôt que la vigilance : une section absente se voit au grep, une vigilance non tenue ne se voit pas.*
3. **Nommer.** Si un rapport du même jour existe déjà pour ce domaine, suffixer le nouveau nom (`-<passe>`), ne jamais éditer l'existant — un rapport est un instantané immuable. Ne pas lire l'existant si le contrat l'exclut.
4. **Verser.** Les propositions touchant la grille (critère manquant, seuil à revoir, test infaisable) vont dans `## À réviser entre deux audits`, jamais dans la grille (règle transverse du routeur : la révision se décide entre deux audits, par l'humain).
   - Celles touchant **ce protocole** vont dans `## Ce que la passe apprend au protocole`, **puis en ajout dans `audits/axes-protocole.md`**, table « Axes observés ». Y porter le symptôme, l'endroit qui le répare, et le compte d'occurrences relevé dans le registre.
   - **Ne rien appliquer.** Le statut d'un axe se lit dans le registre, il ne se décide pas ici : sa porte demande deux passes indépendantes, ou une mesure hors de l'audit. Une convention que la passe a dû trancher faute de réponse du protocole se verse en revanche dans la section « Conventions figées » du registre, pour que la passe suivante la lise au lieu de la réinventer.
5. **Rendre.** Dans le chat : verdict en une phrase, les corrections à fort enjeu (doublons volatils, règles inférables), le chemin du rapport. Proposer le commit, ne pas le faire seul.

## Si ça casse

- **Le criblage est arrivé incomplet** (partiel rendu par `02-cribler`) → rédiger le rapport quand même, sections imposées présentes, les instructions non criblées listées « non jugées » dans le tableau. Un partiel horodaté se reprend ; des verdicts qui attendent en session se perdent.
- **La commande C6 échoue** → pas de verdict C6 : le rapport porte l'erreur et « C6 non mesuré », jamais un chiffre reconstitué.
- **La collision de nom ne se résout pas** (le suffixe existe aussi) → incrémenter le suffixe ; ne jamais éditer un rapport existant, quel qu'il soit.

## Contrôle de sortie

- Le fichier existe sous `audits/`, son nom porte la date du jour et le domaine, et aucun rapport existant n'a été modifié (`git status` ne montre que des ajouts sous `audits/`).
- L'en-tête cite le commit de la grille ; les **cinq** intitulés imposés sont présents (grep), `## Ce que la passe apprend au protocole` comprise, même vide.
- Tout axe de cette section a été versé dans `audits/axes-protocole.md`, et **aucun n'a été appliqué** par la passe.
- Chaque ligne du tableau porte une base « mesuré / jugé sur pièce / supposé » ; aucun constat n'en est dépourvu.
- La grille est intacte : `git diff -- audits/grille-harnais.md` vide sur la passe.

## Test

Scénarios dans `evals/eval.json` — notamment le second rapport du même jour qui suffixe au lieu d'éditer.
