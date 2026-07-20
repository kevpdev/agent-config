---
name: vault-capture-projet
description: >
  Capture une note vault en l'orientant vers le bon PROJET (2_PROJECTS/), depuis une session
  HORS vault (CWD = repo de dev). Devine le projet, propose, attend validation humaine, puis écrit.
  Fallback 0_INBOX/ si aucun projet ne colle. Utiliser quand : "capture dans le projet",
  "note projet", "range ça dans le bon projet", "/vault-capture-projet".
---

# Passerelle vault — capture orientée projet

Capture orientée projet. **Tu n'es PAS dans le vault** : le CWD est un repo de dev, le vault est ailleurs.

## Garde-fou — vault requis (raison : cette config peut tourner sans vault)

Avant toute action, vérifie la présence du vault :

```
bash -lc '[ -n "$OBSIDIAN_VAULT_PRO" ] && [ -d "$OBSIDIAN_VAULT_PRO" ] && echo OK'
```

Si la sortie n'est pas `OK` → dis « Vault non configuré (`$OBSIDIAN_VAULT_PRO` absent). J'arrête. »
et **STOP**. N'écris **jamais** dans le repo courant (sinon note perdue).

## Contexte

- **Racine vault** : `$OBSIDIAN_VAULT_PRO` (chemin absolu). Tout chemin se résout contre cette racine.
- Mécanisme volontairement **probabiliste + validation humaine** : on devine, on propose, l'humain
  tranche. Pas de lien rigide repo↔projet à maintenir.

## Instructions

1. **Récupère ce qu'il faut deviner** :
   - Nom du repo courant : `bash -lc 'basename "$(git rev-parse --show-toplevel 2>/dev/null || pwd)"'`
   - Liste des projets vault : `bash -lc 'ls -1 "$OBSIDIAN_VAULT_PRO/2_PROJECTS"'`
   - Le contenu de la note (ce que l'utilisateur dicte).

2. **Devine le projet** au flair, en croisant : nom du repo + thème de la note vs les noms des
   projets. Choisis le plus probable (un seul). Si rien ne colle clairement → projet = aucun.

3. **Devine la zone** dans le projet, d'après le contenu :
   - Idée / feature à explorer (spec non figée) → `backlog/`
   - Raisonnement, contexte, exploration, narratif → `notes/`
   - Dans le doute → `notes/`

4. **Propose et attends validation** (une seule ligne, réponse rapide) :
   > Projet **`<PROJET>`** → zone **`<zone>`** ? [Y / autre projet / inbox]
   - `Y` → on garde la suggestion.
   - L'utilisateur nomme un autre projet ou une autre zone → on prend ça.
   - `inbox` (ou aucun projet deviné) → fallback `0_INBOX/` (capture brute classique).

5. **Charge la convention de style** (dès que tu composes ou restructures la note — pas pour un dump brut) :
   - Lis `$OBSIDIAN_VAULT_PRO/agent/conventions/notes.md` et applique son style (ton, structure, densité).
   - **Pourquoi** : c'est la source de vérité agnostique des notes vault ; l'output style `vault-notes.md` ne s'active que quand le CWD est le vault, or ici le CWD est un repo dev → sans cette lecture, la note dérive vers le style dense.
   - **Exception** : dump brut verbatim (cf. point 6 « brut tel quel ») → ne pas reformater.

6. **Écris la note** après validation :
   - Date : `bash -lc 'date +%F'`.
   - Nom de fichier : `YYYY-MM-DD-titre-court.md`.
   - **Cible projet** : `$OBSIDIAN_VAULT_PRO/2_PROJECTS/<PROJET>/<zone>/`
   - **Cible fallback** : `$OBSIDIAN_VAULT_PRO/0_INBOX/`
   - Frontmatter :
     ```
     ---
     date: YYYY-MM-DD
     type: inbox
     source: capture
     project: <PROJET>      # omis si fallback inbox
     ---
     ```
   - Contenu : brut tel quel (comme `vault-capture` par défaut) si dump ; sinon convention `notes.md` (point 5).

7. **Confirme** le chemin absolu créé à l'utilisateur.

## Notes

- Si `git rev-parse` échoue (pas un repo), on devine uniquement sur le contenu de la note.
- Pour une capture sans orientation projet (pensée transverse, brouillon), utiliser `vault-capture`
  qui reste le défaut zéro-friction vers `0_INBOX/`.
