#!/usr/bin/env python3
"""Choisit le modèle OpenCode du banc et des évals, sur l'abonnement Go, quota contrôlé.

POURQUOI L'ABONNEMENT GO SEULEMENT
    Mesuré le 2026-10-26 : `opencode/deepseek-v4.1-flash-free` est refusé tant que le
    réglage Privacy du workspace n'autorise pas les modèles gratuits, `opencode/minimax-
    m3.1-flash-free` répond « Model unavailable », `opencode/deepseek-v4.1-flash` (Zen)
    n'a pas de crédit. `opencode-go/deepseek-v4.1-flash` répond. Un modèle hors
    `opencode-go/` est donc refusé, même s'il répond.

POURQUOI UN QUOTA LOCAL
    Aucune API ne donne le restant (`opencode.ai/docs/go` renvoie à la console). Chaque
    session garde son coût dans `session_v2.cost` d'`opencode.db`, et c'est ce qu'on
    additionne. La doc fixe trois fenêtres par modèle : 20 % du plafond mensuel sur 5 h,
    50 % sur 7 jours, 100 % sur 30 jours. On refuse dès 80 % d'une fenêtre.

CE QUE LE CONTRÔLE NE VOIT PAS
    La consommation d'une autre machine ou de la console. La bascule sur une erreur de
    limite Go, dans le banc et le driver, rattrape ce cas. La forme exacte de cette erreur
    dans le flux n'est pas mesurée : le binaire nomme `gousagelimiterror`, et on cherche
    `gousagelimit` sans casse ni séparateurs. La fenêtre de 30 jours glisse, supposé : la
    doc ne dit pas si c'est un mois calendaire.

Usage :
    python3 tools/bench/opencode-go.py                     le premier modèle de la chaîne sous le seuil
    python3 tools/bench/opencode-go.py --apres MODELE      le suivant après MODELE
    python3 tools/bench/opencode-go.py --modele MODELE     contrôler un modèle imposé
    python3 tools/bench/opencode-go.py --limite F...       0 si une sortie de session porte la limite Go

Le modèle retenu sort sur stdout, la consommation par fenêtre sur stderr.
Sortie : 0 si un modèle est retenu, 1 sinon.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3
import sys
import time

PREFIXE = "opencode-go/"
CHAINE = ["opencode-go/deepseek-v4.1-flash", "opencode-go/minimax-m3.1-flash"]
# Plafonds mensuels de l'offre Go à 10 $, en dollars (opencode.ai/docs/go, 2026-10-26).
PLAFONDS = {"opencode-go/deepseek-v4.1-flash": 80.0, "opencode-go/minimax-m3.1-flash": 20.0}
HEURE = 3600 * 1000
FENETRES = [("5 h", 5 * HEURE, 0.2), ("7 j", 7 * 24 * HEURE, 0.5), ("30 j", 30 * 24 * HEURE, 1.0)]
SEUIL = 0.8
DB = os.path.expanduser("~/.local/share/opencode/opencode.db")


def ouvrir(db: str):
    return sqlite3.connect(f"file:{db}?mode=ro", uri=True)


def nom(model) -> str:
    """`session_v2.model` est un JSON `{"id", "providerID"}`."""
    try:
        d = json.loads(model) if isinstance(model, str) else (model or {})
    except json.JSONDecodeError:
        return str(model)
    return "%s/%s" % (d.get("providerID", "?"), d.get("id", "?"))


def conso(con, modele: str, depuis_ms: int) -> float:
    total = 0.0
    for model, cost in con.execute(
            "select model, cost from session_v2 where time_created >= ?", (depuis_ms,)):
        if nom(model) == modele:
            total += cost or 0.0
    return total


def etat(con, modele: str, maintenant_ms: int) -> list[tuple[str, float, float]]:
    """(fenêtre, consommé, limite de refus) pour chaque fenêtre."""
    plafond = PLAFONDS[modele]
    return [(f, conso(con, modele, maintenant_ms - duree), plafond * part * SEUIL)
            for f, duree, part in FENETRES]


def controler(con, modele: str, maintenant_ms: int) -> str | None:
    """None si le modèle peut tourner, sinon le motif."""
    if not modele.startswith(PREFIXE):
        return f"{modele} n'est pas un modèle de l'abonnement Go ({PREFIXE}…)"
    if modele not in PLAFONDS:
        return f"{modele} n'a pas de plafond connu, à ajouter dans PLAFONDS"
    depasse = [f"{f} {c:.2f} $ ≥ {lim:.2f} $" for f, c, lim in etat(con, modele, maintenant_ms) if c >= lim]
    return f"{modele} au-delà de {SEUIL:.0%} : " + ", ".join(depasse) if depasse else None


def choisir(con, maintenant_ms: int, apres: str | None = None) -> tuple[str | None, list[str]]:
    """Le premier modèle de la chaîne qui peut tourner, et les motifs des écartés."""
    chaine = CHAINE[CHAINE.index(apres) + 1:] if apres in CHAINE else list(CHAINE)
    motifs = []
    for modele in chaine:
        motif = controler(con, modele, maintenant_ms)
        if motif is None:
            return modele, motifs
        motifs.append(motif)
    return None, motifs


def est_limite_go(erreur) -> bool:
    return "gousagelimit" in re.sub(r"[^a-z]", "", str(erreur or "").lower())


def suivant(modele: str) -> str | None:
    return CHAINE[CHAINE.index(modele) + 1] if modele in CHAINE[:-1] else None


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--db", default=DB)
    p.add_argument("--apres", help="modèle déjà essayé, prendre le suivant de la chaîne")
    p.add_argument("--modele", help="contrôler ce modèle au lieu de parcourir la chaîne")
    p.add_argument("--limite", nargs="+", metavar="FICHIER",
                   help="sortie 0 si l'un de ces fichiers porte une erreur de limite Go, 1 sinon")
    args = p.parse_args(argv)

    if args.limite:
        textes = (open(f, encoding="utf-8", errors="replace").read() for f in args.limite if os.path.isfile(f))
        return 0 if any(est_limite_go(t) for t in textes) else 1
    maintenant = int(time.time() * 1000)
    if not os.path.isfile(args.db):
        print(f"opencode-go — base introuvable : {args.db}", file=sys.stderr)
        return 1
    con = ouvrir(args.db)
    if args.modele:
        motif = controler(con, args.modele, maintenant)
        retenu, motifs = (None, [motif]) if motif else (args.modele, [])
    else:
        retenu, motifs = choisir(con, maintenant, args.apres)
    for m in motifs:
        print(f"opencode-go — écarté : {m}", file=sys.stderr)
    if not retenu:
        print("opencode-go — aucun modèle Go ne peut tourner.", file=sys.stderr)
        return 1
    fenetres = ", ".join(f"{f} {c:.2f}/{lim:.2f} $" for f, c, lim in etat(con, retenu, maintenant))
    print(f"opencode-go — {retenu} : {fenetres}", file=sys.stderr)
    print(retenu)
    return 0


if __name__ == "__main__":
    sys.exit(main())
