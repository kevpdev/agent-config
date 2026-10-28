#!/usr/bin/env python3
"""Refuse, dans les règles chargées, un POURQUOI qui sert à qui édite la règle.

Une règle chargée garde un fait par pourquoi, celui qui change ce que l'agent fait. Le
rangement, le scope et le « pourquoi ici » vont dans `rules/references/ref-<nom>.md`
(méta-règle de `rules/reasoning.md`). Cette batterie n'attrape que les formes connues :
un libellé `POURQUOI…` qui porte un marqueur de rangement avant son deux-points. Une
raison de rangement écrite autrement passe, c'est la règle qui la couvre.

Pourquoi le calibrage d'abord : un détecteur qui ne voit rien rend « propre » comme un
détecteur juste. Un positif et un négatif fabriqués sont exhibés avant le vrai repo
(`rules/reasoning.md`, calibrage avant comptage).

Usage
  python3 tools/tests/test-rules-no-placement-why.py [RACINE]

RACINE vise un autre arbre que ce repo, par exemple un export de `main`.

Sortie : 0 si tous les cas passent, 1 si un cas échoue.
"""

from __future__ import annotations

import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
LOADED = ("rules/*.md", "wrappers/claude/rules/*.md")
MARKERS = (
    r"ici", r"global", r"paths:", r"fichier", r"découpage", r"page",
    r"placé", r"rangé", r"pas dans", r"plutôt que dans",
)
# Le libellé va de `POURQUOI` au premier `:` hors backticks, d'où `paths:` toléré dedans.
LABEL = re.compile(r"POURQUOI((?:`[^`]*`|[^:`])*):")
PLACEMENT = re.compile(r"\b(?:" + "|".join(MARKERS) + r")", re.IGNORECASE)


def offenders(lines: list[str]) -> list[int]:
    found = []
    for number, line in enumerate(lines, start=1):
        label = LABEL.search(line)
        if label and PLACEMENT.search(label.group(1)):
            found.append(number)
    return found


def scan(root: str) -> list[str]:
    problems = []
    for pattern in LOADED:
        for path in sorted(glob.glob(os.path.join(root, pattern))):
            with open(path, encoding="utf-8") as handle:
                lines = handle.read().splitlines()
            name = os.path.splitext(os.path.basename(path))[0]
            for number in offenders(lines):
                problems.append(
                    f"{os.path.relpath(path, root)}:{number} : POURQUOI de rangement, le mettre "
                    f"dans rules/references/ (ref-{name}.md, ou la ref qui couvre déjà la règle)"
                )
    return problems


def main(argv: list[str]) -> int:
    root = argv[1] if len(argv) > 1 else REPO
    echecs = 0

    def cas(nom: str, ok: bool, detail: str = "") -> None:
        nonlocal echecs
        print(f"  {'ok  ' if ok else 'FAIL'}  {nom}")
        if not ok:
            echecs += 1
            if detail:
                print(detail)

    cas("positif : « POURQUOI ici » est signalé",
        offenders(["**POURQUOI ici et pas dans `CLAUDE.md`** : parce que."]) == [1])
    cas("positif : `paths:` dans le libellé est signalé",
        offenders(["**POURQUOI ce n'est pas un `paths:`** : le scope porte sur le fichier."]) == [1])
    cas("négatif : un POURQUOI simple passe",
        offenders(["**POURQUOI** : le plan mode masque la conversation ici."]) == [])
    cas("négatif : un marqueur après le deux-points passe",
        offenders(["**POURQUOI, mesuré le 2026-08-19** : cette page dit l'inverse."]) == [])

    problems = scan(root)
    cas(f"règles chargées de {root}", not problems,
        "\n".join("        " + p for p in problems))

    print(f"{'✓' if echecs == 0 else '✗'} {echecs} cas en échec.")
    return 0 if echecs == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
