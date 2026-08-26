#!/usr/bin/env python3
"""Lint mécanique des skills de `skills/` : lit les fichiers, n'exécute rien.

Sept vérifications, toutes sans interprétation — un skill conforme passe en une
seconde et sans appel LLM :

1. le frontmatter parse en YAML strict et porte `name`, `description`, `argument-hint`
2. `name` est égal au nom du dossier
3. la `description` tient sous 1 536 caractères
4. les `##` du fichier correspondent à ceux de son gabarit : aucune manquante,
   aucune en trop, dans l'ordre
5. aucun placeholder `<...>` oublié
6. aucun lien markdown relatif mort
7. un skill qui porte `disable-model-invocation: true` ne promet pas de déclenchement
   ailleurs : ni phrase déclencheuse dans sa description (R5), ni cas d'éval positif (R7)

**La liste de sections n'est pas codée ici.** Elle est dérivée des deux gabarits de
`skills/skill-craft/assets/`, qui font foi. Une liste décrite à deux endroits diverge
au premier edit de l'une des deux ; dérivée, elle ne peut pas.

**Ce que ce lint ne vérifie surtout pas** : tout ce qui demande de comprendre ce que
le skill *fait*. Un comptage de « push » ou « commit » attrape `security-reviewer`,
qui cite ces mots pour décrire du code qu'il relit sans rien exécuter. Un lint qui
refuse du travail valide finit désactivé, et on perd aussi ses refus justes.

C'est la moitié de R13 que la vérification 7 laisse dehors : elle ne sait pas dire
qu'un skill qui écrit aurait dû porter le champ, seulement qu'un skill qui le porte
se contredit ailleurs. Détecter l'effet de bord reste à `skill-craft:02-validate`.

Échec fermé : tout ce qui empêche de conclure rend 2 (racine douteuse, gabarit
absent ou illisible, PyYAML manquant). Un défaut mesuré rend 1. Tout au vert rend 0.

Décidé par `audits/2026-08-24-cadrage-refonte-skills-cible.md`, sections 2 et 4.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys

DESCRIPTION_MAX = 1536
FRONTMATTER_KEYS = ("name", "description", "argument-hint")

# Les tournures par lesquelles une description promet un déclenchement automatique.
# Deux suffisent : R5 impose « Utiliser quand » comme forme unique de la liste de
# phrases, et « Utiliser AUSSI » est sa variante proactive.
TRIGGER_PHRASES = ("Utiliser quand", "Utiliser AUSSI")

# Les sections que la refonte supprime, et où va leur contenu (note de cadrage,
# section 2). Le message de l'échec les nomme, pour que le lint dise quoi faire au
# lieu de constater. Comparaison par préfixe : un intitulé réel porte souvent une
# parenthèse de précision (`## Garde-fou — vault requis (raison : …)`).
HOMES = {
    "Contrôle de sortie": (
        "un critère qui décide en cours de route devient une étape `**Garde.**` du "
        "`## Process`, un critère qui constate devient une ligne du `## Test`"
    ),
    "Ne pas s'activer pour": (
        "rien : c'est la clause NE PAS de la `description`, recopiée"
    ),
    "Rôle": "la phrase de portée sous le titre",
    "Règles strictes": "`## Transversal rules`",
    "Règles transverses": "`## Transversal rules`, en anglais",
    "Références": "`## References`, en anglais",
    "Si ça casse": "des sous-puces de l'étape concernée du `## Process`",
    "Garde-fou": "la première étape du `## Process`",
    "Contexte": "`## Input`",
    "Méthode": "`## Process`",
    "Instructions": "`## Process`",
    "Notes": (
        "par nature : une règle qui vaut pour tout le skill va en "
        "`## Transversal rules`, un repli ou un cas particulier va en sous-puce "
        "de son étape du `## Process`, un renvoi vers un frère va en clause NE PAS "
        "de la `description`"
    ),
    "Sortie": "`## Output`",
    "Verdict": "`## Output`",
    "Délégation": "une étape du `## Process`",
    "Flux": "le flux mermaid sous le titre",
    "Le flux": "le flux mermaid sous le titre",
    "Hors périmètre": "la clause NE PAS de la `description`",
    "Hors scope": "la clause NE PAS de la `description`",
    "Avant": "une étape du `## Process`",
    "Pendant": "une étape du `## Process`",
    "Après": "une étape du `## Process`",
}

HOME_DEFAULT = (
    "aucun équivalent nommé. Ranger par la NATURE du contenu, jamais par son "
    "titre : connaissance (table de choix, corpus de critères, patterns) → "
    "sous-puce de l'étape du `## Process` qui l'utilise, tant que le fichier "
    "tient sous le seuil de R4 ; portée du skill → la phrase sous le titre ; "
    "liste de délégations vers des frères → la clause NE PAS de la "
    "`description` ; règle qui vaut pour tout le skill → `## Transversal "
    "rules` ; opération appelable → une étape du `## Process`, l'ordre étant "
    "celui de l'appel naturel ; le reste → `## Input`, `## Output`, "
    "`## Process` ou `## Test`"
)


class CannotConclude(Exception):
    """Le mécanisme ne peut pas rendre de verdict — se traduit par exit 2."""


# --- lecture ---------------------------------------------------------------


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


def read(path: str) -> str:
    try:
        with open(path, encoding="utf-8") as handle:
            return handle.read()
    except OSError as exc:
        raise CannotConclude(f"illisible : {path} ({exc})") from exc


def split_frontmatter(text: str) -> tuple[str | None, str]:
    """Rend (frontmatter brut ou None, corps). Un fichier sans `---` n'en a pas."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, text
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            return "\n".join(lines[1:index]), "\n".join(lines[index + 1 :])
    return None, text


def strip_fences(body: str) -> str:
    """Retire les blocs fencés : un `## X` dans un exemple n'est pas une section."""
    out, fenced = [], False
    for line in body.splitlines():
        if line.lstrip().startswith("```"):
            fenced = not fenced
            continue
        out.append("" if fenced else line)
    return "\n".join(out)


def sections(body: str) -> list[str]:
    """Les `##` du corps, dans l'ordre, hors blocs fencés."""
    return [
        line[3:].strip()
        for line in strip_fences(body).splitlines()
        if line.startswith("## ")
    ]


# --- gabarits --------------------------------------------------------------


class Slot:
    """Un emplacement de section du gabarit, et son statut."""

    def __init__(self, status: str, group: str | None) -> None:
        self.status = status  # OBLIGATOIRE | OPTIONNEL | ALTERNATIF
        self.group = group
        self.names: list[str] = []

    def __repr__(self) -> str:  # pragma: no cover - confort de debug
        return f"Slot({self.status},{self.group},{self.names})"


MARKER = re.compile(r"<(OBLIGATOIRE|OPTIONNEL|ALTERNATIF:([A-Za-z0-9_-]+))\b")


def parse_template(path: str) -> list[Slot]:
    """Dérive les emplacements de sections du gabarit, dans l'ordre.

    Le statut se lit dans le placeholder de la section, pas dans ce script : le
    gabarit reste la seule liste, lisible par l'humain comme par le lint.
    """
    body = split_frontmatter(read(path))[1]
    lines = strip_fences(body).splitlines()
    slots: list[Slot] = []
    groups: dict[str, Slot] = {}
    for index, line in enumerate(lines):
        if not line.startswith("## "):
            continue
        name = line[3:].strip()
        marker = None
        for following in lines[index + 1 :]:
            if following.strip():
                marker = MARKER.search(following)
                break
        if not marker:
            raise CannotConclude(
                f"{path} : la section `## {name}` ne déclare pas son statut "
                "(OBLIGATOIRE, OPTIONNEL ou ALTERNATIF:<groupe>)"
            )
        status = "ALTERNATIF" if marker.group(2) else marker.group(1)
        group = marker.group(2)
        if group and group in groups:
            groups[group].names.append(name)
            continue
        slot = Slot(status, group)
        slot.names.append(name)
        slots.append(slot)
        if group:
            groups[group] = slot
    if not slots:
        raise CannotConclude(f"{path} : aucune section déclarée, gabarit inexploitable")
    return slots


# --- vérifications ---------------------------------------------------------


class Defect:
    def __init__(self, path: str, rule: str, message: str) -> None:
        self.path, self.rule, self.message = path, rule, message


def check_frontmatter(path: str, raw: str | None, folder: str) -> list[Defect]:
    """Vérifications 1, 2 et 3, sur le seul fichier qui porte un frontmatter."""
    try:
        import yaml
    except ImportError as exc:  # pragma: no cover - dépendance d'environnement
        raise CannotConclude("PyYAML absent, le frontmatter ne peut pas être parsé") from exc

    if raw is None:
        return [Defect(path, "frontmatter", "aucun frontmatter `---`")]
    try:
        data = yaml.safe_load(raw)
    except yaml.YAMLError as exc:
        first = str(exc).splitlines()[0]
        return [Defect(path, "frontmatter", f"YAML invalide : {first}")]
    if not isinstance(data, dict):
        return [Defect(path, "frontmatter", "le frontmatter n'est pas un mapping")]

    found = []
    for key in FRONTMATTER_KEYS:
        if key not in data or data[key] in (None, ""):
            found.append(Defect(path, "frontmatter", f"clé `{key}` absente ou vide"))
    name = data.get("name")
    if name and name != folder:
        found.append(
            Defect(path, "name", f"`name: {name}` ≠ nom du dossier `{folder}`")
        )
    description = data.get("description")
    if isinstance(description, str) and len(description) > DESCRIPTION_MAX:
        found.append(
            Defect(
                path,
                "description",
                f"{len(description)} caractères, plafond {DESCRIPTION_MAX}",
            )
        )
    return found


def check_invocation(path: str, raw: str | None, skill_dir: str) -> list[Defect]:
    """Vérification 7 : la cohérence interne d'un skill à invocation manuelle (R13).

    Ne cherche pas à savoir si le skill a un effet de bord, ce que le docstring du
    module explique. Une fois le champ posé, deux promesses de déclenchement se
    lisent mécaniquement, et R5 comme R7 les interdisent nommément.
    """
    if raw is None:
        return []
    import yaml  # check_frontmatter a déjà tranché l'absence de PyYAML

    try:
        data = yaml.safe_load(raw)
    except yaml.YAMLError:
        return []  # check_frontmatter porte déjà ce défaut, ne pas le doubler
    if not isinstance(data, dict) or data.get("disable-model-invocation") is not True:
        return []

    found = []
    description = data.get("description")
    if isinstance(description, str):
        for phrase in TRIGGER_PHRASES:
            if phrase in description:
                found.append(
                    Defect(
                        path,
                        "invocation",
                        f"`disable-model-invocation: true` et « {phrase} » dans la "
                        "description : un skill manuel ne promet aucun déclenchement, "
                        "il dit par quoi on l'appelle (R5)",
                    )
                )

    eval_path = os.path.join(skill_dir, "evals", "eval.json")
    if os.path.isfile(eval_path):
        try:
            cases = json.loads(read(eval_path))
        except json.JSONDecodeError:
            return found  # un corpus illisible n'est pas un défaut d'invocation
        if isinstance(cases, dict):
            cases = cases.get("cases", [])
        if isinstance(cases, list):
            positives = [
                case.get("id", "cas sans `id`")
                for case in cases
                if isinstance(case, dict) and case.get("expect_trigger", True)
            ]
            if positives:
                found.append(
                    Defect(
                        eval_path,
                        "invocation",
                        f"{len(positives)} cas positif(s) sur un skill manuel "
                        f"({', '.join(positives)}) : son corpus n'a que des négatifs, "
                        "le contrat qui compte pour lui étant qu'il ne parte jamais "
                        "tout seul (R7)",
                    )
                )
    return found


def sections_named(home: str) -> list[str]:
    """Les sections `## X` que cette destination nomme, s'il y en a."""
    return [part.split("`")[0] for part in home.split("`## ")[1:]]


def home_of(name: str, allowed: set[str]) -> str:
    """La destination d'une section hors gabarit, bornée aux sections que
    le gabarit du fichier autorise vraiment.

    `allowed` évite d'envoyer un `SKILL.md` vers `## Input`, qui n'existe que
    dans `action-template.md` — le correcteur y créerait un nouveau défaut.
    Mesuré le 2026-08-26 sur `vault-capture-projet`, section `## Contexte`.
    """
    for prefix, home in HOMES.items():
        if name == prefix or name.startswith(prefix + " ") or name.startswith(prefix + " ("):
            if all(section in allowed for section in sections_named(home)):
                return home
            break
    return HOME_DEFAULT


def check_sections(path: str, body: str, slots: list[Slot]) -> list[Defect]:
    """Vérification 4 : aucune manquante, aucune en trop, dans l'ordre."""
    present = sections(body)
    known = {name: slot for slot in slots for name in slot.names}
    found: list[Defect] = []

    for name in present:
        if name not in known:
            found.append(
                Defect(
                    path,
                    "sections",
                    f"`## {name}` est hors gabarit → {home_of(name, set(known))}",
                )
            )

    for slot in slots:
        hits = [name for name in present if name in slot.names]
        if slot.status == "OBLIGATOIRE" and not hits:
            found.append(
                Defect(path, "sections", f"`## {slot.names[0]}` manque (obligatoire)")
            )
        elif slot.status == "ALTERNATIF":
            alternatives = " ou ".join(f"`## {name}`" for name in slot.names)
            if not hits:
                found.append(
                    Defect(path, "sections", f"il faut {alternatives}, aucune n'est là")
                )
            elif len(hits) > 1:
                found.append(
                    Defect(
                        path,
                        "sections",
                        f"{alternatives} s'excluent, les deux sont là",
                    )
                )

    order = [name for name in present if name in known]
    expected = [name for slot in slots for name in slot.names if name in order]
    if order != expected:
        found.append(
            Defect(
                path,
                "sections",
                "ordre du gabarit non respecté : "
                + " → ".join(order)
                + " au lieu de "
                + " → ".join(expected),
            )
        )
    return found


INLINE_CODE = re.compile(r"`[^`\n]*`")
PLACEHOLDER = re.compile(r"<[^<>\n]{1,300}>")


def check_placeholders(path: str, body: str) -> list[Defect]:
    """Vérification 5. Un chevron dans du code inline est de la notation, pas un reste.

    Le gabarit pose ses placeholders nus, hors backticks. Discriminer là-dessus
    laisse passer `$SKILLS_ROOT/<nom>/`, qui est de la notation légitime, et attrape
    la ligne recopiée du gabarit, qui ne l'est jamais.
    """
    text = INLINE_CODE.sub("", strip_fences(body))
    found = []
    for match in PLACEHOLDER.finditer(text):
        span = match.group(0)
        if "://" in span or span.startswith("</"):
            continue
        found.append(Defect(path, "placeholder", f"placeholder du gabarit resté : {span}"))
    return found


LINK = re.compile(r"\[[^\]\n]*\]\(([^)\s]+)\)")


def check_links(path: str, body: str) -> list[Defect]:
    """Vérification 6 : un lien markdown relatif qui ne résout pas."""
    here = os.path.dirname(path)
    found = []
    for match in LINK.finditer(strip_fences(body)):
        target = match.group(1).split("#")[0]
        if not target or target.startswith(("http", "mailto:", "/", "~", "$", "#")):
            continue
        if not os.path.exists(os.path.join(here, target)):
            found.append(Defect(path, "liens", f"lien relatif mort : {target}"))
    return found


# --- parcours --------------------------------------------------------------


def lint_skill(skill_dir: str, templates: dict[str, list[Slot]]) -> list[Defect]:
    folder = os.path.basename(skill_dir.rstrip(os.sep))
    found: list[Defect] = []

    skill_md = os.path.join(skill_dir, "SKILL.md")
    if not os.path.isfile(skill_md):
        return [Defect(skill_md, "frontmatter", "SKILL.md absent")]

    raw, body = split_frontmatter(read(skill_md))
    found += check_frontmatter(skill_md, raw, folder)
    found += check_invocation(skill_md, raw, skill_dir)
    found += check_sections(skill_md, body, templates["skill"])
    found += check_placeholders(skill_md, body)
    found += check_links(skill_md, body)

    actions_dir = os.path.join(skill_dir, "actions")
    if os.path.isdir(actions_dir):
        for name in sorted(os.listdir(actions_dir)):
            if not name.endswith(".md"):
                continue
            path = os.path.join(actions_dir, name)
            action_body = split_frontmatter(read(path))[1]
            found += check_sections(path, action_body, templates["action"])
            found += check_placeholders(path, action_body)
            found += check_links(path, action_body)

    # Les références n'ont pas de liste de sections : elles ne sont copiées depuis
    # aucun gabarit. Seuls leurs liens se vérifient. `assets/` est exclu en entier,
    # un gabarit étant fait de placeholders.
    references_dir = os.path.join(skill_dir, "references")
    if os.path.isdir(references_dir):
        for name in sorted(os.listdir(references_dir)):
            if name.endswith(".md"):
                path = os.path.join(references_dir, name)
                found += check_links(path, split_frontmatter(read(path))[1])

    return found


def load_templates(root: str) -> dict[str, list[Slot]]:
    assets = os.path.join(root, "skills", "skill-craft", "assets")
    return {
        "skill": parse_template(os.path.join(assets, "skill-template.md")),
        "action": parse_template(os.path.join(assets, "action-template.md")),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--skill",
        action="append",
        default=[],
        help="nom d'un skill à linter, répétable. Sans lui, tous.",
    )
    args = parser.parse_args()

    root = derive_root()
    templates = load_templates(root)
    skills_dir = os.path.join(root, "skills")

    wanted = args.skill or sorted(
        name
        for name in os.listdir(skills_dir)
        if os.path.isdir(os.path.join(skills_dir, name)) and not name.startswith("_")
    )

    total, failed = 0, []
    for name in wanted:
        skill_dir = os.path.join(skills_dir, name)
        if not os.path.isdir(skill_dir):
            raise CannotConclude(f"skill introuvable : {skill_dir}")
        defects = lint_skill(skill_dir, templates)
        total += len(defects)
        if defects:
            failed.append(name)
            print(f"\n{name}")
            for defect in defects:
                relative = os.path.relpath(defect.path, root)
                print(f"  FAIL  {defect.rule:<12} {relative}\n        {defect.message}")

    print(
        f"\n{len(wanted) - len(failed)}/{len(wanted)} skills conformes, "
        f"{total} défaut(s)."
    )
    return 1 if total else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except CannotConclude as error:
        print(f"IMPOSSIBLE DE CONCLURE : {error}", file=sys.stderr)
        sys.exit(2)
