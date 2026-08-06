---
name: vault-capture
description: >
  Capture une note dans le vault Obsidian depuis une session HORS vault (CWD = repo de dev).
  Pont vers le skill canonique vault-capture, avec résolution des chemins contre la racine
  absolue du vault. Utiliser quand : "capture", "note rapide", "enregistre ça" depuis un repo,
  "/vault-capture".
---

# Passerelle vault — capture

Shim externe. **Tu n'es PAS dans le vault** : le CWD est un repo de dev, le vault est ailleurs.

## Garde-fou — vault requis (raison : cette config peut tourner sans vault)

Avant toute action, vérifie la présence du vault :

```
bash -lc '[ -n "$OBSIDIAN_VAULT_PRO" ] && [ -d "$OBSIDIAN_VAULT_PRO" ] && echo OK'
```

Si la sortie n'est pas `OK` → dis « Vault non configuré (`$OBSIDIAN_VAULT_PRO` absent). J'arrête. »
et **STOP**. N'écris **jamais** dans le repo courant (sinon capture perdue).

## Délégation

- **Racine vault** : `$OBSIDIAN_VAULT_PRO`.
- **Skill canonique à exécuter** : `$OBSIDIAN_VAULT_PRO/.agents/skills/capture/SKILL.md`.

1. Lis et suis les instructions de `$OBSIDIAN_VAULT_PRO/.agents/skills/capture/SKILL.md`.
2. **Résous tout chemin relatif contre la racine absolue.** Le fichier d'inbox se crée dans
   `$OBSIDIAN_VAULT_PRO/0_INBOX/`, **jamais** dans le repo courant.
3. Pour la date du nom de fichier (`YYYY-MM-DD`) : `bash -lc 'date +%F'`.
4. Confirme à l'utilisateur le chemin absolu créé.

## Test

```
bash ~/.claude/skills/_shared/check-vault-bridge.sh vault-capture
```

- `exit 0` : chaque cible canonique citée plus haut résout réellement.
- Cible renommée ou déplacée → `exit 1`. Vault absent, `SKILL.md` illisible, racine douteuse → `exit 2`. Jamais un succès silencieux.
- Le garde-fou se vérifie à la main : invoquer le skill avec `$OBSIDIAN_VAULT_PRO` vidé doit produire l'arrêt annoncé, pas une écriture dans le repo courant.
