---
name: vault-load
description: >
  Charge le contexte du vault depuis une session HORS vault (CWD = repo de dev). Pont vers le
  skill canonique vault-load, scripts lancés à la racine absolue du vault. Mode global (sans arg)
  ou task-scoped (<task-id>). Utiliser quand : "charge le contexte vault", "/vault-load [id]".
---

# Passerelle vault — load

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
- **Skill canonique à exécuter** : `$OBSIDIAN_VAULT_PRO/.agents/skills/load/SKILL.md`.

1. Lis et suis les instructions de `$OBSIDIAN_VAULT_PRO/.agents/skills/load/SKILL.md`.
2. **Lance tout script depuis la racine du vault**, pas depuis le repo :
   ```
   bash -lc 'cd "$OBSIDIAN_VAULT_PRO" && bash scripts/load.sh'          # mode global
   bash -lc 'cd "$OBSIDIAN_VAULT_PRO" && bash scripts/load.sh <task-id>' # mode task-scoped
   ```
3. Résume à l'utilisateur le contexte chargé (sprint/priorités, ou tâche/statut/blockers/next).
4. Signale tout mode dégradé remonté par le script (id introuvable, liens cassés) — no silent degradation.
