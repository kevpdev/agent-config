---
name: vault-recap-raisonnement
description: >-
  Snapshot graphique jetable du raisonnement d'une conversation Claude à l'instant T, depuis une
  session HORS vault (CWD = repo de dev). Pont vers le skill canonique recap-raisonnement, avec
  résolution des chemins contre la racine absolue du vault. Le cas qui l'appelle : une explication
  repose sur un schéma (mermaid, flowchart, diagramme) qu'un terminal CLI ne rend pas, et le recap
  visuel part dans Obsidian plutôt qu'en diagramme illisible en texte brut. Invocation manuelle
  uniquement, par `/vault-recap-raisonnement` : le skill écrit un snapshot dans le vault, qui est un
  dépôt git, un effet de bord qu'un déclenchement probabiliste ne doit pas pouvoir provoquer.
  NE PAS utiliser pour journaliser une session de travail (→ vault-log-session).
argument-hint: "rien : le skill prend la conversation en cours, ou le sujet qui nommera le dossier du snapshot"
disable-model-invocation: true
---

# vault-recap-raisonnement — publier un snapshot de raisonnement dans le vault

Passerelle vers le vault Obsidian : le CWD est un repo de dev et jamais le vault, et le skill rend la main dès que le snapshot est écrit et son chemin confirmé.

```mermaid
flowchart TD
  entree([invocation depuis un repo de dev]) --> garde{vault résolu, choisi si plusieurs}
  garde -->|non| arret([arrêt annoncé, rien n'est écrit])
  garde -->|oui| canonique[lire le skill canonique du vault]
  canonique --> horodatage[horodater le nom de fichier]
  horodatage --> metadonnees[renseigner le frontmatter déductible]
  metadonnees --> ecriture[écrire le snapshot sous chat-recaps]
  ecriture --> rendu([chemin absolu confirmé à l'utilisateur])
```

## Process

1. **Garde et choix du vault.** Lister les vaults avant toute autre chose, sans supposer lequel existe.
   - `bash -lc 'bash "$SKILLS_ROOT/_shared/resolve-vault.sh"'`
   - `exit 0` → la sortie est le chemin du vault, noté `<vault>` plus bas.
   - `exit 3` → plusieurs vaults. Les proposer à l'utilisateur sous forme numérotée (une ligne `1 PERSO`, `2 PRO`, sans le chemin), lui demander de répondre par le numéro, puis relancer `resolve-vault.sh <numéro>` pour obtenir `<vault>`.
   - `exit 1` → dire « Aucun vault Obsidian configuré (`OBSIDIAN_VAULT_PRO` et `OBSIDIAN_VAULT_PERSO` absents). J'arrête. » et s'arrêter là.
   - *Pourquoi une liste et pas un vault câblé : le même repo tourne sur un poste pro, un poste perso, ou les deux, et chaque poste n'a pas les mêmes vaults.*
2. **Délégation.** Lire et suivre les instructions du skill canonique, `<vault>/.agents/skills/recap-raisonnement/SKILL.md`.
3. **Horodatage.** Dater le nom de fichier avec `bash -lc 'date "+%Y-%m-%d-%H%M"'`, jamais avec une date déduite du contexte.
4. **Métadonnées.** Renseigner `session_id`, `session_path` et `project` dans le frontmatter du snapshot, à partir du chemin du scratchpad et du CWD du repo.
   - Champ indéductible → le laisser vide plutôt que l'inventer.
5. **Confirmation.** Rendre à l'utilisateur le chemin absolu du fichier créé.

## Transversal rules

- **Tout chemin se résout contre `<vault>`.** Le snapshot se crée dans `<vault>/chat-recaps/<sujet>/`. Le CWD étant un repo de dev, un chemin relatif écrirait dans le repo au lieu du vault.
- **Aucune dégradation silencieuse.** Sujet introuvable, lien cassé, script muet : l'anomalie se dit à l'utilisateur au lieu d'être avalée dans la confirmation.

## Test

Jouable seul, sauf la dernière ligne qui se relit à la main.

| Cas | Preuve |
| --- | --- |
| `bash "$SKILLS_ROOT/_shared/check-vault-bridge.sh" vault-recap-raisonnement`, vault en place | `exit 0` : la cible canonique citée au `## Process` résout réellement |
| la même commande, cible canonique renommée ou déplacée | `exit 1` |
| la même commande, vault absent ou `SKILL.md` illisible | `exit 2`, jamais un succès silencieux |
| invocation sans `OBSIDIAN_VAULT_PRO` ni `OBSIDIAN_VAULT_PERSO` | l'arrêt annoncé par la garde, rien n'est écrit dans le repo courant |
| invocation avec un seul vault exporté | aucune question posée, le skill travaille dans ce vault |
| invocation avec les deux vaults exportés | la liste numérotée est proposée, et le skill travaille dans celui choisi |
