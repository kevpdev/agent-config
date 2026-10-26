#!/usr/bin/env python3
"""Calibre `tools/bench-report.py` sur un flux et un journal fabriqués.

Pourquoi cette batterie existe : un rapport qui ne voit rien rend « aucune fuite »
exactement comme un rapport qui voit juste. Chaque cas d'échec est exhibé à la main,
à côté du cas sain qu'il contredit (`rules/reasoning.md`, calibrage avant comptage).

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
SCRIPT = os.path.join(REPO, "tools", "bench-report.py")


def ecrire(chemin, texte):
    with open(chemin, "w", encoding="utf-8") as f:
        f.write(texte)


def flux(skills=("mermaid-craft", "aidd-dev:01-plan"), init=True, mcp=None, outils=()):
    lignes = []
    if init:
        lignes.append(json.dumps({
            "type": "system", "subtype": "init", "skills": list(skills),
            "plugins": [{"name": "aidd-vcs", "path": "/p/aidd-vcs", "version": "2.5.0"},
                        {"name": "cc-plugin-telemetry", "path": "builtin"}],
            "slash_commands": ["loop", "aidd-vcs:01-commit", "aidd-vcs:02-pull-request"],
            "mcp_servers": [{"name": n, "status": s} for n, s in (mcp or {}).items()],
            "tools": ["Read", "Bash", *outils],
        }))
    lignes.append(json.dumps({"type": "result", "result": "ok"}))
    return "\n".join(lignes) + "\n"


def reglages(commandes):
    return json.dumps({"hooks": {"PreToolUse": [{"matcher": "", "hooks": [
        {"type": "command", "command": c} for c in commandes]}]}})


def lancer(racine, texte_flux, texte_journal, banc, texte_reglages=None, mcp=()):
    f = os.path.join(racine, "run.jsonl")
    j = os.path.join(racine, "instructions.log")
    ecrire(f, texte_flux)
    ecrire(j, texte_journal)
    cmd = [sys.executable, SCRIPT, "--stream", f, "--log", j, "--bench", banc, "--repo", REPO]
    if texte_reglages is not None:
        s = os.path.join(racine, "settings.json")
        ecrire(s, texte_reglages)
        cmd += ["--settings", s]
    for nom in mcp:
        cmd += ["--mcp", nom]
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


def main() -> int:
    if not os.path.exists(SCRIPT):
        print(f"  FAIL  bench-report.py introuvable à {SCRIPT}")
        print("✗ 1 échec(s).")
        return 1

    echecs = 0

    def cas(nom, condition):
        nonlocal echecs
        print(f"  {'ok  ' if condition else 'FAIL'}  {nom}")
        if not condition:
            echecs += 1

    with tempfile.TemporaryDirectory() as racine:
        banc = os.path.join(racine, "bench")
        os.makedirs(os.path.join(banc, "rules"))
        # Une rule du banc est un lien vers le worktree, comme après install.py.
        lien = os.path.join(banc, "rules", "style.md")
        os.symlink(os.path.join(REPO, "rules", "style.md"), lien)
        # Un fichier propre au banc, sans lien vers le repo.
        propre = os.path.join(banc, "CLAUDE.md")
        ecrire(propre, "x\n")
        dehors = os.path.join(racine, "ailleurs", "fuite.md")
        os.makedirs(os.path.dirname(dehors))
        ecrire(dehors, "x\n")

        sain = f"2026-10-22 10:00:00\tsession_start\t{lien}\n2026-10-22 10:00:00\tsession_start\t{propre}\n"

        code, sortie = lancer(racine, flux(), sain, banc)
        cas("sain : sort en 0", code == 0)
        cas("sain : skills listés", "mermaid-craft" in sortie and "aidd-dev:01-plan" in sortie)
        cas("sain : rule liée classée worktree", "worktree" in sortie and "style.md" in sortie)
        cas("sain : fichier propre classé banc", "banc" in sortie and "CLAUDE.md" in sortie)
        cas("sain : aucune fuite annoncée", "HORS BANC" not in sortie)
        cas("sain : plugin listé avec sa version et ses skills", "aidd-vcs@2.5.0  2 skills" in sortie)
        cas("sain : plugin intégré ignoré", "cc-plugin-telemetry" not in sortie)

        code, sortie = lancer(racine, flux(init=False), sain, banc)
        cas("sans init : sort en 1", code == 1 and "init" in sortie)

        code, sortie = lancer(racine, flux(), "", banc)
        cas("journal vide : sort en 1", code == 1 and "vide" in sortie)

        erreur = sain + "2026-10-22 10:00:01\tLOG-ERREUR\tentrée illisible: x\n"
        code, sortie = lancer(racine, flux(), erreur, banc)
        cas("LOG-ERREUR : sort en 1", code == 1 and "LOG-ERREUR" in sortie)

        fuite = sain + f"2026-10-22 10:00:02\tsession_start\t{dehors}\n"
        code, sortie = lancer(racine, flux(), fuite, banc)
        cas("fuite : marquée HORS BANC", "HORS BANC" in sortie and "fuite.md" in sortie)
        cas("fuite : sort en 1", code == 1)

        # Un lien du banc qui sort du repo et du banc est une fuite, même rangé dans le banc.
        detour = os.path.join(banc, "rules", "detour.md")
        os.symlink(dehors, detour)
        code, sortie = lancer(racine, flux(), sain + f"x\tsession_start\t{detour}\n", banc)
        cas("lien sortant : marqué HORS BANC", code == 1 and "HORS BANC" in sortie and "detour.md" in sortie)

        # Les hooks : chaque commande du settings.json du banc mène à un fichier du worktree,
        # par un lien du banc comme après install.py.
        os.makedirs(os.path.join(banc, "scripts"))
        hook_lie = os.path.join(banc, "scripts", "garde.py")
        os.symlink(os.path.join(REPO, "tools", "install.py"), hook_lie)
        code, sortie = lancer(racine, flux(), sain, banc, reglages([f"python3 {hook_lie} --notify"]))
        cas("hook résolu : sort en 0 et listé", code == 0 and "Hooks (1)" in sortie and "garde.py" in sortie)

        absent = os.path.join(banc, "scripts", "absent.py")
        code, sortie = lancer(racine, flux(), sain, banc, reglages([f"python3 {absent}"]))
        cas("hook absent : sort en 1", code == 1 and "hook introuvable" in sortie and "absent.py" in sortie)

        hook_sortant = os.path.join(banc, "scripts", "sortant.sh")
        os.symlink(dehors, hook_sortant)
        code, sortie = lancer(racine, flux(), sain, banc, reglages([f"bash {hook_sortant}"]))
        cas("hook hors worktree : sort en 1", code == 1 and "hook introuvable" in sortie and "sortant.sh" in sortie)

        # Un hook posé par l'installateur d'un serveur : une commande du PATH, sans chemin.
        code, sortie = lancer(racine, flux(), sain, banc, reglages(["python3 -c pass"]))
        cas("hook de la machine sur le PATH : sort en 0", code == 0 and "machine  python3 -c pass" in sortie)
        code, sortie = lancer(racine, flux(), sain, banc, reglages(["commande-qui-nexiste-pas prompt-hook"]))
        cas("hook sans chemin hors PATH : sort en 1", code == 1 and "hook introuvable" in sortie)

        # Un serveur MCP exigé par --mcp : connecté, avec au moins un outil à son préfixe.
        outil = "mcp__codegraph__codegraph_explore"
        code, sortie = lancer(racine, flux(mcp={"codegraph": "connected"}, outils=[outil]), sain, banc, mcp=["codegraph"])
        cas("mcp connecté avec ses outils : sort en 0", code == 0 and "codegraph  connected  1 outils" in sortie)
        code, sortie = lancer(racine, flux(), sain, banc, mcp=["codegraph"])
        cas("mcp absent de l'init : sort en 1", code == 1 and "serveur MCP codegraph : absent" in sortie)
        code, sortie = lancer(racine, flux(mcp={"codegraph": "failed"}, outils=[outil]), sain, banc, mcp=["codegraph"])
        cas("mcp en échec : sort en 1", code == 1 and "failed, pas connected" in sortie)
        code, sortie = lancer(racine, flux(mcp={"codegraph": "connected"}), sain, banc, mcp=["codegraph"])
        cas("mcp connecté sans outil : sort en 1", code == 1 and "aucun outil mcp__codegraph__" in sortie)

    print(f"{'✓' if not echecs else '✗'} {echecs} échec(s).")
    return 1 if echecs else 0


if __name__ == "__main__":
    sys.exit(main())
