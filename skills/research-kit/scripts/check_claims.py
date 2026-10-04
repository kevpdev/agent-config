#!/usr/bin/env python3
"""Contrôles déterministes du registre, de la trace et de la réponse (pipeline.md, étapes 5, 7 et 8).

Usage :
    python3 check_claims.py claims.json [--trace trace.jsonl] [--reponse reponse.md] [--en-ligne [--cache D]]
        [--apres-verification]

    Sans trace, les paramètres viennent de la ligne de commande :
        --profondeur L2 --fraicheur evolutif --aujourdhui 2026-10-02 --recherches 6 --pages 9

La trace se lit dans un fichier JSON Lines, ou dans le bloc ```jsonl de la section « ## Trace »
de la réponse. Quand la trace existe, ses valeurs priment sur la ligne de commande.

--en-ligne télécharge chaque source et cherche l'extrait verbatim dans la page.
Ce contrôle demande un accès réseau. Sans lui, faire la même vérification à la main.
Avec --cache DOSSIER (le dossier passé à fetch_page.py), une page déjà lue à la collecte
est relue dans sa copie, sans réseau. Seule une URL absente du cache se télécharge.

Registre (liste JSON, objet {"claims": [...]} ou JSON Lines), un objet par affirmation :
    obligatoires : id, claim, source_url, source_date (AAAA, AAAA-MM ou AAAA-MM-JJ),
        source_type (primaire, secondaire, tertiaire), requete, opened (true), label
        (Établi, Probable, Contesté, Non vérifié, Hypothèse à tester), interet_source
    extrait : phrase verbatim de 25 mots au plus, exigée en L2 et L3
    verifie_par : exigé avec --apres-verification
    optionnels :
        doi : identifiant de la publication. L'indépendance se compte par préfixe DOI
            (l'éditeur), sinon par domaine de source_url.
        url_verification : URL réellement lue (texte brut, API). --en-ligne la télécharge
            à la place de source_url, qui reste la page lisible par un humain.
        constat_date : true si l'affirmation rapporte une étude datée. L'année de
            source_date doit figurer dans claim. Exempte de la fenêtre de fraîcheur,
            tant qu'une autre affirmation reste dans la fenêtre.
        sources_supplementaires : liste d'URL, comptées pour l'indépendance.
    Une affirmation « Non vérifié » peut omettre source_url, source_date, source_type, extrait.

Trace (JSON Lines), champs lus :
    étape 0 : verbe, profil, fraicheur (stable, evolutif, temps reel), risque,
        profondeur (L0 à L3), lentilles, date_du_jour
    étapes 1 à 8 : statut (executee ou sautee), raison si sautée
    toute étape : requetes [{"q": ..., "refutation": true/false}], pages_ouvertes [URL]

Code de sortie : 0 si tous les contrôles passent, 1 sinon, 2 si un fichier est illisible.
La sortie imprimée est la preuve à rapporter dans la trace : « contrôles : script ».
"""
import argparse
import json
import re
import sys
from datetime import date
from urllib.parse import urlparse

import pages
from pages import norm, norm_url

LABELS = {"etabli", "probable", "conteste", "non verifie", "hypothese a tester"}
SOURCE_TYPES = {"primaire", "secondaire", "tertiaire"}
REQUIRED = ["id", "claim", "source_url", "source_date", "source_type",
            "requete", "opened", "label", "interet_source"]
SOURCE_FIELDS = {"source_url", "source_date", "source_type", "extrait"}
EXTRAIT_MAX_MOTS = 25

# valeurs de départ, non calibrées (pipeline.md §3 et étape 4)
BUDGETS = {"L0": {"recherches": 0, "pages": 0},
           "L1": {"recherches": 3, "pages": 5},
           "L2": {"recherches": 8, "pages": 15},
           "L3": {"recherches": 20, "pages": 40}}
MIN_DOMAINES = {"L0": 0, "L1": 1, "L2": 2, "L3": 3}
FENETRE_MOIS = {"evolutif": 12, "temps reel": 3}
# étapes exécutées selon la profondeur (pipeline.md §3), étape 0 comprise
ETAPES_EXIGEES = {"L0": {0, 6, 8},
                  "L1": {0, 1, 3, 4, 6, 7, 8},
                  "L2": set(range(9)),
                  "L3": set(range(9))}

SECTIONS = ["Réponse", "Points clés", "Ce que je n'ai pas pu vérifier",
            "Niveau de garantie", "Trace"]
SOUS_SECTIONS = ["Faits", "Interprétations", "Recommandations"]

# Heuristique de domaine enregistrable, pas la liste publique des suffixes :
# on garde trois labels quand l'avant-dernier est l'un de ces seconds niveaux
# sous un domaine national à deux lettres (bbc.co.uk, service-public.gouv.fr).
SECONDS_NIVEAUX = {"co", "com", "org", "net", "gov", "gouv", "ac", "edu",
                   "ne", "or", "go", "asso", "nic"}


def domaine(url):
    host = (urlparse(str(url)).hostname or "").lower()
    labels = [l for l in host.split(".") if l]
    if len(labels) >= 3 and len(labels[-1]) == 2 and labels[-2] in SECONDS_NIVEAUX:
        return ".".join(labels[-3:])
    return ".".join(labels[-2:])


def origine(url, doi=None):
    """Préfixe DOI (l'éditeur) quand on le connaît, sinon le domaine de l'URL."""
    m = re.search(r"\b(10\.\d{4,9})/", str(doi or ""))
    if not m and (urlparse(str(url)).hostname or "").lower() in ("doi.org", "dx.doi.org"):
        m = re.search(r"\b(10\.\d{4,9})/", urlparse(str(url)).path)
    return f"doi:{m.group(1)}" if m else domaine(url)


def origines(c):
    o = {origine(c.get("source_url", ""), c.get("doi"))}
    o |= {origine(u) for u in c.get("sources_supplementaires", [])}
    o.discard("")
    return o


def url_lue(c):
    return c.get("url_verification") or c.get("source_url")


def est_non_verifie(c):
    return norm(c.get("label", "")) == "non verifie"


def parse_date(text):
    m = re.fullmatch(r"(\d{4})(?:-(\d{2}))?(?:-(\d{2}))?", str(text).strip())
    if not m:
        return None
    return int(m.group(1)), int(m.group(2) or 1), int(m.group(3) or 1)


def mois_ecoules(d, today):
    return (today.year - d[0]) * 12 + (today.month - d[1])


# ---------- chargement ----------

def charger_registre(path):
    with open(path, encoding="utf-8") as f:
        raw = f.read()
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        data = [json.loads(line) for line in raw.splitlines() if line.strip()]
    if isinstance(data, dict):
        data = data.get("claims", [])
    if not isinstance(data, list):
        raise ValueError("le registre doit être une liste d'objets")
    return data


def extraire_bloc_trace(texte):
    """Le bloc ```jsonl placé sous « ## Trace », ou None."""
    m = re.search(r"^##\s+Trace\s*$(.*?)(?=^##\s|\Z)", texte, re.M | re.S)
    if not m:
        return None
    b = re.search(r"```jsonl\s*\n(.*?)```", m.group(1), re.S)
    return b.group(1) if b else None


def charger_trace(path):
    with open(path, encoding="utf-8") as f:
        texte = f.read()
    bloc = extraire_bloc_trace(texte) if "```jsonl" in texte else texte
    if bloc is None:
        raise ValueError("aucun bloc ```jsonl sous « ## Trace »")
    lignes = [json.loads(l) for l in bloc.splitlines() if l.strip()]
    if not lignes:
        raise ValueError("trace vide")
    return lignes


# ---------- rapport ----------

class Rapport:
    def __init__(self):
        self.lignes = []
        self.non_verifiable = []
        self.ok = 0
        self.total = 0

    def critere(self, nom, echecs, detail_ok=""):
        self.total += 1
        if echecs:
            self.lignes.append(f"[ÉCHEC] {nom}")
            self.lignes.extend(f"         - {e}" for e in echecs)
        else:
            self.ok += 1
            self.lignes.append(f"[OK]    {nom}" + (f" ({detail_ok})" if detail_ok else ""))

    def note(self, texte):
        self.lignes.append(f"         note : {texte}")


# ---------- contexte : trace ou ligne de commande ----------

def contexte(args, trace):
    ctx = {"profondeur": args.profondeur, "fraicheur": args.fraicheur,
           "profil": None, "aujourdhui": None, "date_inconnue": False}
    if args.aujourdhui:
        ctx["aujourdhui"] = date.fromisoformat(args.aujourdhui)
    if trace:
        t0 = next((l for l in trace if l.get("etape") == 0), {})
        ctx["profondeur"] = t0.get("profondeur", ctx["profondeur"])
        ctx["fraicheur"] = t0.get("fraicheur", ctx["fraicheur"])
        ctx["profil"] = t0.get("profil") or t0.get("verbe")
        d = str(t0.get("date_du_jour", "")).strip()
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", d):
            ctx["aujourdhui"] = date.fromisoformat(d)
        elif d:
            ctx["date_inconnue"] = True
    if ctx["aujourdhui"] is None and not ctx["date_inconnue"]:
        ctx["aujourdhui"] = date.today()
    if ctx["profondeur"] not in BUDGETS:
        ctx["profondeur"] = "L2"
    return ctx


# ---------- contrôles du registre ----------

def controles_registre(claims, args, ctx, rap):
    prof = ctx["profondeur"]
    ids = [c.get("id") for c in claims]
    rap.critere("registre non vide", [] if claims else ["aucune affirmation"],
                f"{len(claims)} affirmations")
    rap.critere("identifiants uniques",
                [f"id en double : {i}" for i in set(ids) if ids.count(i) > 1])

    exige_extrait = prof in ("L2", "L3")
    manquants = []
    for c in claims:
        champs = REQUIRED + (["extrait"] if exige_extrait else [])
        for champ in champs:
            vide = champ not in c or c[champ] in (None, "")
            if vide and not (champ in SOURCE_FIELDS and est_non_verifie(c)):
                manquants.append(f"#{c.get('id')} : champ « {champ} » absent ou vide")
        if args.apres_verification and not c.get("verifie_par"):
            manquants.append(f"#{c.get('id')} : champ « verifie_par » absent")
    rap.critere("champs obligatoires présents (V1, T2)", manquants)

    rap.critere(f"extraits de {EXTRAIT_MAX_MOTS} mots au plus (V6)",
                [f"#{c.get('id')} : extrait de {len(str(c['extrait']).split())} mots"
                 for c in claims
                 if c.get("extrait") and len(str(c["extrait"]).split()) > EXTRAIT_MAX_MOTS])
    rap.critere("étiquettes valides",
                [f"#{c.get('id')} : étiquette « {c.get('label')} »"
                 for c in claims if norm(c.get("label", "")) not in LABELS])
    rap.critere("types de source valides",
                [f"#{c.get('id')} : type « {c.get('source_type')} »"
                 for c in claims
                 if c.get("source_type") and norm(c["source_type"]) not in SOURCE_TYPES])
    rap.critere("chaque source citée déclarée ouverte (V2)",
                [f"#{c.get('id')} : opened n'est pas vrai"
                 for c in claims if not est_non_verifie(c) and c.get("opened") is not True])
    rap.critere("affirmation sans source étiquetée Non vérifié (V1)",
                [f"#{c.get('id')} : sans source, doit être « Non vérifié »"
                 for c in claims if not c.get("source_url") and not est_non_verifie(c)])

    faibles = []
    for c in claims:
        if norm(c.get("label", "")) != "etabli":
            continue
        if norm(c.get("source_type", "")) != "primaire" and len(origines(c)) < 2:
            faibles.append(f"#{c.get('id')} : « Établi » sans source primaire "
                           "ni deuxième origine indépendante")
    rap.critere("aucun « Établi » sur une seule source non primaire (V3)", faibles)

    fraicheur = norm(ctx["fraicheur"] or "")
    if fraicheur in FENETRE_MOIS:
        limite = FENETRE_MOIS[fraicheur]
        if ctx["date_inconnue"]:
            rap.non_verifiable.append(f"fraîcheur ≤ {limite} mois : date du jour inconnue")
        else:
            echecs, exemptees, recentes = [], 0, 0
            for c in claims:
                if est_non_verifie(c):
                    continue
                d = parse_date(c.get("source_date") or "")
                if d is None:
                    echecs.append(f"#{c.get('id')} : date absente ou illisible "
                                  f"« {c.get('source_date') or ''} »")
                elif c.get("constat_date") is True:
                    if str(d[0]) not in str(c.get("claim", "")):
                        echecs.append(f"#{c.get('id')} : constat daté sans l'année {d[0]} "
                                      "dans l'affirmation")
                    exemptees += 1
                elif mois_ecoules(d, ctx["aujourdhui"]) > limite:
                    echecs.append(f"#{c.get('id')} : source datée {c.get('source_date')}, "
                                  f"plus de {limite} mois")
                else:
                    recentes += 1
            if exemptees and not recentes:
                echecs.append("constats datés seulement : aucune source récente "
                              "sur l'état actuel")
            rap.critere(f"fraîcheur ≤ {limite} mois (V4)", echecs,
                        f"{exemptees} constat(s) daté(s) exempté(s)" if exemptees else "")

    doms = set()
    for c in claims:
        if est_non_verifie(c) or not c.get("source_url"):
            continue
        doms |= origines(c)
    mini = MIN_DOMAINES[prof]
    rap.critere(f"origines indépendantes ≥ {mini} (V3)",
                [] if len(doms) >= mini else [f"{len(doms)} origine(s) : {sorted(doms)}"],
                f"{len(doms)} : {', '.join(sorted(doms))}")
    rap.note("les citations en chaîne ne se détectent pas par script, à juger à l'étape 7")


# ---------- contrôles de la trace ----------

def controles_trace(claims, trace, ctx, rap):
    prof = ctx["profondeur"]
    t0 = next((l for l in trace if l.get("etape") == 0), None)
    champs0 = ["verbe", "fraicheur", "risque", "profondeur", "lentilles", "date_du_jour"]
    rap.critere("étape 0 complète (T2)",
                ["ligne de l'étape 0 absente"] if t0 is None else
                [f"champ « {k} » absent" for k in champs0 if k not in t0])

    par_etape = {}
    for l in trace:
        par_etape.setdefault(l.get("etape"), []).append(l)
    exigees = set(ETAPES_EXIGEES[prof])
    if norm(ctx["profil"] or "") == "fact-check":
        exigees.discard(2)

    echecs = []
    for n in range(9):
        lignes = par_etape.get(n, [])
        if not lignes:
            echecs.append(f"étape {n} absente de la trace")
            continue
        executee = any(norm(l.get("statut", "")) == "executee" or n == 0 for l in lignes)
        if n in exigees and not executee:
            echecs.append(f"étape {n} exigée en {prof}, marquée sautée")
    rap.critere(f"chaque étape tracée, celles exigées en {prof} exécutées (T2)", echecs)

    rap.critere("chaque étape sautée porte une raison (T2)",
                [f"étape {l.get('etape')} sautée sans raison"
                 for l in trace
                 if norm(l.get("statut", "")) == "sautee" and not str(l.get("raison", "")).strip()])

    requetes = [r for l in trace for r in l.get("requetes", [])]
    pages = {norm_url(u) for l in trace for u in l.get("pages_ouvertes", [])}
    b = BUDGETS[prof]
    rap.critere(f"recherches ≤ {b['recherches']} (B5)",
                [] if len(requetes) <= b["recherches"] else [f"{len(requetes)} recherches tracées"],
                f"{len(requetes)}/{b['recherches']}")
    rap.critere(f"pages ouvertes ≤ {b['pages']} (B5)",
                [] if len(pages) <= b["pages"] else [f"{len(pages)} pages tracées"],
                f"{len(pages)}/{b['pages']}")
    if prof != "L0":
        rap.critere("au moins une requête de réfutation (V5)",
                    [] if any(r.get("refutation") is True for r in requetes)
                    else ["aucune requête marquée « refutation »"])

    hors_trace = []
    for c in claims:
        if est_non_verifie(c) or not c.get("source_url"):
            continue
        urls = [url_lue(c)] + list(c.get("sources_supplementaires", []))
        hors_trace += [f"#{c.get('id')} : {u} absente des pages ouvertes"
                       for u in urls if norm_url(u) not in pages]
    rap.critere("chaque source du registre est une page ouverte de la trace (T3)", hors_trace)

    qs = {norm(r.get("q", "")) for r in requetes}
    rap.critere("chaque requête du registre figure dans la trace (T3)",
                [f"#{c.get('id')} : requête « {c.get('requete')} » absente de la trace"
                 for c in claims if c.get("requete") and norm(c["requete"]) not in qs])


def controles_budgets_cli(claims, args, ctx, rap):
    """Repli quand aucune trace n'est fournie."""
    b = BUDGETS[ctx["profondeur"]]
    if args.recherches is not None:
        rap.critere(f"recherches ≤ {b['recherches']} (B5)",
                    [] if args.recherches <= b["recherches"]
                    else [f"{args.recherches} recherches annoncées"],
                    f"{args.recherches}/{b['recherches']}")
    if args.pages is not None:
        rap.critere(f"pages ouvertes ≤ {b['pages']} (B5)",
                    [] if args.pages <= b["pages"] else [f"{args.pages} pages annoncées"],
                    f"{args.pages}/{b['pages']}")
        urls = {norm_url(c["source_url"]) for c in claims if c.get("source_url")}
        rap.critere("sources du registre ≤ pages annoncées (T3)",
                    [] if len(urls) <= args.pages
                    else [f"{len(urls)} URL distinctes, {args.pages} pages annoncées"],
                    f"{len(urls)}/{args.pages}")


# ---------- contrôle en ligne : URL vivante et extrait verbatim ----------

def texte_de_page(url, memo, cache):
    """Renvoie (texte normalisé, None, date de lecture en cache) ou (None, verdict, None)."""
    if url in memo:
        return memo[url]
    entree, texte, depuis_cache = pages.lire_page(url, cache)
    if entree["statut"] == pages.OK:
        res = (norm(texte), None, entree["date_acces"] if depuis_cache else None)
    elif entree["statut"] == pages.MORTE_STATUT:
        res = (None, "URL morte", None)
    else:
        res = (None, f"non vérifiable : {entree['note']}", None)
    memo[url] = res
    return res


def controles_en_ligne(claims, rap, cache=None):
    memo, echecs, trouves, copies = {}, [], 0, set()
    for c in claims:
        url = url_lue(c)
        if est_non_verifie(c) or not url:
            continue
        page, verdict, lu_le = texte_de_page(url, memo, cache)
        if lu_le:
            copies.add(lu_le)
        if verdict == "URL morte":
            echecs.append(f"#{c.get('id')} : URL morte ({url})")
        elif verdict:
            rap.non_verifiable.append(f"#{c.get('id')} : {verdict} ({url})")
        elif c.get("extrait"):
            if norm(c["extrait"]) in page:
                trouves += 1
            else:
                echecs.append(f"#{c.get('id')} : extrait absent de la page ({url})")
    detail = f"{trouves} extrait(s) trouvé(s)"
    if copies:
        detail += f", vérifiés sur copie du {', '.join(sorted(copies))}"
    rap.critere("URL vivantes et extraits présents dans la page (V2, V6, V7)", echecs, detail)


# ---------- contrôle de la réponse ----------

def controles_reponse(texte, rap):
    titres = [(i, m.group(1).strip(), m.group(0).startswith("###"))
              for i, l in enumerate(texte.splitlines())
              for m in [re.match(r"^#{2,3}\s+(.*)$", l)] if m]
    lignes = texte.splitlines()
    h2 = [(i, t) for i, t, sous in titres if not sous]

    def corps(i):
        out = []
        for l in lignes[i + 1:]:
            if re.match(r"^#{1,3}\s", l):
                break
            if l.strip():
                out.append(l)
        return out

    echecs, positions = [], []
    for s in SECTIONS:
        trouve = next(((i, t) for i, t in h2 if norm(t) == norm(s)), None)
        if trouve is None:
            echecs.append(f"section absente : « ## {s} »")
            continue
        positions.append(trouve[0])
        if s != "Points clés" and not corps(trouve[0]):
            echecs.append(f"section vide : « ## {s} »")
    if positions != sorted(positions):
        echecs.append("sections dans le désordre (ordre de guardrails.md §7)")
    pc = next((i for i, t in h2 if norm(t) == norm("Points clés")), None)
    if pc is not None:
        fin = next((i for i, t in h2 if i > pc), len(lignes))
        sous = [(j, t) for j, t, est_sous in titres if est_sous and pc < j < fin]
        for s in SOUS_SECTIONS:
            j = next((j for j, t in sous if norm(t) == norm(s)), None)
            if j is None:
                echecs.append(f"sous-section absente : « ### {s} » sous Points clés")
            elif not corps(j):
                echecs.append(f"sous-section vide : « ### {s} » (écrire « aucune » si besoin)")
    rap.critere("intitulés de sortie présents, dans l'ordre, non vides (guardrails §7)", echecs)


# ---------- programme ----------

def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("registre")
    p.add_argument("--trace", help="trace.jsonl, ou réponse contenant le bloc ```jsonl")
    p.add_argument("--reponse", help="fichier de la réponse livrée")
    p.add_argument("--en-ligne", action="store_true",
                   help="télécharge les sources pour vérifier URL et extraits")
    p.add_argument("--cache", metavar="DOSSIER",
                   help="avec --en-ligne : relit les copies de fetch_page.py au lieu de retélécharger")
    p.add_argument("--apres-verification", action="store_true",
                   help="exige le champ verifie_par (étape 7)")
    p.add_argument("--profondeur", choices=list(BUDGETS), default="L2")
    p.add_argument("--fraicheur", help="stable, evolutif ou temps reel")
    p.add_argument("--aujourdhui", help="AAAA-MM-JJ, si la trace manque")
    p.add_argument("--recherches", type=int, help="si la trace manque")
    p.add_argument("--pages", type=int, help="si la trace manque")
    args = p.parse_args()

    try:
        claims = charger_registre(args.registre)
        reponse = open(args.reponse, encoding="utf-8").read() if args.reponse else None
        trace = None
        if args.trace:
            trace = charger_trace(args.trace)
        elif reponse and extraire_bloc_trace(reponse):
            trace = charger_trace(args.reponse)
    except (OSError, ValueError) as e:
        print(f"[ILLISIBLE] {e}")
        return 2

    ctx = contexte(args, trace)
    rap = Rapport()
    controles_registre(claims, args, ctx, rap)
    if trace:
        controles_trace(claims, trace, ctx, rap)
    else:
        rap.note("aucune trace fournie : budgets et étapes non contrôlés depuis la trace")
        controles_budgets_cli(claims, args, ctx, rap)
    if reponse is not None:
        controles_reponse(reponse, rap)
    if args.en_ligne:
        controles_en_ligne(claims, rap, pages.Cache(args.cache) if args.cache else None)
    else:
        rap.note("sans --en-ligne : URL et extraits à vérifier à la main")

    print("\n".join(rap.lignes))
    if rap.non_verifiable:
        print("\nNon vérifiable par script, à reporter dans « Ce que je n'ai pas pu vérifier » :")
        print("\n".join(f"  - {n}" for n in rap.non_verifiable))
    jour = ctx["aujourdhui"].isoformat() if ctx["aujourdhui"] else "date inconnue"
    print(f"\ncontrôles : script, {rap.ok}/{rap.total} passés "
          f"(profondeur {ctx['profondeur']}, au {jour}, "
          f"trace : {'oui' if trace else 'non'}, en ligne : {'oui' if args.en_ligne else 'non'})")
    return 0 if rap.ok == rap.total else 1


if __name__ == "__main__":
    sys.exit(main())
