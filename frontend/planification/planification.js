const serverUrl = location.protocol === 'https:' ? location.origin : 'http://10.42.0.1:5000';

const map = L.map('map').setView([47.0, -3.5], 8);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '© OpenStreetMap contributors',
  maxZoom: 19
}).addTo(map);

L.control.scale({ imperial: false }).addTo(map);

// ── Couche : points de planification (rouge, déplaçables) ────────────────────
const planningLayer = L.layerGroup().addTo(map);
const markers = [];
let pointIndex = 1;

const planningIcon = (label) => L.divIcon({
  className: '',
  html: `<div style="
    background:#D94F38;color:#fff;border-radius:50%;
    width:28px;height:28px;display:flex;align-items:center;justify-content:center;
    font-size:0.72rem;font-weight:700;border:2px solid #fff;
    box-shadow:0 2px 6px rgba(0,0,0,0.35);">${label}</div>`,
  iconSize: [28, 28],
  iconAnchor: [14, 14]
});

function updateCount() {
  document.getElementById('point-count').textContent = markers.length + ' point(s)';
}

function addMarker(latlng, label) {
  const marker = L.marker(latlng, { icon: planningIcon(label), draggable: true });

  const popup = () => `
    <b>Point ${label}</b><br>
    Lat : ${marker.getLatLng().lat.toFixed(5)}<br>
    Lon : ${marker.getLatLng().lng.toFixed(5)}<br>
    <a href="#" onclick="removeMarker(${markers.indexOf(marker)});return false;"
       style="color:#D94F38;font-size:0.8rem;">Supprimer</a>`;

  marker.bindPopup(popup());
  marker.on('dragend', () => marker.getPopup().setContent(popup()));
  marker.addTo(planningLayer);
  markers.push(marker);
  updateCount();
}

map.on('click', (e) => addMarker(e.latlng, pointIndex++));

document.getElementById('btn-add-point').addEventListener('click', () => {
  addMarker(map.getCenter(), pointIndex++);
});

document.getElementById('btn-clear').addEventListener('click', () => {
  planningLayer.clearLayers();
  markers.length = 0;
  pointIndex = 1;
  updateCount();
});

window.removeMarker = function (idx) {
  if (markers[idx]) {
    planningLayer.removeLayer(markers[idx]);
    markers.splice(idx, 1);
    updateCount();
  }
};

// ── Couche : plongées enregistrées (bleu, non déplaçables) ──────────────────
const divesLayer = L.layerGroup().addTo(map);

const diveIcon = (name) => L.divIcon({
  className: '',
  html: `<div style="
    background:#20415D;color:#fff;border-radius:4px;
    padding:2px 6px;font-size:0.7rem;font-weight:700;
    white-space:nowrap;border:2px solid #fff;
    box-shadow:0 2px 6px rgba(0,0,0,0.35);">${name}</div>`,
  iconAnchor: [0, 10]
});

async function loadDives() {
  divesLayer.clearLayers();
  try {
    const resp = await fetch(serverUrl + '/getRecordsGPS');
    const body = await resp.json();
    const points = body.data || [];
    points.forEach(p => {
      L.marker([p.lat, p.lon], { icon: diveIcon(p.name) })
        .addTo(divesLayer)
        .bindPopup(`<b>${p.name}</b><br>Lat : ${p.lat.toFixed(5)}<br>Lon : ${p.lon.toFixed(5)}`);
    });
    if (points.length > 0) {
      const bounds = points.map(p => [p.lat, p.lon]);
      map.fitBounds(bounds, { padding: [40, 40] });
    }
  } catch (e) {
    console.error('Erreur chargement plongées :', e);
  }
}

document.getElementById('btn-reload-dives').addEventListener('click', loadDives);

// Contrôle de couches
L.control.layers(null, {
  'Plongées enregistrées': divesLayer,
  'Points de planification': planningLayer
}, { collapsed: true }).addTo(map);

// Chargement initial
loadDives();

// Centrer sur position GPS du téléphone si disponible
if (navigator.geolocation) {
  navigator.geolocation.getCurrentPosition(
    (pos) => { if (divesLayer.getLayers().length === 0) map.setView([pos.coords.latitude, pos.coords.longitude], 12); },
    () => {}
  );
}
