#!/usr/bin/env python3
"""Relève dans un document Markdown ce que les règles de son type interdisent.

Outil du skill `doc-sync`, action `06-sync-doc`. Lit le fichier, n'exécute rien,
n'appelle aucun LLM.

Trois vérifications, toutes sans interprétation :

1. **compte** : un nombre suivi d'un nom qui bouge (`les 24 skills`, `6 hooks`). La liste
   des noms vient des règles du type. Une ligne qui porte une date `AAAA-MM-JJ` passe :
   c'est une mesure datée, qui décrit un fait passé et ne périme pas.
2. **inventaire** : au moins `inventory_min_items` puces consécutives, ou lignes de
   tableau, dont chacune s'ouvre sur un nom en backticks ou un lien. C'est la forme d'une
   liste écrite à la main que rien ne tient à jour.
3. **section** : une étape exigée par le type dont aucun titre `##` ou `###` ne contient
   un des mots-clés.

**Un compte écrit en lettres est à trier** (`sept vérifications`) : il s'affiche, mais ne
change pas le code de sortie. *Pourquoi, mesuré le 2026-10-27 : « deux agents » revient 8
fois dans le README d'`agent-config`, et c'est un fait stable. Bloquant, le contrôle sortirait
rouge sur un document conforme.*

Les règles se lisent dans le frontmatter de `skills/doc-sync/references/types/<type>.md`.
Un repo les surcharge par `.doc-rules/<type>.md` à sa racine, clé par clé. `--rules`
désigne un fichier de surcharge explicite.

*Ce que le script ne voit pas, et que la relecture couvre* : la table d'entrée, l'ordre du
fil, un compte écrit en lettres, et le ton.

Sortie : 0 si aucun défaut, 1 si au moins un, 2 si le fichier ou les règles sont illisibles.
"""

from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys

import yaml

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TYPES = os.path.join(REPO, "skills", "doc-sync", "references", "types")

FENCE = re.compile(r"^\s*(```|~~~)")
INLINE_CODE = re.compile(r"`[^`]*`")
DATE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")
HEADING = re.compile(r"^#{2,3}\s+(.*)")
BULLET = re.compile(r"^\s*(?:[-*+]|\d+\.)\s+(.*)")
TABLE_ROW = re.compile(r"^\s*\|(.*)\|\s*$")
TABLE_SEP = re.compile(r"^\s*\|[\s:|-]+\|\s*$")
# Un item d'inventaire s'ouvre sur un nom en backticks ou un lien, gras éventuel compris.
NAMED_ITEM = re.compile(r"^\s*(?:\*\*)?(?:`[^`]+`|\[[^\]]+\]\([^)]+\))")
WORDS = (
    "deux|trois|quatre|cinq|six|sept|huit|neuf|dix|onze|douze|treize|quatorze|quinze|seize"
    "|dix-sept|dix-huit|dix-neuf|vingt"
)


def frontmatter(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        text = f.read()
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        raise ValueError(f"{path} : pas de frontmatter")
    return yaml.safe_load(m.group(1)) or {}


def git_root(path: str) -> str | None:
    r = subprocess.run(
        ["git", "-C", os.path.dirname(os.path.abspath(path)), "rev-parse", "--show-toplevel"],
        capture_output=True, text=True,
    )
    return r.stdout.strip() if r.returncode == 0 else None


def load_rules(doc: str, doc_type: str, override: str | None) -> dict:
    rules = frontmatter(os.path.join(TYPES, f"{doc_type}.md"))
    if override is None:
        root = git_root(doc)
        candidate = os.path.join(root, ".doc-rules", f"{doc_type}.md") if root else None
        override = candidate if candidate and os.path.isfile(candidate) else None
    if override:
        rules.update(frontmatter(override))
    return rules


def prose_lines(lines: list[str]) -> list[tuple[int, str]]:
    """Les lignes hors blocs de code, numérotées à partir de 1."""
    out, in_fence = [], False
    for n, line in enumerate(lines, 1):
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if not in_fence:
            out.append((n, line))
    return out


def check_counts(lines, nouns) -> tuple[list[str], list[str]]:
    """Les comptes en chiffres, qui sont des défauts, et ceux en lettres, à trier."""
    if not nouns:
        return [], []
    alt = "|".join(re.escape(n) for n in nouns)
    tail = rf"\s+(?:[\wÀ-ÿ'’-]+\s+)?(?:{alt})\b"
    digits = re.compile(rf"(?<![\w.,-])\d+{tail}", re.I)
    words = re.compile(rf"(?<![\w-])(?:{WORDS}){tail}", re.I)
    found, to_sort = [], []
    for n, line in lines:
        if line.lstrip().startswith("#") or DATE.search(line):
            continue
        text = INLINE_CODE.sub("", line)
        if m := digits.search(text):
            found.append(f"ligne {n} [compte] « {m.group(0)} »")
        if m := words.search(text):
            to_sort.append(f"ligne {n} [à trier] « {m.group(0)} »")
    return found, to_sort


def check_inventories(lines, minimum) -> list[str]:
    found, run, start, prev = [], 0, None, None

    def close():
        if run >= minimum:
            found.append(f"ligne {start} [inventaire] {run} items nommés à la suite")

    for n, line in lines:
        if TABLE_SEP.match(line):
            prev = n
            continue
        item = None
        b = BULLET.match(line)
        t = TABLE_ROW.match(line)
        if b:
            item = b.group(1)
        elif t:
            item = t.group(1).split("|")[0]
        contiguous = prev is not None and n == prev + 1
        if item is not None and NAMED_ITEM.match(item):
            if not (run and contiguous):
                close()
                run, start = 0, n
            run += 1
        elif item is None and line.startswith((" ", "\t")) and run and contiguous:
            pass  # la suite d'un item sur plusieurs lignes ne coupe pas la liste
        else:
            close()
            run = 0
        prev = n
    close()
    return found


def check_sections(lines, sections) -> list[str]:
    titles = [m.group(1).lower() for _, line in lines if (m := HEADING.match(line))]
    found = []
    for step, keywords in (sections or {}).items():
        if not any(k.lower() in t for t in titles for k in keywords):
            found.append(f"[section] étape « {step} » absente, aucun titre ne contient {keywords}")
    return found


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("file")
    p.add_argument("--type", default="readme")
    p.add_argument("--rules", help="fichier de surcharge, à la place de .doc-rules/<type>.md")
    a = p.parse_args()
    try:
        with open(a.file, encoding="utf-8") as f:
            lines = prose_lines(f.read().splitlines())
        rules = load_rules(a.file, a.type, a.rules)
    except (OSError, ValueError, yaml.YAMLError) as e:
        print(f"illisible : {e}", file=sys.stderr)
        return 2
    counts, to_sort = check_counts(lines, rules.get("counted_nouns"))
    defects = (
        counts
        + check_inventories(lines, int(rules.get("inventory_min_items", 5)))
        + check_sections(lines, rules.get("sections"))
    )
    for d in defects + to_sort:
        print(d)
    print(
        f"{'✗' if defects else '✓'} {a.file} : {len(defects)} défaut(s), "
        f"{len(to_sort)} à trier, type {a.type}."
    )
    return 1 if defects else 0


if __name__ == "__main__":
    sys.exit(main())
