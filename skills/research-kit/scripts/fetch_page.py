#!/usr/bin/env python3
"""Ouvre une page une seule fois, la garde en cache et n'affiche que l'utile (pipeline.md, étape 3).

Usage :
    python3 fetch_page.py <url> [--dossier D] [--cherche "motif" ...] [--mots 400]

    --dossier   dossier de travail de la tâche. Le cache vit dans D/pages/. Sans lui, un
                dossier temporaire est créé et son chemin affiché : le repasser aux appels
                suivants, puis à check_claims.py --cache.
    --cherche   affiche les 3 premières occurrences du motif, avec 300 caractères de contexte,
                pour relever l'extrait verbatim sans relire la page. Répétable. La recherche
                ignore la casse, les accents et les espaces multiples.
    --mots      sans --cherche, nombre de mots affichés depuis le début du texte.

Un deuxième appel sur la même URL lit le cache, sans réseau, y compris pour un échec.

Codes de sortie, tranchés d'avance (pipeline.md, étape 3, politique d'échec) :
    0  page lue, texte en cache
    3  écartée : HTTP 401, 403, 429 ou paywall. Ne pas relancer, passer à une autre source
    4  URL morte : HTTP 404 ou 410
    5  non vérifiable : page sans texte, contenu non textuel, PDF illisible, erreur réseau
"""
import argparse
import re
import sys
import tempfile

import pages

CODES = {pages.OK: 0, pages.ECARTEE: 3, pages.MORTE_STATUT: 4, pages.NON_VERIFIABLE: 5}
OCCURRENCES = 3
CONTEXTE = 300


def plier(texte):
    """Texte normalisé caractère par caractère, avec la position d'origine de chaque caractère.

    Permet de chercher sans casse ni accents tout en citant le texte d'origine, verbatim.
    """
    plie, positions = [], []
    espace = False
    for i, c in enumerate(texte):
        n = pages.norm(c) if not c.isspace() else " "
        if n == " ":
            if espace or not plie:
                continue
            espace = True
        else:
            espace = False
        for k in n:
            plie.append(k)
            positions.append(i)
    return "".join(plie), positions


def passages(texte, motif):
    plie, pos = plier(texte)
    cible = pages.norm(motif)
    sortie, debut = [], 0
    while len(sortie) < OCCURRENCES and cible:
        j = plie.find(cible, debut)
        if j < 0:
            break
        a = pos[j]
        b = pos[min(j + len(cible), len(pos)) - 1] + 1
        g, d = max(0, a - CONTEXTE // 2), min(len(texte), b + CONTEXTE // 2)
        sortie.append(("…" if g else "") + texte[g:d] + ("…" if d < len(texte) else ""))
        debut = j + len(cible)
    return sortie


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("url")
    p.add_argument("--dossier")
    p.add_argument("--cherche", action="append", default=[])
    p.add_argument("--mots", type=int, default=400)
    args = p.parse_args()

    dossier = args.dossier or tempfile.mkdtemp(prefix="research-kit-")
    entree, texte, depuis_cache = pages.lire_page(args.url, pages.Cache(dossier))

    source = "cache" if depuis_cache else "réseau"
    detail = f", {entree['note']}" if entree.get("note") else ""
    if entree["statut"] == pages.OK:
        print(f"[OK] {args.url} ({source}, {entree['type']}, {len(texte.split())} mots, "
              f"lu le {entree['date_acces']}{detail})")
    else:
        libelle = {pages.ECARTEE: "ÉCARTÉE", pages.MORTE_STATUT: "MORTE"}.get(
            entree["statut"], "NON VÉRIFIABLE")
        print(f"[{libelle}] {args.url} ({source}{detail})")
    print(f"dossier : {dossier}")
    if texte is None:
        return CODES[entree["statut"]]

    if args.cherche:
        for motif in args.cherche:
            trouves = passages(texte, motif)
            print(f"\n« {motif} » : {len(trouves)} occurrence(s)"
                  + (f", {OCCURRENCES} premières" if len(trouves) == OCCURRENCES else ""))
            for t in trouves:
                print(f"  - {t}")
    else:
        mots = texte.split()
        print("\n" + " ".join(mots[:args.mots]) + (" …" if len(mots) > args.mots else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
