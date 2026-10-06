#!/usr/bin/env python3
"""Vérifie, ou applique, les clés du wrapper dans `~/.claude/settings.json`.

POURQUOI CE SCRIPT
    `~/.claude/settings.json` ne peut pas être un lien vers le wrapper : Claude Code y
    écrit lui-même (permissions accordées, plugins installés, voice, `/config`). Un lien
    ferait entrer ces écritures machine dans le repo, ou serait remplacé par un fichier
    normal sans signal. C'est ce qui s'est produit, constaté le 2026-10-06 : le wrapper
    déclarait `"model": "sonnet"`, le fichier vivant n'avait aucune clé `model`, et la
    session tournait sur le défaut du compte.

    Le repo ne possède donc que ses clés. Toute clé du wrapper, sauf `EXCLUES`, doit
    valoir dans le fichier vivant ce qu'elle vaut dans le wrapper. Les autres clés du
    fichier vivant appartiennent à la machine et ne sont jamais touchées.

RÈGLES DE FUSION
    scalaire ou liste  la valeur du repo l'emporte
    dict               fusion récursive, les clés propres à la machine restent
    hooks              par événement, chaque (matcher, command) du repo doit exister dans
                       un groupe de même matcher. Un hook de la machine n'est jamais retiré.

ÉCHOUE FERMÉ : tout écart rend un code de sortie non nul (cf. rules/workflow.md).

Usage
    python3 sync-settings.py          vérifie, n'écrit rien
    python3 sync-settings.py --fix    applique, après sauvegarde en settings.json.bak

CLAUDE_SETTINGS_FILE vise un fichier de test au lieu de ~/.claude/settings.json, pour
que le script soit calibrable sans toucher la config vivante.
"""

from __future__ import annotations

import copy
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(os.path.dirname(HERE), "settings.json")

# Lue en OU entre les couches de settings (commit 6d2146d) : un false écrit au niveau
# user ferait revenir l'avertissement du mode bypass dans tous les repos. Dans le
# wrapper, c'est une sentinelle de diff, pas une valeur à appliquer.
EXCLUES = {"skipDangerousModePermissionPrompt"}


def cible_par_defaut() -> str:
    return os.environ.get("CLAUDE_SETTINGS_FILE") or os.path.expanduser("~/.claude/settings.json")


def charger(chemin: str, absent_ok: bool = False) -> dict:
    if absent_ok and not os.path.exists(chemin):
        return {}
    try:
        with open(chemin, encoding="utf-8") as f:
            donnees = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        raise SystemExit(f"sync-settings — lecture impossible de {chemin} : {e}")
    if not isinstance(donnees, dict):
        raise SystemExit(f"sync-settings — {chemin} n'est pas un objet JSON.")
    return donnees


def _court(valeur) -> str:
    return "absent" if valeur is _ABSENT else json.dumps(valeur, ensure_ascii=False)


_ABSENT = object()


def _fusionner_dict(repo: dict, machine: dict, chemin: str, ecarts: list) -> dict:
    resultat = dict(machine)
    for cle, valeur in repo.items():
        actuel = machine.get(cle, _ABSENT)
        sous_chemin = f"{chemin}.{cle}" if chemin else cle
        if isinstance(valeur, dict) and isinstance(actuel, dict):
            resultat[cle] = _fusionner_dict(valeur, actuel, sous_chemin, ecarts)
        elif actuel is _ABSENT or actuel != valeur:
            ecarts.append(f"{sous_chemin} : {_court(actuel)} → {_court(valeur)}")
            resultat[cle] = copy.deepcopy(valeur)
    return resultat


def _fusionner_hooks(repo: dict, machine: dict, ecarts: list) -> dict:
    resultat = copy.deepcopy(machine) if isinstance(machine, dict) else {}
    for evenement, groupes_repo in repo.items():
        groupes = resultat.setdefault(evenement, [])
        for groupe in groupes_repo:
            matcher = groupe.get("matcher")
            presentes = {
                h.get("command")
                for g in groupes
                if g.get("matcher") == matcher
                for h in g.get("hooks", [])
            }
            manquants = [h for h in groupe.get("hooks", []) if h.get("command") not in presentes]
            if not manquants:
                continue
            for h in manquants:
                ecarts.append(f"hooks.{evenement} [{matcher!r}] : absent → {h.get('command')}")
            nouveau = {k: v for k, v in groupe.items() if k != "hooks"}
            nouveau["hooks"] = copy.deepcopy(manquants)
            groupes.append(nouveau)
    return resultat


def fusionner(repo: dict, machine: dict) -> tuple[dict, list[str]]:
    """Rend le fichier machine après application des clés du repo, et la liste des écarts."""
    ecarts: list[str] = []
    possedees = {k: v for k, v in repo.items() if k not in EXCLUES}
    hooks = possedees.pop("hooks", None)
    resultat = _fusionner_dict(possedees, machine, "", ecarts)
    if hooks is not None:
        resultat["hooks"] = _fusionner_hooks(hooks, machine.get("hooks", {}), ecarts)
    return resultat, ecarts


def ecrire(chemin: str, donnees: dict) -> None:
    if os.path.exists(chemin):
        shutil.copy2(chemin, chemin + ".bak")
    dossier = os.path.dirname(os.path.abspath(chemin))
    fd, tmp = tempfile.mkstemp(dir=dossier, prefix=".settings-", suffix=".json")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(donnees, f, indent=2, ensure_ascii=False)
            f.write("\n")
        os.replace(tmp, chemin)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def main(argv: list[str]) -> int:
    fix = "--fix" in argv
    cible = cible_par_defaut()
    repo = charger(SOURCE)
    machine = charger(cible, absent_ok=True)
    resultat, ecarts = fusionner(repo, machine)

    if not ecarts:
        print(f"✓ {cible} porte toutes les clés du wrapper, aucun écart.")
        return 0

    if fix:
        ecrire(cible, resultat)
        for e in ecarts:
            print(f"  appliqué  {e}")
        print(f"✓ {len(ecarts)} écart(s) appliqué(s), ancienne version dans {cible}.bak.")
        return 0

    for e in ecarts:
        print(f"  ÉCART  {e}", file=sys.stderr)
    print(f"✗ {len(ecarts)} écart(s). Relancer avec --fix les applique.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
