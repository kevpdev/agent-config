---
name: vault-capture-projet
description: >-
  Capture une note dans le vault Obsidian en l'orientant vers le bon PROJET (`2_PROJECTS/`), depuis
  une session HORS vault (CWD = repo de dev). Devine le projet, propose, attend la validation
  humaine, puis écrit. Repli sur `0_INBOX/` quand aucun projet ne colle. Invocation manuelle
  uniquement, par `/vault-capture-projet` : le skill écrit une note dans le vault, qui est un
  dépôt git, un effet de bord qu'un déclenchement probabiliste ne doit pas pouvoir provoquer.
  NE PAS
  utiliser pour une capture sans orientation projet, pensée transverse ou brouillon
  (→ vault-capture, le défaut zéro-friction vers `0_INBOX/`).
argument-hint: "le contenu de la note, et le projet vault de destination si tu le connais"
disable-model-invocation: true
---

# vault-capture-projet — capturer une note dans le bon projet du vault depuis un repo

Passerelle vers le vault Obsidian : le CWD est un repo de dev et jamais le vault, et le skill rend la main dès que la note est écrite dans la cible validée et son chemin confirmé.

```mermaid
flowchart TD
  entree([invocation depuis un repo de dev]) --> garde{vault configuré}
  garde -->|non| arret([arrêt annoncé, rien n'est écrit])
  garde -->|oui| collecte[collecter repo, projets du vault et contenu]
  collecte --> devine[deviner le projet, puis la zone]
  devine --> propose{validation humaine}
  propose -->|projet validé| cible[cible dans 2_PROJECTS]
  propose -->|inbox, ou aucun projet| repli[cible dans 0_INBOX]
  cible --> style[appliquer la convention de notes]
  repli --> style
  style --> ecriture[écrire la note datée]
  ecriture --> confirme([chemin absolu confirmé à l'utilisateur])
```

## Process

1. **Garde.** Vérifier que le vault existe avant toute autre chose.
   - `bash -lc '[ -n "$OBSIDIAN_VAULT_PRO" ] && [ -d "$OBSIDIAN_VAULT_PRO" ] && echo OK'`
   - Sortie autre que `OK` → dire « Vault non configuré (`$OBSIDIAN_VAULT_PRO` absent). J'arrête. » et s'arrêter là.
   - *Pourquoi une garde et pas une hypothèse : cette config tourne aussi sur des postes sans vault.*
2. **Collecte.** Réunir les trois entrées de la devinette.
   - Nom du repo courant : `bash -lc 'basename "$(git rev-parse --show-toplevel 2>/dev/null || pwd)"'`
   - Projets existants : `bash -lc 'ls -1 "$OBSIDIAN_VAULT_PRO/2_PROJECTS"'`
   - Le contenu de la note, dicté par l'utilisateur.
3. **Devine le projet.** Croiser le nom du repo et le thème de la note avec les noms de projets, et retenir le plus probable, un seul.
   - `git rev-parse` en échec, donc hors repo : deviner sur le seul contenu de la note.
   - Rien ne colle clairement : aucun projet retenu, la cible sera le repli de l'étape 5.
4. **Devine la zone.** Choisir la zone du projet d'après la nature du contenu.
   - idée ou feature à explorer, spec non figée : `backlog/`
   - raisonnement, contexte, exploration, narratif : `notes/`
   - dans le doute : `notes/`
5. **Propose, et attends.** Poser une ligne unique, puis ne rien écrire avant la réponse.
   - La ligne : « Projet `<PROJET>`, zone `<zone>` ? [Y / autre projet / inbox] »
   - Réponse `Y` : la suggestion est retenue.
   - L'utilisateur nomme un autre projet ou une autre zone : c'est cette cible qui gagne.
   - Réponse `inbox`, ou aucun projet retenu à l'étape 3 : repli sur `$OBSIDIAN_VAULT_PRO/0_INBOX/`, la capture brute classique.
6. **Style.** Lire `$OBSIDIAN_VAULT_PRO/conventions/notes.md` et en appliquer le ton, la structure et la densité, dès que la note est composée ou restructurée.
   - *Pourquoi lire ce fichier ici : l'output style `vault-notes.md` ne s'active que quand le CWD est le vault, or le CWD est un repo de dev.*
   - Exception, le dump brut verbatim : ne pas reformater.
7. **Écriture.** Créer le fichier daté dans la cible validée.
   - Date et nom de fichier : `bash -lc 'date +%F'`, puis `YYYY-MM-DD-titre-court.md`.
   - Cible projet : `$OBSIDIAN_VAULT_PRO/2_PROJECTS/<PROJET>/<zone>/`
   - Cible de repli : `$OBSIDIAN_VAULT_PRO/0_INBOX/`
   - Frontmatter de la note, la clé `project` étant omise sur le repli :

     ```
     ---
     date: YYYY-MM-DD
     type: inbox
     source: capture
     project: <PROJET>
     ---
     ```

   - Contenu brut tel quel si c'est un dump, sinon mis à la convention lue à l'étape 6.
8. **Confirmation.** Rendre à l'utilisateur le chemin absolu du fichier créé.

## Transversal rules

- **Tout chemin se résout contre `$OBSIDIAN_VAULT_PRO`.** Le CWD étant un repo de dev, un chemin relatif écrirait la note dans le repo et non dans le vault.
- **Jamais d'écriture de repli dans le repo courant.** Une note posée là est une capture perdue : elle n'entre pas dans le vault et pollue un diff de code.
- **L'orientation est probabiliste, la validation est humaine.** On devine, on propose, l'utilisateur tranche, et rien ne s'écrit avant sa réponse. C'est ce qui dispense d'entretenir une table de correspondance entre repos et projets.
- **Aucune dégradation silencieuse.** `2_PROJECTS/` introuvable, convention illisible, écriture refusée : l'anomalie se dit à l'utilisateur au lieu d'être avalée dans la confirmation.
- **Le skill écrit une note, il ne commite rien.** Le commit et le push du vault sont des gestes séparés, d'où l'absence de `disable-model-invocation`, comme sur `vault-capture`.

## Test

Jouable seul, sauf la dernière ligne qui se relit à la main.

| Cas | Preuve |
| --- | --- |
| `bash "$SKILLS_ROOT/_shared/check-vault-bridge.sh" vault-capture-projet`, vault en place | `exit 0` : les cibles citées au `## Process` résolvent réellement, dont `conventions/notes.md` dont dépend l'étape 6 |
| la même commande, cible renommée ou déplacée | `exit 1` |
| la même commande, vault absent ou `SKILL.md` illisible | `exit 2`, jamais un succès silencieux |
| invocation du skill avec `$OBSIDIAN_VAULT_PRO` vidé | l'arrêt annoncé par la garde, pas une écriture dans le repo courant |
