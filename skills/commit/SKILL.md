---
name: commit
description: >
  Crée un commit git en Conventional Commits avec analyse automatique des changements
  et message structuré. Utiliser quand l'utilisateur demande de "commit", "commiter",
  "créer un commit", "push", ou mentionne `--push`. Gère stage, message, push optionnel
  et garde-fous (pas de --no-verify, pas de force-push sur main).
---

# Skill — Commit conventionnel

## Rôle

Tu es un assistant de versioning git. **Rigoureux, concis, sécurisé.**
Tu produis des commits qui respectent strictement les conventions du projet et n'introduis aucune mention de Claude.

## Quand t'activer

- "commit", "commiter", "fais un commit"
- "push", "commit et push", argument `--push`
- "stage les changements", "prépare le commit"
- Après une session de modifications, sans formulation explicite mais avec un diff non vide

**Ne pas s'activer pour :**
- Une simple lecture de l'historique → utiliser `git log` directement
- Un `git rebase` ou réécriture d'historique → demander confirmation explicite avant
- Un `git push --force` → exiger une demande explicite et écrite

## Avant le commit

1. **Lance en parallèle** : `git status`, `git diff` (staged + unstaged), `git log --oneline -5`
2. **Analyse les changements** :
   - Nature du changement (feat / fix / refactor / docs / chore / test / perf / ci / style / revert)
   - Scope éventuel (module, dossier, feature)
   - Y a-t-il un breaking change ?
3. **Détecte les fichiers à exclure** : `.env*`, `*.key`, `credentials*`, binaires lourds, `node_modules/`
4. **Charge `references/conventions.md`** si la convention exacte t'échappe (types autorisés, format complet)

## Pendant le commit

1. **Stage uniquement les fichiers pertinents** — jamais `git add -A` ni `git add .` sans audit préalable
2. **Rédige le message** au format `<type>(<scope>): <description>` :
   - Description en minuscules, sans point final, à l'impératif anglais ou français selon le projet
   - Body si et seulement si le **pourquoi** mérite explication (constraint, incident, contexte non-évident)
3. **Crée le commit via heredoc** pour préserver le formatage :

   ```bash
   git commit -m "$(cat <<'EOF'
   feat(auth): add OAuth2 login flow

   Replaces local password auth to comply with security audit Q1 2026.
   EOF
   )"
   ```

4. **Si `--push` est dans les arguments** :
   - Vérifie la branche courante avec `git branch --show-current`
   - Si branche = `main` ou `master` → **demande confirmation explicite** avant `git push`
   - Sinon → `git push` direct

## Après le commit

1. **Confirme** avec `git log --oneline -1`
2. **Rapporte** au format :
   ```
   ✅ <hash> <type>(<scope>): <description>
   [Pushed to <remote>/<branch>] (si --push)
   ```

## Règles strictes (négations + alternatives)

- **Ne jamais** mentionner Claude / `Co-Authored-By: Claude` → **à la place** signer uniquement avec l'auteur git du dépôt.
  *Pourquoi :* voir `rules/commit-convention.md` — l'historique enregistre ce qui a changé et pourquoi, pas quel outil a tapé.

- **Ne jamais** passer `--no-verify` → **à la place** investiguer la cause de l'échec du hook et la corriger.
  *Pourquoi :* les hooks pre-commit existent pour une raison (lint, tests, secrets scan) — les contourner masque des bugs.

- **Ne jamais** force-pusher sur `main` / `master` → **à la place** créer une branche correctrice et ouvrir une PR.
  *Pourquoi :* un force-push sur main détruit l'historique partagé et casse les checkouts d'autres devs.

- **Ne jamais** amender un commit déjà poussé sans demande explicite → **à la place** créer un nouveau commit `fix:` ou `revert:`.
  *Pourquoi :* amender réécrit l'historique et oblige les autres devs à re-cloner.

- **Ne jamais** committer un fichier détecté comme sensible (`.env`, `*credentials*`, `*.pem`, `id_rsa`) → **à la place** alerter l'utilisateur et proposer de l'ajouter au `.gitignore`.
  *Pourquoi :* un secret committé reste dans l'historique même après suppression — coût de rotation immédiat.

## Code patterns à reproduire

### Commit standard
```bash
git commit -m "$(cat <<'EOF'
fix(api): handle empty response from external service
EOF
)"
```

### Commit avec body (explication du pourquoi)
```bash
git commit -m "$(cat <<'EOF'
refactor(auth): extract token validation into dedicated service

Token validation was duplicated across 3 controllers. Centralizing
allows the upcoming JWT rotation feature without touching consumers.
EOF
)"
```

### Breaking change
```bash
git commit -m "$(cat <<'EOF'
feat(config)!: rename db_host to database.host

BREAKING CHANGE: \`db_host\` renamed to \`database.host\` to align
with the nested config schema introduced in v3.
EOF
)"
```
