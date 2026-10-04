"""Lecture d'une page et cache de lecture, partagés par fetch_page.py et check_claims.py.

Une page se télécharge une fois par tâche : la collecte (étape 3) la met en cache, la
vérification (étape 7) relit la copie au lieu de la retélécharger.

POURQUOI une politique d'échec figée ici : mesuré le 2026-10-04, un User-Agent de
navigateur ne débloque aucun 403 (murs anti-robots côté serveur). Relancer ne coûte que
des appels, donc un 401, 403 ou 429 est écarté au premier essai, et le cache retient
l'échec pour qu'il ne soit pas retenté dans la même tâche.
"""
import hashlib
import html
import json
import os
import re
import shutil
import ssl
import subprocess
import tempfile
import unicodedata
import urllib.error
import urllib.request
from datetime import date
from urllib.parse import urlparse, urlunparse

USER_AGENT = "Mozilla/5.0 (research-kit)"
TIMEOUT = 15
TAILLE_MAX = 10_000_000
TEXTE_MIN = 200
BLOQUE = {401, 403, 429}
MORTE = {404, 410}
# Marqueurs de paywall, cherchés seulement sur une page courte : sur une page longue,
# la mention d'un abonnement ne prouve pas que le texte manque.
PAYWALL = ("subscribe to continue", "subscribe to read", "réservé aux abonnés",
           "abonnez-vous pour lire", "article réservé")
PAYWALL_TEXTE_MAX = 1500

OK, ECARTEE, MORTE_STATUT, NON_VERIFIABLE = "ok", "ecartee", "morte", "non verifiable"


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


def html_en_texte(page):
    page = re.sub(r"(?is)<(script|style|noscript|svg|template)\b.*?</\1>", " ", page)
    page = re.sub(r"(?is)<!--.*?-->", " ", page)
    page = html.unescape(re.sub(r"(?s)<[^>]+>", " ", page))
    return re.sub(r"\s+", " ", page).strip()


def pdf_en_texte(brut):
    """Texte d'un PDF par pdftotext, ou None si l'outil manque ou échoue."""
    if not shutil.which("pdftotext"):
        return None
    with tempfile.TemporaryDirectory() as d:
        src = os.path.join(d, "page.pdf")
        with open(src, "wb") as f:
            f.write(brut)
        r = subprocess.run(["pdftotext", "-q", src, "-"], capture_output=True, timeout=60)
    if r.returncode != 0:
        return None
    return re.sub(r"\s+", " ", r.stdout.decode("utf-8", errors="replace")).strip()


def _ouvrir(url, contexte_tls):
    req = urllib.request.Request(url, headers={
        "User-Agent": USER_AGENT,
        "Accept": "text/html,text/plain;q=0.9,application/pdf;q=0.8,*/*;q=0.5"})
    with urllib.request.urlopen(req, timeout=TIMEOUT, context=contexte_tls) as r:
        return r.headers.get("Content-Type", ""), r.headers.get_content_charset(), r.read(TAILLE_MAX)


def telecharger(url):
    """Renvoie (entrée, texte). L'entrée décrit le résultat, le texte vaut None hors succès."""
    entree = {"url": url, "statut": None, "http": None, "type": None,
              "date_acces": date.today().isoformat(), "note": ""}
    try:
        try:
            ctype, charset, brut = _ouvrir(url, None)
        except urllib.error.URLError as e:
            if not isinstance(getattr(e, "reason", None), ssl.SSLCertVerificationError):
                raise
            ctype, charset, brut = _ouvrir(url, ssl._create_unverified_context())
            entree["note"] = "certificat non vérifié"
        entree["http"] = 200
    except urllib.error.HTTPError as e:
        entree["http"] = e.code
        if e.code in BLOQUE:
            entree.update(statut=ECARTEE, note=f"HTTP {e.code}, ne pas relancer")
        elif e.code in MORTE:
            entree.update(statut=MORTE_STATUT, note="URL morte")
        else:
            entree.update(statut=NON_VERIFIABLE, note=f"HTTP {e.code}")
        return entree, None
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        entree.update(statut=NON_VERIFIABLE, note=str(getattr(e, "reason", e)))
        return entree, None

    entree["type"] = ctype.split(";")[0].strip() or "inconnu"
    if "pdf" in ctype or brut[:5] == b"%PDF-":
        texte = pdf_en_texte(brut)
        if texte is None:
            entree.update(statut=NON_VERIFIABLE, note="PDF illisible (pdftotext absent ou en échec)")
            return entree, None
    elif "html" in ctype or "text/plain" in ctype or "xml" in ctype:
        page = brut.decode(charset or "utf-8", errors="replace")
        texte = page.strip() if "text/plain" in ctype else html_en_texte(page)
    else:
        entree.update(statut=NON_VERIFIABLE, note=f"contenu « {entree['type']} »")
        return entree, None

    if len(texte) < TEXTE_MIN:
        entree.update(statut=NON_VERIFIABLE, note="page sans texte (rendue par script ?)")
        return entree, None
    if len(texte) <= PAYWALL_TEXTE_MAX and any(m in texte.casefold() for m in PAYWALL):
        entree.update(statut=ECARTEE, note="paywall, ne pas relancer")
        return entree, None
    entree["statut"] = OK
    return entree, texte


class Cache:
    """Copies de lecture : <dossier>/pages/<sha1>.txt et un index JSON Lines."""

    def __init__(self, dossier):
        self.dir = os.path.join(dossier, "pages")
        self.index = os.path.join(self.dir, "index.jsonl")

    def _cle(self, url):
        return hashlib.sha1(norm_url(url).encode()).hexdigest()[:16]

    def lire(self, url):
        """Dernière entrée connue pour l'URL et son texte, ou (None, None)."""
        if not os.path.exists(self.index):
            return None, None
        cible, entree = norm_url(url), None
        with open(self.index, encoding="utf-8") as f:
            for ligne in f:
                try:
                    e = json.loads(ligne)
                except ValueError:
                    continue
                if norm_url(e.get("url", "")) == cible:
                    entree = e
        if entree is None:
            return None, None
        texte = None
        if entree.get("statut") == OK and entree.get("fichier"):
            chemin = os.path.join(self.dir, entree["fichier"])
            if os.path.exists(chemin):
                with open(chemin, encoding="utf-8") as f:
                    texte = f.read()
        return entree, texte

    def ecrire(self, entree, texte):
        os.makedirs(self.dir, exist_ok=True)
        if texte is not None:
            entree["fichier"] = self._cle(entree["url"]) + ".txt"
            with open(os.path.join(self.dir, entree["fichier"]), "w", encoding="utf-8") as f:
                f.write(texte)
        with open(self.index, "a", encoding="utf-8") as f:
            f.write(json.dumps(entree, ensure_ascii=False) + "\n")


def lire_page(url, cache=None):
    """(entrée, texte, depuis_cache). Avec un cache, une URL déjà lue ne se retélécharge pas.

    Seule exception : une erreur réseau sans réponse HTTP (délai, DNS) peut être passagère,
    elle reste retentable.
    """
    if cache is not None:
        entree, texte = cache.lire(url)
        repondu = entree is not None and entree.get("http") is not None
        if repondu and (entree["statut"] != OK or texte is not None):
            return entree, texte, True
    entree, texte = telecharger(url)
    if cache is not None:
        cache.ecrire(entree, texte)
    return entree, texte, False
