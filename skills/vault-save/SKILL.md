---
name: vault-save
description: >-
  Sauvegarde COMPLÈTE du vault depuis une session HORS vault (CWD = repo de dev) : journalise la
  session (recap + dashboards), puis commit et push de tout le working tree (`add -A`) à la racine
  absolue du vault. Pont vers le skill canonique save. Ne se déclenche jamais au fil de la
  conversation : il s'appelle à la main par `/vault-save`, pour qu'un `add -A` suivi d'un push ne
  parte pas sur une phrase ambiguë.
argument-hint: "rien, ou un titre court qui servira au recap et au message de commit"
disable-model-invocation: true
---

# vault-save — sauvegarder le vault depuis un repo

Passerelle vers le vault Obsidian : le CWD est un repo de dev et jamais le vault, et le skill rend la main une fois le vault journalisé, committé et poussé.

```mermaid
flowchart TD
  entree([invocation manuelle depuis un repo de dev]) --> garde{vault résolu, choisi si plusieurs}
  garde -->|non| arret([arrêt annoncé, rien n'est écrit])
  garde -->|oui| canonique[lire le skill canonique du vault]
  canonique --> journal[journaliser depuis la racine du vault]
  journal --> commit[commit et push depuis la racine du vault]
  commit --> rendu([sauvegarde rendue, dégradations signalées])
```

## Process

1. **Garde et choix du vault.** Lister les vaults avant toute autre chose, sans supposer lequel existe.
   - `bash -lc 'bash "$SKILLS_ROOT/_shared/resolve-vault.sh"'`
   - `exit 0` → la sortie est le chemin du vault, noté `<vault>` plus bas.
   - `exit 3` → plusieurs vaults. Les proposer à l'utilisateur sous forme numérotée (une ligne `1 PERSO`, `2 PRO`, sans le chemin), lui demander de répondre par le numéro, puis relancer `resolve-vault.sh <numéro>` pour obtenir `<vault>`.
   - `exit 1` → dire « Aucun vault Obsidian configuré (`OBSIDIAN_VAULT_PRO` et `OBSIDIAN_VAULT_PERSO` absents). J'arrête. » et s'arrêter là.
   - *Pourquoi une liste et pas un vault câblé : le même repo tourne sur un poste pro, un poste perso, ou les deux, et chaque poste n'a pas les mêmes vaults.*
2. **Délégation.** Lire et suivre les instructions du skill canonique, `<vault>/.agents/skills/save/SKILL.md`.
   - Il enchaîne lui-même la journalisation puis le commit et le push. Le pont ne rejoue ni ses étapes ni son format de message.
3. **Lancement.** Lancer chaque script depuis la racine du vault, jamais depuis le repo courant.
   - `bash -lc 'cd "<vault>" && bash scripts/<script>.sh'`
   - *Pourquoi le `cd` : les scripts du vault résolvent leurs chemins contre le CWD, qui est ici un repo de dev.*
4. **Source externe.** Sourcer le recap depuis le repo courant, `git log` et `git diff`, fichiers touchés.
   - L'écriture, elle, part sous `<vault>` : c'est le vault qui garde la trace, pas le repo.
5. **Rendu.** Dire à l'utilisateur ce qui a été écrit, ce qui a été committé et si le push est passé.

## Transversal rules

- **Tout chemin se résout contre `<vault>`.** Le CWD étant un repo de dev, un chemin relatif écrirait dans le repo et non dans le vault.
- **Le contenu de la sauvegarde appartient au skill canonique.** Le pont ne porte que la résolution des chemins et la source externe du recap. Recopier ici le format du message de commit ou la liste des scripts en ferait une deuxième version, qui dérive au premier edit de l'autre.
- **Aucune dégradation silencieuse.** Script muet, commit vide, push refusé : l'anomalie se dit à l'utilisateur au lieu d'être avalée dans le compte rendu.
- **Le skill écrit, commit et pousse**, d'où `disable-model-invocation: true` et l'appel par `/vault-save`.

## Test

Jouable seul, sauf la dernière ligne qui se relit à la main.

| Cas | Preuve |
| --- | --- |
| `bash "$SKILLS_ROOT/_shared/check-vault-bridge.sh" vault-save`, vault en place | `exit 0` : la cible canonique citée au `## Process` résout réellement |
| la même commande, cible canonique renommée ou déplacée | `exit 1` |
| la même commande, vault absent ou `SKILL.md` illisible | `exit 2`, jamais un succès silencieux |
| invocation sans `OBSIDIAN_VAULT_PRO` ni `OBSIDIAN_VAULT_PERSO` | l'arrêt annoncé par la garde, rien n'est écrit dans le repo courant |
| invocation avec un seul vault exporté | aucune question posée, le skill travaille dans ce vault |
| invocation avec les deux vaults exportés | la liste numérotée est proposée, et le skill travaille dans celui choisi |
