## Commandes Java/Maven — wrapper `bash -lc`

Toute commande `java`, `javac`, `./mvnw` → wrapper `bash -lc '<cmd>'` (ex. `bash -lc './mvnw test'`). Sinon `JAVA_HOME` absent : le Bash tool lance un shell non-login qui ne source pas `~/.bashrc`. Les commandes hors-JDK (`git`, `ls`, `jq`…) n'en ont pas besoin.
