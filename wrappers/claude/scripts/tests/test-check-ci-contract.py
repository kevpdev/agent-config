#!/usr/bin/env python3
"""Calibre `check-ci-contract.py` sur des dépôts fabriqués, un conforme et un par défaut.

N'ouvre aucun dépôt réel et n'appelle pas GitHub : ne teste que les six vérifications,
qui sont déterministes.

Pourquoi cette batterie existe : un script de conformité se comporte pareil qu'il mesure
ou qu'il soit aveugle, il rend « conforme » dans les deux cas. Sans un positif et un
négatif par vérification exhibés à la main, rien ne distingue les deux
(`rules/reasoning.md`, calibrage avant comptage).

Sortie : 0 si tous les cas passent, 1 si un cas échoue.
"""

from __future__ import annotations

import importlib.util
import os
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(os.path.dirname(HERE), "check-ci-contract.py")


def load_script():
    if not os.path.exists(SCRIPT):
        sys.exit(f"check-ci-contract.py introuvable à {SCRIPT}")
    spec = importlib.util.spec_from_file_location("contract", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


SHA = "3d3c42e5aac5ba805825da76410c181273ba90b1"

CI = f"""name: ci
on:
  pull_request:

permissions:
  contents: read

jobs:
  lint:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@{SHA} # v7.0.1
      - run: scripts/lint.sh
  unit-tests:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@{SHA} # v7.0.1
      - run: scripts/test.sh
  e2e:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@{SHA} # v7.0.1
      - uses: ./.github/actions/local
      - run: scripts/e2e.sh
  security:
    runs-on: ubuntu-24.04
    permissions:
      security-events: write
    steps:
      - uses: actions/checkout@{SHA} # v7.0.1
      - uses: aquasecurity/trivy-action@{SHA} # v0.36.0
  ci:
    if: always()
    needs: [lint, unit-tests, e2e, security]
    runs-on: ubuntu-24.04
    steps:
      - run: test "${{{{ contains(needs.*.result, 'failure') }}}}" = false
"""

GATE_RUN = """      - run: test "${{ contains(needs.*.result, 'failure') }}" = false
"""

MATRIX = f"""name: codeql
on:
  pull_request:

permissions:
  contents: read

jobs:
  analyze:
    name: codeql ${{{{ matrix.language }}}}
    runs-on: ubuntu-24.04
    strategy:
      matrix:
        language: [python]
    steps:
      - uses: actions/checkout@{SHA} # v7.0.1
"""

DEPENDABOT = """version: 2
updates:
  - package-ecosystem: github-actions
    directory: /
    schedule:
      interval: weekly
"""


def write(root: str, relative: str, content: str) -> None:
    path = os.path.join(root, relative)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(content)


def build(root: str) -> None:
    write(root, ".github/workflows/ci.yml", CI)
    write(root, ".github/workflows/codeql.yml", MATRIX)
    write(root, ".github/dependabot.yml", DEPENDABOT)


def mutate(root: str, relative: str, old: str, new: str) -> None:
    path = os.path.join(root, relative)
    with open(path, encoding="utf-8") as handle:
        content = handle.read()
    assert old in content, f"{relative} ne contient pas {old!r}"
    write(root, relative, content.replace(old, new, 1))


def main() -> int:
    contract = load_script()
    failures = []

    def case(label: str, expected_fragment: str | None, setup) -> None:
        """Un cas passe si le dépôt est conforme (fragment None) ou si un écart cite le fragment."""
        with tempfile.TemporaryDirectory() as root:
            build(root)
            setup(root)
            problems = contract.check(root)
        if expected_fragment is None:
            ok = problems == []
        else:
            ok = any(expected_fragment in line for line in problems)
        print(f"{'ok  ' if ok else 'ÉCHEC'} {label}")
        if not ok:
            failures.append((label, problems))

    case("dépôt conforme, action locale et matrice ignorées", None, lambda r: None)
    case(
        "tag à la place du SHA",
        "ci.yml:",
        lambda r: mutate(r, ".github/workflows/ci.yml", f"checkout@{SHA}", "checkout@v4"),
    )
    case(
        "branche à la place du SHA",
        "n'est pas épinglé par SHA",
        lambda r: mutate(r, ".github/workflows/ci.yml", f"checkout@{SHA}", "checkout@main"),
    )
    case(
        "SHA trop court",
        "n'est pas épinglé par SHA",
        lambda r: mutate(r, ".github/workflows/ci.yml", f"checkout@{SHA}", "checkout@3d3c42e"),
    )
    case(
        "action sans @",
        "n'est pas épinglé par SHA",
        lambda r: mutate(r, ".github/workflows/ci.yml", f"actions/checkout@{SHA}", "actions/checkout"),
    )
    ci = ".github/workflows/ci.yml"
    needs_all = "needs: [lint, unit-tests, e2e, security]"

    case("porte absente", "job `ci` manquant", lambda r: mutate(r, ci, "  ci:\n", "  gate:\n"))
    case("porte nommée par name:", None, lambda r: mutate(r, ci, "  ci:\n", "  gate:\n    name: ci\n"))
    case(
        "porte définie deux fois",
        "défini 2 fois",
        lambda r: write(
            r,
            ".github/workflows/other.yml",
            "name: other\npermissions:\n  contents: read\njobs:\n  ci:\n    runs-on: x\n    steps:\n      - run: echo\n",
        ),
    )
    case("porte sans if: always()", "n'a pas `if: always()`", lambda r: mutate(r, ci, "    if: always()\n", ""))
    case(
        "porte avec if: success()",
        "n'a pas `if: always()`",
        lambda r: mutate(r, ci, "if: always()", "if: success()"),
    )
    case(
        "porte en ${{ always() }}",
        None,
        lambda r: mutate(r, ci, "if: always()", "if: ${{ always() }}"),
    )
    case(
        "porte qui oublie un job",
        "n'attend pas `e2e`",
        lambda r: mutate(r, ci, needs_all, "needs: [lint, unit-tests, security]"),
    )
    case(
        "porte sans needs",
        "n'attend pas `lint`",
        lambda r: mutate(r, ci, f"    {needs_all}\n", ""),
    )

    def single_job(r):
        write(r, ci, CI.split("  lint:")[0] + (
            "  security:\n    runs-on: ubuntu-24.04\n    steps:\n"
            f"      - uses: aquasecurity/trivy-action@{SHA} # v0.36.0\n"
            "  ci:\n    if: always()\n    needs: security\n    runs-on: ubuntu-24.04\n    steps:\n"
            + GATE_RUN
        ))

    case("needs en chaîne avec un seul autre job", None, single_job)
    case(
        "porte qui ne lit pas les résultats",
        "ne teste pas les résultats",
        lambda r: mutate(r, ci, GATE_RUN, "      - run: echo ok\n"),
    )
    case(
        "porte qui lit toJSON(needs) via une action",
        None,
        lambda r: mutate(r, ci, GATE_RUN, (
            f"      - uses: re-actors/alls-green@{SHA}\n"
            "        with:\n          jobs: ${{ toJSON(needs) }}\n"
        )),
    )
    each = " && ".join(f'test "${{{{ needs.{j}.result }}}}" = success' for j in ("lint", "unit-tests", "e2e", "security"))
    case(
        "porte qui lit le résultat de chaque job",
        None,
        lambda r: mutate(r, ci, GATE_RUN, f"      - run: {each}\n"),
    )
    case(
        "porte qui ne lit le résultat que d'un job",
        "ne teste pas les résultats",
        lambda r: mutate(r, ci, GATE_RUN, '      - run: test "${{ needs.lint.result }}" = success\n'),
    )
    case(
        "Trivy absent du workflow de la porte",
        "aucun job Trivy",
        lambda r: mutate(r, ci, f"      - uses: aquasecurity/trivy-action@{SHA} # v0.36.0\n", ""),
    )

    def trivy_elsewhere(r):
        mutate(r, ci, f"      - uses: aquasecurity/trivy-action@{SHA} # v0.36.0\n", "")
        write(r, ".github/workflows/trivy.yml", (
            "name: trivy\npermissions:\n  contents: read\njobs:\n  scan:\n    runs-on: x\n    steps:\n"
            f"      - uses: aquasecurity/trivy-action@{SHA} # v0.36.0\n"
        ))

    case("Trivy dans un autre workflow que la porte", "aucun job Trivy", trivy_elsewhere)
    case(
        "permissions absentes en tête",
        "bloc `permissions:` absent",
        lambda r: mutate(r, ".github/workflows/ci.yml", "permissions:\n  contents: read\n\n", ""),
    )
    case(
        "écriture en tête de workflow",
        "contents: write",
        lambda r: mutate(r, ".github/workflows/ci.yml", "contents: read", "contents: write"),
    )
    case(
        "dependabot sans github-actions",
        "`github-actions` manque",
        lambda r: mutate(r, ".github/dependabot.yml", "github-actions", "pip"),
    )
    case(
        "dependabot absent",
        "dependabot.yml: absent",
        lambda r: os.remove(os.path.join(r, ".github/dependabot.yml")),
    )
    case(
        "aucun workflow",
        "aucun workflow",
        lambda r: [os.remove(os.path.join(r, ".github/workflows", f)) for f in os.listdir(os.path.join(r, ".github/workflows"))],
    )

    it_class = "src/test/java/fr/demo/FooIT.java"
    pom_plain = "<project><build><plugins></plugins></build></project>\n"
    pom_failsafe = (
        "<project><build><plugins><plugin>"
        "<artifactId>maven-failsafe-plugin</artifactId>"
        "</plugin></plugins></build></project>\n"
    )

    def with_files(files: dict):
        return lambda r: [write(r, path, content) for path, content in files.items()]

    case(
        "classe *IT sans pom",
        "maven-failsafe-plugin",
        with_files({it_class: "class FooIT {}\n"}),
    )
    case(
        "classe *IT et pom sans Failsafe",
        "elles ne seraient jamais lancées",
        with_files({it_class: "class FooIT {}\n", "pom.xml": pom_plain}),
    )
    case(
        "classe *ITCase et pom sans Failsafe",
        "maven-failsafe-plugin",
        with_files({"src/test/java/fr/demo/BarITCase.java": "class BarITCase {}\n", "pom.xml": pom_plain}),
    )
    case(
        "classe *IT et Failsafe déclaré",
        None,
        with_files({it_class: "class FooIT {}\n", "pom.xml": pom_failsafe}),
    )
    case(
        "classe *IT et Failsafe déclaré dans un sous-module",
        None,
        with_files({it_class: "class FooIT {}\n", "pom.xml": pom_plain, "app/pom.xml": pom_failsafe}),
    )
    case(
        "classes *Test et *Tests seules, Failsafe non exigé",
        None,
        with_files({"src/test/java/fr/demo/FooTest.java": "class FooTest {}\n", "src/test/java/fr/demo/BarTests.java": "class BarTests {}\n", "pom.xml": pom_plain}),
    )
    case(
        "classe *IT sous target/ ignorée",
        None,
        with_files({"target/src/test/java/FooIT.java": "class FooIT {}\n"}),
    )
    case(
        "classe *IT hors de src/test ignorée",
        None,
        with_files({"src/main/java/fr/demo/FooIT.java": "class FooIT {}\n"}),
    )

    with tempfile.TemporaryDirectory() as root:
        build(root)
        write(root, ".github/workflows/broken.yml", "jobs: [unclosed\n")
        try:
            contract.check(root)
            raised = False
        except contract.Unreadable:
            raised = True
        print(f"{'ok  ' if raised else 'ÉCHEC'} YAML illisible : on ne conclut pas (code 2)")
        if not raised:
            failures.append(("YAML illisible", []))
        code = contract.main([root])
        print(f"{'ok  ' if code == 2 else 'ÉCHEC'} main() rend 2 sur YAML illisible")
        if code != 2:
            failures.append(("code 2", [code]))

    with tempfile.TemporaryDirectory() as root:
        build(root)
        code = contract.main([root])
        print(f"{'ok  ' if code == 0 else 'ÉCHEC'} main() rend 0 sur un dépôt conforme")
        if code != 0:
            failures.append(("code 0", [code]))
        mutate(root, ".github/workflows/ci.yml", f"checkout@{SHA}", "checkout@v4")
        code = contract.main([root])
        print(f"{'ok  ' if code == 1 else 'ÉCHEC'} main() rend 1 sur un écart mesuré")
        if code != 1:
            failures.append(("code 1", [code]))

    if failures:
        print(f"\n{len(failures)} cas en échec", file=sys.stderr)
        for label, problems in failures:
            print(f"- {label} : {problems}", file=sys.stderr)
        return 1
    print("\ntous les cas passent")
    return 0


if __name__ == "__main__":
    sys.exit(main())
