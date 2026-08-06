## Commandes Java/Maven — `bash -lc` + `sh ./mvnw`

Toute commande `java`, `javac`, `mvnw` → wrapper `bash -lc '<cmd>'`, et le wrapper Maven s'invoque **`sh ./mvnw`**, jamais `./mvnw`. Forme complète : `bash -lc 'sh ./mvnw test'`.

**Pourquoi `bash -lc`** : sinon `JAVA_HOME` est absent — le Bash tool lance un shell non-login qui ne source pas `~/.bashrc`. Les commandes hors-JDK (`git`, `ls`, `jq`…) n'en ont pas besoin.

**Pourquoi `sh`** : neuf des onze repos backend Winggy ont `mvnw` committé en `100644` (mesuré le 2026-08-06 sur `origin/HEAD`), et les modes disque ont été alignés dessus pour supprimer un `M mvnw` permanent. `./mvnw` rend donc « Permission non accordée » : le noyau refuse d'exécuter un fichier sans bit `x`. Passer par `sh` en fait un fichier **lu** et non exécuté — seul le bit `r` est requis, et le shebang devient un commentaire. Tous les wrappers portent `#!/bin/sh`, donc la forme marche partout, y compris sur `comments` et `reporting` dont le bit est committé.

Vérifié le 2026-08-06 sur `ged/mvnw` (mode 664) : `./mvnw --version` → « Permission non accordée » ; `sh ./mvnw --version` → `Apache Maven 3.9.16`.
