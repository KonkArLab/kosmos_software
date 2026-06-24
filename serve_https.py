#!/usr/bin/env python3
"""
Serveur HTTPS pour le frontend KOSMOS.
Sert les fichiers statiques ET proxifie les appels API vers le backend Flask (port 5000).
Requis pour la géolocalisation sur iOS/Android.

Usage : python3 serve_https.py
Puis visiter : https://10.42.0.1:4443  (accepter l'avertissement de sécurité une fois)
"""

import http.server
import ssl
import os
import subprocess
import urllib.request
import urllib.error

BASE_DIR     = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
CERT_FILE    = os.path.join(BASE_DIR, "cert.pem")
KEY_FILE     = os.path.join(BASE_DIR, "key.pem")
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

class ProxyHandler(http.server.SimpleHTTPRequestHandler):

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
                self.send_response(resp.status)
                for k, v in resp.headers.items():
                    if k.lower() not in ('transfer-encoding', 'connection'):
                        self.send_header(k, v)
                self.end_headers()
                self.wfile.write(resp.read())
        except urllib.error.HTTPError as e:
            self.send_response(e.code)
            self.end_headers()
            self.wfile.write(e.read())
        except Exception as e:
            self.send_error(502, str(e))

    def do_GET(self):
        if self._is_static_file():
            super().do_GET()
        else:
            self._proxy()

    def do_POST(self):
        self._proxy()

    def log_message(self, fmt, *args):
        pass  # Silencieux

server = http.server.HTTPServer(("0.0.0.0", PORT), ProxyHandler)
context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain(CERT_FILE, KEY_FILE)
server.socket = context.wrap_socket(server.socket, server_side=True)

print(f"Serveur HTTPS démarré sur https://{IP}")
print("Sur iPhone/Android : accepter l'avertissement de sécurité une fois.")
server.serve_forever()
