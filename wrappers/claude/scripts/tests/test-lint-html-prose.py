#!/usr/bin/env python3
"""Calibre `lint-html-prose.py` sur des documents fabriqués, un propre et un par motif.

Pourquoi cette batterie existe : un lint rend « 0 interdit » qu'il mesure ou qu'il
soit aveugle. Sans un positif et un négatif par motif exhibés à la main, rien ne
distingue les deux (`rules/reasoning.md`, calibrage avant comptage).

Sortie : 0 si tous les cas passent, 1 si un cas échoue.
"""

from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
LINTER = os.path.join(os.path.dirname(HERE), "lint-html-prose.py")


def load_linter():
    spec = importlib.util.spec_from_file_location("lint_html_prose", LINTER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def page(body: str, title: str = "Comparatif OCR") -> str:
    return f"<html><head><title>{title}</title><style>a{{b:c;}}</style></head><body>{body}</body></html>"


CLEAN = page(
    "<h1>Choisir l'OCR des factures</h1>"
    "<p>Le modèle lit la page et le code calcule la masse.</p>"
    "<pre>total = a; b = c != d</pre>"
    "<p>Le test tourne avec <code>x; y!</code> sans bruit.</p>"
    "<svg><text>Étape — 1 ; fin</text></svg>"
)

# Un cas par interdit : (règle attendue, fragment de corps, titre).
FORBIDDEN_CASES = [
    ("point-virgule", "<p>Le modèle lit la page ; le code compte.</p>", None),
    ("tiret long", "<p>Le modèle lit — le code compte.</p>", None),
    ("tiret long", "<p>Texte propre.</p>", "Comparatif — OCR"),
    ("exclamation", "<p>Le code compte !</p>", None),
    ("formule", "<p>Concrètement, le code compte.</p>", None),
    ("emoji", "<p>Le code compte \U0001F680.</p>", None),
    ("emoji", "<p>Le code compte \u2705.</p>", None),
    ("emoji", "<p>Le code compte \u2b50.</p>", None),
]

TO_SORT_CASES = [
    ("contraste", "<p>Le modèle ne compte pas les lignes mais les lit.</p>"),
    ("deux-points", "<p>Le modèle&nbsp;: il lit la page.</p>"),
    ("title case", "<h2>Le LLM Lit Tout</h2>"),
    ("emphase", "<p>C'est là que le code compte.</p>"),
    ("emphase", "<p>C'est <strong>là</strong> que le code compte.</p>"),
    ("contraste", "<p>Le modèle ne compte pas <em>les lignes</em> mais les lit.</p>"),
    ("contraste", "<p>Il ne s'agit pas de compter.</p>"),
    ("title case", "<h2>Le LLM Lit, Le Code Compte</h2>"),
    ("formule", "<p>La mesure est la clé du choix.</p>"),
    ("typographie", "<p>Le prix passe à 2.35 par page.</p>"),
    ("formule", "<p>La suppression en cascade des lignes est native.</p>"),
]

# Des tournures proches d'un interdit, que les règles autorisent : rien ne doit sortir
# en interdit. Mesuré aux relectures du 2026-09-23, les six sortaient à tort.
ALLOWED_CASES = [
    "<p>Les deux passes suffisent pour ce corpus.</p>",
    "<p>Relevé sur la période 2023–2025.</p>",
    "<td>Pris en charge ✓</td>",
    "<p>C'est ce qui explique l'écart.</p>",
    "<p>Nous en sommes à la version 3.</p>",
    "<li>https://example.org/doc;jsessionid=42?x=1!</li>",
]


def main() -> int:
    lint = load_linter()
    failures = []

    forbidden, to_sort = lint.scan(CLEAN)
    if forbidden or to_sort:
        failures.append(f"propre : relevé à tort {forbidden + to_sort}")

    for rule, body, title in FORBIDDEN_CASES:
        forbidden, _ = lint.scan(page(body, title or "Comparatif OCR"))
        if not any(line.startswith(f"[{rule}]") for line in forbidden):
            failures.append(f"{rule} : non relevé dans {body!r} / {title!r}")

    for rule, body in TO_SORT_CASES:
        forbidden, to_sort = lint.scan(page(body))
        if forbidden:
            failures.append(f"{rule} : compté comme interdit {forbidden}")
        if not any(line.startswith(f"[{rule}, à trier]") for line in to_sort):
            failures.append(f"{rule} : non relevé dans {body!r}")

    # Un interdit placé loin dans une longue ligne reste visible dans l'extrait affiché.
    forbidden, _ = lint.scan(page("<p>" + "mot " * 60 + "fin ; suite</p>"))
    if not forbidden or ";" not in forbidden[0]:
        failures.append(f"extrait : le ; relevé n'apparaît pas dans {forbidden}")

    for body in ALLOWED_CASES:
        forbidden, _ = lint.scan(page(body))
        if forbidden:
            failures.append(f"autorisé relevé à tort {forbidden}")

    # Le code de sortie, joué pour de vrai sur des fichiers.
    with tempfile.TemporaryDirectory() as tmp:
        for name, src, want in [
            ("propre.html", CLEAN, 0),
            ("fautif.html", page(FORBIDDEN_CASES[0][1]), 1),
            ("a-trier.html", page(TO_SORT_CASES[1][1]), 0),
        ]:
            path = os.path.join(tmp, name)
            with open(path, "w", encoding="utf-8") as f:
                f.write(src)
            got = subprocess.run([sys.executable, LINTER, path], capture_output=True).returncode
            if got != want:
                failures.append(f"{name} : code {got}, attendu {want}")
        got = subprocess.run(
            [sys.executable, LINTER, os.path.join(tmp, "absent.html")], capture_output=True
        ).returncode
        if got != 2:
            failures.append(f"absent.html : code {got}, attendu 2")

    total = 1 + len(FORBIDDEN_CASES) + len(TO_SORT_CASES) + len(ALLOWED_CASES) + 5
    for failure in failures:
        print(f"ÉCHEC {failure}")
    print(f"{total - len(failures)}/{total} cas passent" if not failures else f"{len(failures)} échec(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
