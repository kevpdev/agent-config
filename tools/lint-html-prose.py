#!/usr/bin/env python3
"""Relève les tics de rédaction interdits dans le texte visible d'un document HTML.

Outil du skill `dev-tech-comparison`, action `check`. Lit le fichier, n'exécute rien,
n'appelle aucun LLM.

Le texte visible, c'est le `<title>` plus le `<body>`, privé de `pre`, `code`, `svg`,
`style` et `script`. Les règles de rédaction ne portent pas sur le code, et un `!=` ou
un `;` dans une ligne de code ne sont pas de la prose.

Deux familles de motifs, et la coupe est ce qui rend le code de sortie utilisable :

- **interdits** : un motif qui n'a aucune occurrence légitime en prose. Une ligne
  relevée est un défaut, et le code de sortie passe à 1.
- **à trier** : un motif qui a des occurrences légitimes (le deux-points d'un libellé,
  un nom de produit en capitales, un « pas… mais » qui n'oppose rien, une emphase
  sans laquelle la phrase boite). Il s'affiche pour la relecture et ne change pas le
  code de sortie.

*Pourquoi la coupe* : mesuré sur le script d'origine du prompt, `\\S : \\S` relève
chaque deux-points de la typographie française. Un code de sortie qui dépend de lui
sort rouge sur un document conforme, et un instrument toujours rouge ne tranche rien.

*Ce que le script d'origine ratait* : il coupe tout ce qui précède `<body`, donc le
`<title>` n'est jamais lu, alors que le prompt y interdit nommément le tiret long.

*Ce que le script ne voit pas, et que le relecteur couvre à la main* : le deux-points
collé au mot (« modèle: »), l'espace des milliers (1000), l'unité collée (100g), les
libellés en capitales, les questions rhétoriques, les `<details>` et toute tournure
bannie dont la forme varie trop pour une regex.

Sortie : 0 si aucun interdit, 1 si au moins un, 2 si le fichier est illisible.
"""

from __future__ import annotations

import argparse
import html
import re
import sys

# Espaces qu'un document français met autour d'un deux-points : l'espace simple, et les
# deux insécables qu'`html.unescape` rend pour `&nbsp;` et `&#8239;`.
SP = r"[   ]"

FORBIDDEN = {
    "point-virgule": r";",
    # Le demi-cadratin entre deux chiffres est une plage (2023–2025), pas une ponctuation.
    "tiret long": r"—|(?<!\d)–|–(?!\d)",
    "exclamation": r"!",
    "formule": (
        r"(?i)règle d'or|vrai piège|sournois|change(r)? la donne"
        r"|deux règles suffisent|reste à savoir|concrètement|\ben somme\b|en définitive"
        r"|il est important de noter|force est de constater"
    ),
    # Les Dingbats (U+2700 à U+27BF) sauf ✓ (U+2713) et ✗ (U+2717), signes de tableau.
    "emoji": "[\U0001F300-\U0001FAFF\u2600-\u26FF\u2700-\u2712\u2714-\u2716\u2718-\u27BF\u2B50\u2B55]",
}

TO_SORT = {
    # La règle garde l'emphase quand la phrase devient bancale sans elle.
    "emphase": r"[Cc]'est (là|ce|elle|lui) (que|qui)",
    "contraste": (
        r"\bpas .{1,40}\bmais\b|, pas (un|une|des|le|la|les|de)\b|ne tient pas tant"
        r"|[Ii]l ne s'agit pas"
    ),
    # Bannies au sens figuré seulement : « la clé » d'une table ou un outil gratuit passent.
    # « en cascade » a aussi un sens technique, la suppression en cascade d'une base.
    "formule": r"(?i)\bla clé\b|\bgratuit|en cascade",
    # Le point décimal d'un numéro de version (OCR 4.1) est légitime, d'où le tri.
    "typographie": r"\d\.\d|\"",
    "deux-points": rf"\S{SP}:{SP}\S",
    "title case": r"^(?:[A-ZÀ-Ý][\wÀ-ÿ'’-]*[,:]?\s+){2,}[A-ZÀ-Ý][\wÀ-ÿ'’-]*[.]?$",
}

HIDDEN = re.compile(r"<(pre|code|svg|style|script)\b.*?</\1>", re.S | re.I)
TAG = re.compile(r"<[^>]+>")
# Une balise en ligne ne coupe pas la phrase, sinon « pas <em>X</em> mais » échappe au
# contraste. Elle s'efface, et seules les autres balises deviennent des sauts de ligne.
INLINE = re.compile(
    r"</?(a|abbr|b|cite|em|i|kbd|mark|q|s|small|span|strong|sub|sup|time|u)\b[^>]*>", re.I
)
TITLE = re.compile(r"<title\b[^>]*>(.*?)</title>", re.S | re.I)
BODY = re.compile(r"<body\b", re.I)


def visible_lines(src: str) -> list[str]:
    """Le titre puis les lignes de texte du corps, code et figures retirés."""
    lines = []
    title = TITLE.search(src)
    if title:
        lines.append(html.unescape(TAG.sub("", title.group(1))).strip())
    start = BODY.search(src)
    body = src[start.start():] if start else ""
    body = INLINE.sub("", HIDDEN.sub("", body))
    text = html.unescape(TAG.sub("\n", body))
    lines.extend(l.strip() for l in text.split("\n"))
    return [l for l in lines if l]


# Une URL écrite en clair dans les sources n'est pas de la prose, son `;` ou son `!` non plus.
URL = re.compile(r"https?://\S+")


def excerpt(line: str, match: re.Match) -> str:
    """Une fenêtre de 160 caractères autour de ce qui a été relevé, pas le début de ligne."""
    start = max(0, match.start() - 60)
    prefix = "…" if start else ""
    suffix = "…" if start + 160 < len(line) else ""
    return prefix + line[start:start + 160] + suffix


def scan(src: str) -> tuple[list[str], list[str]]:
    """Rend les lignes relevées, interdits d'abord, à trier ensuite."""
    forbidden, to_sort = [], []
    for line in visible_lines(src):
        line = URL.sub("", line)
        for name, pat in FORBIDDEN.items():
            match = re.search(pat, line)
            if match:
                forbidden.append(f"[{name}] {excerpt(line, match)}")
        for name, pat in TO_SORT.items():
            match = re.search(pat, line)
            if match:
                to_sort.append(f"[{name}, à trier] {excerpt(line, match)}")
    return forbidden, to_sort


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("file", help="le document HTML à relire")
    args = parser.parse_args()
    try:
        with open(args.file, encoding="utf-8") as f:
            src = f.read()
    except (OSError, UnicodeDecodeError) as exc:
        print(f"illisible : {exc}", file=sys.stderr)
        return 2
    forbidden, to_sort = scan(src)
    for line in forbidden + to_sort:
        print(line)
    print(f"{len(forbidden)} interdit(s), {len(to_sort)} à trier")
    return 1 if forbidden else 0


if __name__ == "__main__":
    sys.exit(main())
