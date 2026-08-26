# 02 - Tenir l'app en vie

Démarre l'app, la sonde, puis l'arrête. Idempotent d'un bout à l'autre.

## Input

La `recipe` de `01-discover`, et le scope d'exécution du caller (parent ou subagent).

## Output

L'état de l'app : `{ up: bool, url, pid|handle, logs }`, avec l'emplacement des logs pour le
diagnostic.

## Process

1. **Démarrer.** Lancer la `startCmd` avec les `env` découverts, puis attendre le signal « prête »
   sur `readyUrl` avant de rendre la main.
   - **Locus.** Porter le process côté **parent** quand l'app doit survivre à une boucle de debug,
     pour ne pas la rebooter à chaque tour. Sinon **subagent one-shot**, qui démarre, teste, arrête
     et rend le rapport. *Pourquoi le locus se décide avant de lancer : un serveur meurt avec le
     subagent qui l'a lancé, donc le choix ne se rattrape pas après coup.*
   - **Idempotence.** Si le health de `readyUrl` répond déjà, réutiliser l'existant au lieu de
     relancer.
2. **Sonder.** Rendre ce qui tourne, l'URL et l'emplacement des logs. Lecture seule, aucun effet sur
   le process.
3. **Arrêter.** Tuer uniquement ce que l'étape 1 a lancé, jamais un process que l'humain tenait
   déjà.
   - **Garde.** Un process Bash orphelin se tue explicitement, donc toujours un arrêt en fin de
     scope subagent.

## Test

| Cas | Preuve |
| --- | --- |
| lancer le démarrage deux fois de suite | le second réutilise le process du premier, aucun second port ouvert |
| lancer le démarrage sur une app déjà tenue à la main par l'humain | l'arrêt la laisse vivante, seul ce que l'étape 1 a lancé est tué |
| `ps` après la fin d'un scope subagent | aucun process du run ne survit |
| relire ce que rend le démarrage | `up`, `url` et l'emplacement des logs sont tous les trois renseignés |
