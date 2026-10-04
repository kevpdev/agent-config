---
name: vault-load
description: >-
  Charge le contexte du vault depuis une session HORS vault (CWD = repo de dev). Pont vers le
  skill canonique vault-load, scripts lancés à la racine absolue du vault. Mode global (sans arg)
  ou task-scoped (identifiant de tâche). Utiliser quand : "charge le contexte vault", "/vault-load [id]".
argument-hint: "rien pour le mode global, un identifiant de tâche pour le mode task-scoped"
---

# vault-load — charger le contexte du vault depuis un repo

Passerelle vers le vault Obsidian : le CWD est un repo de dev et jamais le vault, et le skill rend la main dès que le contexte est chargé et résumé.

```mermaid
flowchart TD
  entree([invocation depuis un repo de dev]) --> garde{vault résolu, choisi si plusieurs}
  garde -->|non| arret([arrêt annoncé, rien n'est chargé])
  garde -->|oui| canonique[lire le skill canonique du vault]
  canonique --> mode{argument reçu}
  mode -->|aucun| global[load.sh en mode global]
  mode -->|identifiant de tâche| tache[load.sh en mode task-scoped]
  global --> resume[résumer le contexte chargé]
  tache --> resume
  resume --> rendu([contexte rendu, dégradations signalées])
```

## Process

1. **Garde et choix du vault.** Lister les vaults avant toute autre chose, sans supposer lequel existe.
   - `bash -lc 'bash "$SKILLS_ROOT/_shared/resolve-vault.sh"'`
   - `exit 0` → la sortie est le chemin du vault, noté `<vault>` plus bas.
   - `exit 3` → plusieurs vaults. Les proposer à l'utilisateur sous forme numérotée (une ligne `1 PERSO`, `2 PRO`, sans le chemin), lui demander de répondre par le numéro, puis relancer `resolve-vault.sh <numéro>` pour obtenir `<vault>`.
   - `exit 1` → dire « Aucun vault Obsidian configuré (`OBSIDIAN_VAULT_PRO` et `OBSIDIAN_VAULT_PERSO` absents). J'arrête. » et s'arrêter là.
   - *Pourquoi une liste et pas un vault câblé : le même repo tourne sur un poste pro, un poste perso, ou les deux, et chaque poste n'a pas les mêmes vaults.*
2. **Délégation.** Lire et suivre les instructions du skill canonique, `<vault>/.agents/skills/load/SKILL.md`.
3. **Lancement.** Lancer le script depuis la racine du vault, jamais depuis le repo.
   - Mode global : `bash -lc 'cd "<vault>" && bash scripts/load.sh'`
   - Mode task-scoped : `bash -lc 'cd "<vault>" && bash scripts/load.sh <task-id>'`
4. **Résumé.** Rendre à l'utilisateur le contexte chargé : sprint et priorités en mode global, tâche, statut, blockers et next en mode task-scoped.

## Transversal rules

- **Tout chemin se résout contre `<vault>`.** Le CWD étant un repo de dev, un chemin relatif pointerait dans le repo et non dans le vault.
- **Aucune dégradation silencieuse.** Identifiant introuvable, lien cassé, script muet : l'anomalie se dit à l'utilisateur au lieu d'être avalée dans le résumé.
- **Le skill ne fait que lire.** Il n'écrit ni dans le vault ni dans le repo courant, d'où l'absence de `disable-model-invocation`.

## Test

Jouable seul, sauf la dernière ligne qui se relit à la main.

| Cas | Preuve |
| --- | --- |
| `bash "$SKILLS_ROOT/_shared/check-vault-bridge.sh" vault-load`, vault en place | `exit 0` : la cible canonique citée au `## Process` résout réellement |
| la même commande, cible canonique renommée ou déplacée | `exit 1` |
| la même commande, vault absent ou `SKILL.md` illisible | `exit 2`, jamais un succès silencieux |
| invocation sans `OBSIDIAN_VAULT_PRO` ni `OBSIDIAN_VAULT_PERSO` | l'arrêt annoncé par la garde, rien n'est écrit dans le repo courant |
| invocation avec un seul vault exporté | aucune question posée, le skill travaille dans ce vault |
| invocation avec les deux vaults exportés | la liste numérotée est proposée, et le skill travaille dans celui choisi |
