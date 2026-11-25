---
name: vault-capture
description: >-
  Capture une note dans le vault Obsidian depuis une session HORS vault (CWD = repo de dev).
  Pont vers le skill canonique capture, avec résolution des chemins contre la racine absolue
  du vault. Utiliser quand l'utilisateur dit "note ça dans le vault", "capture cette idée",
  "garde ça dans Obsidian" ou "mets ça dans l'inbox". Avec --idea, range une idée à faire
  (issue, skill, script) dans le dossier d'idées du vault perso, quand l'utilisateur dit "idée à
  faire" ou qu'une tangente hors contrat d'analyse mérite d'être gardée. NE PAS utiliser quand la
  session tourne dans le vault lui-même (→ capture, le skill du vault).
argument-hint: "[--idea] [--clean] le contenu de la note à capturer, en clair"
---

# vault-capture — capturer une note dans le vault depuis un repo

Passerelle vers le vault Obsidian : le CWD est un repo de dev et jamais le vault, et le skill rend la main dès que la note est écrite et son chemin confirmé.

```mermaid
flowchart TD
  entree([invocation depuis un repo de dev]) --> liste[lister les vaults exportés par le shell]
  liste --> n{combien}
  n -->|aucun| arret([arrêt annoncé, rien n'est écrit])
  n -->|un| canonique[lire le skill canonique du vault]
  n -->|plusieurs| choix[faire choisir l'utilisateur]
  choix --> canonique
  canonique --> date[relever la date du jour]
  date --> ecriture[écrire la note dans le dossier que désigne le mode]
  ecriture --> confirme([chemin absolu confirmé à l'utilisateur])
```

## Process

1. **Garde et choix du vault.** Lister les vaults avant toute autre chose, sans supposer lequel existe.
   - `bash -lc 'bash "$SKILLS_ROOT/_shared/scripts/resolve-vault.sh"'`
   - `exit 0` → la sortie est le chemin du vault, noté `<vault>` plus bas.
   - `exit 3` → plusieurs vaults. Les proposer à l'utilisateur sous forme numérotée (une ligne `1 PERSO`, `2 PRO`, sans le chemin), lui demander de répondre par le numéro, puis relancer `resolve-vault.sh <numéro>` pour obtenir `<vault>`.
   - `exit 1` → dire « Aucun vault Obsidian configuré (aucune variable `OBSIDIAN_VAULT_*` dans le shell). J'arrête. » et s'arrêter là.
   - **Avec `--idea`**, sauter la liste : `bash -lc 'bash "$SKILLS_ROOT/_shared/scripts/resolve-vault.sh" PERSO'`. Un `exit` non nul arrête la capture, sans repli vers un autre vault.
   - *Pourquoi une liste et pas un vault câblé : le même repo tourne sur un poste pro, un poste perso, ou les deux, et chaque poste n'a pas les mêmes vaults.*
2. **Délégation.** Lire et suivre les instructions du skill canonique, `<vault>/.agents/skills/capture/SKILL.md`, options `--idea` et `--clean` comprises. Avec `--idea`, le champ `origin` vaut le nom du repo courant (`basename -s .git "$(git remote get-url origin)"`, juste dans un worktree, à défaut le nom du dossier racine), jamais `vault`. Ses chemins sont relatifs à la racine du vault et ses scripts se lancent depuis cette racine : `bash -lc 'cd "<vault>" && bash scripts/<script>.sh'`.
3. **Date.** Relever la date du jour pour le nom de fichier au format `YYYY-MM-DD` : `bash -lc 'date +%F'`.
4. **Écriture.** Créer le fichier de note dans le dossier que désigne le skill canonique, sous `<vault>` : l'inbox par défaut, `8 IDEAS/` avec `--idea`. Ne pas écrire `0_INBOX` de mémoire : le nom du dossier varie d'un vault à l'autre (`0 INBOX/` dans le vault perso).
5. **Confirmation.** Rendre à l'utilisateur le chemin absolu du fichier créé.

## Transversal rules

- **Tout chemin se résout contre `<vault>`.** Le CWD étant un repo de dev, un chemin relatif écrirait la note dans le repo et non dans le vault.
- **Jamais d'écriture de repli dans le repo courant.** Une note posée là est une capture perdue : elle n'entre pas dans le vault et pollue un diff de code.
- **Aucune dégradation silencieuse.** Inbox introuvable, écriture refusée, skill canonique muet : l'anomalie se dit à l'utilisateur au lieu d'être avalée dans la confirmation.

## Test

Jouable seul, sauf la dernière ligne qui se relit à la main.

| Cas | Preuve |
| --- | --- |
| `bash "$SKILLS_ROOT/_shared/scripts/check-vault-bridge.sh" vault-capture`, vault en place | `exit 0` : les cibles canoniques citées au `## Process` résolvent réellement |
| la même commande, cible canonique renommée ou déplacée | `exit 1` |
| la même commande, vault absent ou `SKILL.md` illisible | `exit 2`, jamais un succès silencieux |
| invocation sans aucune variable `OBSIDIAN_VAULT_*` | l'arrêt annoncé par la garde, pas une écriture dans le repo courant |
| invocation avec un seul vault exporté | aucune question posée, la note part dans ce vault |
| invocation avec deux vaults exportés | la liste numérotée est proposée, et la note part dans celui choisi |
| invocation `--idea` avec deux vaults exportés | aucune question, la note part dans `8 IDEAS/` du vault perso avec `type: idea`, `status: raw` et `origin` égal au repo courant, rien dans l'inbox |
| invocation `--idea` sans `OBSIDIAN_VAULT_PERSO` | l'arrêt annoncé, aucune écriture dans un autre vault |
