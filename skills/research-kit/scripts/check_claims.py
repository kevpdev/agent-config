#!/usr/bin/env python3
"""Contrôles déterministes du registre, de la trace et de la réponse (pipeline.md, étapes 5, 7 et 8).

Usage :
    python3 check_claims.py claims.json [--trace trace.jsonl] [--reponse reponse.md] [--en-ligne]
        [--apres-verification]

    Sans trace, les paramètres viennent de la ligne de commande :
        --profondeur L2 --fraicheur evolutif --aujourdhui 2026-10-02 --recherches 6 --pages 9

La trace se lit dans un fichier JSON Lines, ou dans le bloc ```jsonl de la section « ## Trace »
de la réponse. Quand la trace existe, ses valeurs priment sur la ligne de commande.

--en-ligne télécharge chaque source et cherche l'extrait verbatim dans la page.
Ce contrôle demande un accès réseau. Sans lui, faire la même vérification à la main.

Code de sortie : 0 si tous les contrôles passent, 1 sinon, 2 si un fichier est illisible.
La sortie imprimée est la preuve à rapporter dans la trace : « contrôles : script ».
"""
import argparse
import html
import json
import re
import sys
import unicodedata
import urllib.error
import urllib.request
from datetime import date
from urllib.parse import urlparse, urlunparse

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


def norm(text):
    text = unicodedata.normalize("NFD", str(text))
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    text = re.sub(r"[’‘`´ʼ]", "'", text)
    text = re.sub(r"[«»“”„]", '"', text)
    return re.sub(r"\s+", " ", text).casefold().strip()


def norm_url(url):
    p = urlparse(str(url).strip())
    path = p.path.rstrip("/") or "/"
    return urlunparse((p.scheme.lower(), (p.hostname or "").lower(), path, "", p.query, ""))


def domaine(url):
    host = (urlparse(str(url)).hostname or "").lower()
    labels = [l for l in host.split(".") if l]
    if len(labels) >= 3 and len(labels[-1]) == 2 and labels[-2] in SECONDS_NIVEAUX:
        return ".".join(labels[-3:])
    return ".".join(labels[-2:])


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
        doms = {domaine(c.get("source_url", ""))}
        doms |= {domaine(u) for u in c.get("sources_supplementaires", [])}
        doms.discard("")
        if norm(c.get("source_type", "")) != "primaire" and len(doms) < 2:
            faibles.append(f"#{c.get('id')} : « Établi » sans source primaire "
                           "ni deuxième domaine indépendant")
    rap.critere("aucun « Établi » sur une seule source non primaire (V3)", faibles)

    fraicheur = norm(ctx["fraicheur"] or "")
    if fraicheur in FENETRE_MOIS:
        limite = FENETRE_MOIS[fraicheur]
        if ctx["date_inconnue"]:
            rap.non_verifiable.append(f"fraîcheur ≤ {limite} mois : date du jour inconnue")
        else:
            echecs = []
            for c in claims:
                if est_non_verifie(c):
                    continue
                d = parse_date(c.get("source_date") or "")
                if d is None:
                    echecs.append(f"#{c.get('id')} : date absente ou illisible "
                                  f"« {c.get('source_date') or ''} »")
                elif mois_ecoules(d, ctx["aujourdhui"]) > limite:
                    echecs.append(f"#{c.get('id')} : source datée {c.get('source_date')}, "
                                  f"plus de {limite} mois")
            rap.critere(f"fraîcheur ≤ {limite} mois (V4)", echecs)

    doms = set()
    for c in claims:
        if est_non_verifie(c) or not c.get("source_url"):
            continue
        doms.add(domaine(c["source_url"]))
        doms |= {domaine(u) for u in c.get("sources_supplementaires", [])}
    doms.discard("")
    mini = MIN_DOMAINES[prof]
    rap.critere(f"domaines indépendants ≥ {mini} (V3)",
                [] if len(doms) >= mini else [f"{len(doms)} domaine(s) : {sorted(doms)}"],
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
        urls = [c["source_url"]] + list(c.get("sources_supplementaires", []))
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

def texte_de_page(url, cache):
    """Renvoie (texte normalisé, None) ou (None, verdict)."""
    if url in cache:
        return cache[url]
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (research-kit check_claims)",
        "Accept": "text/html,text/plain;q=0.9"})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            ctype = r.headers.get("Content-Type", "")
            if "html" not in ctype and "text/plain" not in ctype:
                res = (None, f"non vérifiable : contenu « {ctype or 'inconnu'} »")
            else:
                brut = r.read(5_000_000)
                charset = r.headers.get_content_charset() or "utf-8"
                page = brut.decode(charset, errors="replace")
                page = re.sub(r"(?is)<(script|style|noscript)\b.*?</\1>", " ", page)
                page = html.unescape(re.sub(r"(?s)<[^>]+>", " ", page))
                page = norm(page)
                res = (page, None) if len(page) >= 200 else \
                    (None, "non vérifiable : page sans texte (rendue par script ?)")
    except urllib.error.HTTPError as e:
        res = (None, "URL morte" if e.code in (404, 410) else f"non vérifiable : HTTP {e.code}")
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        res = (None, f"non vérifiable : {getattr(e, 'reason', e)}")
    cache[url] = res
    return res


def controles_en_ligne(claims, rap):
    cache, echecs, trouves = {}, [], 0
    for c in claims:
        url = c.get("source_url")
        if est_non_verifie(c) or not url:
            continue
        page, verdict = texte_de_page(url, cache)
        if verdict == "URL morte":
            echecs.append(f"#{c.get('id')} : URL morte ({url})")
        elif verdict:
            rap.non_verifiable.append(f"#{c.get('id')} : {verdict} ({url})")
        elif c.get("extrait"):
            if norm(c["extrait"]) in page:
                trouves += 1
            else:
                echecs.append(f"#{c.get('id')} : extrait absent de la page ({url})")
    rap.critere("URL vivantes et extraits présents dans la page (V2, V6, V7)", echecs,
                f"{trouves} extrait(s) trouvé(s)")


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
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("registre")
    p.add_argument("--trace", help="trace.jsonl, ou réponse contenant le bloc ```jsonl")
    p.add_argument("--reponse", help="fichier de la réponse livrée")
    p.add_argument("--en-ligne", action="store_true",
                   help="télécharge les sources pour vérifier URL et extraits")
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
        controles_en_ligne(claims, rap)
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
