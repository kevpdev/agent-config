#!/usr/bin/env python3
"""mesure-reponses.py — mesure le style des RÉPONSES, pas des fichiers.

POURQUOI cet instrument existe : le harnais mesurait ses fichiers et n'avait jamais
mesuré une réponse. Le 2026-08-11, la dette de ponctuation a été payée dans les
fichiers (10,85 -> 2,17 tirets pour 1 000 mots) alors que les réponses de la même
session étaient à 13,93, soit pires que le point de départ des fichiers. Un défaut
qu'aucune commande du repo ne pouvait voir.

Usage :
    python3 mesure-reponses.py <transcript.jsonl>
    python3 mesure-reponses.py            # dernier transcript du projet courant

Baseline pré-enregistrée (2026-08-11 18h, session agent-config, 258 réponses) :
    tirets cadratins   13,93 / 1 000 mots
    points-virgules     1,77 / 1 000 mots
    phrases > 30 mots   240 sur 1 398  (17 %)
    ouvertures abstraites  39 sur 112
    demandes de reformulation  12 sur 110 prompts

Cible : la ponctuation s'aligne sur ponctuation.md (1,09 point-virgule). Les trois
autres n'ont pas de cible chiffrée, elles servent de comparaison avant/après.

LIMITE DE L'INSTRUMENT, à lire avant de conclure. Il compte des formes, pas du sens.
« Trop technique » et « flou » ne sont pas mesurés ici et ne le seront pas : aucun
comptage ne les distingue. Un zéro sur les quatre compteurs ne vaut donc pas
« la réponse est claire ». Cf. le trigger « un comptage qui rend zéro » de reasoning.md.
"""
import json
import re
import sys
import glob
import os
import unicodedata

SEUIL_FOND = 60      # une réponse de fond, par opposition à la narration d'un tool call
SEUIL_PHRASE = 30    # au-delà, la phrase demande une relecture

# Une ouverture concrète porte un chiffre, un chemin, une citation ou du code inline.
CONCRET = re.compile(r"\d|`|/|\.md|«|\"")

# Formulations par lesquelles l'utilisateur redemande la même chose plus simplement.
# Les accents sont retirés des deux côtés avant de matcher : l'utilisateur tape
# « pour etre clair », « ca veut dire », « rexplique ». Une regex accentuée en
# ratait une occurrence sur douze, mesuré le 2026-08-11 en calibrant l'instrument.
REFORMULATION = re.compile(
    r"plus simple|simplement|c'est quoi|ca veut dire|signifie quoi|explique|xplique"
    r"|pour etre clair|consiste a quoi|fait quoi|comprends pas|c'est flou",
    re.I,
)


def sans_accent(s):
    return (unicodedata.normalize("NFD", s)
            .encode("ascii", "ignore")
            .decode("ascii"))


def charge(path):
    """Rend (réponses assistant, prompts utilisateur) en texte brut."""
    replies, prompts = [], []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            try:
                e = json.loads(line)
            except ValueError:
                continue
            m = e.get("message") or {}
            role, c = m.get("role"), m.get("content")
            if not role or c is None:
                continue
            if isinstance(c, str):
                txt = c
            else:
                txt = "\n".join(
                    b.get("text", "")
                    for b in c
                    if isinstance(b, dict) and b.get("type") == "text"
                )
            txt = txt.strip()
            if not txt:
                continue
            if role == "assistant":
                replies.append(txt)
            elif role == "user" and not txt.startswith("<"):
                prompts.append(txt)
    return replies, prompts


def premiere_ligne(t):
    for l in t.split("\n"):
        if l.strip():
            return l.strip()
    return ""


def phrases(t):
    """Phrases de prose : les blocs de code et les lignes de tableau ne comptent pas."""
    prose = re.sub(r"```.*?```", " ", t, flags=re.S)
    prose = re.sub(r"^\|.*$", " ", prose, flags=re.M)
    return [len(s.split()) for s in re.split(r"(?<=[.!?])\s+", prose) if len(s.split()) > 2]


def main():
    if len(sys.argv) > 1:
        path = sys.argv[1]
    else:
        pat = os.path.expanduser("~/.claude/projects/*/*.jsonl")
        cands = sorted(glob.glob(pat), key=os.path.getmtime)
        if not cands:
            sys.exit("aucun transcript trouvé, passer le chemin en argument")
        path = cands[-1]

    replies, prompts = charge(path)
    if not replies:
        sys.exit("aucune réponse texte dans " + path)

    fond = [r for r in replies if len(r.split()) >= SEUIL_FOND]
    if not fond:
        sys.exit("aucune réponse de fond (>= %d mots)" % SEUIL_FOND)

    mots = sum(len(r.split()) for r in fond)
    em = sum(r.count(" — ") for r in fond)
    sc = sum(r.count(" ; ") for r in fond)
    sents = sorted(n for r in fond for n in phrases(r))
    longues = sum(1 for n in sents if n > SEUIL_PHRASE)
    abstraites = sum(1 for r in fond if not CONCRET.search(premiere_ligne(r)))
    reform = sum(1 for p in prompts
                 if len(p) < 200 and REFORMULATION.search(sans_accent(p)))

    print("transcript : %s" % path)
    print("réponses %d, dont %d de fond, %d mots de prose"
          % (len(replies), len(fond), mots))
    print()
    print("tirets cadratins      %6.2f / 1 000   (baseline 13,93)" % (em * 1000 / mots))
    print("points-virgules       %6.2f / 1 000   (baseline 1,77, cible 1,09)"
          % (sc * 1000 / mots))
    print("phrases > %d mots      %4d sur %d  (%d %%)  (baseline 17 %%)"
          % (SEUIL_PHRASE, longues, len(sents), round(100 * longues / len(sents))))
    print("ouvertures abstraites   %4d sur %d          (baseline 39 sur 112)"
          % (abstraites, len(fond)))
    print("demandes de reformul.   %4d sur %d prompts  (baseline 12 sur 110)"
          % (reform, len(prompts)))
    print()
    print("Rappel : ces cinq compteurs ne voient pas « trop technique » ni « flou ».")


if __name__ == "__main__":
    main()
