#!/usr/bin/env python3
"""Calibre `sync-settings.py` sur des settings fabriqués, sans toucher la config vivante.

Pourquoi cette batterie existe : un script de sync qui ne voit rien rend « aucun écart »
exactement comme un script qui voit juste. Seuls un positif et un négatif par règle de
fusion, exhibés à la main, distinguent les deux (`rules/reasoning.md`, calibrage avant
comptage).

Pourquoi des fichiers fabriqués : la cible réelle est la config de la session en cours,
et `--fix` y écrit. Le script est pointé sur un dossier temporaire par `SOURCE` et
`CLAUDE_SETTINGS_FILE`.

Sortie : 0 si tous les cas passent, 1 si un cas échoue.
"""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(os.path.dirname(HERE), "sync-settings.py")


def load_script():
    if not os.path.exists(SCRIPT):
        sys.exit(f"sync-settings.py introuvable à {SCRIPT}")
    spec = importlib.util.spec_from_file_location("sync_settings", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


REPO = {
    "model": "sonnet",
    "skipDangerousModePermissionPrompt": False,
    "statusLine": {"type": "command", "command": "bash repo.sh"},
    "enabledPlugins": {"a@m": True},
    "hooks": {
        "PreToolUse": [
            {"matcher": "", "hooks": [{"type": "command", "command": "garde-1"},
                                      {"type": "command", "command": "garde-2"}]}
        ]
    },
}

MACHINE = {
    "permissions": {"allow": ["Bash(ls)"]},
    "voice": {"enabled": True},
    "skipDangerousModePermissionPrompt": True,
    "statusLine": {"type": "command", "command": "bash machine.sh"},
    "enabledPlugins": {"b@m": True},
    "hooks": {
        "PreToolUse": [{"matcher": "", "hooks": [{"type": "command", "command": "garde-1"}]}],
        "MessageDisplay": [{"hooks": [{"type": "command", "command": "cc-views"}]}],
    },
}


def lancer(module, dossier, machine, argv):
    """Écrit les deux fichiers, lance main, rend (code, cible relue, sortie)."""
    source = os.path.join(dossier, "repo.json")
    cible = os.path.join(dossier, "settings.json")
    with open(source, "w") as f:
        json.dump(REPO, f)
    if machine is None:
        if os.path.exists(cible):
            os.unlink(cible)
    elif isinstance(machine, str):
        with open(cible, "w") as f:
            f.write(machine)
    else:
        with open(cible, "w") as f:
            json.dump(machine, f)
    module.SOURCE = source
    os.environ["CLAUDE_SETTINGS_FILE"] = cible
    sortie = io.StringIO()
    with contextlib.redirect_stdout(sortie), contextlib.redirect_stderr(sortie):
        try:
            code = module.main(argv)
        except SystemExit as e:
            code = 1 if e.code else 0
            print(e.code)
    relu = None
    if os.path.exists(cible):
        with open(cible) as f:
            texte = f.read()
        try:
            relu = json.loads(texte)
        except json.JSONDecodeError:
            relu = texte
    return code, relu, sortie.getvalue()


def commandes(hooks, evenement):
    return [h["command"] for g in hooks.get(evenement, []) for h in g.get("hooks", [])]


def main() -> int:
    module = load_script()
    echecs = 0

    def cas(nom, condition):
        nonlocal echecs
        print(f"  {'ok  ' if condition else 'FAIL'}  {nom}")
        if not condition:
            echecs += 1

    with tempfile.TemporaryDirectory() as d:
        code, relu, sortie = lancer(module, d, MACHINE, [])
        cas("vérif : des écarts sortent en 1", code == 1)
        cas("vérif : model absent est signalé", "model : absent" in sortie)
        cas("vérif : statusLine différent est signalé", "statusLine.command" in sortie)
        cas("vérif : hook manquant est signalé", "garde-2" in sortie)
        cas("vérif : garde-1 déjà présent n'est pas signalé", "garde-1" not in sortie)
        cas("vérif : clé exclue non signalée", "skipDangerous" not in sortie)
        cas("vérif : n'écrit rien", relu == MACHINE)

        code, relu, _ = lancer(module, d, MACHINE, ["--fix"])
        cas("fix : sort en 0", code == 0)
        cas("fix : scalaire du repo appliqué", relu.get("model") == "sonnet")
        cas("fix : dict fusionné, valeur du repo", relu["statusLine"]["command"] == "bash repo.sh")
        cas("fix : clés machine conservées", relu.get("permissions") == MACHINE["permissions"]
            and relu.get("voice") == MACHINE["voice"])
        cas("fix : plugin machine conservé et plugin repo ajouté",
            relu["enabledPlugins"] == {"b@m": True, "a@m": True})
        cas("fix : clé exclue garde la valeur machine",
            relu.get("skipDangerousModePermissionPrompt") is True)
        pre = commandes(relu["hooks"], "PreToolUse")
        cas("fix : hook repo ajouté sans doublon", sorted(pre) == ["garde-1", "garde-2"])
        cas("fix : hook machine jamais retiré",
            commandes(relu["hooks"], "MessageDisplay") == ["cc-views"])
        cas("fix : sauvegarde .bak créée",
            os.path.exists(os.path.join(d, "settings.json.bak")))

        avant = relu
        code, relu, sortie = lancer(module, d, avant, [])
        cas("conforme : sort en 0", code == 0 and "aucun écart" in sortie)
        code, relu, _ = lancer(module, d, avant, ["--fix"])
        cas("idempotence : second fix ne change rien", code == 0 and relu == avant)

        code, relu, _ = lancer(module, d, None, ["--fix"])
        cas("cible absente : créée avec les clés du repo", code == 0 and relu.get("model") == "sonnet")

        code, relu, _ = lancer(module, d, "{ cassé", ["--fix"])
        cas("JSON cassé : sort en 1 sans écrire", code == 1 and relu == "{ cassé")

    print(f"{'✓' if not echecs else '✗'} {echecs} échec(s).")
    return 1 if echecs else 0


if __name__ == "__main__":
    sys.exit(main())
