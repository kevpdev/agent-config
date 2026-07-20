---
name: vault-slides
description: >
  Génère une présentation Slidev (un deck.md) dans le vault depuis une session HORS vault
  (CWD = repo de dev). Pont vers le skill canonique vault-slides, avec résolution des chemins
  contre la racine absolue du vault.
  Utiliser quand : "génère une présentation", "fais des slides", "slides Slidev", "/vault-slides".
---

# Passerelle vault — slides

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
- **Skill canonique à exécuter** : `$OBSIDIAN_VAULT_PRO/agent/skills/slides/SKILL.md`.

1. Lis et suis les instructions de `$OBSIDIAN_VAULT_PRO/agent/skills/slides/SKILL.md`.
2. **Résous tout chemin relatif contre la racine absolue.** Le deck se crée dans
   `$OBSIDIAN_VAULT_PRO/2_PROJECTS/<projet>/slides/`, **jamais** dans le repo courant.
3. Si la source de contenu est le repo courant, lis-le depuis le CWD ; n'y écris rien.
4. Pour la date / les noms de fichier : `bash -lc 'date +%F'`.
5. Confirme à l'utilisateur le chemin absolu créé + la commande de rendu.
