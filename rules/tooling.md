# Outillage — deux invariants, tenus par un hook

- Toute commande `java`, `javac`, `mvnw` → `bash -lc 'sh ./mvnw <goals>'`.
- Aucun heredoc imbriqué dans un `bash -lc '…'` → écrire par le tool **Write**, puis `cat <source> >> <cible>`.

**Volontairement non argumenté ici.** `wrappers/claude/scripts/hooks/guard-bash-tooling.py` refuse les deux à l'appel, et son refus porte la raison, la mesure qui la fonde et la forme correcte. Ne pas recopier ses critères dans cette page : deux copies divergent au premier edit, et une page qui a l'air complète dispense de lire le garde.

**POURQUOI ces deux lignes survivent quand même** : un hook ne parle qu'après coup. Elles évitent d'écrire la commande fautive ; le garde attrape ce qu'elles ratent.
