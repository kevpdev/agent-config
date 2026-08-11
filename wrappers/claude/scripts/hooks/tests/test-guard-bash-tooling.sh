#!/usr/bin/env bash
# Batterie de cas pour ../guard-bash-tooling.py
#
# Usage : bash wrappers/claude/scripts/hooks/tests/test-guard-bash-tooling.sh
# Sortie 0 si tous les cas passent, 1 sinon. N'ecrit rien, ne lance aucun java.
#
# POURQUOI CE FICHIER EXISTE
#   Le garde remplace deux regles de prose (rules/tooling.md) par un mecanisme
#   deterministe. Un mecanisme sans cible vivante se comporte exactement pareil
#   qu'il soit casse ou intact : les cas POSITIFS ci-dessous sont donc fabriques
#   a la main, et ce sont eux qui prouvent que le garde voit quelque chose.
#
#   Les deux defauts viennent du terrain, pas d'une hypothese :
#     - `./mvnw` sur un wrapper committe en 100644 → « Permission non accordee »
#       (mesure le 2026-08-06 sur ged/mvnw, mode 664).
#     - un heredoc imbrique dans `bash -lc '…'` → zsh EVALUE le corps au lieu de
#       l'ecrire. Constate le 2026-08-06 sur scripts/logs/decisions.md du vault,
#       qui a recu une ligne tronquee. La panne n'echoue pas : elle ecrit a moitie.
#
# CE QUI EST VERIFIE : la DECISION du garde (bloque / passe), pas son message.
#   Le libelle est de la prose et changera ; la decision est le contrat.
#
#   Les cas NEGATIFS pesent autant que les positifs : `bash -lc 'sh ./mvnw test'`
#   est la forme prescrite et passe des dizaines de fois par jour. Un garde qui la
#   refuserait serait desactive dans l'heure, et ne protegerait alors plus rien.

set -uo pipefail

ICI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK="$ICI/../guard-bash-tooling.py"
ECHECS=0

if [ ! -f "$HOOK" ]; then
  echo "garde introuvable : $HOOK" >&2
  exit 1
fi

verifier() {
  local nom="$1" attendu="$2" commande="$3"
  local sortie obtenu

  # Le garde lit un payload PreToolUse(Bash) sur stdin. Aucun cas ne depend d'un
  # depot reel ni d'un JDK installe : le garde juge une chaine, il n'execute rien.
  sortie=$(python3 -c "
import json, sys
print(json.dumps({
    'tool_name': 'Bash',
    'cwd': '/tmp',
    'tool_input': {'command': sys.argv[1]},
}))
" "$commande" | python3 "$HOOK" 2>/dev/null)

  obtenu="PASSE"
  printf '%s' "$sortie" | grep -q '"permissionDecision": "deny"' && obtenu="BLOQUE"

  if [ "$obtenu" = "$attendu" ]; then
    printf '  OK    %-55s %s\n' "$nom" "$obtenu"
  else
    printf '  ECHEC %-55s attendu=%s obtenu=%s\n' "$nom" "$attendu" "$obtenu"
    ECHECS=$((ECHECS + 1))
  fi
}

echo "=== T1 — le cas fondateur : ./mvnw sur un wrapper sans bit x ==="
verifier "./mvnw nu"                         BLOQUE './mvnw test'
verifier "./mvnw apres un cd"                BLOQUE 'cd /home/kevin/projects/ged && ./mvnw clean install'
verifier "./mvnw dans un bash -lc"           BLOQUE "bash -lc './mvnw test'"
verifier "chemin absolu vers un mvnw"        BLOQUE '/home/kevin/projects/ged/mvnw test'

echo
echo "=== T1 — JAVA_HOME absent faute de shell de login ==="
verifier "sh ./mvnw sans bash -lc"           BLOQUE 'sh ./mvnw test'
verifier "java nu"                           BLOQUE 'java -version'
verifier "javac nu"                          BLOQUE 'javac Foo.java'
verifier "bash -c (sans -l)"                 BLOQUE "bash -c 'sh ./mvnw test'"
verifier "sh -c (jamais de login)"           BLOQUE "sh -c 'java -version'"

echo
echo "=== T2 — heredoc imbrique dans bash -lc : la panne silencieuse ==="
verifier "heredoc EOF en append"             BLOQUE "$(printf "bash -lc 'cat >> cible.md << EOF\ncontenu\nEOF'")"
verifier "heredoc delimiteur quote"          BLOQUE "$(printf "bash -lc \"cat > cible.md <<'MSG'\ncontenu\nMSG\"")"
verifier "heredoc <<- indente"               BLOQUE "$(printf "bash -lc 'cat >> f <<-FIN\ncontenu\nFIN'")"

echo
echo "=== Commande illisible : refus sur PREUVE, jamais sur l'incapacite a lire ==="
# Premiere conception : refuser tout ce qui ne se tokenise pas, au motif qu'un
# quoting casse EST le defaut de T2. Le corpus reel l'a tuee — mesure du
# 2026-08-11 sur les 986 commandes du perimetre tirees des transcripts : 8 refus,
# dont 5 `git commit -F - <<'EOF'` parfaitement valides, entres dans le perimetre
# par le seul chemin `src/main/java` mis en index. D'ou les cas ci-dessous : ce
# qui se lit sans tokeniser refuse, le reste renonce.
verifier "commit heredoc, chemin src/main/java"  PASSE "$(cat <<'CMD'
git add backend/service/src/main/java/com/testbed/service/Quote.java && git commit -F - <<'EOF'
docs(quote): document the derived total invariant

Le corps porte l'apostrophe et des `backticks` qui cassent le lexer.
EOF
CMD
)"
verifier "javap + regex quotee dans bash -lc"    PASSE "bash -lc 'javap -p -c Foo.class | grep -oE \"// String .*|public .*\\(\"'"
verifier "illisible MAIS ./mvnw lisible dedans"  BLOQUE "bash -lc './mvnw test -Dmsg=\"quote non fermee'"
# Le tout premier commit de ce garde s'est fait refuser par lui : l'apostrophe
# francaise du message laissait un nombre impair de quotes, donc le corps du
# heredoc partait au scan brut, ou « ./mvnw » se lisait comme une invocation.
# Un corps de heredoc est de la PROSE, jamais une commande.
verifier "message de commit qui parle de ./mvnw" PASSE "$(cat <<'CMD'
git add -A && git commit -F - <<'EOF'
feat(hooks): add the bash tooling guard

Le corpus montre que ./mvnw etait tape quand meme, malgre l'interdit.
La forme prescrite reste bash -lc 'sh ./mvnw <goals>'.
EOF
CMD
)"

echo
echo "=== La forme prescrite : doit passer, sinon le garde sera desactive ==="
verifier "bash -lc sh ./mvnw"                PASSE "bash -lc 'sh ./mvnw test'"
verifier "avec des options Maven"            PASSE "bash -lc 'sh ./mvnw -DskipTests package'"
verifier "avec un pipe derriere"             PASSE "bash -lc 'sh ./mvnw test' 2>&1 | tail -20"
verifier "avec un cd interne"                PASSE "bash -lc 'cd /home/kevin/projects/ged && sh ./mvnw test'"
verifier "chemin absolu du wrapper"          PASSE "bash -lc 'sh /home/kevin/projects/ged/mvnw test'"
verifier "java dans un bash -lc"             PASSE "bash -lc 'java -version'"
verifier "bash -l -c en deux flags"          PASSE "bash -l -c 'sh ./mvnw test'"
verifier "JAVA_HOME pose explicitement"      PASSE 'JAVA_HOME=/opt/jdk-21 java -version'

echo
echo "=== « java » mentionne sans etre invoque : ne doit pas etre juge ==="
verifier "chemin src/main/java"              PASSE 'ls src/main/java'
verifier "grep sur le mot javac"             PASSE 'grep -rn "javac" src/'
verifier "git log --grep=java"               PASSE 'git log --grep=java --oneline'
verifier "un fichier .java en argument"      PASSE 'wc -l src/main/java/App.java'
verifier "hors perimetre"                    PASSE 'cat pom.xml'

echo
echo "=== Heredoc de PREMIER niveau : explicitement autorise ==="
# L'interdit porte sur l'imbrication, pas sur le heredoc. Ces deux formes sont
# celles dont depend la mecanique de commit ; les bloquer casserait le harnais.
verifier "git commit -F - heredoc"           PASSE "$(printf 'git commit -F - <<%sEOF%s\ndocs(x): sujet\nEOF\n' "'" "'")"
verifier "heredoc vers un fichier"           PASSE "$(printf 'cat >> notes.md <<%sEOF%s\ncontenu\nEOF\n' "'" "'")"
verifier "decalage arithmetique, pas heredoc" PASSE "bash -lc 'echo \$((1 << 2))'"

echo
if [ "$ECHECS" -eq 0 ]; then
  echo "TOUS LES CAS PASSENT"
else
  echo "$ECHECS ECHEC(S)"
  exit 1
fi
