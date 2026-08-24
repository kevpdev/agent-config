#!/usr/bin/env python3
"""Joue les cas `evals/eval.json` des skills et rend un tableau de deux verdicts.

Spécifique à Claude Code : ouvrir une session neuve passe par `claude -p`. Les cas
eux-mêmes restent portables — ce fichier est le seul à connaître l'agent.

Deux verdicts, aucun juge LLM :

- **DÉCLENCHEMENT** — le registre de la session. Un appel à l'outil `Skill` nomme le
  skill ouvert, c'est une preuve directe et binaire. Sur un cas négatif le verdict
  s'inverse : le skill ne doit pas y figurer.
- **ARTEFACT** — le fichier annoncé par `artifact` existe, et porte les `##` de son
  gabarit ou les sections nommées. Verdict par script, sans interprétation.

**Le champ `artifact` choisit le mode, et c'est mécanique.** Sans lui, le cas tourne
`--tools "Skill"` : le skill peut s'ouvrir et rien d'autre ne peut s'exécuter, donc un
skill à effet de bord se teste sans risque et sans worktree. Avec lui, le cas tourne
outils ouverts dans un worktree jetable du repo, seul moyen de constater un fichier.

**Pourquoi `Skill` reste autorisé et pas zéro outil** : mesuré le 2026-08-24, couper
tous les outils coupe aussi celui qui ouvre un skill, et tous les cas positifs
rendraient rouge. L'instrument mesurerait alors sa propre censure.

**Ce qui est refusé, et ne reviendra pas** : l'ordre des outils appelés (fragile, il
punit les chemins valides que personne n'avait prévus), une regexp sur de la prose
(casse à la première variation valide), le style et le ton (ne se décompose pas en
pass/fail). C'est de la relecture humaine.

Échec fermé : tout ce qui empêche de conclure rend 2 (dépendance absente, racine
douteuse, cas illisible, skill absent du listing de la session, sortie vide, repo réel
modifié pendant la passe). Un défaut mesuré rend 1. Tout au vert rend 0.

Décidé par `audits/2026-08-24-cadrage-refonte-skills-cible.md`, sections 3 et 4.
"""

from __future__ import annotations

import argparse
import glob as globlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed

DEFAULT_RUN_TIMEOUT_S = 900
CASE_FIELDS = {"skill", "id", "query", "expect_trigger", "artifact", "files"}


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


def load_linter(root: str):
    """Le lint est importé, pas recopié : il possède déjà la liste des sections."""
    path = os.path.join(root, "wrappers", "claude", "scripts", "lint-skills.py")
    if not os.path.isfile(path):
        raise CannotConclude(f"lint-skills.py introuvable à {path}")
    spec = importlib.util.spec_from_file_location("linter", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_cases(skills_dir: str, wanted: list[str]) -> list[dict]:
    """Lit chaque evals/eval.json et rend les cas à plat, validés."""
    names = sorted(
        name
        for name in os.listdir(skills_dir)
        if os.path.isfile(os.path.join(skills_dir, name, "evals", "eval.json"))
    )
    if wanted:
        unknown = [w for w in wanted if w not in names]
        if unknown:
            raise CannotConclude(f"aucun evals/eval.json pour : {', '.join(unknown)}")
        names = [n for n in names if n in wanted]
    if not names:
        raise CannotConclude(f"aucun evals/eval.json sous {skills_dir}")

    cases = []
    for name in names:
        path = os.path.join(skills_dir, name, "evals", "eval.json")
        try:
            with open(path, encoding="utf-8") as handle:
                data = json.load(handle)
        except (OSError, json.JSONDecodeError) as exc:
            raise CannotConclude(f"{path} illisible : {exc}") from exc
        if not isinstance(data, list) or not data:
            raise CannotConclude(f"{path} n'est pas une liste non vide de cas")
        for index, case in enumerate(data):
            where = f"{path}[{index}]"
            # Échec fermé sur un champ inconnu : un corpus resté à l'ancien format
            # se jouerait sinon en silence, ses assertions perdues sans un mot.
            extra = sorted(set(case) - CASE_FIELDS)
            if extra:
                raise CannotConclude(
                    f"{where} : champ(s) hors format → {', '.join(extra)}. "
                    f"Le format ne porte que {', '.join(sorted(CASE_FIELDS))}"
                )
            for field in ("skill", "query"):
                if not case.get(field):
                    raise CannotConclude(f"{where} : champ '{field}' absent")
            if case["skill"] != name:
                raise CannotConclude(
                    f"{where} : `skill: {case['skill']}` ≠ dossier `{name}`"
                )
            expect = case.get("expect_trigger", True)
            if not isinstance(expect, bool):
                raise CannotConclude(f"{where} : 'expect_trigger' doit être un booléen")
            artifact = case.get("artifact")
            if artifact is not None:
                if not isinstance(artifact, dict) or not artifact.get("path"):
                    raise CannotConclude(f"{where} : 'artifact' exige un 'path'")
                if not expect:
                    raise CannotConclude(
                        f"{where} : un cas négatif ne produit rien, il ne peut pas "
                        "porter 'artifact'"
                    )
            # Mesuré deux fois le 2026-08-21 puis deux fois le 2026-08-24 : `claude -p`
            # sur un `/<nom>` n'ouvre pas le skill, ni appel à l'outil ni ligne du
            # SKILL.md au transcript. Un cas positif préfixé mesurerait le harnais.
            if expect and case["query"].lstrip().startswith("/"):
                raise CannotConclude(
                    f"{where} : une `query` de cas positif ne peut pas commencer par "
                    "`/` — une invocation forcée n'ouvre pas le skill sous `claude -p`, "
                    "le cas sortirait rouge sans avoir mesuré le skill"
                )
            if case.get("files") and artifact is None:
                raise CannotConclude(
                    f"{where} : 'files' n'a de sens qu'avec 'artifact' — sans lui les "
                    "outils sont coupés et la session ne peut rien lire"
                )
            case["_eval_dir"] = os.path.dirname(path)
            case["_label"] = case.get("id") or (
                name if len(data) == 1 else f"{name}#{index}"
            )
            cases.append(case)
    return cases


# --- isolation -------------------------------------------------------------


def git_status(root: str) -> str:
    proc = subprocess.run(
        ["git", "-C", root, "status", "--porcelain"], capture_output=True, text=True
    )
    if proc.returncode != 0:
        raise CannotConclude(f"git status impossible sur {root} : {proc.stderr.strip()}")
    return proc.stdout


def stage_workdir(case: dict, out_dir: str, repo_root: str) -> str:
    """Le répertoire où la session joue.

    Un cas à artefact reçoit un worktree jetable du repo : ses écritures y tombent.
    Un cas de déclenchement reçoit un répertoire vide, ses outils étant coupés — pas
    de worktree à monter pour une session qui ne peut rien écrire.
    """
    workdir = os.path.join(out_dir, case["_label"], "repo")
    os.makedirs(os.path.dirname(workdir), exist_ok=True)
    if not case.get("artifact"):
        os.makedirs(workdir, exist_ok=True)
        return workdir

    proc = subprocess.run(
        ["git", "-C", repo_root, "worktree", "add", "--detach", workdir, "HEAD"],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise CannotConclude(
            f"{case['_label']} : worktree impossible : {proc.stderr.strip()}"
        )
    for relative in case.get("files", []):
        source = os.path.join(case["_eval_dir"], relative)
        if not os.path.isfile(source):
            raise CannotConclude(f"{case['_label']} : fixture absente → {source}")
        shutil.copy2(source, os.path.join(workdir, os.path.basename(relative)))
    return workdir


def teardown_workdir(case: dict, repo_root: str, workdir: str) -> list[str]:
    """Rend les chemins écrits par la session, puis détruit le worktree."""
    if not case.get("artifact"):
        return []
    wrote = git_status(workdir).splitlines()
    proc = subprocess.run(
        ["git", "-C", repo_root, "worktree", "remove", "--force", workdir],
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        raise CannotConclude(
            f"worktree non détruit ({workdir}) : {proc.stderr.strip()}"
        )
    return wrote


# --- exécution -------------------------------------------------------------


def run_session(claude: str, case: dict, workdir: str, model: str, timeout: int):
    """Lance une session neuve. Rend (skills ouverts, skills disponibles, coût)."""
    cmd = [
        claude,
        "-p",
        case["query"],
        "--model",
        model,
        "--output-format",
        "stream-json",
        "--verbose",
        "--no-session-persistence",
        "--permission-mode",
        "bypassPermissions",
    ]
    if not case.get("artifact"):
        cmd += ["--tools", "Skill"]
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
            f"{case['_label']} : session au-delà de {timeout}s"
        ) from exc

    stream_path = os.path.join(os.path.dirname(workdir), "run.jsonl")
    with open(stream_path, "w", encoding="utf-8") as handle:
        handle.write(proc.stdout)

    opened, available, result, cost = [], None, None, 0.0
    for line in proc.stdout.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        kind = event.get("type")
        if kind == "system" and event.get("subtype") == "init":
            listed = event.get("skills")
            if isinstance(listed, list):
                available = [str(item) for item in listed]
        elif kind == "assistant":
            for block in event.get("message", {}).get("content", []):
                if block.get("type") == "tool_use" and block.get("name") == "Skill":
                    name = block.get("input", {}).get("skill")
                    if name:
                        opened.append(str(name))
        elif kind == "result":
            result = event.get("result")
            cost = event.get("total_cost_usd") or 0.0

    if not result or not str(result).strip():
        raise CannotConclude(
            f"{case['_label']} : sortie vide (rc={proc.returncode}) → {stream_path}"
        )
    # Calibrage avant comptage : un skill absent du listing de la session ne peut pas
    # s'ouvrir, et son cas rendrait rouge sans avoir rien mesuré.
    if available is not None and case["skill"] not in available:
        raise CannotConclude(
            f"{case['_label']} : `{case['skill']}` absent des {len(available)} skills "
            f"listés par la session → {stream_path}"
        )
    return opened, available, cost


# --- verdicts --------------------------------------------------------------


def trigger_verdict(case: dict, opened: list[str]):
    """Verdict binaire, lu au registre. Aucun marqueur, aucune forme de sortie."""
    skill = case["skill"]
    took_over = skill in opened
    others = sorted({name for name in opened if name != skill})

    if not case.get("expect_trigger", True):
        if took_over:
            return "FAIL", "déclenchement non voulu, le skill a pris la main"
        if others:
            return "OK", "a cédé la main à " + ", ".join(others)
        return "OK", "n'a pas pris la main, et aucun autre skill ne s'est ouvert"
    if took_over:
        return "OK", "le skill s'est ouvert"
    if others:
        return "FAIL", "un autre skill a pris la main : " + ", ".join(others)
    return "FAIL", "aucun skill ne s'est ouvert"


def artifact_verdict(case: dict, workdir: str, linter, templates):
    """Le fichier annoncé existe, et porte les sections attendues."""
    spec = case.get("artifact")
    if not spec:
        return "N/A", "aucun artefact annoncé"

    matches = sorted(globlib.glob(os.path.join(workdir, spec["path"])))
    if not matches:
        return "FAIL", f"aucun fichier ne correspond à {spec['path']}"
    path = matches[0]
    relative = os.path.relpath(path, workdir)
    try:
        with open(path, encoding="utf-8") as handle:
            body = linter.split_frontmatter(handle.read())[1]
    except OSError as exc:
        return "FAIL", f"{relative} illisible : {exc}"

    present = linter.sections(body)
    template = spec.get("template")
    if template:
        if template not in templates:
            raise CannotConclude(
                f"{case['_label']} : gabarit inconnu « {template} », "
                f"attendus : {', '.join(sorted(templates))}"
            )
        defects = linter.check_sections(path, body, templates[template])
        if defects:
            return "FAIL", f"{relative} : " + " ; ".join(d.message for d in defects)
        return "OK", f"{relative} porte les sections du gabarit {template}"

    expected = spec.get("sections") or []
    missing = [name for name in expected if name not in present]
    if missing:
        return "FAIL", f"{relative} sans " + ", ".join(f"`## {m}`" for m in missing)
    if expected:
        return "OK", f"{relative} porte ses {len(expected)} section(s)"
    return "OK", f"{relative} existe"


# --- passe -----------------------------------------------------------------


def play_case(claude: str, case: dict, out_dir: str, repo_root: str, linter, templates, args):
    """Joue un cas de bout en bout. Rend (ligne de rapport, coût, défaut)."""
    workdir = stage_workdir(case, out_dir, repo_root)
    try:
        opened, _available, cost = run_session(
            claude, case, workdir, args.model, args.timeout
        )
        trigger, trigger_why = trigger_verdict(case, opened)
        artifact, artifact_why = artifact_verdict(case, workdir, linter, templates)
    finally:
        wrote = teardown_workdir(case, repo_root, workdir)

    details = [f"déclenchement : {trigger_why}"]
    if artifact != "N/A":
        details.append(f"artefact : {artifact_why}")
    if wrote:
        details.append(f"worktree : {len(wrote)} chemin(s) écrit(s) par la session")

    row = {
        "label": case["_label"],
        "mode": "artefact" if case.get("artifact") else "déclenchement",
        "trigger": trigger,
        "artifact": artifact,
        "details": details,
    }
    return row, cost, "FAIL" in (trigger, artifact)


def report(rows: list[dict], out_dir: str, spent: float) -> None:
    width = max([len(row["label"]) for row in rows] + [5])
    print(f"\n{'cas'.ljust(width)}  mode           déclenché  artefact")
    print("-" * (width + 38))
    for row in rows:
        print(
            f"{row['label'].ljust(width)}  "
            f"{row['mode'].ljust(13)}  "
            f"{row['trigger'].ljust(9)}  "
            f"{row['artifact']}"
        )
    print()
    for row in rows:
        print(f"{row['label']} :")
        for line in row["details"]:
            print(f"  - {line}")
    print(f"\nCoût : {spent:.2f} $   Traces : {out_dir}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--skill", action="append", default=[], help="restreindre à ce skill (répétable)"
    )
    parser.add_argument(
        "--model",
        default="opus",
        help=(
            "modèle de la session jouée (défaut: opus — mesuré le 2026-08-06 : 7/8 "
            "déclenchements sur opus contre 0/8 sur sonnet, à skills et contexte "
            "identiques)"
        ),
    )
    parser.add_argument("--out", help="répertoire des traces (défaut: temporaire)")
    parser.add_argument(
        "--timeout",
        type=int,
        default=DEFAULT_RUN_TIMEOUT_S,
        help=f"plafond d'une session, en secondes (défaut: {DEFAULT_RUN_TIMEOUT_S})",
    )
    parser.add_argument(
        "--jobs",
        type=int,
        default=4,
        help="cas joués en parallèle (défaut: 4) — indépendants, chacun dans son répertoire",
    )
    args = parser.parse_args()

    try:
        claude = require_tools()
        repo_root = derive_root()
        linter = load_linter(repo_root)
        templates = linter.load_templates(repo_root)
        cases = load_cases(os.path.join(repo_root, "skills"), args.skill)
        out_dir = args.out or tempfile.mkdtemp(prefix="skill-evals-")
        os.makedirs(out_dir, exist_ok=True)

        artefacts = sum(1 for case in cases if case.get("artifact"))
        print(
            f"{len(cases)} cas — session {args.model}, "
            f"{artefacts} en mode artefact, {len(cases) - artefacts} outils coupés"
        )

        # Le worktree ne bloque pas un accès par chemin absolu : la comparaison
        # avant/après rend cette fuite visible et bloquante.
        real_before = git_status(repo_root)

        rows, spent, defects, errors = [], 0.0, 0, []
        with ThreadPoolExecutor(max_workers=max(1, min(args.jobs, len(cases)))) as pool:
            futures = {
                pool.submit(
                    play_case, claude, case, out_dir, repo_root, linter, templates, args
                ): case["_label"]
                for case in cases
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
            rows.sort(key=lambda row: row["label"])
            report(rows, out_dir, spent)
            print(f"{len(rows) - defects} cas au vert sur {len(rows)}")

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
