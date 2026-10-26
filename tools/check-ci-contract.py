#!/usr/bin/env python3
"""Mesure qu'un dépôt respecte le contrat CI de `rules/references/ref-ci-github.md`.

Lit les fichiers, n'exécute rien et n'appelle pas GitHub. Six vérifications :

1. la porte : un seul job `ci`, le seul check que le ruleset exige. Elle a `if: always()`,
   son `needs` couvre tous les autres jobs de son workflow, ses steps lisent leurs
   résultats, et un job de ce workflow lance Trivy
2. chaque `uses:` pointe un SHA de 40 caractères (hors action locale `./` et `docker://`)
3. chaque workflow a un bloc `permissions:` en tête
4. ce bloc ne contient que `read` ou `none` (l'écriture se pose sur le job)
5. `dependabot.yml` couvre l'écosystème `github-actions`
6. une classe de test `*IT` (Maven) suppose `maven-failsafe-plugin` déclaré dans un
   `pom.xml`, sinon Surefire l'ignore et `verify` reste vert sans la lancer

Le nom d'un job est le contexte que le ruleset exige : on lit donc `name:` s'il existe,
l'identifiant du job sinon. Un nom construit par matrice (`${{ ... }}`) n'est pas un
contexte stable, il est ignoré.

Pourquoi `if: always()` : GitHub compte un job sauté comme réussi. Sans lui, la porte est
sautée dès qu'un job qu'elle attend échoue, et la fusion passe.

**Ce que ce script ne vérifie pas** : le découpage des autres jobs, libre selon la stack,
la sémantique du test des résultats (il constate que la porte les lit, pas qu'elle
échoue au bon moment), ni le tag en commentaire après le SHA.

Sortie : une ligne `fichier:ligne: message` par écart. Code 0 si conforme, 1 si un écart
est mesuré, 2 si on ne peut pas conclure (dossier absent, YAML illisible, PyYAML manquant).
"""

from __future__ import annotations

import argparse
import os
import re
import sys

try:
    import yaml
except ImportError:
    sys.exit("PyYAML manquant : impossible de conclure")

SHA = re.compile(r"^[0-9a-f]{40}$")
USES = re.compile(r"^\s*(?:-\s*)?uses:\s*([^\s#]+)")
GATE = "ci"
TRIVY = "aquasecurity/trivy-action"
READS_ALL_RESULTS = re.compile(r"needs\.\*\.result|tojson\(\s*needs\s*\)", re.IGNORECASE)
SKIPPED_DIRS = {".git", "node_modules", "target", ".venv"}


class Unreadable(Exception):
    """Une entrée empêche de conclure : le code de sortie est alors 2."""


def workflow_files(root: str) -> list[str]:
    folder = os.path.join(root, ".github", "workflows")
    if not os.path.isdir(folder):
        return []
    return sorted(
        os.path.join(folder, name)
        for name in os.listdir(folder)
        if name.endswith((".yml", ".yaml"))
    )


def load(path: str):
    try:
        with open(path, encoding="utf-8") as handle:
            return yaml.safe_load(handle) or {}
    except (OSError, yaml.YAMLError) as error:
        raise Unreadable(f"{path}: illisible ({error})") from error


def jobs_of(document) -> dict:
    jobs = document.get("jobs") if isinstance(document, dict) else None
    return {str(k): v for k, v in jobs.items()} if isinstance(jobs, dict) else {}


def context_of(job_id: str, job) -> str | None:
    name = str(job.get("name", job_id)) if isinstance(job, dict) else job_id
    return None if "${{" in name else name


def as_list(value) -> list[str]:
    if isinstance(value, str):
        return [value]
    return [str(v) for v in value] if isinstance(value, list) else []


def check_gate(root: str, files: list[str], documents: dict) -> list[str]:
    gates = [
        (path, job_id, job)
        for path in files
        for job_id, job in jobs_of(documents[path]).items()
        if context_of(job_id, job) == GATE
    ]
    if not gates:
        return [f".github/workflows: job `{GATE}` manquant, c'est la porte que le ruleset exige"]
    if len(gates) > 1:
        where = ", ".join(os.path.relpath(path, root) for path, _, _ in gates)
        return [f".github/workflows: job `{GATE}` défini {len(gates)} fois ({where})"]

    path, gate_id, gate = gates[0]
    relative = os.path.relpath(path, root)
    gate = gate if isinstance(gate, dict) else {}
    others = [job_id for job_id in jobs_of(documents[path]) if job_id != gate_id]
    needs = as_list(gate.get("needs"))
    problems = []

    if "always()" not in str(gate.get("if", "")):
        problems.append(
            f"{relative}: la porte `{GATE}` n'a pas `if: always()`, un job sauté compte comme réussi"
        )
    for job_id in others:
        if job_id not in needs:
            problems.append(f"{relative}: la porte `{GATE}` n'attend pas `{job_id}`")

    steps = " ".join(
        str(step.get("run", "")) + " " + str(step.get("with", ""))
        for step in gate.get("steps") or []
        if isinstance(step, dict)
    )
    reads_each = bool(needs) and all(f"needs.{job_id}.result" in steps for job_id in needs)
    if not (READS_ALL_RESULTS.search(steps) or reads_each):
        problems.append(f"{relative}: la porte `{GATE}` ne teste pas les résultats de ses jobs")

    runs_trivy = any(
        isinstance(step, dict) and str(step.get("uses", "")).startswith(TRIVY + "@")
        for job in jobs_of(documents[path]).values()
        if isinstance(job, dict)
        for step in job.get("steps") or []
    )
    if not runs_trivy:
        problems.append(f"{relative}: aucun job Trivy dans le workflow de la porte `{GATE}`")
    return problems


def check_uses(root: str, path: str) -> list[str]:
    problems = []
    with open(path, encoding="utf-8") as handle:
        for number, line in enumerate(handle, start=1):
            match = USES.match(line)
            if not match:
                continue
            target = match.group(1).strip("'\"")
            if target.startswith(("./", "docker://")):
                continue
            ref = target.rpartition("@")[2] if "@" in target else ""
            if not SHA.match(ref):
                problems.append(
                    f"{os.path.relpath(path, root)}:{number}: `{target}` n'est pas épinglé par SHA"
                )
    return problems


def check_permissions(root: str, path: str, document) -> list[str]:
    relative = os.path.relpath(path, root)
    permissions = document.get("permissions") if isinstance(document, dict) else None
    if permissions is None:
        return [f"{relative}: bloc `permissions:` absent en tête"]
    if isinstance(permissions, str):
        if permissions in ("read-all", "{}"):
            return []
        return [f"{relative}: permissions en tête `{permissions}`, seul read ou none est permis"]
    problems = []
    for scope, level in permissions.items():
        if level not in ("read", "none"):
            problems.append(
                f"{relative}: permissions en tête `{scope}: {level}`, "
                "l'écriture se pose sur le job"
            )
    return problems


def check_dependabot(root: str) -> list[str]:
    for name in ("dependabot.yml", "dependabot.yaml"):
        path = os.path.join(root, ".github", name)
        if os.path.isfile(path):
            document = load(path)
            updates = document.get("updates") if isinstance(document, dict) else None
            ecosystems = [u.get("package-ecosystem") for u in updates or [] if isinstance(u, dict)]
            if "github-actions" in ecosystems:
                return []
            return [f".github/{name}: l'écosystème `github-actions` manque"]
    return [".github/dependabot.yml: absent"]


def find_files(root: str, matches) -> list[str]:
    found = []
    for folder, dirs, names in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIPPED_DIRS]
        found += [os.path.join(folder, n) for n in names if matches(folder, n)]
    return sorted(found)


def check_failsafe(root: str) -> list[str]:
    """Maven ignore en silence une classe `*IT` tant que Failsafe n'est pas déclaré."""
    classes = find_files(
        root,
        lambda folder, name: name.endswith(".java")
        and f"{os.sep}src{os.sep}test{os.sep}" in folder + os.sep
        and name.endswith(("IT.java", "ITCase.java")),
    )
    if not classes:
        return []
    for pom in find_files(root, lambda _, name: name == "pom.xml"):
        with open(pom, encoding="utf-8") as handle:
            if "maven-failsafe-plugin" in handle.read():
                return []
    return [
        f"{os.path.relpath(classes[0], root)}: {len(classes)} classe(s) de test d'intégration "
        "(*IT) mais `maven-failsafe-plugin` n'est déclaré dans aucun pom.xml, "
        "elles ne seraient jamais lancées"
    ]


def check(root: str) -> list[str]:
    if not os.path.isdir(root):
        raise Unreadable(f"{root}: dossier introuvable")
    files = workflow_files(root)
    if not files:
        return [".github/workflows: aucun workflow"]
    documents = {path: load(path) for path in files}
    problems = check_gate(root, files, documents)
    for path in files:
        problems += check_uses(root, path)
        problems += check_permissions(root, path, documents[path])
    return problems + check_dependabot(root) + check_failsafe(root)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("repo", nargs="?", default=".", help="racine du dépôt à mesurer")
    args = parser.parse_args(argv)
    try:
        problems = check(os.path.abspath(args.repo))
    except Unreadable as error:
        print(error, file=sys.stderr)
        return 2
    for problem in problems:
        print(problem)
    if problems:
        return 1
    print("conforme")
    return 0


if __name__ == "__main__":
    sys.exit(main())
