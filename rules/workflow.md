## Règle absolue — Demander avant d'implémenter

**INTERDIT**
- Écrire ou modifier du code sans "go ahead" explicite — même en mode bypass, même si la question appelle une implémentation directe

**AUTORISÉ**
- Proposer, expliquer, puis attendre la validation avant de toucher un fichier

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

**GARDER au parent** : la décision, l'édition ciblée, le fil de conversation.

**À LA PLACE de** lire 10 fichiers toi-même → un Agent qui renvoie la conclusion.

## Règle — Skills : pas de liste figée

**POURQUOI** : une liste de skills recopiée dans une règle dérive dès qu'on en ajoute ou renomme un — et une liste fausse coûte plus qu'une liste absente.

**SOURCE DE VÉRITÉ** = le dossier `skills/`. Les skills sont proposés selon le prompt, ou chargés explicitement via `/<nom>`.
