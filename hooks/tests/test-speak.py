#!/usr/bin/env python3
"""Batterie du cœur de la lecture vocale, `hooks/speak.py`.

Pourquoi cette batterie existe : la voix ne s'entend pas en CI. Ce qui se prouve
sans haut-parleur, c'est le texte envoyé à Piper. Un bloc de code ou un tableau
lu à voix haute rend la réponse inécoutable, donc le nettoyage porte le risque.

Ce qui est vérifié : le texte nettoyé, la coupe sur une fin de phrase,
l'interrupteur `AGENT_VOICE`, et le mode à la demande (mémoriser sans jouer,
puis `--last` et `--stop`).

Sortie : 0 si tous les cas passent, 1 si un cas échoue.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
SPEAK = os.path.join(REPO, "hooks", "speak.py")
sys.path.insert(0, os.path.join(REPO, "hooks"))

import speak  # noqa: E402

echecs = 0


def egal(nom, obtenu, attendu):
    global echecs
    ok = obtenu == attendu
    print("  %s %s" % ("OK   " if ok else "ECHEC", nom))
    if not ok:
        print("        attendu=%r obtenu=%r" % (attendu, obtenu))
        echecs += 1


egal("titre et gras", speak.clean("## Titre\nBonjour **toi**."), "Titre. Bonjour toi.")
egal("bloc de code retiré", speak.clean("Avant\n```py\nx = 1\n```\nAprès"), "Avant. Après.")
egal("tableau et décorateur retirés",
     speak.clean("Voici.\n@{view:columns}\n| a | b |\n| --- | --- |\n| 1 | 2 |\nFin."), "Voici. Fin.")
egal("lien gardé, URL retirée", speak.clean("Lis [la doc](https://x.y) ou https://a.b"), "Lis la doc ou.")
egal("code inline gardé", speak.clean("Lance `speak.py` maintenant"), "Lance speak.py maintenant.")
egal("puces et citation", speak.clean("- un\n* deux\n> [!WARNING]\n> trois"), "un. deux. trois.")
egal("ponctuation finale conservée", speak.clean("On y va ?"), "On y va ?")

LEX = {"units": {"ms": "millisecondes", "%": "pour cent"},
       "lexicon": {"pipeline": "païpe-laïne", "hook": "houk"}}
egal("unité après un nombre", speak.pronounce("en 23 ms.", LEX), "en 23 millisecondes.")
egal("unité collée au nombre", speak.pronounce("en 1,5ms", LEX), "en 1,5 millisecondes")
egal("unité sans nombre intacte", speak.pronounce("le ms seul", LEX), "le ms seul")
egal("pourcentage", speak.pronounce("12 % des cas", LEX), "12 pour cent des cas")
egal("mot du lexique, casse ignorée", speak.pronounce("Pipeline et HOOK", LEX), "païpe-laïne et houk")
egal("mot entier seulement", speak.pronounce("pipelines hooked", LEX), "pipelines hooked")
egal("sans lexique ni unités", speak.pronounce("23 ms pipeline", {}), "23 ms pipeline")

egal("coupe sur fin de phrase", speak.truncate("Une phrase. Deux phrases longues.", 20), "Une phrase.")
egal("pas de coupe sous le seuil", speak.truncate("Court.", 20), "Court.")
egal("coupe franche sans fin de phrase", speak.truncate("abcdefghij", 4), "abcd")

for valeur, attendu in (("0", False), ("off", False), ("1", True)):
    os.environ["AGENT_VOICE"] = valeur
    egal("AGENT_VOICE=%s" % valeur, speak.enabled({"enabled": True}), attendu)
del os.environ["AGENT_VOICE"]
egal("config enabled=false", speak.enabled({"enabled": False}), False)

r = subprocess.run([sys.executable, SPEAK, "--dry-run"], input="# Salut\nça va ?",
                   capture_output=True, text=True)
egal("--dry-run de bout en bout", (r.returncode, r.stdout.strip()), (0, "Salut. ça va ?"))

# Les cas suivants écrivent l'état dans un dossier jetable. Piper pointe sur un
# chemin absent : une tentative de lecture se voit donc à sa ligne sur stderr.
etat = tempfile.mkdtemp()
dernier = os.path.join(etat, "agent-voice", "last.txt")


def lancer(mode, *argv, entree="", **env):
    config = os.path.join(etat, "speak-%s.json" % mode)
    with open(config, "w") as fh:
        json.dump({"mode": mode, "piper": "/nonexistent/piper", "voices_dir": etat,
                   "voice": "absente", "lexicon": {"hook": "houk"}}, fh)
    return subprocess.run([sys.executable, SPEAK, *argv], input=entree, capture_output=True, text=True,
                          env={**os.environ, "XDG_RUNTIME_DIR": etat, "AGENT_VOICE_CONFIG": config, **env})


r = lancer("on-demand", "--last")
egal("--last sans réponse mémorisée : sortie 0, une ligne d'aide",
     (r.returncode, "aucune réponse" in r.stderr), (0, True))

r = lancer("on-demand", entree="Le hook a fini.")
egal("à la demande : mémorise sans jouer", (r.returncode, r.stderr), (0, ""))
egal("à la demande : texte mémorisé nettoyé", open(dernier).read(), "Le houk a fini.")

r = lancer("on-demand", "--last")
egal("--last tente de jouer la réponse mémorisée", (r.returncode, "introuvable" in r.stderr), (0, True))

r = lancer("auto", entree="Rien.")
egal("auto : tente de jouer", (r.returncode, "introuvable" in r.stderr), (0, True))

r = lancer("auto", entree="Rien.", AGENT_VOICE="0")
egal("auto coupé par AGENT_VOICE : mémorise sans jouer", (r.returncode, r.stderr), (0, ""))

r = lancer("on-demand", "--stop")
egal("--stop sans lecture en cours : sortie 0", (r.returncode, r.stderr), (0, ""))

shutil.rmtree(etat)

print("%d échec(s)" % echecs)
sys.exit(1 if echecs else 0)
