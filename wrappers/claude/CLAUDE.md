# CLAUDE.md — instructions globales (squelette d'imports)

Chaque catégorie de règles vit dans son fichier importé ci-dessous.
Partagé team → `config/*.md`. Override perso non partagé → `local-*.md` (gitignore `local-*`).
Ordre = team d'abord, perso ensuite (override). Un import vers un fichier absent dégrade sans casse.

## Règles & méthodo (team)
@~/.claude/config/reasoning.md
@~/.claude/config/workflow.md

## Style (team)
Style commun transverse : `~/.claude/core-rules.md`, injecté au system prompt via l'alias `--append-system-prompt-file` (inconditionnel, survit au compact). Deltas par contexte : output styles (`output-styles/cognitive-load-min.md` chat, `<vault>/.claude/output-styles/vault-notes.md` vault).

## Conventions & environnement (team)
@~/.claude/config/commit-convention.md
@~/.claude/config/tooling.md
@~/.claude/config/memory-policy.md

## Perso — non partagé
@~/.claude/local-profil.md
@~/.claude/local-persona.md
