# Références — `rules/workflow.md`

Les cas mesurés qui fondent les règles de `workflow.md`.

**Jamais chargé automatiquement.** Ce dossier n'est pas lié dans `~/.claude/rules/`, et le chargement y est **plat, pas récursif** — vérifié le 2026-08-11 : un marqueur planté dans un sous-dossier de `~/.claude/rules/` était invisible d'un sous-agent neuf interrogé sans aucun appel d'outil.

**Ce qui reste dans la règle, ce qui descend ici** : la règle garde l'instruction **et** son pourquoi ; ici vit l'anecdote chiffrée qui l'a produite. Une règle sans son pourquoi n'est pas suivie — c'est la méta-règle de `reasoning.md`. Une règle sans sa preuve l'est quand même : la preuve ne sert qu'à qui doute, qui conteste, ou qui veut réviser la règle. C'est ce qui la rend extractible sans perte de comportement.

---

## Pré-vol — trois valeurs fausses dans un même plan

Trois valeurs fausses dans un même document de plan : un clone 16 commits en retard, une route lue dans le wiki, un port recopié d'un plan frère.

**Cause unique** : une source adjacente consultée à la place de la source d'autorité. Aucune des trois n'aurait survécu à l'ouverture du fichier correspondant.

**Ce que ça a coûté** : des cycles de correction qui relisent un artefact entier pour une ligne fausse, contre quelques appels d'outil au moment de la rédaction.

## Échec fermé — deux pannes silencieuses le même jour (2026-08-05)

Le même défaut, deux fois, sur deux mécanismes différents :

- **`jq` absent du poste** rendait une chaîne vide. Le hook prenait cette chaîne vide pour « outil sans chemin de fichier » et laissait passer. Conséquence : le `PreToolUse` du Garden **autorisait toute écriture depuis son installation**, sans que rien ne le signale.
- **`VAULT_ROOT` pointant l'ancien poste** faisait rendre `0` à douze scripts de comptage. Un vault vide est parfaitement plausible — le zéro ne ressemblait pas à une panne.

**La leçon** : dans les deux cas le mécanisme ne pouvait pas conclure, et dans les deux cas il a répondu « rien à signaler » au lieu de « je ne peux pas savoir ».

## Échec fermé — un garde conditionné à l'artefact dont l'absence est le défaut

Un garde écrit puis supprimé le même jour. Il refusait d'écrire une recommandation tant que la note d'analyse du ticket restait incomplète — mais il ne se déclenchait qu'**en présence** de cette note.

Or celui qui ne mesure pas est précisément celui qui ne l'a pas ouverte. Le verrou ne pouvait donc attraper qu'une passe déjà à moitié conduite, jamais celle qui sautait le processus entier.

**Ce qui a marché à la place** : la règle de prose, qui a bien déclenché trois mesures ce jour-là. Quand le défaut vit dans le raisonnement et non dans un artefact, aucun hook ne l'atteint — un hook ne voit que les appels d'outil.

## Échec fermé — le premier garde outillage, refusé par le trafic réel (2026-08-11)

`guard-bash-tooling.py`, première conception : refuser toute commande que le lexer shell n'arrivait pas à tokeniser, au motif qu'un quoting cassé **est** le défaut que le garde surveille (un heredoc imbriqué ne se forme pas, donc son contenu s'évalue). Raisonnement juste, batterie de 32 cas au vert.

**Rejeu sur trafic réel** — les 993 commandes du périmètre extraites des transcripts de sessions (`~/.claude/projects/*/*.jsonl`), que personne n'avait écrites pour ce garde : 8 refus dans cette classe, dont **5 faux positifs**. Tous des `git commit -F - <<'EOF'` ordinaires, entrés dans le périmètre par le seul chemin `src/main/java` mis en index, et devenus illisibles à cause d'une apostrophe française dans le message.

**Puis un sixième, sur moi-même** : le premier message de commit du garde s'est fait refuser par le garde. Il *parlait* de `./mvnw`, et le corps du message était encore lu comme une commande.

**La leçon** : une batterie écrite par l'auteur du détecteur hérite de ses angles morts. Elle prouve les vrais positifs, jamais l'absence de faux. Et un garde qui refuse un commit ordinaire est désactivé dans la journée — même résultat qu'un échec ouvert.
