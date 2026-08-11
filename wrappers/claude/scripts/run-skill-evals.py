#!/usr/bin/env python3
"""Joue les scénarios `evals/eval.json` des skills et rend un tableau de verdicts.

Spécifique à Claude Code : lancer une session neuve passe par `claude -p`.
Les scénarios eux-mêmes restent portables — ce fichier est le seul à connaître l'agent.

Deux verdicts par scénario, dont un seul coûte un appel LLM :

- DÉCLENCHEMENT — déterministe. Les `trigger_markers` du scénario apparaissent-ils
  dans le message final, le fil de la session ou les fichiers qu'elle a écrits ?
  Chercher dans le message final seul rend des faux négatifs dès que le skill produit
  un artefact : les marqueurs vivent dans le rapport, pas dans le chat (mesuré le
  2026-08-10, 3 faux FAIL sur 4). Sans marqueur déclaré, le verdict est N/A.

  Un scénario **négatif** porte `expect_trigger: false` : il vérifie que le skill NE
  part PAS sur une requête destinée à un frère, et le verdict s'inverse — marqueurs
  absents = OK, présents = FAIL. Pourquoi ce champ existe : sans lui, un scénario qui
  réussit sort rouge, et un test qu'on apprend à ignorer ne protège plus rien. Il exige
  `trigger_markers` (l'absence de marqueur ne se distingue pas de l'absence de mesure)
  et il est incompatible avec `--force`, qui garantit le chargement qu'on teste.
- COMPORTEMENT — un juge LLM confronte aux `expected_behavior` le message final PLUS
  les fichiers écrits par la session (le livrable d'un skill à artefact est le
  fichier). Rendu `N/I` quand le déclenchement a échoué : la sortie vient alors d'une
  session sans le skill, et un critère raté n'y est pas imputable. Le scénario reste
  rouge par son déclenchement — `N/I` ne blanchit rien, il empêche d'accuser le
  mauvais artefact.

Un scénario qui suppose un état du repo (grille salie, rapport déjà présent) le
fabrique via son champ `setup` : des commandes shell jouées dans le worktree avant la
session. Affirmer l'état dans la query sans le fabriquer teste le modèle face à une
prémisse fausse, pas le skill.

Échec fermé : tout ce qui empêche de conclure rend 2 (dépendance absente, racine
douteuse, scénario illisible, fixture manquante, sortie vide, juge muet, repo réel
modifié pendant la passe). Un défaut mesuré rend 1. Tout au vert rend 0.

Isolation : chaque scénario joue dans un git worktree jetable du repo — ses écritures
y tombent et s'archivent, jamais dans le repo réel. Le worktree n'empêche pas un accès
par chemin absolu : l'état du repo réel est comparé avant/après la passe, et toute
dérive rend 2. Les scénarios sont indépendants, donc joués en parallèle (`--jobs`).
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed

DEFAULT_RUN_TIMEOUT_S = 900
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


def derive_root() -> str:
    """Racine dérivée de l'emplacement du script, jamais un chemin en dur."""
    here = os.path.dirname(os.path.realpath(__file__))
    root = os.path.abspath(os.path.join(here, "..", "..", ".."))
    for marker in ("skills", "rules"):
        if not os.path.isdir(os.path.join(root, marker)):
            raise CannotConclude(
                f"racine dérivée invalide : {root} ne porte pas '{marker}/'"
            )
    return root


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
            setup = scenario.get("setup", [])
            if not isinstance(setup, list) or any(not isinstance(c, str) for c in setup):
                raise CannotConclude(
                    f"{path}[{index}] : 'setup' doit être une liste de commandes shell"
                )
            expect = scenario.get("expect_trigger", True)
            if not isinstance(expect, bool):
                raise CannotConclude(
                    f"{path}[{index}] : 'expect_trigger' doit être un booléen"
                )
            # Échec fermé : sans marqueur, « absent » ne se distingue pas de « non
            # mesuré », et le scénario rendrait OK sans avoir rien vérifié.
            if not expect and not scenario.get("trigger_markers"):
                raise CannotConclude(
                    f"{path}[{index}] : 'expect_trigger: false' exige 'trigger_markers' — "
                    "sans marqueur, l'absence de déclenchement n'est pas mesurable"
                )
            scenario["_skill"] = name
            scenario["_eval_dir"] = os.path.dirname(path)
            scenario["_label"] = name if len(data) == 1 else f"{name}#{index}"
            scenarios.append(scenario)
    return scenarios


def git_status(root: str) -> str:
    proc = subprocess.run(
        ["git", "-C", root, "status", "--porcelain"],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise CannotConclude(f"git status impossible sur {root} : {proc.stderr.strip()}")
    return proc.stdout


def stage_worktree(scenario: dict, out_dir: str, repo_root: str) -> str:
    """Worktree jetable du repo par scénario : la session y joue, ses écritures y tombent."""
    workdir = os.path.join(out_dir, scenario["_label"].replace("#", "-"), "repo")
    os.makedirs(os.path.dirname(workdir), exist_ok=True)
    proc = subprocess.run(
        ["git", "-C", repo_root, "worktree", "add", "--detach", workdir, "HEAD"],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise CannotConclude(
            f"{scenario['_label']} : worktree impossible : {proc.stderr.strip()}"
        )
    for relative in scenario.get("files", []):
        source = os.path.join(scenario["_eval_dir"], relative)
        if not os.path.isfile(source):
            raise CannotConclude(
                f"{scenario['_label']} : fixture absente → {source}"
            )
        shutil.copy2(source, os.path.join(workdir, os.path.basename(relative)))
    for command in scenario.get("setup", []):
        proc = subprocess.run(
            ["bash", "-c", command], cwd=workdir, capture_output=True, text=True
        )
        if proc.returncode != 0:
            raise CannotConclude(
                f"{scenario['_label']} : setup en échec « {command} » : {proc.stderr.strip()}"
            )
    return workdir


def git_diff(root: str) -> str:
    return subprocess.run(
        ["git", "-C", root, "diff"], capture_output=True, text=True
    ).stdout


def teardown_worktree(
    repo_root: str, workdir: str, staged: list[str], staged_diff: str
) -> tuple[list[str], str]:
    """Archive ce que la SESSION a écrit dans le worktree, puis le détruit.

    `staged`/`staged_diff` sont l'état du worktree juste après fixtures et setup :
    ce que le scénario a fabriqué ne s'impute pas à la session — sans cette
    soustraction, le juge accuserait la session d'avoir sali ce que le setup a sali.
    Rend (chemins écrits par la session, contenu écrit : diffs étiquetés + fichiers créés).
    """
    scen_dir = os.path.dirname(workdir)
    wrote_all = git_status(workdir).splitlines()
    wrote = [line for line in wrote_all if line not in set(staged)]
    written = []
    if staged_diff.strip():
        written.append(
            "--- état fabriqué par le setup du scénario, déjà présent AVANT la session ---\n"
            + staged_diff
        )
    if wrote_all:
        diff = git_diff(workdir)
        if diff.strip() and diff != staged_diff:
            written.append(
                "--- diff du worktree en fin de session (l'état setup ci-dessus inclus) ---\n"
                + diff
            )
        with open(os.path.join(scen_dir, "worktree-writes.txt"), "w", encoding="utf-8") as fh:
            fh.write("\n".join(wrote_all) + "\n\n" + diff)
        for line in wrote:
            if line.startswith("??"):
                relative = line[3:].strip()
                source = os.path.join(workdir, relative)
                target = os.path.join(scen_dir, "artefacts", relative)
                if os.path.isfile(source):
                    os.makedirs(os.path.dirname(target), exist_ok=True)
                    shutil.copy2(source, target)
                    with open(source, encoding="utf-8", errors="replace") as fh:
                        written.append(f"--- fichier créé par la session : {relative} ---\n{fh.read()}")
    proc = subprocess.run(
        ["git", "-C", repo_root, "worktree", "remove", "--force", workdir],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise CannotConclude(
            f"worktree non détruit ({workdir}) : {proc.stderr.strip()}"
        )
    return wrote, "\n\n".join(written)


# --- exécution -------------------------------------------------------------


def run_session(claude: str, scenario: dict, workdir: str, model: str, force: bool, timeout: int):
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
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        raise CannotConclude(
            f"{scenario['_label']} : session au-delà de {timeout}s"
        ) from exc

    stream_path = os.path.join(os.path.dirname(workdir), "run.jsonl")
    with open(stream_path, "w", encoding="utf-8") as fh:
        fh.write(proc.stdout)

    output, transcript, tools, cost = None, [], [], 0.0
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
                elif block.get("type") == "text":
                    transcript.append(block.get("text", ""))
        elif event.get("type") == "result":
            output = event.get("result")
            cost = event.get("total_cost_usd") or 0.0
    if not output or not str(output).strip():
        raise CannotConclude(
            f"{scenario['_label']} : sortie vide (rc={proc.returncode}) → {stream_path}"
        )
    return str(output), "\n".join(transcript), tools, cost


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
    present = [m for m in markers if m.casefold() in haystack]
    missing = [m for m in markers if m.casefold() not in haystack]
    if not scenario.get("expect_trigger", True):
        # Scénario négatif : le succès est l'absence. Un seul marqueur présent
        # suffit à prouver que le skill a pris la main au lieu de la céder.
        if present:
            return "FAIL", (
                "déclenchement non voulu — marqueur présent : " + ", ".join(present)
            )
        return "OK", f"aucun des {len(markers)} marqueur(s) — le skill a cédé la main"
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


def play_scenario(claude: str, scenario: dict, out_dir: str, repo_root: str, args):
    """Joue un scénario de bout en bout dans son worktree. Rend (row, coût, défaut)."""
    workdir = stage_worktree(scenario, out_dir, repo_root)
    # Instantané post-setup : ce que le scénario a fabriqué ne s'impute pas à la session.
    staged = git_status(workdir).splitlines()
    staged_diff = git_diff(workdir)
    try:
        output, transcript, tools, cost = run_session(
            claude, scenario, workdir, args.model, args.force, args.timeout
        )
    finally:
        wrote, written = teardown_worktree(repo_root, workdir, staged, staged_diff)

    # Les marqueurs vivent où le skill s'exprime : chat final, fil de session, fichiers écrits.
    haystack = "\n\n".join(filter(None, (output, transcript, written)))
    trigger, trigger_why = trigger_verdict(scenario, haystack)
    if args.force:
        trigger, trigger_why = "N/A", "mode forcé"
    tools_state, tools_why = tools_verdict(scenario, tools)
    criteria = scenario["expected_behavior"]
    judged = output
    if written:
        judged += f"\n\n=== FICHIERS ÉCRITS PAR LA SESSION ===\n{written}"
    verdicts, judge_cost = judge(claude, criteria, judged, args.judge_model)
    cost += judge_cost

    failed = [v for v in verdicts if not v["pass"]]
    # Déclenchement en échec sur un scénario POSITIF : la sortie vient d'une session
    # où le skill n'a jamais été chargé. Ce qui est mesuré est le comportement du
    # modèle nu, pas celui du skill — l'imputer au skill ferait réécrire un artefact
    # que la mesure n'a pas touché. On le déclare non interprétable.
    # Sur un scénario NÉGATIF, l'inverse : un déclenchement en échec veut dire que le
    # skill s'est bien chargé, donc ce qu'il a produit lui est imputable et se juge.
    negative = not scenario.get("expect_trigger", True)
    interpretable = trigger != "FAIL" or negative
    if not interpretable:
        behavior = "N/I"
    else:
        behavior = "OK" if not failed else f"FAIL {len(failed)}/{len(criteria)}"

    details = []
    if trigger == "FAIL":
        details.append(f"déclenchement : {trigger_why}")
    if tools_state == "FAIL":
        details.append(f"outils : {tools_why}")
    if not interpretable:
        details.append(
            f"comportement non interprétable : le skill ne s'est pas chargé, "
            f"les {len(failed)} critère(s) en échec sur {len(criteria)} ne lui sont pas imputables"
        )
    for verdict in failed if interpretable else []:
        index = verdict["criterion_index"]
        criterion = criteria[index - 1] if 1 <= index <= len(criteria) else "?"
        details.append(f"critère {index} « {criterion} » → {verdict['reason']}")
    if wrote:
        details.append(
            f"worktree : {len(wrote)} chemin(s) écrit(s), archivés sous les artefacts du scénario"
        )

    defect = "FAIL" in (trigger, tools_state) or (interpretable and bool(failed))
    row = {
        "label": scenario["_label"],
        "trigger": trigger,
        "tools": tools_state,
        "behavior": behavior,
        "details": details,
    }
    return row, cost, defect


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--skill", action="append", default=[], help="restreindre à ce skill (répétable)")
    parser.add_argument("--model", default="opus", help="modèle de la session jouée (défaut: opus — mesuré le 2026-08-06 : 7/8 déclenchements sur opus contre 0/8 sur sonnet, à skills et contexte identiques)")
    parser.add_argument("--judge-model", default="haiku", help="modèle du juge (défaut: haiku)")
    parser.add_argument("--force", action="store_true", help="préfixer la query par /<skill> pour isoler le comportement du déclenchement")
    parser.add_argument("--self-test", action="store_true", help="calibrer le juge et sortir, sans jouer aucun scénario")
    parser.add_argument("--out", help="répertoire des artefacts (défaut: temporaire)")
    parser.add_argument("--timeout", type=int, default=DEFAULT_RUN_TIMEOUT_S, help=f"plafond d'une session jouée, en secondes (défaut: {DEFAULT_RUN_TIMEOUT_S})")
    parser.add_argument("--jobs", type=int, default=4, help="scénarios joués en parallèle (défaut: 4) — indépendants, chacun dans son worktree")
    args = parser.parse_args()

    try:
        claude = require_tools()
        if args.self_test:
            return self_test(claude, args.judge_model)

        repo_root = derive_root()
        scenarios = load_scenarios(os.path.join(repo_root, "skills"), args.skill)
        out_dir = args.out or tempfile.mkdtemp(prefix="skill-evals-")
        os.makedirs(out_dir, exist_ok=True)

        if args.force:
            # Un scénario qui teste l'abstention n'a pas de sens forcé : le forcer
            # mesurerait l'inverse de ce qu'il affirme. `expect_trigger: false` est
            # une abstention par définition — le déduire, plutôt que d'exiger aussi
            # `skip_force` : deux champs pour un même fait divergent au premier edit.
            def tests_abstention(s: dict) -> bool:
                return bool(s.get("skip_force")) or not s.get("expect_trigger", True)

            skipped = [s["_label"] for s in scenarios if tests_abstention(s)]
            scenarios = [s for s in scenarios if not tests_abstention(s)]
            if not scenarios:
                raise CannotConclude(
                    "tous les scénarios retenus testent l'abstention — rien à jouer en mode forcé"
                )

        print(f"{len(scenarios)} scénario(s) — session {args.model}, juge {args.judge_model}")
        if args.force:
            print("Mode forcé : le déclenchement n'est pas mesuré, seul le comportement l'est.")
            if skipped:
                print(f"Écarté(s) car testant l'abstention : {', '.join(skipped)}")

        # Instantané du repo réel : le worktree ne bloque pas un accès par chemin
        # absolu, la comparaison avant/après rend cette fuite visible et bloquante.
        real_before = git_status(repo_root)

        rows, spent, defects, errors = [], 0.0, 0, []
        with ThreadPoolExecutor(max_workers=max(1, min(args.jobs, len(scenarios)))) as pool:
            futures = {
                pool.submit(play_scenario, claude, s, out_dir, repo_root, args): s["_label"]
                for s in scenarios
            }
            for future in as_completed(futures):
                label = futures[future]
                try:
                    row, cost, defect = future.result()
                except CannotConclude as exc:
                    errors.append(str(exc))
                    print(f"  ✗ {label} : {exc}", flush=True)
                    continue
                print(f"  ✓ {label}", flush=True)
                rows.append(row)
                spent += cost
                defects += 1 if defect else 0

        if rows:
            rows.sort(key=lambda r: r["label"])
            report(rows, out_dir, spent)
            print(f"{len(rows) - defects} scénario(s) au vert sur {len(rows)}")

        real_after = git_status(repo_root)
        if real_after != real_before:
            delta = set(real_after.splitlines()) ^ set(real_before.splitlines())
            raise CannotConclude(
                "le repo réel a été modifié pendant la passe (accès hors worktree) :\n  "
                + "\n  ".join(sorted(delta))
            )
        if errors:
            raise CannotConclude("; ".join(errors))
        return 1 if defects else 0

    except CannotConclude as exc:
        print(f"ARRÊT — impossible de conclure : {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
