#!/usr/bin/env python3
"""Calibre les deux verdicts de `run-skill-evals.py` sur des cas fabriqués.

Ne joue aucune session et n'appelle aucun LLM : ne teste que la logique de verdict et
la validation du corpus, qui sont déterministes et donc les seules choses qu'une
batterie peut trancher.

Pourquoi cette batterie existe : un verdict se comporte exactement pareil qu'il soit
juste ou cassé — il rend « OK » dans les deux cas. Sans un positif et un négatif
exhibés à la main, rien ne distingue l'instrument qui mesure de l'instrument aveugle
(`rules/reasoning.md`, calibrage avant comptage).

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


def load(path: str, name: str):
    if not os.path.exists(path):
        sys.exit(f"{os.path.basename(path)} introuvable à {path}")
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# (nom, cas, skills ouverts, verdict attendu, fragment attendu dans la raison)
CASES_TRIGGER = [
    (
        "positif — le skill s'est ouvert",
        {"skill": "demo", "query": "q"},
        ["demo"],
        "OK",
        "s'est ouvert",
    ),
    (
        "positif — rien ne s'est ouvert",
        {"skill": "demo", "query": "q"},
        [],
        "FAIL",
        "aucun skill",
    ),
    (
        "positif — un frère a pris la main",
        {"skill": "demo", "query": "q"},
        ["autre"],
        "FAIL",
        "autre",
    ),
    (
        "négatif — le skill a pris la main quand même",
        {"skill": "demo", "query": "q", "expect_trigger": False},
        ["demo"],
        "FAIL",
        "non voulu",
    ),
    (
        "négatif — a cédé la main au frère",
        {"skill": "demo", "query": "q", "expect_trigger": False},
        ["autre"],
        "OK",
        "cédé la main",
    ),
    (
        "négatif — personne ne s'est ouvert",
        {"skill": "demo", "query": "q", "expect_trigger": False},
        [],
        "OK",
        "aucun autre skill",
    ),
]

SKILL_OK = """---
name: git-hygiene
description: Contrôle l'état d'un repo. Utiliser quand l'utilisateur veut le vérifier.
argument-hint: le repo visé
---

# Git hygiene

Skill fabriqué pour la batterie.

## Actions

Dérouler le flux. Ne lire que la prochaine action.

| Action | Fait |
| --- | --- |
| mesurer | mesurer l'état du repo |

## Transversal rules

- Ne rien committer.

## Test

Jouable seul.

| Cas | Preuve |
| --- | --- |
| le lint tourne | il rend zéro |
"""

RAPPORT_OK = """# Rapport d'audit

## Contrat

Le périmètre de la passe.

## Captures hors grille

Rien.
"""


def write(root: str, relative: str, content: str) -> None:
    path = os.path.join(root, relative)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(content)


# (nom, spec artifact, fichiers à poser, verdict attendu, fragment attendu)
CASES_ARTIFACT = [
    ("aucun artefact annoncé", None, {}, "N/A", "aucun artefact"),
    (
        "sections attendues présentes",
        {"path": "audits/*.md", "sections": ["Contrat", "Captures hors grille"]},
        {"audits/2026-01-01-audit.md": RAPPORT_OK},
        "OK",
        "porte ses 2 section",
    ),
    (
        "une section attendue manque",
        {"path": "audits/*.md", "sections": ["Contrat", "À réviser entre deux audits"]},
        {"audits/2026-01-01-audit.md": RAPPORT_OK},
        "FAIL",
        "À réviser entre deux audits",
    ),
    (
        "aucun fichier ne correspond au glob",
        {"path": "audits/*.md", "sections": ["Contrat"]},
        {},
        "FAIL",
        "aucun fichier",
    ),
    (
        "gabarit respecté",
        {"path": "skills/git-hygiene/SKILL.md", "template": "skill"},
        {"skills/git-hygiene/SKILL.md": SKILL_OK},
        "OK",
        "gabarit skill",
    ),
    (
        "gabarit non respecté",
        {"path": "skills/git-hygiene/SKILL.md", "template": "skill"},
        {
            "skills/git-hygiene/SKILL.md": SKILL_OK
            + "\n## Contrôle de sortie\n\n- l'artefact parse\n"
        },
        "FAIL",
        "Garde",
    ),
]

# (nom, contenu du corpus, fragment attendu du refus)
CASES_CORPUS = [
    (
        "champ hors format — un corpus resté à l'ancien schéma",
        [{"skill": "demo", "query": "q", "expected_behavior": ["…"]}],
        "hors format",
    ),
    (
        "champ setup — supprimé du format",
        [{"skill": "demo", "query": "q", "setup": ["rm -rf /"]}],
        "hors format",
    ),
    (
        "skill différent du dossier",
        [{"skill": "autre", "query": "q"}],
        "≠ dossier",
    ),
    (
        "query absente",
        [{"skill": "demo"}],
        "'query' absent",
    ),
    (
        "cas négatif porteur d'un artefact",
        [
            {
                "skill": "demo",
                "query": "q",
                "expect_trigger": False,
                "artifact": {"path": "x.md"},
            }
        ],
        "cas négatif ne produit rien",
    ),
    (
        "fixtures sans artefact",
        [{"skill": "demo", "query": "q", "files": ["fixtures/x.md"]}],
        "n'a de sens qu'avec 'artifact'",
    ),
    (
        "artefact sans path",
        [{"skill": "demo", "query": "q", "artifact": {"sections": ["X"]}}],
        "exige un 'path'",
    ),
    (
        "cas positif à query forcée par un slash",
        [{"skill": "demo", "query": "/demo publie le brouillon"}],
        "ne peut pas commencer par",
    ),
]


def check(name: str, got, expected, fragment: str | None, reason: str) -> int:
    problems = []
    if got != expected:
        problems.append(f"verdict {got!r} au lieu de {expected!r}")
    if fragment and fragment not in reason:
        problems.append(f"raison sans « {fragment} » : {reason}")
    if problems:
        print(f"ÉCHEC  {name}")
        for problem in problems:
            print(f"       {problem}")
        return 1
    print(f"OK     {name}")
    return 0


def main() -> int:
    runner = load(RUNNER, "runner")
    root = runner.derive_root()
    linter = runner.load_linter(root)
    templates = linter.load_templates(root)

    failures = 0

    for name, case, opened, expected, fragment in CASES_TRIGGER:
        verdict, reason = runner.trigger_verdict(case, opened)
        failures += check(name, verdict, expected, fragment, reason)

    for name, spec, files, expected, fragment in CASES_ARTIFACT:
        with tempfile.TemporaryDirectory() as tmp:
            for relative, content in files.items():
                write(tmp, relative, content)
            case = {"skill": "demo", "query": "q", "_label": name}
            if spec:
                case["artifact"] = spec
            verdict, reason = runner.artifact_verdict(case, tmp, linter, templates)
        failures += check(name, verdict, expected, fragment, reason)

    for name, corpus, fragment in CASES_CORPUS:
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "demo", "evals", "eval.json")
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as handle:
                json.dump(corpus, handle)
            try:
                runner.load_cases(tmp, [])
                verdict, reason = "ACCEPTÉ", ""
            except runner.CannotConclude as exc:
                verdict, reason = "REFUSÉ", str(exc)
        failures += check(name, verdict, "REFUSÉ", fragment, reason)

    # Arme positive de la validation : un corpus au format passe.
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "demo", "evals", "eval.json")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(
                [
                    {"skill": "demo", "id": "positif", "query": "q"},
                    {
                        "skill": "demo",
                        "id": "negatif",
                        "query": "q",
                        "expect_trigger": False,
                    },
                ],
                handle,
            )
        try:
            loaded = runner.load_cases(tmp, [])
            got = f"{len(loaded)} cas"
            reason = ""
        except runner.CannotConclude as exc:
            got, reason = "REFUSÉ", str(exc)
    failures += check("corpus au format — accepté", got, "2 cas", None, reason)

    total = len(CASES_TRIGGER) + len(CASES_ARTIFACT) + len(CASES_CORPUS) + 1
    print(f"\n{total - failures}/{total} cas passent.")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
