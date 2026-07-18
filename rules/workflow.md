## Règle absolue — Demander avant d'implémenter

**INTERDIT**
- Écrire ou modifier du code sans "go ahead" explicite — même en mode bypass, même si la question appelle une implémentation directe

**AUTORISÉ**
- Proposer, expliquer, puis attendre la validation avant de toucher un fichier

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

## Memory-Bank & Workflows

Le contexte de session (Focus, Next Steps) est chargé automatiquement par le hook `SessionStart`.
Les skills sont proposés nativement par le harness selon le prompt, ou chargés via `/skill <nom>`.

### Workflow quotidien
- **Début** : `/session-start` — confirme le focus ou en fixe un nouveau
- **En cours** : `/capture "note"` — capture sans casser le flow
- **Fin** : `/session-end` — sauvegarde progress et next steps

### Commandes principales
| Commande | Usage |
|---|---|
| `/session-start` · `/session-end` | Charge / sauvegarde le contexte de session |
| `/capture` | Note rapide sans interrompre le flow |
| `/memory-bank-init` · `/memory-bank-setup` | Initialise / configure le memory-bank projet |
| `/plan` → `/epct` | Plan (s'arrête avant le code) puis implémentation |
| `/create-pull-request` | PR avec titre + description auto |
| `/skill <nom>` | Charge manuellement un skill (sinon auto-proposé) |

### Skills
Source de vérité = le dossier `skills/`. Pas de liste figée ici (elle dériverait) ; les skills sont proposés nativement selon le prompt, ou chargés via `/skill <nom>`.
