#!/usr/bin/env python3
"""Calibre `check-doc.py` sur des README fabriqués, un propre et un par défaut.

Pourquoi cette batterie existe : un contrôle rend « 0 défaut » qu'il mesure ou qu'il
soit aveugle. Un positif et un négatif par vérification, fabriqués à la main, sont ce
qui distingue les deux (`rules/reasoning.md`, calibrage avant comptage).

Sortie : 0 si tous les cas passent, 1 si un cas échoue.
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
CHECKER = os.path.join(os.path.dirname(HERE), "check-doc.py")

SECTIONS = """
## Démarrage rapide
## Comment ça marche
## Faire un changement
## Référence
## Contribuer
"""

CLEAN = "# Projet\n\nLes skills vivent dans `skills/`, un `ls` les liste.\n" + SECTIONS

# (nom du cas, contenu, code attendu, fragment attendu dans la sortie ou None)
CASES = [
    ("propre", CLEAN, 0, None),
    ("compte relevé", CLEAN + "\nLe repo porte les 24 skills du harnais.\n", 1, "[compte]"),
    ("mesure datée laissée", CLEAN + "\nMesuré le 2026-10-26, 24 skills.\n", 0, None),
    ("compte dans du code laissé", CLEAN + "\n```\necho 24 skills\n```\n", 0, None),
    (
        "inventaire de puces relevé",
        CLEAN + "\n" + "".join(f"- `hook-{i}.sh` fait {i}\n" for i in range(5)),
        1,
        "[inventaire]",
    ),
    (
        "liste courte laissée",
        CLEAN + "\n" + "".join(f"- `hook-{i}.sh` fait {i}\n" for i in range(4)),
        0,
        None,
    ),
    (
        "inventaire en tableau relevé",
        CLEAN + "\n| Garde | Rôle |\n| --- | --- |\n"
        + "".join(f"| `garde-{i}.py` | refuse {i} |\n" for i in range(5)),
        1,
        "[inventaire]",
    ),
    (
        "puces de prose laissées",
        CLEAN + "\n" + "".join(f"- Étape {i}, lancer `make`\n" for i in range(6)),
        0,
        None,
    ),
    ("section manquante relevée", CLEAN.replace("## Contribuer\n", ""), 1, "contribuer"),
    ("compte de cas relevé", CLEAN + "\nUne trentaine de dollars pour les 31 cas.\n", 1, "[compte]"),
    ("compte en lettres à trier", CLEAN + "\nLe lint joue sept vérifications.\n", 0, "[à trier]"),
    ("fait stable en lettres à trier", CLEAN + "\nLe harnais sert deux agents.\n", 0, "[à trier]"),
    ("compte en lettres daté laissé", CLEAN + "\nAu 2026-10-27, sept vérifications.\n", 0, "0 à trier"),
]


def run(content: str, override: str | None = None) -> tuple[int, str]:
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, "README.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        cmd = [sys.executable, CHECKER, path]
        if override:
            rules = os.path.join(tmp, "rules.md")
            with open(rules, "w", encoding="utf-8") as f:
                f.write(override)
            cmd += ["--rules", rules]
        r = subprocess.run(cmd, capture_output=True, text=True)
        return r.returncode, r.stdout + r.stderr


def main() -> int:
    failures = 0
    for name, content, code, fragment in CASES:
        rc, out = run(content)
        ok = rc == code and (fragment is None or fragment in out)
        failures += not ok
        print(f"  {'ok' if ok else 'ÉCHEC'}  {name}" + ("" if ok else f" (rc={rc})\n{out}"))

    # La surcharge du repo gagne, clé par clé : retirer l'exigence de section la fait taire.
    rc, out = run(CLEAN.replace("## Contribuer\n", ""), "---\nsections: {}\n---\n")
    ok = rc == 0
    failures += not ok
    print(f"  {'ok' if ok else 'ÉCHEC'}  surcharge par le repo" + ("" if ok else f"\n{out}"))

    rc, out = run(CLEAN, "pas de frontmatter\n")
    ok = rc == 2
    failures += not ok
    print(f"  {'ok' if ok else 'ÉCHEC'}  règles illisibles sortent en 2")

    print(f"{'✗' if failures else '✓'} {failures} échec(s).")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
