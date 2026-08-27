# 02 - Classer l'impact

Pour chaque fichier du scope validé, détermine le régime (reflet/décision) et la surface doc cible.

## Input

Le scope validé de l'action 01 : la liste de fichiers changés, par repo. En `--audit`, c'est la liste des fichiers de **mémoire** retenus, et non des fichiers de code.

## Output

Une classification par fichier : `chemin → impact → régime → cible doc`. Ou, si rien d'impactant, un constat d'arrêt (« aucune surface doc touchée ») — **jamais en `--audit`**, où chaque fichier du scope ressort classé.

## Process

1. **Classer.** Pour chaque fichier du scope, déterminer l'impact, le régime, puis la surface cible. Le régime commande le traitement aval (reflet → réécrit, décision → signalé).

   | Pattern de chemin | Impact | Régime | Cible doc |
   |---|---|---|---|
   | `migration/`, `*Entity*`, `*Repository*`, `.sql` | schéma DB | reflet | memory `database.md` + README (section DB/archi) |
   | `*Controller*`, `*Dto*`, `*Request*`, `*Response*` | contrat API | reflet côté repo, **décision** côté contrat partagé | memory `api-docs.md` + README (section API) + **signaler** l'écart au contrat partagé (→ action 07) |
   | `*Service*`, `*Config*`, `*Orchestrator*` | archi/comportement | reflet | memory `codebase-map.md` + README (section archi/pipeline) |

   - **Choisir l'instrument avant de chercher, la question est « symbole ou texte ? »**

     | Ce qu'on va vérifier | Instrument |
     |---|---|
     | une classe, une méthode, qui appelle quoi, ce qu'un changement casse | l'**outil de symboles** que le projet déclare, s'il en déclare un |
     | la même question **à travers plusieurs dépôts** | l'outil **inter-dépôts** du projet, quand il en expose un |
     | une clé de properties, du SQL, une migration, un template CI, une URL littérale | **grep**, scopé sur les dossiers d'enfants et jamais lancé depuis la racine du parent |

     Appliqué aux trois lignes de la table ci-dessus : `.sql` et `migration/` sont du **texte**, `*Entity*`/`*Repository*` demandent les deux (l'outil de symboles pour la classe, grep pour le SQL), `*Controller*`/`*Service*`/`*Config*` sont du **symbole** — l'URL de l'endpoint restant du texte.
     - **Où sont les noms concrets de ces outils** : dans la memory du projet, jamais ici. Ce skill sert plusieurs projets, donc il nomme des rôles et pas des outils. Chez Winggy-v3, c'est `aidd_docs/memory/codebase-map.md`, encadré « Pour une question de symbole, il existe un graphe ».
     - **Un zéro rendu par un outil de graphe ne se lit pas comme une absence** sans l'avoir calibré sur un symbole dont on sait qu'il est là. *Pourquoi : un index périmé répond « aucun résultat » exactement comme un symbole qui n'existe pas. Mesuré le 2026-08-26 chez Winggy-v3, un symbole ajouté une seconde plus tôt ressortait absent.*

   **En `--audit`, sauter la table d'impact ci-dessus** — pas celle de l'instrument, qui vaut dans les deux entrées. Elle classe du **code** par son chemin, et un fichier de mémoire ne matche aucun de ses patterns. Classer alors chaque fichier du scope directement par la **table des régimes** de [regimes-de-doc.md](../references/regimes-de-doc.md), que l'étape 3 désigne déjà comme la source unique. La cible doc **est** le fichier lui-même, il n'y a pas de cible à déduire.
   - *Pourquoi le dire au lieu de laisser déduire : sans cette ligne, la table ne rend aucune correspondance et l'audit ressort en « aucune surface impactée » — un arrêt sur un faux négatif, sur une action dont c'est précisément l'étape 4.*

2. **Cibler.** Les **noms de sections README ne sont pas figés** : viser « la section qui couvre X ». La structure réelle du README (lue au préalable, cf. action 06) fait foi.
3. **Router par régime.** Les cibles reflet memory partent vers le triptyque 03 → 04 → 05, puis les cibles reflet README vers l'action 06. Les cibles décision partent vers l'action 07 (signaler, ne pas écraser). Lire la table des régimes de [regimes-de-doc.md](../references/regimes-de-doc.md) pour savoir laquelle est laquelle — ne pas travailler de mémoire sur une liste recopiée ici. *Pourquoi : une énumération dupliquée finit par omettre une surface ajoutée depuis, et cette surface se fait réécrire au lieu d'être signalée.* En coordinateur, la classification vaut par repo : chaque enfant contre son propre code, le contrat partagé au parent.
4. **Arrêter si vide.** Si rien d'impactant (fix pur, test, refacto interne sans surface publique) → **le dire et s'arrêter**. Ne pas inventer de mises à jour pour justifier le run.
   - **Cette étape ne se déclenche pas en `--audit`.** « Aucune surface doc touchée » n'a pas de sens sans diff : le scope d'audit **est** la surface. Un audit qui ne rend aucun constat est un **verdict** (le banc passe le critère), il se prononce en fin de cycle par l'action 05, jamais ici.

## Test

- Chaque fichier du scope reçoit un régime (reflet ou décision) et une cible doc, ou est explicitement écarté comme sans impact.
- Un fichier `*Controller*`/`*Dto*` en contexte coordinateur est marqué décision côté contrat partagé (routé vers 07), pas réécrit d'office.
- Un scope sans surface publique impactée produit un arrêt annoncé, aucune cible inventée.
- **En `--audit`, aucun arrêt à l'étape 4 et aucun fichier du scope classé « sans impact ».** Chaque fichier de mémoire du scope ressort avec un régime. Un audit qui s'arrête ici a pris la table d'impact au lieu de la table des régimes.
