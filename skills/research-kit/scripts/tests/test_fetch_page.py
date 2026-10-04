#!/usr/bin/env python3
"""Calibre fetch_page.py contre un serveur HTTP local : chaque ligne de la politique d'échec
rend son code, et une page lue une fois ne se retélécharge pas.

Usage :
    python3 test_fetch_page.py

Hors ligne : le serveur tourne sur 127.0.0.1, dans ce processus. Le cas PDF est sauté,
et le dit, si pdftotext est absent.
Code de sortie : 0 si tous les cas passent, 1 sinon.
"""
import http.server
import os
import shutil
import subprocess
import sys
import tempfile
import threading
from collections import Counter

SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "fetch_page.py")

PHRASE = "La taxe forfaitaire s’applique au prix de cession, même en cas de moins-value."
LONGUE = ("<html><head><style>.x{color:red}</style><script>var a=1;</script></head><body>"
          + "<p>Introduction du guide fiscal.</p>" * 20 + f"<p>{PHRASE}</p>"
          + "<p>Suite du texte, sans intérêt pour le test.</p>" * 200 + "</body></html>")
VIDE = "<html><body><div id='app'></div><script>render()</script></body></html>"
PAYWALL = "<html><body><h1>Titre</h1><p>Article réservé aux abonnés. " + "x " * 120 + "</p></body></html>"


def pdf_minimal(lignes):
    """PDF d'une page, une ligne de texte par objet Tj, offsets de xref exacts."""
    flux = "BT /F1 11 Tf 50 750 Td 14 TL " + " ".join(f"({l}) Tj T*" for l in lignes) + " ET"
    objets = [
        "<< /Type /Catalog /Pages 2 0 R >>",
        "<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        "/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        "<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        f"<< /Length {len(flux)} >>\nstream\n{flux}\nendstream",
    ]
    sortie, offsets = "%PDF-1.4\n", []
    for i, o in enumerate(objets, 1):
        offsets.append(len(sortie))
        sortie += f"{i} 0 obj\n{o}\nendobj\n"
    xref = len(sortie)
    sortie += f"xref\n0 {len(objets) + 1}\n0000000000 65535 f \n"
    sortie += "".join(f"{o:010d} 00000 n \n" for o in offsets)
    sortie += f"trailer\n<< /Size {len(objets) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n"
    return sortie.encode("latin-1")


PDF = pdf_minimal([f"Ligne {i} du guide AMF sur l'or, pas plus de 5% du patrimoine." for i in range(8)])

ROUTES = {
    "/ok": (200, "text/html; charset=utf-8", LONGUE.encode()),
    "/bloque": (403, "text/html", b"<html>Forbidden</html>"),
    "/limite": (429, "text/html", b"<html>Too many</html>"),
    "/morte": (404, "text/html", b"<html>Not found</html>"),
    "/vide": (200, "text/html", VIDE.encode()),
    "/paywall": (200, "text/html; charset=utf-8", PAYWALL.encode()),
    "/image": (200, "image/png", b"\x89PNG" + b"0" * 500),
    "/doc.pdf": (200, "application/pdf", PDF),
}
APPELS = Counter()


class Serveur(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        APPELS[self.path] += 1
        code, ctype, corps = ROUTES.get(self.path, (404, "text/plain", b"absent"))
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(corps)))
        self.end_headers()
        self.wfile.write(corps)

    def log_message(self, *args):
        pass


def lancer(url, dossier, *options):
    return subprocess.run([sys.executable, SCRIPT, url, "--dossier", dossier, *options],
                          capture_output=True, text=True, timeout=60)


def main():
    serveur = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Serveur)
    threading.Thread(target=serveur.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{serveur.server_address[1]}"
    resultats = []

    def cas(nom, ok, sortie=""):
        resultats.append(ok)
        print(f"{'OK    ' if ok else 'RATÉ  '} {nom}")
        if not ok:
            print("\n".join(f"        {l}" for l in sortie.splitlines()))

    with tempfile.TemporaryDirectory() as d:
        r = lancer(base + "/ok", d)
        cas("page lue : code 0, script et style retirés", r.returncode == 0
            and "[OK]" in r.stdout and "var a=1" not in r.stdout and "color:red" not in r.stdout,
            r.stdout)
        r = lancer(base + "/ok", d, "--cherche", "taxe forfaitaire s'applique au prix")
        cas("second appel : lu dans le cache, zéro requête réseau de plus",
            r.returncode == 0 and "(cache," in r.stdout and APPELS["/ok"] == 1, r.stdout)
        cas("--cherche rend la phrase verbatim, apostrophe typographique comprise",
            PHRASE in r.stdout, r.stdout)
        r = lancer(base + "/ok", d, "--mots", "50")
        corps = r.stdout.split("\n\n", 1)[-1]
        cas("sortie bornée à --mots", len(corps.split()) <= 51, r.stdout)

        for chemin, code, motif in [("/bloque", 3, "HTTP 403, ne pas relancer"),
                                    ("/limite", 3, "HTTP 429, ne pas relancer"),
                                    ("/paywall", 3, "paywall"),
                                    ("/morte", 4, "URL morte"),
                                    ("/vide", 5, "page sans texte"),
                                    ("/image", 5, "contenu « image/png »")]:
            r = lancer(base + chemin, d)
            cas(f"{chemin} : code {code}, « {motif} »", r.returncode == code and motif in r.stdout,
                r.stdout)
        r = lancer(base + "/bloque", d)
        cas("403 déjà vu : pas de nouvelle requête", r.returncode == 3 and APPELS["/bloque"] == 1,
            r.stdout)

        if shutil.which("pdftotext"):
            r = lancer(base + "/doc.pdf", d, "--cherche", "pas plus de 5%")
            cas("PDF : texte extrait par pdftotext", r.returncode == 0
                and "3 occurrence(s)" in r.stdout, r.stdout)
        else:
            print("SAUTÉ  PDF : pdftotext absent")

        r = subprocess.run([sys.executable, SCRIPT, "http://127.0.0.1:9/rien", "--dossier", d],
                           capture_output=True, text=True, timeout=60)
        cas("erreur réseau : code 5", r.returncode == 5 and "NON VÉRIFIABLE" in r.stdout, r.stdout)

    serveur.shutdown()
    print(f"\n{sum(resultats)}/{len(resultats)} cas")
    return 0 if all(resultats) else 1


if __name__ == "__main__":
    sys.exit(main())
