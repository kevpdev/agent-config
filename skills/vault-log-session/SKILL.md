---
name: vault-log-session
description: >
  Journalise une session vault SANS commit, depuis une session HORS vault (CWD = repo de dev). Pont vers
  le skill canonique vault-log-session : régénère les fichiers auto-générés et rédige le recap, le tout à
  la racine absolue du vault. Le commit est séparé (→ /vault-save). Utiliser quand : "log session",
  "recap", "fin de session" depuis un repo, "/vault-log-session".
---

# Passerelle vault — log-session

Shim externe. **Tu n'es PAS dans le vault** : le CWD est un repo de dev, le vault est ailleurs.

## Garde-fou — vault requis (raison : cette config peut tourner sans vault)

Avant toute action, vérifie la présence du vault :

```
bash -lc '[ -n "$OBSIDIAN_VAULT_PRO" ] && [ -d "$OBSIDIAN_VAULT_PRO" ] && echo OK'
```

Si la sortie n'est pas `OK` → dis « Vault non configuré (`$OBSIDIAN_VAULT_PRO` absent). J'arrête. »
et **STOP**.

## Délégation

- **Racine vault** : `$OBSIDIAN_VAULT_PRO`.
- **Skill canonique à exécuter** : `$OBSIDIAN_VAULT_PRO/.agents/skills/log-session/SKILL.md`.

1. Lis et suis les instructions de `$OBSIDIAN_VAULT_PRO/.agents/skills/log-session/SKILL.md`.
2. **Lance tout script depuis la racine du vault** :
   ```
   bash -lc 'cd "$OBSIDIAN_VAULT_PRO" && bash scripts/vault-stats.sh'
   bash -lc 'cd "$OBSIDIAN_VAULT_PRO" && bash scripts/regen-all.sh "$OBSIDIAN_VAULT_PRO"'
   ```
3. **Toute écriture va sous la racine absolue**, jamais dans le repo courant :
   recap → `$OBSIDIAN_VAULT_PRO/scripts/logs/sessions/<date>.md` ;
   decisions/CHANGELOG → `$OBSIDIAN_VAULT_PRO/scripts/logs/`.
   Date : `bash -lc 'date +%F'`.
4. Nuance recap : la session porte sur un **repo externe**. Source le travail depuis ce repo
   (git log/diff, fichiers touchés), mais écris le recap **dans le vault**.
5. **Pas de commit** : le skill canonique log-session ne commit pas. Pour sauvegarder le vault, lance `/vault-save`.

## Test

```
bash ~/.claude/skills/_shared/check-vault-bridge.sh vault-log-session
```

- `exit 0` : chaque cible canonique citée plus haut résout réellement.
- Cible renommée ou déplacée → `exit 1`. Vault absent, `SKILL.md` illisible, racine douteuse → `exit 2`. Jamais un succès silencieux.
- Le garde-fou se vérifie à la main : invoquer le skill avec `$OBSIDIAN_VAULT_PRO` vidé doit produire l'arrêt annoncé, pas une écriture dans le repo courant.
