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
echo "=== Message inline multi-lignes : ne pas couper a l'interieur ==="
# Mesure du 2026-08-11 sur trafic reel : 21 commits VALIDES refuses sur 26 refus
# format. Le decoupage en segments tombait sur le retour a la ligne DU MESSAGE,
# laissait un guillemet ouvert, shlex renoncait, et le repli grossier rendait le
# moignon `"docs(x):` — qui echoue au controle. Corrige par un decoupage qui ne
# separe que hors guillemets. Ces formes viennent du trafic, pas de mon imagination.
verifier "deux -m, corps multi-lignes"       PASSE "$(printf 'git commit -m "docs(analysis): add the ci centralisation analysis" -m "Measured scope is 21 projects,\nnot the 6 announced."')"
verifier "un -m, sujet puis corps"           PASSE "$(printf 'git commit -q -m "fix(db): harden the catalogue constraints\n\nCorps sur deux lignes."')"
verifier "multi-lignes non conforme"         BLOQUE "$(printf 'git commit -m "wip on the db\n\nCorps."')"
# Apostrophe dans le corps, entre guillemets doubles : legale en shell, et c'est
# elle qui faisait renoncer shlex sur la moitie des cas.
verifier "apostrophe dans le corps"          PASSE "$(printf 'git commit -m "docs(db): expliquer le bootstrap\n\nCe que l%sanalyse montre."' "'")"

echo
echo "=== Message dans un fichier : une source lisible, pas une ambiguite ==="
# Mesure du 2026-08-11, en bac a sable : `git commit -F badmsg.txt` dont le sujet
# etait « wip stuff » a atterri sans etre valide, et les quatre commits du jour
# avaient tous pris ce chemin. Le garde ne reconnaissait `-F` que suivi de `-`.
#
# Ces cas ecrivent des fichiers temporaires, contrairement aux precedents : le
# garde ouvre desormais le chemin, donc le fichier doit exister. Aucun depot n'est
# touche pour autant.
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
printf 'wip stuff\n'                          > "$TMP/mauvais.txt"
printf 'docs(db): explain the bootstrap\n\nCorps.\n' > "$TMP/bon.txt"

verifier "-F fichier, sujet non conforme"    BLOQUE "git commit -F $TMP/mauvais.txt"
verifier "-F fichier, sujet conforme"        PASSE  "git commit -F $TMP/bon.txt"
verifier "--file=fichier non conforme"       BLOQUE "git commit --file=$TMP/mauvais.txt"
verifier "--file=fichier conforme"           PASSE  "git commit --file=$TMP/bon.txt"
# Fichier absent : le garde ne peut pas lire, donc il renonce — meme fail-open que
# partout ailleurs dans cet extracteur, et un chemin faux fera de toute facon
# echouer le `git commit` lui-meme.
verifier "-F fichier absent"                 PASSE  "git commit -F $TMP/jamais-ecrit.txt"

# CHEMIN RELATIF — le cas que cette batterie ne savait pas voir. Les quatre cas
# ci-dessus utilisent un chemin absolu, ils passaient donc au vert alors que le
# commit reel, lui, n'etait toujours pas controle : le trafic ecrit `-F msg.txt`
# apres un `cd`, et le hook ne tourne pas depuis ce dossier. Le payload fabrique
# ici porte cwd=/tmp, comme la fonction `verifier` ci-dessus, donc un chemin
# relatif au dossier temporaire s'y resout.
REL="$(basename "$TMP")"
verifier "-F chemin relatif non conforme"    BLOQUE "git commit -F $REL/mauvais.txt"
verifier "-F chemin relatif conforme"        PASSE  "git commit -F $REL/bon.txt"
# Avec un `cd` en tete, c'est ce `cd` qui fixe le dossier, pas le cwd du payload.
verifier "cd puis -F relatif non conforme"   BLOQUE "cd $TMP && git commit -F mauvais.txt"
verifier "cd puis -F relatif conforme"       PASSE  "cd $TMP && git commit -F bon.txt"

# CHEMIN VIA VARIABLE SHELL — echoue FERME, et c'est le seul cas de ce fichier.
# Le shell resout la variable, le garde non (il n'evalue jamais son entree), donc
# laisser passer signifie un commit non controle. Deux correctifs successifs sont
# passes au vert sur cette batterie pendant que le commit reel atterrissait, les
# deux fois parce que la commande portait `-F "$VAR/msg.txt"`. Le message conforme
# est refuse AUSSI : le garde ne peut pas savoir qu'il l'est.
verifier "-F via variable shell"             BLOQUE 'S=/tmp/x && git commit -F "$S/msg.txt"'
verifier "-F via variable, sujet conforme"   BLOQUE 'S=/tmp/x && git commit -F "$S/bon.txt"'
# Substitution de commande : meme raisonnement, meme refus.
verifier "-F via substitution"               BLOQUE 'git commit -F "$(pwd)/msg.txt"'
# LA FORME REELLE, celle qui a survecu a trois correctifs : l'argument est un chemin
# relatif propre, sans variable — c'est le DOSSIER CIBLE qui vient d'un `cd "$VAR"`.
# Un correctif qui n'inspecte que l'argument passe ici au vert et laisse le trou.
verifier "cd via variable puis -F relatif"   BLOQUE 'G=/tmp/x && cd "$G" && git commit -q -F badmsg.txt'
# Meme forme, mais le dossier est litteral : la resolution aboutit, donc on juge.
verifier "cd litteral puis -F relatif"       BLOQUE "cd $TMP && git commit -q -F mauvais.txt"

echo
if [ "$ECHECS" -eq 0 ]; then
  echo "TOUS LES CAS PASSENT"
else
  echo "$ECHECS ECHEC(S)"
  exit 1
fi
