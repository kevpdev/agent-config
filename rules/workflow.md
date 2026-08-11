## Règle absolue — Demander avant d'implémenter

**INTERDIT**
- Écrire ou modifier du code sans "go ahead" explicite — même en mode bypass, même si la question appelle une implémentation directe

**AUTORISÉ**
- Proposer, expliquer, puis attendre la validation avant de toucher un fichier

## Règle — Pré-vol avant toute conclusion durable sur une codebase

**DÉCLENCHEUR** : avant de rédiger un plan, un audit, une note d'archi — tout document sur lequel quelqu'un décidera ensuite. Pas avant une réponse de conversation. Chercher **avant**, pas quand le doute apparaît : un doute qui n'apparaît pas ne déclenche aucune vérification.

**OBLIGATOIRE — trois gestes, dans cet ordre**

1. **Rafraîchir le workspace** — `git fetch --all --prune` sur **chaque** repo, puis relever branche / avance-retard / état sale. Un clone en retard rend invisible le travail déjà fait.
2. **Chercher le précédent** — `git log --all --grep="<sujet>"` sur les repos **voisins**, pas seulement celui qu'on modifie. Le même changement a souvent déjà été fait ailleurs ; le lire coûte moins cher que le reconcevoir.
3. **Lire la source qui fait autorité** — le code, la config, le jar. Jamais le wiki, jamais un plan frère, jamais la mémoire de session.

**INTERDIT**
- Reprendre une valeur mécanique (port, route, signature, version, chemin) depuis un wiki ou un plan voisin sans l'avoir retrouvée dans le code ou la config
- **À LA PLACE** : ouvrir le fichier, et citer `fichier:ligne` dans le document produit. Une valeur non traçable se marque « supposé ».

**POURQUOI** : quelques appels d'outil contre des cycles de correction qui relisent un artefact entier pour une ligne fausse. Trois valeurs fausses dans un même plan, cause unique : une source adjacente consultée à la place de la source d'autorité → `rules/references/ref-workflow.md`.

## Règle — Vérifier après édition d'un fichier de build

**OBLIGATOIRE**
- Après édition d'un fichier de build (migration, fixture, config CI, dépendances) : lancer la **suite complète**, pas un spot-check, **et** un `git diff` de contrôle avant de déclarer *done*.

**POURQUOI** : un spot-check laisse passer les régressions et les corruptions silencieuses (ex. un nom de contrainte corrompu par une édition). La suite complète est la seule preuve ; le `git diff` attrape ce que l'édition a modifié à ton insu.

## Règle — Un mécanisme déterministe échoue fermé

**DÉCLENCHEUR** : écrire ou modifier un hook, un garde-fou, un script de lint — tout ce dont le métier est de refuser ou d'alerter.

**OBLIGATOIRE**
- Refuser quand le mécanisme ne peut pas conclure : dépendance absente, entrée illisible, racine introuvable. Ne pas laisser le chemin d'erreur retomber sur `exit 0` — c'est là que la panne devient invisible.
- Aucun chemin absolu en dur : le dériver de l'emplacement du script (`$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)`), puis s'arrêter si la racine dérivée ne porte pas un marqueur attendu.
- Ne pas conditionner le garde à l'artefact dont l'absence **est** le mode de défaillance : il ne surveillerait que les passes déjà bien conduites. Faire porter le contrôle sur ce que le défaut produit, jamais sur ce que produit la bonne pratique.
- Calibrer sur un cas positif **fabriqué à la main** avant de déclarer le garde en place. Un garde sans cible vivante se comporte exactement pareil qu'il soit cassé ou intact.
- Puis le rejouer sur un **corpus de trafic réel** que personne n'a écrit pour lui (transcripts, historique, logs) et compter les **faux** positifs : sa propre batterie hérite des angles morts de qui l'a conçue. Un garde qui refuse du travail valide finit désactivé, même résultat qu'un échec ouvert.

**POURQUOI** : un garde qui échoue ouvert est pire que pas de garde, parce qu'il inspire confiance — on cesse de surveiller la zone qu'il ne protège plus. Même famille de panne qu'une mesure aveugle (cf. `reasoning.md`), et l'échec ouvert est le défaut par nature : il faut l'écrire pour qu'il n'arrive pas.

**Quatre cas mesurés** fondent ces cinq points, dont deux pannes silencieuses le même jour et un garde qui refusait des commits valides → `rules/references/ref-workflow.md`.

## Règle — Préserver le contexte parent (déléguer par défaut)

**POURQUOI** : un fan-out de lectures sature le contexte parent de file dumps dont seule la conclusion compte. Le rapport reçu dépense ensuite le budget attentionnel du lecteur — la vraie ressource rare (`profil.md`) : la charge est déplacée, pas supprimée, d'où « traduire » ci-dessous.

**DÉLÉGUER** (Agent / skill `context: fork`)
- Recherche multi-fichiers, exploration codebase, « où est X » → Explore
- Lecture de gros fichiers / logs dont tu ne veux que la synthèse
- Tâche autonome multi-étapes vérifiable → subagent dédié
- Skill au trigger large mais au contenu massif pour une tâche qui n'en couvre qu'une fraction → juger la pertinence réelle avant de charger inline ; si le skill reste nécessaire, l'exécuter en sous-agent plutôt que de l'injecter dans le contexte parent

**GARDER au parent** : la décision, l'édition ciblée, le fil de conversation.

**AU RETOUR — traduire, ne pas relayer.** Un rapport de subagent est écrit pour toi, pas pour le lecteur. En extraire ce qui change une décision et le dire en langage courant ; le détail reste disponible si on le demande.

**TEST** : retirer de la réponse tous les chemins de fichiers et numéros de ligne. Si elle ne tient plus debout, c'est un dump, pas une réponse.

## Règle — Skills : pas de liste figée

**POURQUOI** : une liste de skills recopiée dans une règle dérive dès qu'on en ajoute ou renomme un — et une liste fausse coûte plus qu'une liste absente.

**SOURCE DE VÉRITÉ** = le dossier `skills/`. Les skills sont proposés selon le prompt, ou chargés explicitement via `/<nom>`.
