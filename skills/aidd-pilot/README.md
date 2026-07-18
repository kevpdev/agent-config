# aidd-pilot — prérequis

Ce skill n'est pas autonome : il **compose** les plugins du framework AI-Driven Dev. Sans eux, il n'a rien à orchestrer.

> Framework : https://github.com/ai-driven-dev/framework

Ce fichier est de la documentation pour un lecteur humain — il ne se charge pas en contexte. Le comportement du skill vit dans `SKILL.md`, `actions/` et `references/`.

## Ce qu'est le framework

Il installe un cycle de développement complet dans les outils de code IA, sous forme de skills, agents et commandes — de l'idée brute à la pull request relue. Il s'installe via le marketplace de plugins du runtime (Claude Code, Cursor, Codex, Copilot, OpenCode), par exemple :

```
/plugin install aidd-dev@aidd-framework
```

## Les plugins composés ici

| Plugin | Rôle | Utilisé par |
|---|---|---|
| `aidd-dev` | SDLC : plan, implémentation, test, review | `actions/02-pipeline.md`, `actions/03-validate.md` |
| `aidd-vcs` | commits, PR, releases | `actions/04-doc-ship.md` |
| `aidd-pm` | tickets, user stories, specs | `actions/01-intake.md` |
| `aidd-refine` | idéation, affinage, fact-checking | `actions/01-intake.md` |
| `aidd-context` | initialisation projet, mémoire, contexte | prérequis général |

Le framework livre aussi `aidd-orchestrator` (automatisation asynchrone) et `aidd-ui` (alpha), non composés ici.

## Ce que `aidd-pilot` ajoute

Le framework fournit les briques ; ce skill fournit **l'enchaînement voulu** — tunnel besoin → commit doc, autonomie sélective (`references/governor.md`), validation e2e réelle et gestion multi-repo. C'est une couche personnelle au-dessus du framework, pas une partie de celui-ci.

Même logique pour `test-runner`, skill maison consommé par ce pilote.
