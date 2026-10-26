#!/bin/bash
# InstructionsLoaded — journalise, pour le banc, quel fichier d'instructions se charge.
#
# Repris de MyObsidianVault/.claude/hooks/log-instructions-loaded.sh. Le journal est
# nommé par BENCH_LOG, que seul tools/bench.sh pose : hors du banc, le hook ne fait rien.
#
# Le champ `content` de l'événement porte le fichier entier : on ne journalise que le
# chemin et la raison.
#
# Échec ouvert, comme le hook du vault : il observe, il ne protège rien. Mais une entrée
# illisible laisse une ligne LOG-ERREUR, que tools/bench-report.py compte comme un échec.
set -uo pipefail

[ -z "${BENCH_LOG:-}" ] && exit 0

python3 -c '
import json, sys
try:
    d = json.load(sys.stdin)
except Exception as e:
    print(sys.argv[1] + "\tLOG-ERREUR\tentrée illisible: " + str(e))
    sys.exit(0)
print("\t".join([sys.argv[1], str(d.get("load_reason", "?")), str(d.get("file_path", "?"))]))
' "$(date '+%Y-%m-%d %H:%M:%S')" >> "$BENCH_LOG" 2>&1

exit 0
