const serverUrl = location.protocol === 'https:' ? location.origin : 'http://10.42.0.1';

const map = L.map('map').setView([47.6, -3.45], 11);

// ── Mise en page : la carte démarre juste sous l'en-tête (hauteur variable) ──
function adjustLayout() {
  const header = document.querySelector('header');
  const visible = header && getComputedStyle(header).display !== 'none';
  document.getElementById('carte-section').style.top =
    (visible ? header.getBoundingClientRect().bottom : 0) + 'px';
  map.invalidateSize();
}
window.addEventListener('resize', adjustLayout);
window.addEventListener('orientationchange', () => setTimeout(adjustLayout, 300));
if (window.visualViewport) window.visualViewport.addEventListener('resize', adjustLayout);
window.addEventListener('load', adjustLayout);
adjustLayout();

// ── Tuiles hors ligne dans le téléphone ─────────────────────────────────────
// Les tuiles reçues du Raspberry sont aussi rangées dans le cache du navigateur
// (Cache API) : la carte reste affichée hors de portée du wifi KOSMOS.
const TILE_CACHE = 'kosmos-tiles-v1';
const hasCacheApi = 'caches' in window;

// Si le stockage du navigateur ne répond pas vite (Safari avec certificat
// auto-signé, stockage plein…), on abandonne et on charge la tuile normalement :
// le cache hors ligne ne doit jamais empêcher l'affichage de la carte.
const CACHE_TIMEOUT_MS = 1500;

function withTimeout(promise, ms) {
  return Promise.race([promise, new Promise((_, reject) => setTimeout(() => reject(new Error('timeout')), ms))]);
}

let tileCachePromise = null;
function openTileCache() {
  if (!tileCachePromise) {
    tileCachePromise = withTimeout(caches.open(TILE_CACHE), CACHE_TIMEOUT_MS)
      .catch(() => null);   // stockage indisponible : on n'insiste pas
  }
  return tileCachePromise;
}

async function cachedTileSrc(url) {
  if (!hasCacheApi) return url;
  try {
    const cache = await openTileCache();
    if (!cache) return url;
    const hit = await withTimeout(cache.match(url), CACHE_TIMEOUT_MS);
    if (hit) return URL.createObjectURL(await hit.blob());
    // Absente du cache : le navigateur charge la tuile directement (plus rapide),
    // et on la range en parallèle pour l'usage hors ligne.
    fetch(url).then(resp => { if (resp.ok) cache.put(url, resp); }).catch(() => {});
    return url;
  } catch (e) {
    return url;
  }
}

const OfflineTileLayer = L.TileLayer.extend({
  createTile(coords, done) {
    const tile = document.createElement('img');
    tile.alt = '';
    tile.setAttribute('role', 'presentation');
    L.DomEvent.on(tile, 'load', () => {
      if (tile.src.startsWith('blob:')) URL.revokeObjectURL(tile.src);
      this._tileOnLoad(done, tile);
    });
    L.DomEvent.on(tile, 'error', (e) => this._tileOnError(done, tile, e));
    cachedTileSrc(this.getTileUrl(coords)).then(src => { tile.src = src; });
    return tile;
  }
});

// ── Fonds de carte ──────────────────────────────────────────────────────────
// Les tuiles passent par le Raspberry (cache local) : la carte marche sans Internet
// sur la zone pré-téléchargée autour des points du déploiement.
const satellite = new OfflineTileLayer(serverUrl + '/tiles/sat/{z}/{x}/{y}.png', {
  attribution: 'Imagerie © Esri',
  maxNativeZoom: 17,
  maxZoom: 19
}).addTo(map);

const osm = L.tileLayer(serverUrl + '/tiles/osm/{z}/{x}/{y}.png', {
  attribution: '© OpenStreetMap contributors',
  maxZoom: 19
});

// ── Surcouche OpenSeaMap (balisage maritime) ────────────────────────────────
const seamarks = new OfflineTileLayer(serverUrl + '/tiles/seamark/{z}/{x}/{y}.png', {
  attribution: '© OpenSeaMap contributors',
  maxNativeZoom: 17,
  maxZoom: 19
}).addTo(map);

L.control.scale({ imperial: false }).addTo(map);

// ── Couche : points du déploiement (une couleur et un filtre par date) ──────
const deployLayer = L.layerGroup().addTo(map);
const waypointMarkers = {};   // index du point -> { marker, color }
const dateGroups = new Map(); // date -> { color, layer, count }
let selected = null;          // { index, label, date, latlng }

// Couleurs des dates, de la plus récente à la plus ancienne. Le bleu et l'orange
// sont réservés au téléphone et au KOSMOS.
const DATE_COLORS = ['#D94F38', '#9B59B6', '#2ECC71', '#F1C40F', '#E84393', '#00BCD4', '#8D6E63', '#7F8C8D'];
const SANS_DATE = 'sans-date';
const HIDDEN_DATES_KEY = 'kosmos_dates_masquees';

function readHiddenDates() {
  try { return new Set(JSON.parse(localStorage.getItem(HIDDEN_DATES_KEY)) || []); } catch (e) { return new Set(); }
}

function writeHiddenDates(set) {
  try { localStorage.setItem(HIDDEN_DATES_KEY, JSON.stringify([...set])); } catch (e) {}
}

const hiddenDates = readHiddenDates();

function escapeHtml(text) {
  return String(text).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
}

function formatDate(date) {
  if (date === SANS_DATE) return 'Sans date';
  const [y, m, d] = date.split('-');
  return d && m && y ? `${d}/${m}/${y}` : date;
}

function isToday(date) {
  const t = new Date();
  const iso = `${t.getFullYear()}-${String(t.getMonth() + 1).padStart(2, '0')}-${String(t.getDate()).padStart(2, '0')}`;
  return date === iso;
}

const waypointIcon = (label, color, isSelected) => L.divIcon({
  className: '',
  html: `<div style="
    background:${color};color:#fff;border-radius:50%;
    width:${isSelected ? 36 : 28}px;height:${isSelected ? 36 : 28}px;
    display:flex;align-items:center;justify-content:center;
    font-size:${isSelected ? '0.9rem' : '0.72rem'};font-weight:700;
    text-shadow:0 0 2px rgba(0,0,0,0.6);
    border:${isSelected ? 3 : 2}px solid #fff;
    box-shadow:${isSelected ? '0 0 0 4px #2778A2,' : ''}0 2px 6px rgba(0,0,0,0.35);">${label}</div>`,
  iconSize: isSelected ? [36, 36] : [28, 28],
  iconAnchor: isSelected ? [18, 18] : [14, 14]
});

function selectPoint(p) {
  const prev = selected && waypointMarkers[selected.index];
  if (prev) prev.marker.setIcon(waypointIcon(selected.index, prev.color, false));
  const cur = waypointMarkers[p.index];
  selected = {
    index: p.index,
    label: p.label || 'Point ' + p.index,
    date: p.date || SANS_DATE,
    latlng: L.latLng(p.latitude, p.longitude)
  };
  cur.marker.setIcon(waypointIcon(p.index, cur.color, true));
  updateNavigation();
}

function deselectPoint() {
  const prev = selected && waypointMarkers[selected.index];
  if (prev) prev.marker.setIcon(waypointIcon(selected.index, prev.color, false));
  selected = null;
  updateNavigation();
}

// ── Légende + filtres par date ──────────────────────────────────────────────
const LegendControl = L.Control.extend({
  options: { position: 'topright' },
  onAdd() {
    const div = L.DomUtil.create('div', 'leaflet-bar legend-dates');
    div.innerHTML = `
      <button type="button" class="legend-toggle">Dates <span class="legend-arrow">▾</span></button>
      <div class="legend-body"></div>`;
    L.DomEvent.disableClickPropagation(div);
    L.DomEvent.disableScrollPropagation(div);
    // Repliée par défaut sur petit écran
    if (window.innerWidth <= 520) div.classList.add('collapsed');
    div.querySelector('.legend-toggle').addEventListener('click', () => div.classList.toggle('collapsed'));
    this._body = div.querySelector('.legend-body');
    this.render();
    return div;
  },
  render() {
    if (!this._body) return;   // pas encore ajoutée à la carte
    if (dateGroups.size === 0) { this._body.innerHTML = '<div class="legend-empty">Aucun point</div>'; return; }
    const rows = [...dateGroups.entries()].map(([date, g]) => `
      <label class="legend-row">
        <input type="checkbox" data-date="${escapeHtml(date)}" ${hiddenDates.has(date) ? '' : 'checked'}>
        <span class="legend-swatch" style="background:${g.color}"></span>
        <span class="legend-date">${formatDate(date)}${isToday(date) ? ' <em>aujourd’hui</em>' : ''}</span>
        <span class="legend-count">${g.count}</span>
      </label>`).join('');
    this._body.innerHTML = rows + (dateGroups.size > 1 ? `
      <div class="legend-actions">
        <a href="#" data-action="all">Tout</a> · <a href="#" data-action="none">Aucun</a>
      </div>` : '');

    this._body.querySelectorAll('input[data-date]').forEach(cb =>
      cb.addEventListener('change', () => setDateVisible(cb.dataset.date, cb.checked)));
    this._body.querySelectorAll('[data-action]').forEach(a =>
      a.addEventListener('click', (e) => {
        e.preventDefault();
        const show = a.dataset.action === 'all';
        for (const date of dateGroups.keys()) setDateVisible(date, show, false);
        this.render();
      }));
  }
});
const legend = new LegendControl();

function setDateVisible(date, visible, rerender = true) {
  const g = dateGroups.get(date);
  if (!g) return;
  if (visible) {
    hiddenDates.delete(date);
    deployLayer.addLayer(g.layer);
  } else {
    hiddenDates.add(date);
    deployLayer.removeLayer(g.layer);
    if (selected && selected.date === date) deselectPoint();
  }
  writeHiddenDates(hiddenDates);
  if (rerender) legend.render();
}

// ── Chargement du déploiement : rafraîchi automatiquement, avec copie locale ──
// Le dernier fichier reçu est gardé dans le navigateur (localStorage) : si le
// wifi KOSMOS est perdu, les points restent affichés et le calcul continue.
const DEPLOY_CACHE_KEY = 'kosmos_deploiement';
const DEPLOY_POLL_MS = 10000;
let lastDeployJson = null;

function readDeployCache() {
  try { return JSON.parse(localStorage.getItem(DEPLOY_CACHE_KEY)); } catch (e) { return null; }
}

function writeDeployCache(data) {
  try { localStorage.setItem(DEPLOY_CACHE_KEY, JSON.stringify(data)); } catch (e) {}
}

function drawDeploiement(data) {
  deployLayer.clearLayers();
  dateGroups.clear();
  for (const k in waypointMarkers) delete waypointMarkers[k];

  const points = (data.waypoints || []).slice().sort((a, b) => a.index - b.index);

  // Regroupement par date (la plus récente en premier) ; à défaut de date propre
  // au point, on prend la date du déploiement.
  const dateOf = p => p.date || data.date_deploiement || SANS_DATE;
  const dates = [...new Set(points.map(dateOf))].sort().reverse();
  if (dates.includes(SANS_DATE)) dates.push(dates.splice(dates.indexOf(SANS_DATE), 1)[0]);
  dates.forEach((date, i) => {
    dateGroups.set(date, { color: DATE_COLORS[i % DATE_COLORS.length], layer: L.layerGroup(), count: 0 });
  });

  // Tracé reliant dans l'ordre les points de la date la plus récente (le
  // déploiement en cours) ; les dates plus anciennes servent de repères.
  if (dates.length > 0 && dates[0] !== SANS_DATE) {
    const g = dateGroups.get(dates[0]);
    const latlngs = points.filter(p => dateOf(p) === dates[0]).map(p => [p.latitude, p.longitude]);
    if (latlngs.length > 1) {
      L.polyline(latlngs, { color: g.color, weight: 2, opacity: 0.8, dashArray: '6 6' }).addTo(g.layer);
    }
  }

  points.forEach(p => {
    const date = dateOf(p);
    const g = dateGroups.get(date);
    g.count++;
    const pt = { ...p, date };
    const marker = L.marker([p.latitude, p.longitude], { icon: waypointIcon(p.index, g.color, false) })
      .addTo(g.layer)
      .bindPopup(`<b>${escapeHtml(p.label || 'Point ' + p.index)}</b> <small>(n° ${p.index})</small><br>
        Date : ${formatDate(date)}<br>
        Lat : ${p.latitude.toFixed(5)}<br>
        Lon : ${p.longitude.toFixed(5)}`)
      .on('click', () => selectPoint(pt));
    waypointMarkers[p.index] = { marker, color: g.color };
  });

  for (const [date, g] of dateGroups) {
    if (!hiddenDates.has(date)) deployLayer.addLayer(g.layer);
  }
  legend.render();

  // Conserver la sélection si le point existe toujours et que sa date est affichée
  const still = selected && points.find(p => p.index === selected.index);
  if (still && !hiddenDates.has(dateOf(still))) selectPoint({ ...still, date: dateOf(still) });
  else { selected = null; updateNavigation(); }

  // Cadrage sur les points affichés (ou sur tous si tout est masqué)
  const visibles = points.filter(p => !hiddenDates.has(dateOf(p)));
  const cadre = (visibles.length ? visibles : points).map(p => [p.latitude, p.longitude]);
  if (cadre.length > 0) map.fitBounds(cadre, { padding: [40, 40], maxZoom: 15 });
}

// ── Carte hors ligne dans le téléphone ──────────────────────────────────────
// Si BenthOS a envoyé des tuiles avec le JSON, on télécharge exactement celles-là.
// Sinon, on prend la zone autour des points (points + 2 km, zoom 8 à 17) que le
// Raspberry a pu mettre en cache.
const PREFETCH_ZOOM_MIN = 8, PREFETCH_ZOOM_MAX = 17, PREFETCH_MARGE_KM = 2;
let prefetchRunning = false;
let lastTilesSig = null;

function tileXY(lat, lon, z) {
  const n = 2 ** z;
  const x = Math.floor((lon + 180) / 360 * n);
  const y = Math.floor((1 - Math.asinh(Math.tan(lat * Math.PI / 180)) / Math.PI) / 2 * n);
  return [x, y];
}

function zoneTiles(data) {
  const points = data.waypoints || [];
  if (points.length === 0) return [];
  const lats = points.map(p => p.latitude), lons = points.map(p => p.longitude);
  const latMoy = lats.reduce((a, b) => a + b, 0) / lats.length;
  const dLat = PREFETCH_MARGE_KM / 111, dLon = PREFETCH_MARGE_KM / (111 * Math.cos(latMoy * Math.PI / 180));
  const nord = Math.max(...lats) + dLat, sud = Math.min(...lats) - dLat;
  const ouest = Math.min(...lons) - dLon, est = Math.max(...lons) + dLon;

  const tuiles = [];
  for (let z = PREFETCH_ZOOM_MIN; z <= PREFETCH_ZOOM_MAX; z++) {
    const [x0, y0] = tileXY(nord, ouest, z), [x1, y1] = tileXY(sud, est, z);
    for (let x = x0; x <= x1; x++)
      for (let y = y0; y <= y1; y++)
        for (const layer of ['sat', 'seamark'])
          tuiles.push(`${layer}/${z}/${x}/${y}`);
  }
  return tuiles;
}

// Au-delà du zoom max disponible, Leaflet agrandit les tuiles du dernier niveau
// au lieu d'afficher du gris.
function setNativeZoom(z) {
  for (const layer of [satellite, seamarks]) {
    if (layer.options.maxNativeZoom === z) continue;
    layer.options.maxNativeZoom = z;
    if (map.hasLayer(layer)) layer._resetView();
  }
}

async function syncOfflineTiles(data) {
  if (prefetchRunning) return;   // on réessaiera au prochain rafraîchissement
  let info = null;
  try {
    const resp = await fetch(serverUrl + '/api/tuiles', { cache: 'no-store' });
    if (resp.ok) info = await resp.json();
  } catch (e) {
    return;   // Raspberry injoignable
  }
  const benthos = (info && info.tuiles) || [];

  // Ne relancer que si le déploiement ou les tuiles reçues ont changé
  const sig = lastDeployJson + '|' + benthos.length;
  if (sig === lastTilesSig) return;
  lastTilesSig = sig;

  if (benthos.length > 0) {
    setNativeZoom(info.zoom_max);
    await prefetchTiles(benthos);
  } else {
    setNativeZoom(PREFETCH_ZOOM_MAX);
    await prefetchTiles(zoneTiles(data));
  }
}

// 2 téléchargements en parallèle seulement : Safari limite à 6 connexions par
// serveur, il en faut de libres pour les tuiles affichées à l'écran.
const PREFETCH_WORKERS = 2;
const PREFETCH_DELAY_MS = 5000;   // laisser d'abord la carte visible se charger

async function prefetchTiles(tuiles) {
  const status = document.getElementById('offline-status');
  if (!hasCacheApi) { status.textContent = 'Carte hors ligne non supportée'; return; }
  if (tuiles.length === 0) return;
  prefetchRunning = true;
  await new Promise(r => setTimeout(r, PREFETCH_DELAY_MS));

  const urls = tuiles.map(t => `${serverUrl}/tiles/${t}.png`);
  const total = urls.length;
  try {
    const cache = await openTileCache();
    if (!cache) throw new Error('cache indisponible');
    let done = 0, failed = 0;
    const worker = async () => {
      while (urls.length) {
        const url = urls.pop();
        try {
          if (!(await cache.match(url))) {
            const resp = await fetch(url);
            if (resp.ok) await cache.put(url, resp);
            else failed++;
          }
        } catch (e) { failed++; }
        done++;
        if (done % 20 === 0) status.textContent = `Carte hors ligne : ${Math.round(100 * done / total)} %`;
      }
    };
    await Promise.all(Array.from({ length: PREFETCH_WORKERS }, worker));
    status.textContent = failed === 0 ? 'Carte hors ligne ✓' : `Carte hors ligne : ${total - failed}/${total} tuiles`;
  } catch (e) {
    status.textContent = 'Carte hors ligne indisponible';
  }
  prefetchRunning = false;
}

async function loadDeploiement() {
  const info = document.getElementById('mission-info');
  let data = null, offline = false;
  try {
    const resp = await fetch(serverUrl + '/api/deploiement', { cache: 'no-store' });
    const body = await resp.json();
    if (!resp.ok) throw new Error(body.error || resp.status);
    data = body;
    writeDeployCache(data);
  } catch (e) {
    data = readDeployCache();
    offline = true;
  }

  if (!data) {
    info.textContent = 'Aucun déploiement disponible';
    return;
  }

  // Ne redessiner que si le fichier a changé (évite de recentrer la carte en boucle)
  const json = JSON.stringify(data);
  if (json !== lastDeployJson) {
    lastDeployJson = json;
    drawDeploiement(data);
  }
  // Vérifié à chaque rafraîchissement : les tuiles BenthOS arrivent après le JSON
  if (!offline) syncOfflineTiles(data);

  const nb = (data.waypoints || []).length;
  info.textContent = `${data.mission || 'Mission'} — ${data.date_deploiement || ''} — ${nb} point(s)`
    + (offline ? ' · hors ligne (copie locale)' : '');
}


// ── Positions GPS : KOSMOS en priorité, téléphone en secours ────────────────
// Le GPS du KOSMOS est lu sur le Raspberry tant que le wifi est disponible et
// qu'il a un fix ; sinon le calcul bascule sur le GPS du téléphone.
const positionLayer = L.layerGroup().addTo(map);
const accuracyCircle = L.circle([0, 0], { radius: 0, color: '#2778A2', weight: 1, fillOpacity: 0.12 });
const phoneDot = L.circleMarker([0, 0], {
  radius: 8, color: '#fff', weight: 3, fillColor: '#2778A2', fillOpacity: 1
}).bindTooltip('Téléphone');
const kosmosDot = L.marker([0, 0], {
  icon: L.divIcon({
    className: '',
    html: `<div style="
      background:#F5A623;width:18px;height:18px;border:3px solid #fff;
      border-radius:4px;box-shadow:0 2px 6px rgba(0,0,0,0.35);"></div>`,
    iconSize: [18, 18],
    iconAnchor: [9, 9]
  })
}).bindTooltip('KOSMOS');
const guideLine = L.polyline([], { color: '#2778A2', weight: 3, dashArray: '4 8' });

let phonePosition = null;    // { latlng, accuracy }
let kosmosPosition = null;   // { latlng, time } — null si wifi perdu ou pas de fix
let kosmosStatus = 'Connexion au KOSMOS…';
let geoError = null;

const KOSMOS_POLL_MS = 2000;
const KOSMOS_TIMEOUT_MS = 3000;

function formatDistance(m) {
  return `${Math.round(m).toLocaleString('fr-FR')} m`;
}

function cardinal(deg) {
  return ['N', 'NE', 'E', 'SE', 'S', 'SO', 'O', 'NO'][Math.round(deg / 45) % 8];
}

// Cap (azimut) en degrés depuis le nord, de a vers b
function bearing(a, b) {
  const toRad = d => d * Math.PI / 180;
  const φ1 = toRad(a.lat), φ2 = toRad(b.lat), Δλ = toRad(b.lng - a.lng);
  const y = Math.sin(Δλ) * Math.cos(φ2);
  const x = Math.cos(φ1) * Math.sin(φ2) - Math.sin(φ1) * Math.cos(φ2) * Math.cos(Δλ);
  return (Math.atan2(y, x) * 180 / Math.PI + 360) % 360;
}

// Source utilisée pour le calcul : KOSMOS si disponible, sinon téléphone
function currentSource() {
  if (kosmosPosition) return { latlng: kosmosPosition.latlng, label: 'GPS KOSMOS' };
  if (phonePosition) {
    return {
      latlng: phonePosition.latlng,
      label: `GPS téléphone ±${Math.round(phonePosition.accuracy)} m (${kosmosStatus})`
    };
  }
  return null;
}

function updateNavigation() {
  const panel = document.getElementById('nav-panel');
  if (!selected) {
    panel.hidden = true;
    positionLayer.removeLayer(guideLine);
    return;
  }
  panel.hidden = false;
  document.getElementById('nav-target').textContent = selected.label;

  const src = currentSource();
  if (!src) {
    document.getElementById('nav-distance').textContent = '—';
    document.getElementById('nav-cap').textContent = '—';
    document.getElementById('nav-details').textContent = geoError || 'En attente de la position GPS…';
    positionLayer.removeLayer(guideLine);
    return;
  }

  const d = map.distance(src.latlng, selected.latlng);
  const cap = Math.round(bearing(src.latlng, selected.latlng));
  document.getElementById('nav-distance').textContent = formatDistance(d);
  document.getElementById('nav-cap').textContent = `${cap}° ${cardinal(cap)}`;
  document.getElementById('nav-details').textContent = src.label;
  guideLine.setLatLngs([src.latlng, selected.latlng]).addTo(positionLayer);
}

// ── GPS du téléphone (suivi continu) ──
function onPosition(pos) {
  geoError = null;
  phonePosition = {
    latlng: L.latLng(pos.coords.latitude, pos.coords.longitude),
    accuracy: pos.coords.accuracy
  };
  accuracyCircle.setLatLng(phonePosition.latlng).setRadius(phonePosition.accuracy).addTo(positionLayer);
  phoneDot.setLatLng(phonePosition.latlng).addTo(positionLayer);
  updateNavigation();
}

function onPositionError(err) {
  geoError = err.code === err.PERMISSION_DENIED
    ? 'Localisation refusée (autoriser dans le navigateur)'
    : 'Position GPS indisponible';
  updateNavigation();
}

if (navigator.geolocation) {
  navigator.geolocation.watchPosition(onPosition, onPositionError, {
    enableHighAccuracy: true,
    maximumAge: 2000,
    timeout: 20000
  });
} else {
  geoError = 'Géolocalisation non supportée';
}

// ── GPS du KOSMOS (interrogé toutes les 2 s via le wifi) ──
async function pollKosmos() {
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), KOSMOS_TIMEOUT_MS);
  try {
    const resp = await fetch(serverUrl + '/gpsPosition', { cache: 'no-store', signal: ctrl.signal });
    const data = await resp.json();
    if (resp.ok && data.has_fix) {
      kosmosPosition = { latlng: L.latLng(data.lat, data.lon), time: Date.now() };
      kosmosDot.setLatLng(kosmosPosition.latlng).addTo(positionLayer);
      kosmosStatus = '';
    } else {
      kosmosPosition = null;
      kosmosStatus = 'KOSMOS sans fix GPS';
    }
  } catch (e) {
    kosmosPosition = null;
    kosmosStatus = 'wifi KOSMOS perdu';
  } finally {
    clearTimeout(timer);
  }
  if (!kosmosPosition) positionLayer.removeLayer(kosmosDot);
  updateNavigation();
  setTimeout(pollKosmos, KOSMOS_POLL_MS);
}
pollKosmos();

document.getElementById('btn-locate').addEventListener('click', () => {
  const src = currentSource();
  if (src) map.setView(src.latlng, Math.max(map.getZoom(), 15));
  else alert(geoError || 'Position GPS pas encore disponible');
});

// Contrôle de couches
L.control.layers(
  { 'Satellite': satellite, 'OpenStreetMap': osm },
  { 'OpenSeaMap': seamarks, 'Points du déploiement': deployLayer, 'Positions GPS': positionLayer },
  { collapsed: true }
).addTo(map);
legend.addTo(map);

loadDeploiement();
setInterval(loadDeploiement, DEPLOY_POLL_MS);
