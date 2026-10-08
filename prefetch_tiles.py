#!/usr/bin/env python3
"""
Pré-télécharge les tuiles de carte (satellite + OpenSeaMap) autour des points
du dernier fichier de déploiement, pour consulter la carte sans Internet.

Lancé automatiquement à la réception d'un JSON (surveillance_deployments.sh),
ou à la main : python3 prefetch_tiles.py
"""

import glob
import json
import math
import os
import urllib.request
from concurrent.futures import ThreadPoolExecutor

BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
DEPLOY_DIR = os.path.join(os.path.dirname(BASE_DIR), "deployments")
TILES_DIR  = os.path.join(os.path.dirname(BASE_DIR), "cache_tuiles")   # hors du dépôt git
BENTHOS_TILES = os.path.join(DEPLOY_DIR, "tiles")   # tuiles déjà envoyées par BenthOS
SOURCES = {
    "sat":     "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
    "seamark": "https://tiles.openseamap.org/seamark/{z}/{x}/{y}.png",
}
ZOOM_MIN, ZOOM_MAX = 8, 17
MARGE_KM = 2.0   # marge autour des points


def tile_xy(lat, lon, z):
    n = 2 ** z
    x = int((lon + 180) / 360 * n)
    y = int((1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * n)
    return x, y


def download(job):
    layer, z, x, y = job
    local = os.path.join(TILES_DIR, layer, str(z), str(x), f"{y}.png")
    if os.path.isfile(local) or os.path.isfile(os.path.join(BENTHOS_TILES, layer, str(z), str(x), f"{y}.png")):
        return 0
    url = SOURCES[layer].format(z=z, x=x, y=y)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "KOSMOS/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read()
        os.makedirs(os.path.dirname(local), exist_ok=True)
        with open(local, "wb") as f:
            f.write(data)
        return 1
    except Exception:
        return 0


def main():
    fichiers = glob.glob(os.path.join(DEPLOY_DIR, "deploiement_*.json"))
    if not fichiers:
        print("Aucun fichier de déploiement")
        return
    with open(max(fichiers, key=os.path.getmtime), encoding="utf-8") as f:
        points = json.load(f).get("waypoints", [])
    if not points:
        print("Aucun point dans le fichier")
        return

    lats = [p["latitude"] for p in points]
    lons = [p["longitude"] for p in points]
    dlat = MARGE_KM / 111.0
    dlon = MARGE_KM / (111.0 * math.cos(math.radians(sum(lats) / len(lats))))
    nord, sud = max(lats) + dlat, min(lats) - dlat
    ouest, est = min(lons) - dlon, max(lons) + dlon

    jobs = []
    for z in range(ZOOM_MIN, ZOOM_MAX + 1):
        x0, y0 = tile_xy(nord, ouest, z)
        x1, y1 = tile_xy(sud, est, z)
        for x in range(x0, x1 + 1):
            for y in range(y0, y1 + 1):
                for layer in SOURCES:
                    jobs.append((layer, z, x, y))

    with ThreadPoolExecutor(max_workers=4) as pool:
        nouvelles = sum(pool.map(download, jobs))
    print(f"{len(jobs)} tuiles couvertes, {nouvelles} nouvelles téléchargées")


if __name__ == "__main__":
    main()
