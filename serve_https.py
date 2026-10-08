#!/usr/bin/env python3
"""
Serveur HTTPS pour le frontend KOSMOS.
Sert les fichiers statiques ET proxifie les appels API vers le backend Flask (port 5000).
Requis pour la géolocalisation sur iOS/Android.

Usage : python3 serve_https.py
Puis visiter : https://10.42.0.1
"""

import http.server
import ssl
import os
import glob
import json
import re
import subprocess
import urllib.request
import urllib.error
from socketserver import ThreadingMixIn

BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
CERT_FILE    = os.path.join(BASE_DIR, "cert.pem")
KEY_FILE     = os.path.join(BASE_DIR, "key.pem")
DEPLOY_DIR   = os.path.join(os.path.dirname(BASE_DIR), "deployments")
TILES_DIR    = os.path.join(os.path.dirname(BASE_DIR), "cache_tuiles")   # hors du dépôt git
BENTHOS_TILES = os.path.join(DEPLOY_DIR, "tiles")   # tuiles envoyées par BenthOS avec le JSON
TILE_SOURCES = {
    "sat":     "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    "seamark": "https://tiles.openseamap.org/seamark/{z}/{x}/{y}.png",
    "osm":     "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
}
TILE_RE      = re.compile(r"^/tiles/(\w+)/(\d+)/(\d+)/(\d+)\.png$")
PORT         = 443
IP           = "10.42.0.1"
BACKEND      = "http://127.0.0.1:5000"

# Génère un certificat auto-signé si absent
if not os.path.exists(CERT_FILE) or not os.path.exists(KEY_FILE):
    print("Génération du certificat auto-signé...")
    subprocess.run([
        "openssl", "req", "-x509", "-newkey", "rsa:2048",
        "-keyout", KEY_FILE, "-out", CERT_FILE,
        "-days", "825", "-nodes",
        "-subj", f"/CN={IP}",
        "-addext", f"subjectAltName=IP:{IP}"
    ], check=True)
    print("Certificat généré.")

os.chdir(FRONTEND_DIR)

def _parents(path, stop):
    """Dossiers entre path (exclu) et stop (inclus)."""
    d = os.path.dirname(path)
    while d.startswith(stop):
        yield d
        if d == stop:
            break
        d = os.path.dirname(d)

def _benthos_tiles():
    """Liste des tuiles envoyées par BenthOS : {"tuiles": ["sat/15/x/y", ...], "zoom_max": n}."""
    tuiles, zoom_max = [], None
    for chemin in glob.glob(os.path.join(BENTHOS_TILES, "*", "*", "*", "*.png")):
        layer, z, x, y = os.path.relpath(chemin, BENTHOS_TILES)[:-4].split(os.sep)
        if layer in TILE_SOURCES and z.isdigit():
            tuiles.append(f"{layer}/{z}/{x}/{y}")
            zoom_max = max(zoom_max or 0, int(z))
    return {"tuiles": tuiles, "zoom_max": zoom_max}

class ProxyHandler(http.server.SimpleHTTPRequestHandler):

    # Délai max d'inactivité d'une connexion : un client qui disparaît (téléphone
    # hors de portée du wifi) ne bloque pas un thread indéfiniment.
    timeout = 15

    # HTTP/1.1 : la connexion (et sa négociation TLS) est réutilisée pour les
    # requêtes suivantes au lieu d'être refaite pour chaque tuile de carte.
    protocol_version = "HTTP/1.1"
    disable_nagle_algorithm = True   # sinon ~40 ms de latence par réponse en keep-alive

    def setup(self):
        super().setup()
        # Négociation TLS faite ici, dans le thread de la requête, et non dans la
        # boucle principale : une connexion muette ne peut plus bloquer le serveur.
        self.request.do_handshake()

    def _is_static_file(self):
        path = self.path.split('?')[0].split('#')[0]
        local = os.path.join(FRONTEND_DIR, path.lstrip('/'))
        return os.path.isfile(local) or (os.path.isdir(local) and
               os.path.isfile(os.path.join(local, 'index.html')))

    def _proxy(self):
        url = BACKEND + self.path
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length) if length else None
        req = urllib.request.Request(url, data=body, method=self.command)
        for k, v in self.headers.items():
            if k.lower() not in ('host', 'connection', 'transfer-encoding'):
                req.add_header(k, v)
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = resp.read()
                self.send_response(resp.status)
                for k, v in resp.headers.items():
                    if k.lower() not in ('transfer-encoding', 'connection', 'content-length'):
                        self.send_header(k, v)
                # Longueur exacte obligatoire pour garder la connexion ouverte (HTTP/1.1)
                self.send_header('Content-Length', str(len(data)))
                self.end_headers()
                self.wfile.write(data)
        except urllib.error.HTTPError as e:
            data = e.read()
            self.send_response(e.code)
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        except Exception as e:
            self.send_error(502, str(e))

    def _send_deploiement(self):
        """Renvoie le dernier fichier JSON de déploiement reçu (dossier ~/deployments)."""
        fichiers = glob.glob(os.path.join(DEPLOY_DIR, "deploiement_*.json"))
        status, data = 404, {"error": "Aucun fichier de déploiement"}
        if fichiers:
            dernier = max(fichiers, key=os.path.getmtime)
            try:
                with open(dernier, encoding="utf-8") as f:
                    status, data = 200, json.load(f)
                data["fichier"] = os.path.basename(dernier)
            except (OSError, ValueError) as e:
                status, data = 500, {"error": f"Lecture impossible : {e}"}
        self._send_json(status, data)

    def _send_json(self, status, data):
        body = json.dumps(data).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_tile(self, layer, z, x, y):
        """Sert une tuile de carte, par ordre de priorité : tuiles envoyées par
        BenthOS, cache local, puis téléchargement (si le Raspberry a Internet)."""
        if layer not in TILE_SOURCES:
            self.send_error(404)
            return
        benthos = os.path.join(BENTHOS_TILES, layer, z, x, y + ".png")
        local = os.path.join(TILES_DIR, layer, z, x, y + ".png")
        data = None
        if os.path.isfile(benthos):
            with open(benthos, "rb") as f:
                data = f.read()
        elif os.path.isfile(local):
            with open(local, "rb") as f:
                data = f.read()
        else:
            url = TILE_SOURCES[layer].format(z=z, x=x, y=y)
            req = urllib.request.Request(url, headers={"User-Agent": "KOSMOS/5.0"})
            try:
                with urllib.request.urlopen(req, timeout=5) as resp:
                    data = resp.read()
                os.makedirs(os.path.dirname(local), exist_ok=True)
                with open(local, "wb") as f:
                    f.write(data)
                # Le serveur tourne en root : rendre le cache à l'utilisateur kosmos
                st = os.stat(BASE_DIR)
                for p in (local, *_parents(local, TILES_DIR)):
                    os.chown(p, st.st_uid, st.st_gid)
            except Exception:
                data = None
        if data is None:
            self.send_error(404)
            return
        self.send_response(200)
        # Les tuiles satellite sont des JPEG malgré l'extension .png
        self.send_header("Content-Type", "image/jpeg" if data[:2] == b"\xff\xd8" else "image/png")
        self.send_header("Cache-Control", "max-age=86400")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        tile = TILE_RE.match(self.path.split('?')[0])
        if tile:
            self._send_tile(*tile.groups())
        elif self.path.split('?')[0] == '/api/deploiement':
            self._send_deploiement()
        elif self.path.split('?')[0] == '/api/tuiles':
            self._send_json(200, _benthos_tiles())
        elif self._is_static_file():
            super().do_GET()
        else:
            self._proxy()

    def do_POST(self):
        self._proxy()

    def end_headers(self):
        # Oblige le navigateur à revérifier les fichiers de l'appli (html/js/css)
        # pour qu'une mise à jour soit prise en compte sans vider le cache.
        if self.path.split('?')[0].endswith(('.html', '.js', '.css', '/')):
            self.send_header("Cache-Control", "no-cache")
        super().end_headers()

    def log_message(self, fmt, *args):
        pass

class ThreadedHTTPSServer(ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    request_queue_size = 64

    def handle_error(self, request, client_address):
        pass   # connexions coupées / négociations TLS ratées : sans importance

server = ThreadedHTTPSServer(("0.0.0.0", PORT), ProxyHandler)
context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain(CERT_FILE, KEY_FILE)
server.socket = context.wrap_socket(server.socket, server_side=True,
                                     do_handshake_on_connect=False)

print(f"Serveur HTTPS démarré sur https://{IP}")
server.serve_forever()
