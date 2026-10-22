#!/usr/bin/env python3
"""Calibre `tools/install.py` sur une cible fabriquée, sans toucher la config vivante.

Pourquoi cette batterie existe : un installateur qui ne voit rien rend « aucun écart »
exactement comme un installateur qui voit juste. Seuls un positif et un négatif par
classe d'écart, exhibés à la main, distinguent les deux (`rules/reasoning.md`,
calibrage avant comptage).

Pourquoi une cible fabriquée : la cible réelle est la config de la session en cours, et
`--fix` y écrit. Le script est lancé en sous-processus, avec `HOME` redirigé quand le
cas porte sur le rendu des chemins.

Sortie : 0 si tous les cas passent, 1 si un cas échoue.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
SCRIPT = os.path.join(REPO, "tools", "install.py")


def lancer(cible, *argv, home=None):
    """Lance l'installateur, rend (code, sortie fusionnée)."""
    env = dict(os.environ)
    env.pop("CLAUDE_SETTINGS_FILE", None)
    if home:
        env["HOME"] = home
    r = subprocess.run(
        [sys.executable, SCRIPT, "--agent", "claude", "--target", cible, *argv],
        capture_output=True, text=True, env=env,
    )
    return r.returncode, r.stdout + r.stderr


def lire_settings(cible):
    with open(os.path.join(cible, "settings.json"), encoding="utf-8") as f:
        return json.load(f)


def commandes(settings):
    sortie = [h["command"] for groupes in settings.get("hooks", {}).values()
              for g in groupes for h in g.get("hooks", [])]
    if "statusLine" in settings:
        sortie.append(settings["statusLine"]["command"])
    return sortie


def main() -> int:
    if not os.path.exists(SCRIPT):
        print(f"  FAIL  install.py introuvable à {SCRIPT}")
        print("✗ 1 échec(s).")
        return 1

    echecs = 0

    def cas(nom, condition):
        nonlocal echecs
        print(f"  {'ok  ' if condition else 'FAIL'}  {nom}")
        if not condition:
            echecs += 1

    code, liste = lancer("/nulle-part", "--list")
    attendus = [l for l in liste.splitlines() if " -> " in l]
    cas("list : sort en 0 et rend des liens", code == 0 and len(attendus) > 0)

    with tempfile.TemporaryDirectory() as racine:
        autre_home = os.path.join(racine, "home")
        os.makedirs(autre_home)
        cible = os.path.join(racine, "cfg")

        # Cible vide : tout est absent, et rien n'est écrit.
        code, sortie = lancer(cible, "--check", home=autre_home)
        cas("vide : des écarts sortent en 1", code == 1)
        cas("vide : un ABSENT par lien attendu", sortie.count("ABSENT") == len(attendus))
        cas("vide : settings.json signalé", "settings.json" in sortie and "model" in sortie)
        cas("vide : --check n'écrit rien", not os.path.exists(cible))

        # --fix pose tout, puis --check est propre.
        code, _ = lancer(cible, "--fix", home=autre_home)
        cas("fix : sort en 0", code == 0)
        code, sortie = lancer(cible, "--check", home=autre_home)
        cas("fix puis check : aucun écart", code == 0 and "aucun écart" in sortie)

        regle = os.path.join(cible, "rules", "style.md")
        cas("fix : lien de règle vers le repo",
            os.readlink(regle) == os.path.join(REPO, "rules", "style.md"))
        cas("fix : lien de dossier pour hooks/tests",
            os.readlink(os.path.join(cible, "scripts", "hooks", "tests"))
            == os.path.join(REPO, "wrappers", "claude", "scripts", "hooks", "tests"))

        # Rendu des chemins : hors du home, absolu.
        cmds = commandes(lire_settings(cible))
        cas("rendu hors home : plus aucun ~/.claude",
            cmds and not any("~/.claude" in c for c in cmds))
        cas("rendu hors home : chemin absolu de la cible",
            any(f"{cible}/scripts/hooks/guard-bash-tooling.py" in c for c in cmds))

        # Lien redirigé.
        os.unlink(regle)
        os.symlink("/ailleurs/style.md", regle)
        code, sortie = lancer(cible, "--check", home=autre_home)
        cas("redirigé : signalé", code == 1 and "MAUVAISE CIBLE" in sortie and "style.md" in sortie)
        lancer(cible, "--fix", home=autre_home)
        cas("redirigé : réparé par --fix",
            os.readlink(regle) == os.path.join(REPO, "rules", "style.md"))

        # Orphelin : un lien vers le repo dont la source n'existe pas.
        orphelin = os.path.join(cible, "rules", "disparue.md")
        os.symlink(os.path.join(REPO, "rules", "disparue.md"), orphelin)
        code, sortie = lancer(cible, "--check", home=autre_home)
        cas("orphelin : signalé", code == 1 and "ORPHELIN" in sortie and "disparue.md" in sortie)
        lancer(cible, "--fix", home=autre_home)
        cas("orphelin : retiré par --fix", not os.path.lexists(orphelin))

        # Intrus : un vrai fichier dans le dossier des règles.
        intrus = os.path.join(cible, "rules", "a-la-main.md")
        with open(intrus, "w") as f:
            f.write("x\n")
        code, sortie = lancer(cible, "--check", home=autre_home)
        cas("intrus : signalé", code == 1 and "INTRUS" in sortie and "a-la-main.md" in sortie)
        code, _ = lancer(cible, "--fix", home=autre_home)
        cas("intrus : jamais supprimé, même en --fix", os.path.exists(intrus) and code == 1)
        os.unlink(intrus)

        # Pas un lien : un vrai fichier à la place d'un lien attendu.
        os.unlink(regle)
        with open(regle, "w") as f:
            f.write("copie\n")
        code, sortie = lancer(cible, "--fix", home=autre_home)
        cas("pas un lien : signalé et laissé", code == 1 and "PAS UN LIEN" in sortie
            and not os.path.islink(regle))
        os.unlink(regle)
        lancer(cible, "--fix", home=autre_home)

        # Dossier propre à la machine dans skills/.
        os.makedirs(os.path.join(cible, "skills", "synced", "x"))
        code, sortie = lancer(cible, "--check", home=autre_home)
        cas("skills/synced : ignoré", code == 0 and "synced" not in sortie)

        # Clés propres à la machine conservées.
        s = lire_settings(cible)
        s["voice"] = {"enabled": True}
        s["hooks"].setdefault("UserPromptSubmit", []).append(
            {"hooks": [{"type": "command", "command": "codegraph prompt-hook"}]})
        with open(os.path.join(cible, "settings.json"), "w") as f:
            json.dump(s, f)
        code, sortie = lancer(cible, "--check", home=autre_home)
        cas("machine : ses clés ne sont pas des écarts", code == 0)
        s["model"] = "haiku"
        with open(os.path.join(cible, "settings.json"), "w") as f:
            json.dump(s, f)
        lancer(cible, "--fix", home=autre_home)
        s = lire_settings(cible)
        cas("machine : clés et hooks conservés après --fix",
            s.get("voice") == {"enabled": True} and "codegraph prompt-hook" in commandes(s))
        cas("machine : clé du repo réappliquée", s.get("model") != "haiku")

        # Rendu des chemins : sous le home, écrit avec ~.
        home = os.path.join(racine, "h2")
        cible_home = os.path.join(home, ".claude")
        os.makedirs(home)
        lancer(cible_home, "--fix", home=home)
        cmds = commandes(lire_settings(cible_home))
        cas("rendu sous le home : ~/.claude/scripts gardé",
            any(c == "bash ~/.claude/scripts/hooks/guard-no-claude-in-commit.sh" for c in cmds))
        cas("rendu sous le home : aucun chemin absolu",
            not any(home in c for c in cmds))

        # --repo change la source des liens, pas le reste.
        code, sortie = lancer(cible, "--check", "--repo", "/autre/repo", home=autre_home)
        cas("--repo : les liens visent l'autre repo",
            code == 1 and "MAUVAISE CIBLE" in sortie and "/autre/repo/" in sortie)

    code, sortie = lancer("/nulle-part", "--list", "--agent", "opencode")
    cas("agent inconnu : refusé", code != 0)

    print(f"{'✓' if not echecs else '✗'} {echecs} échec(s).")
    return 1 if echecs else 0


if __name__ == "__main__":
    sys.exit(main())
