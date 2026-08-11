#!/usr/bin/env python3
"""Calibre les verdicts déterministes de `run-skill-evals.py` sur des cas fabriqués.

Ne joue aucune session et n'appelle aucun LLM : ne teste que la logique de verdict et
la validation des scénarios, qui sont déterministes et donc les seules choses qu'une
batterie peut trancher.

Pourquoi cette batterie existe : un verdict de déclenchement se comporte exactement
pareil qu'il soit juste ou cassé — il rend « OK » dans les deux cas. Sans un positif
et un négatif exhibés à la main, rien ne distingue l'instrument qui mesure de
l'instrument aveugle (`rules/reasoning.md`, calibrage avant comptage).

Sortie : 0 si tout passe, 1 si un cas échoue.
"""

from __future__ import annotations

import importlib.util
import json
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
RUNNER = os.path.join(os.path.dirname(HERE), "run-skill-evals.py")


def load_runner():
    if not os.path.exists(RUNNER):
        sys.exit(f"run-skill-evals.py introuvable à {RUNNER}")
    spec = importlib.util.spec_from_file_location("runner", RUNNER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


CASES_TRIGGER = [
    # (nom, scénario, sortie de session, registre des skills ouverts, verdict attendu)
    (
        "positif — marqueurs présents",
        {"_skill": "code-reviewer", "trigger_markers": ["Bloquants", "Contexte assumé"]},
        "## Contexte assumé\nprod\n## Bloquants\nAucun",
        [],
        "OK",
    ),
    (
        "positif — un marqueur manque et rien au registre",
        {"_skill": "code-reviewer", "trigger_markers": ["Bloquants", "Contexte assumé"]},
        "## Bloquants\nAucun",
        [],
        "FAIL",
    ),
    (
        # Le cas mesuré le 2026-08-11 sur brain-expert : chargé pour de bon, mais sa
        # signature n'apparaît pas dans la sortie. Le seul marqueur rendait FAIL.
        "positif — marqueur absent mais registre positif : faux négatif rattrapé",
        {"_skill": "brain-expert", "trigger_markers": ["Problème cognitif"]},
        "Voici comment alléger ce flux, étape par étape.",
        ["brain-expert"],
        "OK",
    ),
    (
        "positif — registre nommant un AUTRE skill ne vaut pas déclenchement",
        {"_skill": "brain-expert", "trigger_markers": ["Problème cognitif"]},
        "Voici comment alléger ce flux.",
        ["frontend-expert"],
        "FAIL",
    ),
    (
        "négatif — le frère a pris la main (abstention réelle)",
        {"_skill": "code-reviewer", "expect_trigger": False, "trigger_markers": ["Bloquants"]},
        "Cette question porte sur la sécurité, va voir security-reviewer.",
        ["security-reviewer"],
        "OK",
    ),
    (
        "négatif — rien ne s'est chargé : vert, mais rien n'a été mesuré",
        {"_skill": "code-reviewer", "expect_trigger": False, "trigger_markers": ["Bloquants"]},
        "Voici mon avis sur la sécurité de ce endpoint.",
        [],
        "OK",
    ),
    (
        "négatif — le skill a pris la main, vu au registre malgré une sortie muette",
        {"_skill": "code-reviewer", "expect_trigger": False, "trigger_markers": ["Bloquants"]},
        "Rien qui ressemble à mon gabarit.",
        ["code-reviewer"],
        "FAIL",
    ),
    (
        "négatif — le skill a pris la main (marqueur, sans registre)",
        {"_skill": "code-reviewer", "expect_trigger": False, "trigger_markers": ["Bloquants"]},
        "## Bloquants\n- rien à signaler",
        [],
        "FAIL",
    ),
    (
        "négatif — un seul marqueur sur deux suffit à trahir le déclenchement",
        {"_skill": "code-reviewer", "expect_trigger": False, "trigger_markers": ["Bloquants", "Suggestions"]},
        "## Suggestions\n- extraire la méthode",
        [],
        "FAIL",
    ),
    (
        "sans marqueur ni registre — non mesurable, jamais un succès",
        {"_skill": "code-reviewer"},
        "n'importe quoi",
        [],
        "N/A",
    ),
]


def scenario_file(tmp: str, skill: str, scenarios: list) -> str:
    """Écrit un `evals/eval.json` jetable et rend la racine de skills à charger."""
    root = os.path.join(tmp, "skills")
    evals = os.path.join(root, skill, "evals")
    os.makedirs(evals, exist_ok=True)
    with open(os.path.join(evals, "eval.json"), "w", encoding="utf-8") as fh:
        json.dump(scenarios, fh)
    return root


BASE = {"query": "q", "expected_behavior": ["c"]}

CASES_LOAD = [
    # (nom, scénario, doit lever CannotConclude)
    ("scénario positif minimal", {**BASE}, False),
    ("négatif complet", {**BASE, "expect_trigger": False, "trigger_markers": ["M"]}, False),
    (
        "négatif SANS marqueur — l'absence n'est pas mesurable, doit refuser",
        {**BASE, "expect_trigger": False},
        True,
    ),
    (
        "négatif avec marqueurs vides — même défaut, doit refuser",
        {**BASE, "expect_trigger": False, "trigger_markers": []},
        True,
    ),
    (
        "expect_trigger non booléen — doit refuser",
        {**BASE, "expect_trigger": "false", "trigger_markers": ["M"]},
        True,
    ),
]


def main() -> int:
    runner = load_runner()
    failures = 0

    print("Verdicts de déclenchement")
    for name, scenario, output, loaded, expected in CASES_TRIGGER:
        got, why = runner.trigger_verdict(scenario, output, loaded)
        ok = got == expected
        failures += not ok
        print(f"  {'OK  ' if ok else 'FAIL'} {name} : attendu {expected}, obtenu {got} — {why}")

    print("\nValidation des scénarios au chargement")
    with tempfile.TemporaryDirectory() as tmp:
        for index, (name, scenario, must_raise) in enumerate(CASES_LOAD):
            root = scenario_file(os.path.join(tmp, str(index)), "faux-skill", [scenario])
            try:
                runner.load_scenarios(root, [])
                raised = False
                why = "chargé sans erreur"
            except runner.CannotConclude as exc:
                raised = True
                why = str(exc).split(" : ", 1)[-1]
            ok = raised == must_raise
            failures += not ok
            verb = "refus attendu" if must_raise else "acceptation attendue"
            print(f"  {'OK  ' if ok else 'FAIL'} {name} : {verb}, {'refusé' if raised else 'accepté'} — {why}")

    print("\nIncompatibilité avec --force")
    negative = {**BASE, "expect_trigger": False, "trigger_markers": ["M"]}
    positive = {**BASE, "trigger_markers": ["M"]}
    # Le filtre vit dans main() ; on rejoue son prédicat pour vérifier qu'un scénario
    # négatif est bien écarté sans que son auteur ait eu à poser aussi `skip_force`.
    def tests_abstention(s: dict) -> bool:
        return bool(s.get("skip_force")) or not s.get("expect_trigger", True)

    for name, scenario, expected in [
        ("négatif écarté du mode forcé sans skip_force explicite", negative, True),
        ("positif conservé en mode forcé", positive, False),
        ("skip_force explicite toujours honoré", {**positive, "skip_force": True}, True),
    ]:
        got = tests_abstention(scenario)
        ok = got == expected
        failures += not ok
        print(f"  {'OK  ' if ok else 'FAIL'} {name} : attendu {expected}, obtenu {got}")

    total = len(CASES_TRIGGER) + len(CASES_LOAD) + 3
    print(f"\n{total - failures}/{total} cas au vert")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
