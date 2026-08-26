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
  entree([invocation depuis un repo de dev]) --> garde{vault configuré}
  garde -->|non| arret([arrêt annoncé, rien n'est écrit])
  garde -->|oui| canonique[lire le skill canonique du vault]
  canonique --> horodatage[horodater le nom de fichier]
  horodatage --> metadonnees[renseigner le frontmatter déductible]
  metadonnees --> ecriture[écrire le snapshot sous chat-recaps]
  ecriture --> rendu([chemin absolu confirmé à l'utilisateur])
```

## Process

1. **Garde.** Vérifier que le vault existe avant toute autre chose.
   - `bash -lc '[ -n "$OBSIDIAN_VAULT_PRO" ] && [ -d "$OBSIDIAN_VAULT_PRO" ] && echo OK'`
   - Sortie autre que `OK` → dire « Vault non configuré (`$OBSIDIAN_VAULT_PRO` absent). J'arrête. » et s'arrêter là.
   - *Pourquoi une garde et pas une hypothèse : cette config tourne aussi sur des postes sans vault.*
2. **Délégation.** Lire et suivre les instructions du skill canonique, `$OBSIDIAN_VAULT_PRO/.agents/skills/recap-raisonnement/SKILL.md`.
3. **Horodatage.** Dater le nom de fichier avec `bash -lc 'date "+%Y-%m-%d-%H%M"'`, jamais avec une date déduite du contexte.
4. **Métadonnées.** Renseigner `session_id`, `session_path` et `project` dans le frontmatter du snapshot, à partir du chemin du scratchpad et du CWD du repo.
   - Champ indéductible → le laisser vide plutôt que l'inventer.
5. **Confirmation.** Rendre à l'utilisateur le chemin absolu du fichier créé.

## Transversal rules

- **Tout chemin se résout contre `$OBSIDIAN_VAULT_PRO`.** Le snapshot se crée dans `$OBSIDIAN_VAULT_PRO/chat-recaps/<sujet>/`. Le CWD étant un repo de dev, un chemin relatif écrirait dans le repo au lieu du vault.
- **Aucune dégradation silencieuse.** Sujet introuvable, lien cassé, script muet : l'anomalie se dit à l'utilisateur au lieu d'être avalée dans la confirmation.

## Test

Jouable seul, sauf la dernière ligne qui se relit à la main.

| Cas | Preuve |
| --- | --- |
| `bash "$SKILLS_ROOT/_shared/check-vault-bridge.sh" vault-recap-raisonnement`, vault en place | `exit 0` : la cible canonique citée au `## Process` résout réellement |
| la même commande, cible canonique renommée ou déplacée | `exit 1` |
| la même commande, vault absent ou `SKILL.md` illisible | `exit 2`, jamais un succès silencieux |
| invocation du skill avec `$OBSIDIAN_VAULT_PRO` vidé | l'arrêt annoncé par la garde, pas une écriture dans le repo courant |
