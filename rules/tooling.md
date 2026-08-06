## Commandes Java/Maven — `bash -lc` + `sh ./mvnw`

Toute commande `java`, `javac`, `mvnw` → wrapper `bash -lc '<cmd>'`, et le wrapper Maven s'invoque **`sh ./mvnw`**, jamais `./mvnw`. Forme complète : `bash -lc 'sh ./mvnw test'`.

**Pourquoi `bash -lc`** : sinon `JAVA_HOME` est absent — le Bash tool lance un shell non-login qui ne source pas `~/.bashrc`. Les commandes hors-JDK (`git`, `ls`, `jq`…) n'en ont pas besoin.

**Pourquoi `sh`** : neuf des onze repos backend Winggy ont `mvnw` committé en `100644` (mesuré le 2026-08-06 sur `origin/HEAD`), et les modes disque ont été alignés dessus pour supprimer un `M mvnw` permanent. `./mvnw` rend donc « Permission non accordée » : le noyau refuse d'exécuter un fichier sans bit `x`. Passer par `sh` en fait un fichier **lu** et non exécuté — seul le bit `r` est requis, et le shebang devient un commentaire. Tous les wrappers portent `#!/bin/sh`, donc la forme marche partout, y compris sur `comments` et `reporting` dont le bit est committé.

Vérifié le 2026-08-06 sur `ged/mvnw` (mode 664) : `./mvnw --version` → « Permission non accordée » ; `sh ./mvnw --version` → `Apache Maven 3.9.16`.

## Écrire dans un fichier — jamais un heredoc imbriqué dans `bash -lc`

**À LA PLACE DE** `bash -lc 'cat >> cible << EOF … EOF'` → écrire le contenu avec le tool **Write**, puis l'ajouter par `cat <source> >> <cible>`. Pour remplacer plutôt qu'ajouter, Write ou Edit directement sur la cible.

**POURQUOI** : le Bash tool lance **zsh**, et `bash -lc '…'` ajoute une seconde passe de quoting. Un heredoc ouvert au troisième niveau ne se forme pas, et zsh évalue alors le contenu **comme du code** : les backticks deviennent des substitutions de commande, `**` un glob, l'apostrophe ferme la chaîne. Le markdown technique est le pire cas possible — il est saturé de ces trois caractères.

**Et la panne est silencieuse** : elle n'échoue pas, elle écrit à moitié. Constaté le 2026-08-06 sur `scripts/logs/decisions.md` du vault, qui a reçu la ligne tronquée `## 2026-08-06 (1) — Le mode de \`mvnw\` saligne` au lieu du bloc entier, avec en sortie `command not found: mvnw`, `no matches found: **Décision`. Sans relecture, le fichier restait corrompu.

**CE QUI RESTE AUTORISÉ** — l'interdit porte sur l'**imbrication**, pas sur le heredoc :

- `git commit -F - <<'EOF'` tapé au premier niveau, délimiteur quoté : aucune expansion, et `guard-no-claude-in-commit.sh` sait le lire (il en fait un cas de test).
- les heredocs à l'intérieur d'un script `.sh` versionné (`new-project.sh`, `new-daily.sh` du vault) : bash les exécute directement, sans surcouche.

Les mécaniques de commit existantes ne sont pas concernées : le vault passe par `vault-commit.sh "<msg>"` et `agent-config` par `git commit -m`, deux arguments quotés.
