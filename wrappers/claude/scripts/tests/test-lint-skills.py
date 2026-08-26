#!/usr/bin/env python3
"""Calibre `lint-skills.py` sur des skills fabriqués, un conforme et un par défaut.

N'ouvre aucun skill réel et n'appelle aucun LLM : ne teste que les sept vérifications,
qui sont déterministes et donc les seules choses qu'une batterie peut trancher.

Pourquoi cette batterie existe : un lint se comporte exactement pareil qu'il mesure
ou qu'il soit aveugle — il rend « conforme » dans les deux cas. Sans un positif et un
négatif par vérification exhibés à la main, rien ne distingue les deux
(`rules/reasoning.md`, calibrage avant comptage).

Pourquoi des skills fabriqués et pas les skills réels : un instrument calibré sur le
corpus qu'il juge ne peut pas dire si un « zéro défaut » vient du corpus ou de
l'instrument. Les gabarits, eux, sont les vrais — si l'un change, la batterie casse.

Sortie : 0 si tous les cas passent, 1 si un cas échoue.
"""

from __future__ import annotations

import importlib.util
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
LINTER = os.path.join(os.path.dirname(HERE), "lint-skills.py")


def load_linter():
    if not os.path.exists(LINTER):
        sys.exit(f"lint-skills.py introuvable à {LINTER}")
    spec = importlib.util.spec_from_file_location("linter", LINTER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


SKILL_OK = """---
name: demo
description: Fait la démo du lint. Utiliser quand l'utilisateur veut calibrer le lint.
argument-hint: la démo voulue
---

# Demo

Skill fabriqué pour la batterie du lint, jamais installé.

```mermaid
flowchart TD
  intention --> faire
```

## Actions

Dérouler le flux. Ne lire que la prochaine action.

| Action | Fait |
| --- | --- |
| faire | faire la démo |

## Transversal rules

- Ne rien inventer.

## Test

Jouable seul.

| Cas | Preuve |
| --- | --- |
| le lint tourne sur ce skill | il rend zéro défaut |
"""

ACTION_OK = """# 01 - Faire

Fait la démo.

## Output

Une ligne de sortie sur la console.

## Process

1. **Faire.** Faire la démo.

## Test

| Cas | Preuve |
| --- | --- |
| l'action tourne | elle rend une ligne |
"""


def swap(text: str, old: str, new: str) -> str:
    if old not in text:
        sys.exit(f"fixture cassée : « {old} » absent du modèle")
    return text.replace(old, new, 1)


MANUEL = swap(
    SKILL_OK,
    "argument-hint: la démo voulue",
    "argument-hint: la démo voulue\ndisable-model-invocation: true",
)

# (nom du cas, SKILL.md, action, règles attendues, fragment attendu, [evals/eval.json])
# Le sixième membre est optionnel : sans lui, le skill fabriqué n'a pas d'`evals/`.
CASES = [
    (
        "positif — tout conforme",
        SKILL_OK,
        ACTION_OK,
        set(),
        None,
    ),
    (
        "frontmatter — YAML invalide",
        swap(SKILL_OK, "argument-hint: la démo voulue", "argument-hint: [la démo"),
        ACTION_OK,
        {"frontmatter"},
        "YAML invalide",
    ),
    (
        "frontmatter — argument-hint absent",
        swap(SKILL_OK, "argument-hint: la démo voulue\n", ""),
        ACTION_OK,
        {"frontmatter"},
        "`argument-hint`",
    ),
    (
        "name — différent du dossier",
        swap(SKILL_OK, "name: demo", "name: autre-chose"),
        ACTION_OK,
        {"name"},
        "nom du dossier",
    ),
    (
        "description — au-delà du plafond",
        swap(SKILL_OK, "Fait la démo du lint.", "Fait la démo du lint. " + "mot " * 500),
        ACTION_OK,
        {"description"},
        "plafond 1536",
    ),
    (
        "sections — une section hors gabarit dans une action",
        SKILL_OK,
        ACTION_OK + "\n## Contrôle de sortie\n\n- l'artefact parse\n",
        {"sections"},
        "`**Garde.**` du `## Process`",
    ),
    (
        "sections — un home nommé que le gabarit du fichier n'a pas",
        SKILL_OK + "\n## Contexte\n\n- la racine du vault\n",
        ACTION_OK,
        {"sections"},
        "Ranger par la NATURE",
    ),
    (
        "sections — le même home, valide dans une action",
        SKILL_OK,
        ACTION_OK + "\n## Contexte\n\n- la racine du vault\n",
        {"sections"},
        "`## Input`",
    ),
    (
        "sections — une obligatoire manquante",
        swap(SKILL_OK, "## Transversal rules\n\n- Ne rien inventer.\n", ""),
        ACTION_OK,
        {"sections"},
        "manque (obligatoire)",
    ),
    (
        "sections — hors de l'ordre du gabarit",
        swap(
            SKILL_OK,
            "## Transversal rules\n\n- Ne rien inventer.\n\n## Test\n\nJouable seul.\n",
            "## Test\n\nJouable seul.\n\n## Transversal rules\n\n- Ne rien inventer.\n",
        ),
        ACTION_OK,
        {"sections"},
        "ordre du gabarit",
    ),
    (
        "sections — les deux alternatives présentes",
        swap(
            SKILL_OK,
            "## Transversal rules",
            "## Process\n\n1. **Faire.** Faire la démo.\n\n## Transversal rules",
        ),
        ACTION_OK,
        {"sections"},
        "s'excluent",
    ),
    (
        "invocation — un skill manuel qui promet un déclenchement",
        MANUEL,
        ACTION_OK,
        {"invocation"},
        "un skill manuel ne promet aucun déclenchement",
    ),
    (
        "invocation — un skill manuel avec un cas d'éval positif",
        swap(MANUEL, "Utiliser quand l'utilisateur veut calibrer le lint.", "S'appelle par /demo."),
        ACTION_OK,
        {"invocation"},
        "cas positif(s) sur un skill manuel",
        '[{"skill": "demo", "id": "positif-demo", "query": "fais la démo"}]',
    ),
    (
        "invocation — le champ absent laisse les phrases déclencheuses tranquilles",
        SKILL_OK,
        ACTION_OK,
        set(),
        None,
        '[{"skill": "demo", "id": "positif-demo", "query": "fais la démo"}]',
    ),
    (
        "placeholder — un chevron du gabarit resté",
        SKILL_OK,
        swap(ACTION_OK, "Une ligne de sortie sur la console.", "<Une ligne de sortie.>"),
        {"placeholder"},
        "placeholder du gabarit resté",
    ),
    (
        "placeholder — la notation en backticks ne compte pas",
        SKILL_OK,
        swap(
            ACTION_OK,
            "Une ligne de sortie sur la console.",
            "Une ligne écrite dans `skills/<nom>/SKILL.md`.",
        ),
        set(),
        None,
    ),
    (
        "liens — un lien relatif mort",
        SKILL_OK,
        swap(
            ACTION_OK,
            "1. **Faire.** Faire la démo.",
            "1. **Faire.** Lire [la convention](../references/absente.md).",
        ),
        {"liens"},
        "lien relatif mort",
    ),
]


def build(tmp: str, skill_md: str, action_md: str, eval_json: str | None = None) -> str:
    skill_dir = os.path.join(tmp, "demo")
    os.makedirs(os.path.join(skill_dir, "actions"), exist_ok=True)
    with open(os.path.join(skill_dir, "SKILL.md"), "w", encoding="utf-8") as handle:
        handle.write(skill_md)
    with open(
        os.path.join(skill_dir, "actions", "01-faire.md"), "w", encoding="utf-8"
    ) as handle:
        handle.write(action_md)
    if eval_json is not None:
        os.makedirs(os.path.join(skill_dir, "evals"), exist_ok=True)
        with open(
            os.path.join(skill_dir, "evals", "eval.json"), "w", encoding="utf-8"
        ) as handle:
            handle.write(eval_json)
    return skill_dir


def main() -> int:
    linter = load_linter()
    templates = linter.load_templates(linter.derive_root())

    failures = 0
    for case in CASES:
        name, skill_md, action_md, expected, fragment = case[:5]
        eval_json = case[5] if len(case) > 5 else None
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = build(tmp, skill_md, action_md, eval_json)
            defects = linter.lint_skill(skill_dir, templates)
        rules = {defect.rule for defect in defects}
        messages = " | ".join(defect.message for defect in defects)

        problems = []
        if rules != expected:
            problems.append(f"règles {sorted(rules)} au lieu de {sorted(expected)}")
        if fragment and fragment not in messages:
            problems.append(f"message sans « {fragment} »")
        if not expected and defects:
            problems.append(f"défauts inattendus : {messages}")

        if problems:
            failures += 1
            print(f"ÉCHEC  {name}")
            for problem in problems:
                print(f"       {problem}")
            if messages:
                print(f"       messages rendus : {messages}")
        else:
            print(f"OK     {name}")

    print(f"\n{len(CASES) - failures}/{len(CASES)} cas passent.")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
