---
name: vault-save
description: >
  Sauvegarde COMPLÈTE manuelle du vault depuis une session HORS vault (CWD = repo de dev). Pont vers le
  skill canonique vault-save : journalise (recap + dashboards) PUIS commit + push (add -A) à la racine
  absolue du vault. À lancer délibérément (backup, urgence). Utiliser quand : "save", "sauvegarde
  complète", "backup du vault" depuis un repo, "/vault-save".
---

# Passerelle vault — save

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
- **Skill canonique à exécuter** : `$OBSIDIAN_VAULT_PRO/.agents/skills/save/SKILL.md`.

1. Lis et suis les instructions de `$OBSIDIAN_VAULT_PRO/.agents/skills/save/SKILL.md` (= journaliser via log-session, puis commit + push).
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
5. **Commit + push** depuis la racine du vault :
   ```
   bash -lc 'cd "$OBSIDIAN_VAULT_PRO" && bash scripts/vault-commit.sh "vault: $(date +%F) — <titre court>"'
   ```

## Test

```
bash "$SKILLS_ROOT/_shared/check-vault-bridge.sh" vault-save
```

- `exit 0` : chaque cible canonique citée plus haut résout réellement.
- Cible renommée ou déplacée → `exit 1`. Vault absent, `SKILL.md` illisible, racine douteuse → `exit 2`. Jamais un succès silencieux.
- Le garde-fou se vérifie à la main : invoquer le skill avec `$OBSIDIAN_VAULT_PRO` vidé doit produire l'arrêt annoncé, pas un commit dans le repo courant.
