#!/usr/bin/env bash
# Batterie de cas pour ../guard-no-claude-in-commit.sh
#
# Usage : bash wrappers/claude/scripts/hooks/tests/test-guard-no-claude-in-commit.sh
# Sortie 0 si tous les cas passent, 1 sinon. N'ecrit rien, ne touche aucun depot.
#
# POURQUOI CE FICHIER EXISTE
#   Ce hook s'interpose devant CHAQUE commit. Un faux positif y coute plus cher
#   qu'ailleurs : il refuse un travail valide, et un garde-fou qui refuse du
#   travail valide finit desactive — il ne protege alors plus rien.
#   Le cas fondateur, mesure le 2026-07-30 : l'extracteur prenait le premier `-m`
#   de la commande entiere, donc un `git commit -F - <<'EOF' … EOF` suivi d'un
#   `git tag -m 'annotation'` faisait juger le message du TAG. Le bug a survecu
#   parce que rien ne rejouait ces formes. Il est desormais le premier cas ci-dessous.
#
#   A LA PLACE de relire le hook a l'oeil apres chaque retouche → relancer ce
#   fichier. Toute nouvelle forme de commande rencontree s'ajoute ici avant d'etre
#   corrigee dans le hook, sinon la meme classe de bug revient sans etre vue.
#
# CE QUI EST VERIFIE : la DECISION du hook (bloque / passe), pas son message.
#   Le libelle d'erreur est de la prose et changera ; la decision est le contrat.

set -uo pipefail

ICI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOOK="$ICI/../guard-no-claude-in-commit.sh"
ECHECS=0

if [ ! -x "$HOOK" ]; then
  echo "hook introuvable ou non executable : $HOOK" >&2
  exit 1
fi

verifier() {
  local nom="$1" attendu="$2" commande="$3"
  local sortie obtenu

  # Le hook lit un payload PreToolUse(Bash) sur stdin. Le cwd est arbitraire :
  # aucun cas ci-dessous ne depend d'un depot reel.
  sortie=$(python3 -c "
import json, sys
print(json.dumps({
    'tool_name': 'Bash',
    'cwd': '/tmp',
    'tool_input': {'command': sys.argv[1]},
}))
" "$commande" | "$HOOK" 2>/dev/null)

  obtenu="PASSE"
  printf '%s' "$sortie" | grep -q '"decision": "block"' && obtenu="BLOQUE"

  if [ "$obtenu" = "$attendu" ]; then
    printf '  OK    %-55s %s\n' "$nom" "$obtenu"
  else
    printf '  ECHEC %-55s attendu=%s obtenu=%s\n' "$nom" "$attendu" "$obtenu"
    ECHECS=$((ECHECS + 1))
  fi
}

echo "=== Le cas fondateur : un -m qui n'appartient pas au commit ==="
verifier "commit heredoc + git tag -m derriere" PASSE "$(cat <<'CMD'
git add -A && git commit -q -F - <<'EOF'
refactor(db): let the project create its own databases

Corps du message avec un && dedans et un ; aussi.
EOF
git log --oneline -2 && git tag -f -a fixture/base -m 'point de depart propre du banc' HEAD
CMD
)"

echo
echo "=== -m alimente par une substitution de commande ==="
# Mesure le 2026-07-31 : c'est la forme standard d'un message multi-lignes, et le
# hook la bloquait alors qu'elle est conforme. Ce qui suit `-m` n'est pas le
# message mais le debut de `$(cat …)` ; l'extracteur en tirait le jeton `"$(cat`
# et jugeait CA contre la convention. Le `-F -` voisin, lui, etait deja teste et
# passait — d'ou un garde-fou qui refusait la forme la plus courante.
verifier "-m \$(cat heredoc) conforme"       PASSE "$(cat <<'CMD'
git commit -m "$(cat <<'EOF'
feat(db): add the bootstrap script

Corps du message.
EOF
)"
CMD
)"
verifier "-m \$(cat heredoc) non conforme"   BLOQUE "$(cat <<'CMD'
git commit -m "$(cat <<'EOF'
ajout du script
EOF
)"
CMD
)"
# Garde-fou du correctif : une substitution FERMEE dans le sujet reste un sujet.
# Sans cette borne, le correctif renoncerait a valider tout message contenant
# `$(...)`, et un sujet non conforme passerait par cette porte.
verifier "substitution fermee dans le sujet" BLOQUE 'git commit -m "ajout de $(pwd)"'

echo
echo "=== Messages non conformes : doivent bloquer ==="
verifier "-m sujet libre"                    BLOQUE 'git commit -m "ajout du script"'
verifier "-am sujet libre"                   BLOQUE 'git commit -am "ajout du script"'
verifier "heredoc sujet libre"               BLOQUE "$(printf 'git commit -F - <<%sEOF%s\najout du script\nEOF\n' "'" "'")"
verifier "git -C chemin commit"              BLOQUE 'git -C /tmp/x commit -m "ajout du script"'
verifier "type inconnu"                      BLOQUE 'git commit -m "wip(db): quelque chose"'

echo
echo "=== Messages conformes : doivent passer ==="
verifier "-m conforme"                       PASSE 'git commit -m "feat(db): add bootstrap script"'
verifier "-am conforme"                      PASSE 'git commit -am "fix(db): repair the probe"'
verifier "--message= conforme"               PASSE 'git commit --message="chore: bump deps"'
verifier "heredoc conforme"                  PASSE "$(printf 'git commit -F - <<%sEOF%s\ndocs(db): explain the bootstrap\n\nCorps.\nEOF\n' "'" "'")"
verifier "delimiteur heredoc autre que EOF"  PASSE "$(printf 'git commit -F - <<%sMSG%s\ntest(db): cover the probe\nMSG\n' "'" "'")"
verifier "amend sans message"                PASSE 'git commit --amend --no-edit'
verifier "vault : sujet francais autorise"   PASSE 'git commit -m "docs(2026-07-30): import des refs"'

echo
echo "=== Ce qui n'est pas un commit : ne doit pas etre juge ==="
verifier "git tag seul"                      PASSE "git tag -f -a fixture/base -m 'point de depart' HEAD"
verifier "git log avec -m"                   PASSE 'git log -m --oneline'

echo
echo "=== Garde-fou Claude : inchange ==="
verifier "mention Co-Authored-By"            BLOQUE 'git commit -m "feat(x): ok

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>"'

echo
echo "=== Ambiguite : on renonce plutot que deviner (fail-open) ==="
verifier "deux heredocs"                     PASSE "$(cat <<'CMD'
git commit -F - <<'EOF'
sujet non conforme
EOF
cat <<'AUTRE'
autre chose
AUTRE
CMD
)"

echo
if [ "$ECHECS" -eq 0 ]; then
  echo "TOUS LES CAS PASSENT"
else
  echo "$ECHECS ECHEC(S)"
  exit 1
fi
