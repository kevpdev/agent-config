# 05 - Contrôler la mémoire

Fait juger la mémoire écrite par un checker qui n'a pas participé à l'écriture, et route chaque constat
vers l'étape qui le répare.

## Input

Les fichiers de mémoire touchés par l'action 04, le plan cadré de l'action 03, et le home résolu par
l'action 01.

**En `--audit`, le checker juge le scope d'audit entier**, pas seulement ce que l'action 04 a réécrit.
*Pourquoi c'est le seul contrat d'input qui doit s'élargir : une entrée que l'action 03 a gardée **à
tort** ne produit aucune édition, donc l'action 04 ne la touche pas, donc le checker ne la voit jamais.
Cas mesuré le 2026-08-21 : l'encadré « trois couches » d'un `architecture.md` a été gardé à la main
avec sa paire de ports codée en dur. En entrée par diff, rien ne conteste ce jugement.*

## Output

Un rapport rempli depuis le gabarit `02-project-memory/assets/report.md` du framework, écrit sous
`aidd_docs/tasks/<yyyy_mm>/<yyyy_mm_dd>_memory-check/report.md`, plus le routage de chaque constat.
Aucune édition de mémoire.

## Process

1. **Dispatcher un checker frais.** Un seul `@aidd-dev:checker`, indépendant de l'écriture, sur le
   modèle de `aidd-orchestrator/skills/01-sdlc/references/03-check.md` (« one fresh checker,
   independent from implementation »).
   - *Pourquoi un agent neuf et non l'action 04 qui se relit : celui qui vient d'écrire juge sa propre
     intention, pas son résultat. Il lit ce qu'il voulait dire.*
   - Sa checklist de base porte déjà les deux items qui comptent ici — « No information duplication…
     link to the canonical home instead of copying » et « No incoherence or contradiction ».
2. **Lui tendre le critère par son chemin absolu.** Le checker n'étend sa checklist qu'avec « the
   project's own review checklist **when it provides one** ». `references/memory-criteria.md` vit dans
   le harnais, pas dans le projet audité : **il ne le trouvera pas seul**. Le prompt de dispatch lui
   passe son chemin absolu, en le nommant comme l'extension de checklist à appliquer.
   - *Pourquoi le dire ici : sans ce passage explicite, le check tourne sur la checklist de base et le
     critère d'inclusion n'est jamais vérifié — le rapport sort vert sans avoir rien mesuré.*
3. **Ajouter la passe périmée.** Lui passer aussi
   `aidd-context/skills/02-project-memory/references/review-protocol.md`, qui couvre ce que le critère
   ne voit pas : la revendication que le code contredit, le chemin ou la commande qui n'existe pas, le
   « pourquoi » que le code et l'historique ne soutiennent pas.
   - **Lui écrire son instrument dans le prompt, pas seulement le nom de l'outil.** « La revendication
     que le code contredit » est une question de code, donc elle se tranche avec l'outil de symboles du
     projet quand elle porte sur une classe ou une méthode, et avec un **grep** quand elle porte sur du
     SQL, une clé de properties ou un template CI. Ajouter aussi qu'un zéro rendu par un graphe se
     calibre sur un symbole connu présent avant d'être lu comme une absence.
     - *Pourquoi le prompt et pas l'outil : le harnais n'injecte au sous-agent que les **noms** des
       outils MCP, jamais leurs descriptions — vérifié le 2026-08-27. Le checker verra donc qu'un outil
       de symboles existe, et rien de ce que sa description interdit. Un checker qui interroge un
       graphe de symboles sur une migration Flyway obtient zéro résultat, et déclare la doc fausse.*
4. **Ne pas déléguer l'audit en bloc à `02-project-memory:03-check`.** Réutiliser son **protocole de
   revue** (étape 2), son **gabarit de rapport** et sa table « Duplicated facts ». Sauter son étape de
   correspondance structurelle.
   - *Pourquoi : chaque ligne de son `memory-destinations.md` écrit dans `aidd_docs/memory/<fichier>.md`
     à la racine, et son `structure.md` dit « flat, never nested ». Sur un home centralisé, il
     classerait chaque `<enfant>/tooling.md` en orphelin — un faux positif par enfant.*
5. **Router les constats.** Chaque constat nomme l'étape qui le répare, et une seule.

   | Constat | Où il repart |
   |---|---|
   | manquement au critère d'inclusion, doublon, copie d'un fichier du disque | action 03, le verdict était faux |
   | fait faux, périmé, chemin ou commande qui n'existe pas | action 04, l'écriture était fausse |
   | écart sur une surface de régime décision | action 07, il se signale et s'arbitre |
   | hausse de l'ensemble @-importé non justifiée | action 03, qui nomme l'ajout |
   | entrée sortie pour faire du chiffre, sans volet du critère cité | action 03, la sortie était fausse |

   **La ligne de la hausse ne se déclenche pas sur une passe de pointeur.** Quand chaque mot ajouté
   est un chemin qui remplace une copie, ou un fait neuf que la passe nomme, la hausse **est** la
   justification et il n'y a aucun constat. Le cas et sa mesure sont dans
   [`../references/memory-criteria.md`](../references/memory-criteria.md), § Verbosité. *Pourquoi le
   dire ici : le checker est dispatché en contexte neuf, il ne voit qu'un décompte qui monte.*

6. **Compter la passe, et s'arrêter.** Le retour vers 03 ou 04 rouvre un cycle, donc il lui faut une
   sortie qui ne dépend pas du jugement du modèle. **Le compteur vit dans le rapport, pas dans le
   contexte** : chaque checker est dispatché en contexte neuf, il n'a aucun souvenir de la passe
   précédente. Le rapport ouvre donc sur une ligne `Passe <n> sur 3` et la liste des constats déjà
   déclarés réparés.

   **Borne dure : deux retours au maximum**, donc trois contrôles en tout. *Pourquoi deux : un constat
   correctement diagnostiqué se répare en une passe, la seconde couvre le cas où la réparation en a
   créé un autre. Une troisième signifie que le diagnostic lui-même est faux, et aucune itération ne
   répare un diagnostic.*

   **Trois sorties avant la borne**, parce qu'un compteur seul laisse tourner deux passes inutiles :

   | Signal | Sortie |
   |---|---|
   | zéro constat actionnable | nominale, le banc est à jour |
   | un constat **déjà déclaré réparé** revient | **arrêt immédiat**, sans attendre le compteur — c'est la signature du cercle vicieux |
   | le lot de constats ne **rétrécit** pas d'une passe à l'autre | arrêt, la réparation ne converge pas |

   **Les constats routés vers l'action 07 ne comptent pas dans ce lot.** Ils quittent le cycle dès leur
   première apparition, partent à l'arbitrage humain et n'y reviennent pas. Le rapport les rend dans
   une section à part, dont l'intitulé dit qu'ils sortent du cycle.
   - *Pourquoi : l'action 07 signale et n'écrase jamais, donc un constat de régime décision ne peut pas
     être réparé par une passe suivante. Compté dans le lot, il le rend structurellement non
     décroissant et déclenche l'arrêt sur un signal qui ne mesure plus rien. Mesuré le 2026-08-21 sur
     une passe 1 : 4 constats sur 31, soit un lot qui ne pouvait pas descendre sous 4.*

7. **Échouer fermé.** À toute sortie non nominale : ne **jamais** déclarer le banc à jour, ne rien
   réparer de plus, et ne rien annuler tout seul. Le rapport nomme la passe atteinte, les constats non
   réparés, et joint `git diff --stat -- aidd_docs/memory/` pour que l'humain voie l'état intermédiaire
   et décide de continuer ou de revenir en arrière.
   - *Pourquoi ne pas annuler : un retour en arrière automatique est une édition que personne n'a
     demandée, et il détruirait les réparations justes des passes précédentes en même temps que les
     fausses.*
8. **Rendre.** Écrire le rapport, imprimer le résumé court avec son chemin, et poser la question de
   clôture : quels constats on applique. Le checker n'édite jamais, et cette action non plus.

## Test

- Le rapport existe au chemin attendu, et le résumé imprimé le nomme.
- Le prompt de dispatch cite le chemin absolu de `references/memory-criteria.md` en extension de
  checklist. Sans cette citation, l'action n'a pas tourné.
- Le prompt de dispatch porte la règle « symbole ou texte ? » en clair. Nommer l'outil sans sa règle
  ne compte pas : sa description ne traverse pas jusqu'au sous-agent.
- Chaque doublon relevé nomme les **deux** chemins et lequel garde le fait.
- Chaque constat porte l'action qui le répare, une seule.
- Le rapport ouvre sur `Passe <n> sur 3` et liste les constats déjà déclarés réparés. Un rapport sans
  ce numéro rend le cycle non bornable : il ne passe pas.
- **Aucune quatrième passe n'existe.** Un rapport à `Passe 4` est un défaut de l'action, pas un
  résultat.
- **Le lot compté à la passe `n` exclut les constats d'action 07.** Le rapport donne les deux nombres,
  le lot du cycle et le résidu sorti. Un rapport qui n'en donne qu'un rend le signal de décroissance
  illisible.
- Un constat déjà déclaré réparé qui revient produit un **arrêt immédiat**, avant même la borne.
- À toute sortie non nominale, le rapport nomme les constats non réparés et joint le `git diff --stat`.
  Le banc n'est jamais déclaré à jour dans ce cas, et aucune réparation n'a été annulée.
- Le rapport rend le décompte de mots de la racine, sans le confronter à une cible.
- **En `--audit`, le rapport couvre chaque fichier du scope**, y compris ceux que l'action 04 n'a pas
  touchés. Un rapport qui ne parle que des fichiers modifiés a tourné en entrée par diff.
- Aucun fichier sous `aidd_docs/memory/` n'a changé pendant cette action :
  `git status --porcelain aidd_docs/memory/` rend la même sortie avant et après.
