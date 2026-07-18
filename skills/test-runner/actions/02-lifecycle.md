# 02 — lifecycle : start / status / stop

Tient l'app en vie pour la validation. Consomme la `recipe` de `01-discover`.

## start

- **Idempotent** : si l'app tourne déjà (health OK sur `readyUrl`), réutiliser l'existant, ne pas relancer.
- Démarrer avec la `startCmd` + les `env` découverts, attendre le **signal « prête »** avant de rendre la main.
- Rendre : `{ up: bool, url, pid|handle, logs }`.

## status

- Rendre ce qui tourne, l'URL, où sont les logs. Lecture seule.

## stop

- Arrêter **uniquement** ce que `start` a lancé (ne pas tuer un process que l'humain tenait déjà).

## Locus — qui exécute

- **Parent** si l'app doit **survivre** à une boucle debug (éviter de rebooter à chaque tour).
- **Subagent one-shot** sinon (démarre → teste → arrête → rend le rapport).
- Garde-fou : un process Bash orphelin doit être **tué explicitement** — toujours un `stop` en fin de scope subagent.
