#!/usr/bin/env python3
"""Calibre check_claims.py : un cas valide doit passer, chaque défaut injecté doit échouer sur son critère.

Usage :
    python3 test_check_claims.py            # cas hors ligne
    python3 test_check_claims.py --reseau   # ajoute les cas --en-ligne (accès réseau requis)

Un `attendu` préfixé par « + » exige le succès et la présence du texte dans la sortie.
Les fichiers d'essai sont écrits dans un dossier temporaire, jamais dans le kit.
Code de sortie : 0 si tous les cas passent, 1 sinon.
"""
import copy
import json
import os
import subprocess
import sys
import tempfile

SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "check_claims.py")
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import pages  # noqa: E402

# URL jamais servie : le cas réussit seulement si la copie en cache est relue sans réseau.
EN_CACHE = "http://127.0.0.1:9/page-en-cache"

# Page stable et phrase relevée le 2026-10-02 dans son résumé.
RFC = "https://www.rfc-editor.org/rfc/rfc9110.html"
EXTRAIT = "The Hypertext Transfer Protocol (HTTP) is a stateless application-level protocol"
RFC_ABSENTE = "https://www.rfc-editor.org/rfc/rfc99999999.html"

CLAIMS = [
    {"id": 1, "claim": "HTTP est sans état", "source_url": RFC, "source_date": "2022-06",
     "source_type": "primaire", "requete": "rfc http semantics", "opened": True,
     "label": "Établi", "interet_source": "aucun", "extrait": EXTRAIT},
    {"id": 2, "claim": "b", "source_url": "https://fr.wikipedia.org/wiki/HTTP",
     "source_date": "2026-05", "source_type": "tertiaire", "requete": "http critique état",
     "opened": True, "label": "Probable", "interet_source": "aucun", "extrait": "x"},
    {"id": 3, "claim": "c", "requete": "http critique état", "opened": False,
     "label": "Non vérifié", "interet_source": "n/a"},
]
TRACE = [
    {"etape": 0, "verbe": "research", "profil": "research", "fraicheur": "stable",
     "risque": "faible", "profondeur": "L2", "lentilles": ["numerique-ia"],
     "date_du_jour": "2026-10-02"},
    {"etape": 1, "statut": "executee"},
    {"etape": 2, "statut": "executee"},
    {"etape": 3, "statut": "executee",
     "requetes": [{"q": "rfc http semantics", "refutation": False},
                  {"q": "http critique état", "refutation": True}],
     "pages_ouvertes": [RFC, "https://fr.wikipedia.org/wiki/HTTP/"]},
    {"etape": 4, "statut": "executee"}, {"etape": 5, "statut": "executee"},
    {"etape": 6, "statut": "executee"}, {"etape": 7, "statut": "executee"},
    {"etape": 8, "statut": "executee"},
]
REPONSE = """## Réponse
HTTP est sans état.
## Points clés
### Faits
- HTTP est sans état (Établi, RFC 9110, 2022-06)
### Interprétations
aucune
### Recommandations
aucune
## Ce que je n'ai pas pu vérifier
rien à signaler
## Niveau de garantie
contrôles : script. vérification : non indépendante. profil : research L2.
## Trace
voir trace.jsonl
"""


def variante(modif=None, reponse=None):
    c, t = copy.deepcopy(CLAIMS), copy.deepcopy(TRACE)
    if modif:
        modif(c, t)
    return c, t, reponse or REPONSE


def lancer(dossier, c, t, r, options=()):
    with open(os.path.join(dossier, "claims.json"), "w", encoding="utf-8") as f:
        json.dump(c, f, ensure_ascii=False)
    with open(os.path.join(dossier, "trace.jsonl"), "w", encoding="utf-8") as f:
        f.write("\n".join(json.dumps(l, ensure_ascii=False) for l in t))
    with open(os.path.join(dossier, "reponse.md"), "w", encoding="utf-8") as f:
        f.write(r)
    args = [sys.executable, SCRIPT, "claims.json", "--reponse", "reponse.md", *options]
    if t is not None:
        args[3:3] = ["--trace", "trace.jsonl"]
    return subprocess.run(args, cwd=dossier, capture_output=True, text=True)


def cas_hors_ligne():
    L = []
    L.append(("cas valide", variante(), None))
    L.append(("étape exigée marquée sautée",
              variante(lambda c, t: t[2].update(statut="sautee", raison="x")), "exigée en L2"))
    L.append(("étape absente", variante(lambda c, t: t.pop(5)), "étape 5 absente"))
    L.append(("étape sautée sans raison",
              variante(lambda c, t: t.__setitem__(2, {"etape": 2, "statut": "sautee"})),
              "sautée sans raison"))
    L.append(("fact-check peut sauter l'étape 2",
              variante(lambda c, t: (t[0].update(profil="fact-check"),
                                     t[2].update(statut="sautee", raison="profil fact-check"))),
              None))
    L.append(("source hors des pages ouvertes",
              variante(lambda c, t: t[3].update(pages_ouvertes=[RFC])), "absente des pages ouvertes"))
    L.append(("requête du registre absente de la trace",
              variante(lambda c, t: c[0].update(requete="autre")), "absente de la trace"))
    L.append(("aucune requête de réfutation",
              variante(lambda c, t: [q.update(refutation=False) for q in t[3]["requetes"]]),
              "aucune requête marquée"))
    L.append(("budget de recherches dépassé",
              variante(lambda c, t: t[3]["requetes"].extend({"q": f"q{i}"} for i in range(8))),
              "10 recherches tracées"))
    L.append(("extrait manquant en L2",
              variante(lambda c, t: c[1].pop("extrait")), "« extrait » absent"))
    L.append(("extrait de plus de 25 mots",
              variante(lambda c, t: c[1].update(extrait="mot " * 30)), "extrait de 30 mots"))
    L.append(("intitulé manquant",
              variante(reponse=REPONSE.replace("## Niveau de garantie", "## Garantie")),
              "section absente"))
    L.append(("intitulés dans le désordre",
              variante(reponse=REPONSE.replace("## Réponse\nHTTP est sans état.\n", "")
                       + "## Réponse\nHTTP.\n"), "désordre"))
    L.append(("sous-section Faits absente",
              variante(reponse=REPONSE.replace("### Faits", "### Données")),
              "« ### Faits »"))
    L.append(("fr. et en.wikipedia comptés comme un seul domaine",
              variante(lambda c, t: (c[0].update(source_url="https://en.wikipedia.org/wiki/HTTP"),
                                     t[3]["pages_ouvertes"].append("https://en.wikipedia.org/wiki/HTTP"))),
              "1 origine(s)"))

    # Session de test du 2026-10-02 : revues lues via PubMed, sites des revues en 403.
    PUBMED = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed&id="

    def via_pubmed(prefixe2):
        def modif(c, t):
            c.pop(2)
            c[0].update(source_url=PUBMED + "1", doi="10.1136/bmj-2024-082007")
            c[1].update(source_url=PUBMED + "2", doi=f"{prefixe2}/nutrit/nuaf001")
            t[3]["pages_ouvertes"] = [PUBMED + "1", PUBMED + "2"]
        return modif
    L.append(("deux revues lues via PubMed : deux origines par DOI",
              variante(via_pubmed("10.1093")), None))
    L.append(("deux DOI du même éditeur : une seule origine",
              variante(via_pubmed("10.1136")), "1 origine(s)"))

    def evolutif(c, t):
        t[0].update(fraicheur="evolutif")
        c[0].update(claim="un essai de 2022 trouve que HTTP est sans état", constat_date=True)
    L.append(("constat daté avec l'année, autre source récente",
              variante(evolutif), None))
    L.append(("constat daté sans l'année dans l'affirmation",
              variante(lambda c, t: (evolutif(c, t), c[0].update(claim="HTTP est sans état"))),
              "sans l'année 2022"))
    L.append(("constats datés seulement",
              variante(lambda c, t: (evolutif(c, t),
                                     c[1].update(claim="avis de 2026", constat_date=True))),
              "aucune source récente"))
    L.append(("url_verification lue, source_url pour l'humain",
              variante(lambda c, t: c[0].update(source_url="https://doi.org/10.17487/RFC9110",
                                                url_verification=RFC)), None))
    L = [(n, v, a, ()) for n, v, a in L]

    def depuis_cache(c, t):
        c.pop(1)
        c[0].update(source_url=EN_CACHE)
        t[0].update(profondeur="L1")
        t[3]["pages_ouvertes"].append(EN_CACHE)
    L.append(("extrait relu dans la copie en cache, sans réseau",
              variante(depuis_cache), "+vérifiés sur copie du 2026-10-04",
              ("--en-ligne", "--cache", "cache")))
    L.append(("extrait absent de la copie en cache",
              variante(lambda c, t: (depuis_cache(c, t),
                                     c[0].update(extrait="HTTP is a stateful protocol"))),
              "extrait absent de la page", ("--en-ligne", "--cache", "cache")))
    return L


def preparer_cache(dossier):
    texte = "Introduction. " + EXTRAIT + " that enables distributed systems. " * 10
    pages.Cache(os.path.join(dossier, "cache")).ecrire(
        {"url": EN_CACHE, "statut": pages.OK, "http": 200, "type": "text/html",
         "date_acces": "2026-10-04", "note": ""}, texte)


def cas_en_ligne():
    return [
        ("extrait réel retrouvé dans la RFC 9110",
         variante(lambda c, t: (c.pop(1), t[0].update(profondeur="L1"))), None, ("--en-ligne",)),
        ("extrait modifié : absent de la page",
         variante(lambda c, t: c[0].update(extrait="HTTP is a stateful protocol")),
         "extrait absent de la page", ("--en-ligne",)),
        ("URL inexistante : morte",
         variante(lambda c, t: (c[0].update(source_url=RFC_ABSENTE),
                                t[3]["pages_ouvertes"].append(RFC_ABSENTE))),
         "URL morte", ("--en-ligne",)),
    ]


def main():
    cas = cas_hors_ligne() + (cas_en_ligne() if "--reseau" in sys.argv else [])
    passes = 0
    with tempfile.TemporaryDirectory() as dossier:
        preparer_cache(dossier)
        for nom, (c, t, r), attendu, options in cas:
            out = lancer(dossier, c, t, r, options)
            lignes = out.stdout.splitlines()
            if attendu is None:
                ok = out.returncode == 0
            elif attendu.startswith("+"):
                # succès attendu, et la preuve que le bon chemin a été pris
                ok = out.returncode == 0 and any(attendu[1:] in l for l in lignes)
            else:
                ok = out.returncode == 1 and any(attendu in l for l in lignes)
            passes += ok
            print(f"{'OK    ' if ok else 'RATÉ  '} {nom}")
            if not ok:
                print("\n".join(f"        {l}" for l in lignes if not l.startswith("[OK]")))
    print(f"\n{passes}/{len(cas)} cas")
    return 0 if passes == len(cas) else 1


if __name__ == "__main__":
    sys.exit(main())
