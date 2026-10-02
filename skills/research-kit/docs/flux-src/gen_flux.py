"""Génère docs/flux.html, le schéma du flux du kit, depuis page.tpl et la table des étapes ci-dessous.

Usage : python3 docs/flux-src/gen_flux.py
À relancer après toute modification de pipeline.md ou guardrails.md qui touche au flux.
"""
import os
from html import escape as e

ICI = os.path.dirname(os.path.abspath(__file__))

X, W, CX = 190, 290, 335          # colonne principale
RX, RW = 570, 220                 # colonne des fichiers
BAR = 100                         # barre de trace
P, H = 92, 64                     # pas vertical, hauteur d'une étape

rows = [
 ("Demande", "question, vérification, comparaison", "rédaction sourcée", "n"),
 ("SKILL.md", "déclenche le kit, déclare les prérequis", "dossier de travail désigné ou non", "m"),
 ("guardrails.md", "posture, bornes B1 à B7, sources, trace", "lu en entier à chaque tâche", "m"),
 ("Étape 0 : triage", "verbe, profondeur L0 à L3, lentilles", "date du jour lue dans l'environnement", "n"),
 ("Étapes 1 et 2 : cadrage, plan", "prémisse testée, périmètre figé (B1)", "une requête vise à réfuter", "n"),
 ("Étape 3 : collecte", "rôle researcher, lecture seule (B2)", "chaque page ouverte avant citation", "n"),
 ("Étapes 4 et 5 : sources, registre", "qui produit, qui finance, quelle date", "une ligne par affirmation clé", "n"),
 ("Étape 6 : synthèse", "la réponse d'abord, courte", "faits, interprétations, recommandations", "n"),
 ("Étape 7 : vérification", "rôle verifier, relecture contradictoire", "échec : une relance, puis dégradé", "key"),
 ("Étape 8 : livraison", "réponse, points clés étiquetés,", "lacunes, garantie, trace", "n"),
]
# (ligne, titre, sous1, sous2, sens, label, style, mono)
side = [
 (1, "lite.md", "si le contexte est limité :", "remplace pipeline.md", "out", "mobile", "", True),
 (3, "Règles de bascule", "sensible ou temps réel :", "L0 interdit (S1)", "in", "contraint", "", False),
 (4, "lenses/", "deux lentilles au maximum", "+ _technique.md si chiffre ou norme", "in", "lit", "", True),
 (5, "Budget et arrêt (B5, B6)", "budget atteint ou saturation :", "arrêt et rapport d'état", "in", "borne", "stop", False),
 (6, "claims.json", "affirmation, source, date,", "requête, extrait, étiquette", "out", "écrit", "", True),
 (8, "pieges.md, check_claims.py", "script : trace, budgets, extraits", "puis 43 pièges au jugement", "in", "lit", "key", False),
 (9, "Niveau de garantie", "contrôles : script ou manuels", "vérification : indépendante ou non", "out", "déclare", "", False),
]

def y(i): return 30 + i * P
def cy(i): return y(i) + H // 2

o = []
o.append('<svg viewBox="0 0 800 1010" role="img" aria-label="Flux du kit : une demande passe par SKILL.md, guardrails.md, le triage, puis les étapes 1 à 8, avec une trace écrite à chaque étape et un niveau de garantie annoncé à la livraison" xmlns="http://www.w3.org/2000/svg">')
o.append('<defs>'
 '<marker id="a-flow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto"><path class="mk-flow" d="M0 1 L10 5 L0 9 z"/></marker>'
 '<marker id="a-side" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path class="mk-side" d="M0 1 L10 5 L0 9 z"/></marker>'
 '<marker id="a-trace" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path class="mk-trace" d="M0 1 L10 5 L0 9 z"/></marker>'
 '</defs>')

# barre de trace
o.append(f'<text class="t" x="{BAR}" y="{cy(3)-34}" text-anchor="middle" font-weight="600" font-size="12">trace.jsonl</text>')
o.append(f'<text class="s" x="{BAR}" y="{cy(3)-20}" text-anchor="middle" font-size="10.5">au fil de l\'exécution</text>')
o.append(f'<line class="trace" x1="{BAR}" y1="{cy(3)}" x2="{BAR}" y2="{cy(9)}"/>')

# étapes principales
for i, (t, s1, s2, k) in enumerate(rows):
    cls = {"n": "box", "m": "box", "key": "box key"}[k]
    o.append(f'<rect class="{cls}" x="{X}" y="{y(i)}" width="{W}" height="{H}" rx="4"/>')
    fam = ' class="t mono"' if k == "m" else ' class="t"'
    o.append(f'<text{fam} x="{X+14}" y="{y(i)+22}" font-weight="600" font-size="13">{e(t)}</text>')
    o.append(f'<text class="s" x="{X+14}" y="{y(i)+39}" font-size="11">{e(s1)}</text>')
    o.append(f'<text class="s" x="{X+14}" y="{y(i)+53}" font-size="11">{e(s2)}</text>')
    if i < len(rows) - 1:
        o.append(f'<line class="flow" x1="{CX}" y1="{y(i)+H}" x2="{CX}" y2="{y(i+1)-3}" marker-end="url(#a-flow)"/>')
o.append(f'<text class="s" x="{CX+8}" y="{y(1)+H+19}" font-size="10.5">toujours</text>')
o.append(f'<text class="s" x="{CX+8}" y="{y(2)+H+19}" font-size="10.5">à chaque tâche</text>')

# ticks de trace
for i in range(3, 9):
    o.append(f'<line class="trace-t" x1="{X-2}" y1="{cy(i)}" x2="{BAR+4}" y2="{cy(i)}" marker-end="url(#a-trace)"/>')
o.append(f'<line class="trace-t" x1="{BAR}" y1="{cy(9)}" x2="{X-3}" y2="{cy(9)}" marker-end="url(#a-trace)"/>')
o.append(f'<text class="s" x="{(BAR+X)//2}" y="{cy(9)-7}" text-anchor="middle" font-size="10.5">livrée</text>')

# fichiers et règles à droite
for (r, t, s1, s2, sens, lab, st, mono) in side:
    by = cy(r) - 28
    cls = "box side-box" + (" key" if st == "key" else "") + (" stop" if st == "stop" else "")
    o.append(f'<rect class="{cls}" x="{RX}" y="{by}" width="{RW}" height="56" rx="4"/>')
    fam = 't mono' if mono else 't'
    o.append(f'<text class="{fam}" x="{RX+12}" y="{by+20}" font-weight="600" font-size="12">{e(t)}</text>')
    o.append(f'<text class="s" x="{RX+12}" y="{by+36}" font-size="11">{e(s1)}</text>')
    o.append(f'<text class="s" x="{RX+12}" y="{by+49}" font-size="11">{e(s2)}</text>')
    if sens == "out":
        o.append(f'<line class="side" x1="{X+W+2}" y1="{cy(r)}" x2="{RX-2}" y2="{cy(r)}" marker-end="url(#a-side)"/>')
    else:
        o.append(f'<line class="side" x1="{RX}" y1="{cy(r)}" x2="{X+W+4}" y2="{cy(r)}" marker-end="url(#a-side)"/>')
    o.append(f'<text class="s" x="{(X+W+RX)//2}" y="{cy(r)-6}" text-anchor="middle" font-size="10.5">{e(lab)}</text>')

# légende
ly = 985
o.append(f'<line class="flow" x1="{BAR-40}" y1="{ly}" x2="{BAR}" y2="{ly}" marker-end="url(#a-flow)"/>')
o.append(f'<text class="s" x="{BAR+10}" y="{ly+4}" font-size="11">enchaînement des étapes</text>')
o.append(f'<line class="side" x1="320" y1="{ly}" x2="360" y2="{ly}" marker-end="url(#a-side)"/>')
o.append(f'<text class="s" x="370" y="{ly+4}" font-size="11">lecture ou écriture d\'un fichier</text>')
o.append(f'<line class="trace-t" x1="610" y1="{ly}" x2="650" y2="{ly}" marker-end="url(#a-trace)"/>')
o.append(f'<text class="s" x="660" y="{ly+4}" font-size="11">ligne de trace</text>')
o.append('</svg>')
svg = "\n".join(o)

html = open(os.path.join(ICI, "page.tpl"), encoding="utf-8").read().replace("%%SVG%%", svg)
sortie = os.path.join(ICI, "..", "flux.html")
with open(sortie, "w", encoding="utf-8") as f:
    f.write(html)
print("écrit", os.path.normpath(sortie), len(html), "octets")
