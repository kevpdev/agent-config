#!/usr/bin/env python3
"""Joue les scénarios `evals/eval.json` des skills et rend un tableau de verdicts.

Spécifique à Claude Code : lancer une session neuve passe par `claude -p`.
Les scénarios eux-mêmes restent portables — ce fichier est le seul à connaître l'agent.

Deux verdicts par scénario, dont un seul coûte un appel LLM :

- DÉCLENCHEMENT — déterministe. Les `trigger_markers` du scénario apparaissent-ils
  dans la sortie ? Aucun appel `Skill` n'étant observable dans le flux (mesuré le
  2026-08-06, y compris sur une invocation forcée), la forme de la sortie est le seul
  signal disponible. Sans marqueur déclaré, le verdict est N/A, jamais un succès.
- COMPORTEMENT — un juge LLM confronte la sortie aux `expected_behavior`.

Échec fermé : tout ce qui empêche de conclure rend 2 (dépendance absente, racine
douteuse, scénario illisible, fixture manquante, sortie vide, juge muet). Un défaut
mesuré rend 1. Tout au vert rend 0.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile

RUN_TIMEOUT_S = 600
JUDGE_TIMEOUT_S = 300
WRITE_TOOLS = "Edit Write NotebookEdit"

JUDGE_SCHEMA = {
    "type": "object",
    "properties": {
        "verdicts": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "criterion_index": {"type": "integer"},
                    "pass": {"type": "boolean"},
                    "reason": {"type": "string"},
                },
                "required": ["criterion_index", "pass", "reason"],
                "additionalProperties": False,
            },
        }
    },
    "required": ["verdicts"],
    "additionalProperties": False,
}

JUDGE_PREAMBLE = (
    "Tu juges la sortie d'un skill contre des critères attendus.\n"
    "Pour chaque critère, dis s'il est satisfait par la sortie telle qu'elle est.\n"
    "Juge le fond, jamais la formulation. Un critère satisfait avec d'autres mots est\n"
    "satisfait : n'exige aucune tournure, aucun intitulé de section, aucun mot-clé.\n"
    "En revanche, une exigence de fond absente de la sortie est un échec, pas un doute —\n"
    "ne l'accorde pas au bénéfice de l'intention.\n"
    "Ne juge pas la qualité du code discuté, seulement la conformité de la sortie.\n"
)


class CannotConclude(Exception):
    """Le mécanisme ne peut pas rendre de verdict — se traduit par exit 2."""


# --- préparation -----------------------------------------------------------


def derive_skills_dir() -> str:
    """Racine dérivée de l'emplacement du script, jamais un chemin en dur."""
    here = os.path.dirname(os.path.realpath(__file__))
    root = os.path.abspath(os.path.join(here, "..", "..", ".."))
    for marker in ("skills", "rules"):
        if not os.path.isdir(os.path.join(root, marker)):
            raise CannotConclude(
                f"racine dérivée invalide : {root} ne porte pas '{marker}/'"
            )
    return os.path.join(root, "skills")


def require_tools() -> str:
    claude = shutil.which("claude")
    if not claude:
        raise CannotConclude("`claude` introuvable dans le PATH")
    return claude


def load_scenarios(skills_dir: str, wanted: list[str]) -> list[dict]:
    """Lit chaque evals/eval.json et rend les scénarios à plat."""
    names = sorted(
        d
        for d in os.listdir(skills_dir)
        if os.path.isfile(os.path.join(skills_dir, d, "evals", "eval.json"))
    )
    if wanted:
        unknown = [w for w in wanted if w not in names]
        if unknown:
            raise CannotConclude(f"aucun evals/eval.json pour : {', '.join(unknown)}")
        names = [n for n in names if n in wanted]
    if not names:
        raise CannotConclude(f"aucun evals/eval.json sous {skills_dir}")

    scenarios = []
    for name in names:
        path = os.path.join(skills_dir, name, "evals", "eval.json")
        try:
            with open(path, encoding="utf-8") as fh:
                data = json.load(fh)
        except (OSError, json.JSONDecodeError) as exc:
            raise CannotConclude(f"{path} illisible : {exc}") from exc
        if not isinstance(data, list) or not data:
            raise CannotConclude(f"{path} n'est pas une liste non vide de scénarios")
        for index, scenario in enumerate(data):
            for field in ("query", "expected_behavior"):
                if not scenario.get(field):
                    raise CannotConclude(f"{path}[{index}] : champ '{field}' absent")
            scenario["_skill"] = name
            scenario["_eval_dir"] = os.path.dirname(path)
            scenario["_label"] = name if len(data) == 1 else f"{name}#{index}"
            scenarios.append(scenario)
    return scenarios


def stage_workdir(scenario: dict, out_dir: str) -> str:
    """Copie les fixtures dans un répertoire de travail isolé du repo."""
    workdir = os.path.join(out_dir, scenario["_label"].replace("#", "-"), "workdir")
    os.makedirs(workdir, exist_ok=True)
    for relative in scenario.get("files", []):
        source = os.path.join(scenario["_eval_dir"], relative)
        if not os.path.isfile(source):
            raise CannotConclude(
                f"{scenario['_label']} : fixture absente → {source}"
            )
        shutil.copy2(source, os.path.join(workdir, os.path.basename(relative)))
    return workdir


# --- exécution -------------------------------------------------------------


def run_session(claude: str, scenario: dict, workdir: str, model: str, force: bool):
    """Lance une session neuve et rend (texte de sortie, outils appelés, coût)."""
    prompt = scenario["query"]
    if force:
        prompt = f"/{scenario['_skill']} {prompt}"
    cmd = [
        claude,
        "-p",
        prompt,
        "--model",
        model,
        "--output-format",
        "stream-json",
        "--verbose",
        "--no-session-persistence",
        "--disallowedTools",
        WRITE_TOOLS,
        "--permission-mode",
        "bypassPermissions",
    ]
    try:
        proc = subprocess.run(
            cmd,
            cwd=workdir,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            timeout=RUN_TIMEOUT_S,
        )
    except subprocess.TimeoutExpired as exc:
        raise CannotConclude(
            f"{scenario['_label']} : session au-delà de {RUN_TIMEOUT_S}s"
        ) from exc

    stream_path = os.path.join(os.path.dirname(workdir), "run.jsonl")
    with open(stream_path, "w", encoding="utf-8") as fh:
        fh.write(proc.stdout)

    output, tools, cost = None, [], 0.0
    for line in proc.stdout.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("type") == "assistant":
            for block in event.get("message", {}).get("content", []):
                if block.get("type") == "tool_use":
                    tools.append(block.get("name", "?"))
        elif event.get("type") == "result":
            output = event.get("result")
            cost = event.get("total_cost_usd") or 0.0
    if not output or not str(output).strip():
        raise CannotConclude(
            f"{scenario['_label']} : sortie vide (rc={proc.returncode}) → {stream_path}"
        )
    return str(output), tools, cost


def judge(claude: str, criteria: list[str], output: str, model: str):
    """Confronte une sortie à des critères. Rend (verdicts, coût)."""
    numbered = "\n".join(f"{i + 1}. {c}" for i, c in enumerate(criteria))
    prompt = (
        f"{JUDGE_PREAMBLE}\n=== CRITÈRES\n{numbered}\n\n=== SORTIE À JUGER\n{output}\n"
    )
    cmd = [
        claude,
        "-p",
        prompt,
        "--model",
        model,
        "--tools",
        "",
        "--no-session-persistence",
        "--output-format",
        "json",
        "--json-schema",
        json.dumps(JUDGE_SCHEMA),
    ]
    try:
        proc = subprocess.run(
            cmd,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            timeout=JUDGE_TIMEOUT_S,
        )
    except subprocess.TimeoutExpired as exc:
        raise CannotConclude(f"juge au-delà de {JUDGE_TIMEOUT_S}s") from exc

    raw = proc.stdout
    start = raw.find("{")
    if start < 0:
        raise CannotConclude(f"juge sans JSON exploitable : {raw[:200]!r}")
    try:
        payload = json.loads(raw[start:])
    except json.JSONDecodeError as exc:
        raise CannotConclude(f"juge illisible : {exc}") from exc

    structured = payload.get("structured_output")
    if not isinstance(structured, dict) or "verdicts" not in structured:
        raise CannotConclude("juge sans sortie structurée — verdict impossible")
    verdicts = structured["verdicts"]
    if len(verdicts) != len(criteria):
        raise CannotConclude(
            f"juge : {len(verdicts)} verdicts pour {len(criteria)} critères"
        )
    return verdicts, payload.get("total_cost_usd") or 0.0


# --- verdicts déterministes ------------------------------------------------


def trigger_verdict(scenario: dict, output: str):
    markers = scenario.get("trigger_markers") or []
    if not markers:
        return "N/A", "aucun marqueur déclaré — non mesurable"
    haystack = output.casefold()
    missing = [m for m in markers if m.casefold() not in haystack]
    if missing:
        return "FAIL", "marqueur absent : " + ", ".join(missing)
    return "OK", f"{len(markers)} marqueur(s) présent(s)"


def tools_verdict(scenario: dict, tools: list[str]):
    forbidden = scenario.get("forbidden_tools") or []
    if not forbidden:
        return "N/A", "aucun outil interdit déclaré"
    hits = sorted({t for t in tools for f in forbidden if f.casefold() in t.casefold()})
    if hits:
        return "FAIL", "outil interdit appelé : " + ", ".join(hits)
    return "OK", "aucun outil interdit appelé"


# --- calibration -----------------------------------------------------------

SELF_TEST_CRITERIA = [
    "La sortie cite au moins un emplacement précis dans le code, fichier et ligne",
    "La sortie déclare les hypothèses ou le contexte qu'elle assume",
    "La sortie dit si le code peut être mergé",
]

# Critères de fond, jamais de forme : le juge doit reconnaître un critère satisfait
# avec d'autres mots. Les vecteurs attendus sont fixés avant lecture des réponses.
SELF_TEST_CASES = [
    (
        "conforme",
        "Ça peut partir en merge. Je pars du principe qu'on est sur une branche de dev "
        "et que la revue ne couvre que le diff. Un point mineur traîne en Foo.java:42.\n",
        [True, True, True],
    ),
    (
        "muet",
        "Je n'ai pas d'avis particulier sur ce code.\n",
        [False, False, False],
    ),
    (
        "partiel",
        "Ça peut partir en merge. Un point mineur traîne en Foo.java:42.\n",
        [True, False, True],
    ),
]


def self_test(claude: str, model: str) -> int:
    """Calibre le juge sur trois sorties fabriquées à la main.

    Un juge qui répond toujours PASS échoue sur « vide » et « partiel ».
    Un juge qui répond toujours FAIL échoue sur « conforme ». Sans cette passe,
    un juge aveugle est indiscernable d'un juge intact.
    """
    print(f"Calibration du juge ({model}) sur 3 sorties fabriquées\n")
    failures, spent = 0, 0.0
    for name, output, expected in SELF_TEST_CASES:
        verdicts, cost = judge(claude, SELF_TEST_CRITERIA, output, model)
        spent += cost
        got = [bool(v["pass"]) for v in sorted(verdicts, key=lambda v: v["criterion_index"])]
        ok = got == expected
        failures += 0 if ok else 1
        print(f"  {'OK  ' if ok else 'FAIL'} cas « {name} » : attendu {expected}, obtenu {got}")
        if not ok:
            for verdict in verdicts:
                print(f"        {verdict['criterion_index']}. {verdict['reason']}")
    print(f"\nCoût : {spent:.3f} $")
    if failures:
        print(f"\n{failures} cas de calibration en échec — le juge n'est pas fiable, ne pas s'appuyer sur une passe.")
        return 1
    print("\nJuge calibré : il distingue conforme, vide et partiel.")
    return 0


# --- rapport ---------------------------------------------------------------


def report(rows: list[dict], out_dir: str, spent: float) -> None:
    width = max([len(r["label"]) for r in rows] + [5])
    print(f"\n{'skill'.ljust(width)}  déclenché  outils  comportement")
    print("-" * (width + 34))
    for row in rows:
        print(
            f"{row['label'].ljust(width)}  "
            f"{row['trigger'].ljust(9)}  "
            f"{row['tools'].ljust(6)}  "
            f"{row['behavior']}"
        )
    print()
    for row in rows:
        if row["details"]:
            print(f"{row['label']} :")
            for line in row["details"]:
                print(f"  - {line}")
    print(f"\nCoût : {spent:.2f} $   Artefacts : {out_dir}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--skill", action="append", default=[], help="restreindre à ce skill (répétable)")
    parser.add_argument("--model", default="opus", help="modèle de la session jouée (défaut: opus — mesuré le 2026-08-06 : 7/8 déclenchements sur opus contre 0/8 sur sonnet, à skills et contexte identiques)")
    parser.add_argument("--judge-model", default="haiku", help="modèle du juge (défaut: haiku)")
    parser.add_argument("--force", action="store_true", help="préfixer la query par /<skill> pour isoler le comportement du déclenchement")
    parser.add_argument("--self-test", action="store_true", help="calibrer le juge et sortir, sans jouer aucun scénario")
    parser.add_argument("--out", help="répertoire des artefacts (défaut: temporaire)")
    args = parser.parse_args()

    try:
        claude = require_tools()
        if args.self_test:
            return self_test(claude, args.judge_model)

        skills_dir = derive_skills_dir()
        scenarios = load_scenarios(skills_dir, args.skill)
        out_dir = args.out or tempfile.mkdtemp(prefix="skill-evals-")
        os.makedirs(out_dir, exist_ok=True)

        if args.force:
            # Un scénario qui teste l'abstention n'a pas de sens forcé : le forcer
            # mesurerait l'inverse de ce qu'il affirme.
            skipped = [s["_label"] for s in scenarios if s.get("skip_force")]
            scenarios = [s for s in scenarios if not s.get("skip_force")]
            if not scenarios:
                raise CannotConclude("tous les scénarios retenus portent skip_force")

        print(f"{len(scenarios)} scénario(s) — session {args.model}, juge {args.judge_model}")
        if args.force:
            print("Mode forcé : le déclenchement n'est pas mesuré, seul le comportement l'est.")
            if skipped:
                print(f"Écarté(s) car testant l'abstention : {', '.join(skipped)}")

        rows, spent, defects = [], 0.0, 0
        for scenario in scenarios:
            label = scenario["_label"]
            print(f"  … {label}", flush=True)
            workdir = stage_workdir(scenario, out_dir)
            output, tools, cost = run_session(claude, scenario, workdir, args.model, args.force)
            spent += cost

            trigger, trigger_why = trigger_verdict(scenario, output)
            if args.force:
                trigger, trigger_why = "N/A", "mode forcé"
            tools_state, tools_why = tools_verdict(scenario, tools)

            criteria = scenario["expected_behavior"]
            verdicts, judge_cost = judge(claude, criteria, output, args.judge_model)
            spent += judge_cost
            failed = [v for v in verdicts if not v["pass"]]
            behavior = "OK" if not failed else f"FAIL {len(failed)}/{len(criteria)}"

            details = []
            if trigger == "FAIL":
                details.append(f"déclenchement : {trigger_why}")
            if tools_state == "FAIL":
                details.append(f"outils : {tools_why}")
            for verdict in failed:
                index = verdict["criterion_index"]
                criterion = criteria[index - 1] if 1 <= index <= len(criteria) else "?"
                details.append(f"critère {index} « {criterion} » → {verdict['reason']}")

            if "FAIL" in (trigger, tools_state) or failed:
                defects += 1
            rows.append(
                {
                    "label": label,
                    "trigger": trigger,
                    "tools": tools_state,
                    "behavior": behavior,
                    "details": details,
                }
            )

        report(rows, out_dir, spent)
        print(f"{len(rows) - defects} scénario(s) au vert sur {len(rows)}")
        return 1 if defects else 0

    except CannotConclude as exc:
        print(f"ARRÊT — impossible de conclure : {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
