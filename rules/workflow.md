## Règle absolue — Demander avant d'implémenter

**INTERDIT**
- Écrire ou modifier du code sans "go ahead" explicite — même en mode bypass, même si la question appelle une implémentation directe

**AUTORISÉ**
- Proposer, expliquer, puis attendre la validation avant de toucher un fichier

## Règle — Pré-vol avant toute conclusion durable sur une codebase

**DÉCLENCHEUR** : avant de rédiger un plan, un audit, une note d'archi — tout document sur lequel quelqu'un décidera ensuite. Pas avant une réponse de conversation.

**OBLIGATOIRE — trois gestes, dans cet ordre**

1. **Rafraîchir le workspace** — `git fetch --all --prune` sur **chaque** repo, puis relever branche / avance-retard / état sale. Un clone en retard rend invisible le travail déjà fait.
2. **Chercher le précédent** — `git log --all --grep="<sujet>"` sur les repos **voisins**, pas seulement celui qu'on modifie. Le même changement a souvent déjà été fait ailleurs ; le lire coûte moins cher que le reconcevoir.
3. **Lire la source qui fait autorité** — le code, la config, le jar. Jamais le wiki, jamais un plan frère, jamais la mémoire de session.

**INTERDIT**
- Reprendre une valeur mécanique (port, route, signature, version, chemin) depuis un wiki ou un plan voisin sans l'avoir retrouvée dans le code ou la config
- **À LA PLACE** : ouvrir le fichier, et citer `fichier:ligne` dans le document produit. Une valeur non traçable se marque « supposé ».

**POURQUOI** : ces trois gestes coûtent quelques appels d'outil ; les sauter coûte des cycles de correction sur un document long, et chaque cycle relit un artefact entier pour une ligne fausse. Cas vécu : un consommateur avait **déjà** été basculé vers le même service cible, mais son clone était 16 commits en retard — le précédent est resté invisible pendant tout l'audit et n'a été trouvé que par accident, après coup. Deux autres erreurs du même plan venaient d'une route lue dans le wiki et d'un port recopié d'un plan frère, tous deux faux. Cause unique aux trois : une source adjacente consultée à la place de la source d'autorité.

**Rapport avec `reasoning.md`** : « ne jamais affirmer sans vérifier » dit *quoi* ne pas faire au moment d'écrire. Cette règle dit *quand* aller chercher — avant, pas au moment où le doute apparaît. Un doute qui n'apparaît pas ne déclenche aucune vérification.

## Règle — Vérifier après édition d'un fichier de build

**OBLIGATOIRE**
- Après édition d'un fichier de build (migration, fixture, config CI, dépendances) : lancer la **suite complète**, pas un spot-check, **et** un `git diff` de contrôle avant de déclarer *done*.

**POURQUOI** : un spot-check laisse passer les régressions et les corruptions silencieuses (ex. un nom de contrainte corrompu par une édition, vu seulement après coup). La suite complète est la seule preuve ; le `git diff` attrape ce que l'édition a modifié à ton insu.

## Règle — Préserver le contexte parent (déléguer par défaut)

**POURQUOI** : le contexte parent est la ressource rare. Un fan-out de
lectures/recherches le sature de file dumps dont seule la conclusion compte —
un subagent lit, le parent ne garde que le résultat.

**DÉLÉGUER** (Agent / skill `context: fork`)
- Recherche multi-fichiers, exploration codebase, « où est X » → Explore
- Lecture de gros fichiers / logs dont tu ne veux que la synthèse
- Tâche autonome multi-étapes vérifiable → subagent dédié
- Invocation d'un skill au trigger large mais au contenu massif face à une tâche qui n'en couvre qu'une fraction (ex. skill de référence SDK entier déclenché par un simple fetch/résumé d'article) → juger la pertinence réelle avant de charger inline ; si le skill reste nécessaire, l'exécuter via un sous-agent plutôt que d'injecter son contenu dans le contexte parent

**GARDER au parent** : la décision, l'édition ciblée, le fil de conversation.

**À LA PLACE de** lire 10 fichiers toi-même → un Agent qui renvoie la conclusion.

**AU RETOUR — traduire, ne pas relayer.** Un rapport de subagent est écrit pour toi,
pas pour le lecteur : dense, exhaustif, saturé de `fichier:ligne`. Ne pas le
répercuter dans la réponse — à la place, en extraire ce qui change une décision et
le dire en langage courant. Le détail reste disponible si on le demande.

**TEST** : retirer de la réponse tous les chemins de fichiers et numéros de ligne.
Si elle ne tient plus debout, c'est un dump, pas une réponse.

**POURQUOI** : déléguer économise le contexte parent, puis le rapport reçu dépense le
budget attentionnel du lecteur — la charge est déplacée, pas supprimée. C'est le
budget attentionnel qui est la ressource rare (`profil.md`), pas le contexte.

**Cas limite — trigger de skill littéral vs intention réelle** : un trigger de skill formulé au sens large (« dès que X est nommé ») ne dispense pas de juger si la tâche en cours a besoin du contenu complet. Rattaché à `ai-principles.md` — « l'agent sert l'intention, pas la commande littérale ».

## Règle — Skills : pas de liste figée

**POURQUOI** : une liste de skills recopiée dans une règle dérive dès qu'on en ajoute ou renomme un — et une liste fausse coûte plus qu'une liste absente.

**SOURCE DE VÉRITÉ** = le dossier `skills/`. Les skills sont proposés selon le prompt, ou chargés explicitement via `/<nom>`.
