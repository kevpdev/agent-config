---
name: vault-recap-raisonnement
description: >
  Snapshot graphique jetable du raisonnement d'une conversation Claude à l'instant T, depuis
  une session HORS vault (CWD = repo de dev). Pont vers le skill canonique recap-raisonnement,
  avec résolution des chemins contre la racine absolue du vault.
  Utiliser quand : "recap", "recap raisonnement", "fais un snapshot" depuis un repo,
  "/vault-recap-raisonnement".
---

# Passerelle vault — recap-raisonnement

Shim externe. **Tu n'es PAS dans le vault** : le CWD est un repo de dev, le vault est ailleurs.

## Garde-fou — vault requis (raison : cette config peut tourner sans vault)

Avant toute action, vérifie la présence du vault :

```
bash -lc '[ -n "$OBSIDIAN_VAULT_PRO" ] && [ -d "$OBSIDIAN_VAULT_PRO" ] && echo OK'
```

Si la sortie n'est pas `OK` → dis « Vault non configuré (`$OBSIDIAN_VAULT_PRO` absent). J'arrête. »
et **STOP**. N'écris **jamais** dans le repo courant.

## Délégation

- **Racine vault** : `$OBSIDIAN_VAULT_PRO`.
- **Skill canonique à exécuter** : `$OBSIDIAN_VAULT_PRO/.agents/skills/recap-raisonnement/SKILL.md`.

1. Lis et suis les instructions de `$OBSIDIAN_VAULT_PRO/.agents/skills/recap-raisonnement/SKILL.md`.
2. **Résous tout chemin relatif contre la racine absolue.** Le fichier se crée dans
   `$OBSIDIAN_VAULT_PRO/agent/chat recap/<sujet>/`, **jamais** dans le repo courant.
3. Horodatage du nom de fichier : `bash -lc 'date "+%Y-%m-%d-%H%M"'`.
4. Renseigne `session_id`, `session_path` et `project` dans le frontmatter si tu peux les
   déduire du contexte (chemin scratchpad, CWD du repo).
5. Confirme à l'utilisateur le chemin absolu créé.
