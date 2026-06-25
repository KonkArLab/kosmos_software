const map = L.map('map').setView([47.0, -3.5], 8);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '© OpenStreetMap contributors',
  maxZoom: 19
}).addTo(map);

L.control.scale({ imperial: false }).addTo(map);

const markers = [];
let pointIndex = 1;

const kosmosDivIcon = (label) => L.divIcon({
  className: '',
  html: `<div style="
    background:var(--c-accent,#D94F38);
    color:#fff;
    border-radius:50%;
    width:28px;height:28px;
    display:flex;align-items:center;justify-content:center;
    font-size:0.72rem;font-weight:700;
    border:2px solid #fff;
    box-shadow:0 2px 6px rgba(0,0,0,0.35);
  ">${label}</div>`,
  iconSize: [28, 28],
  iconAnchor: [14, 14]
});

function updateCount() {
  document.getElementById('point-count').textContent = markers.length + ' point(s)';
}

function addMarker(latlng, label) {
  const marker = L.marker(latlng, { icon: kosmosDivIcon(label), draggable: true })
    .addTo(map)
    .bindPopup(`
      <b>Point ${label}</b><br>
      Lat : ${latlng.lat.toFixed(5)}<br>
      Lon : ${latlng.lng.toFixed(5)}<br>
      <a href="#" onclick="removeMarker(${markers.length});return false;"
         style="color:#D94F38;font-size:0.8rem;">Supprimer</a>
    `);

  marker.on('dragend', function () {
    const p = marker.getLatLng();
    marker.getPopup().setContent(`
      <b>Point ${label}</b><br>
      Lat : ${p.lat.toFixed(5)}<br>
      Lon : ${p.lng.toFixed(5)}<br>
      <a href="#" onclick="removeMarker(${markers.indexOf(marker)});return false;"
         style="color:#D94F38;font-size:0.8rem;">Supprimer</a>
    `);
  });

  markers.push(marker);
  updateCount();
}

// Clic sur la carte → ajoute un point
map.on('click', function (e) {
  addMarker(e.latlng, pointIndex++);
});

// Bouton "+ Point" → centre de la vue actuelle
document.getElementById('btn-add-point').addEventListener('click', function () {
  addMarker(map.getCenter(), pointIndex++);
});

// Bouton "Effacer"
document.getElementById('btn-clear').addEventListener('click', function () {
  markers.forEach(m => map.removeLayer(m));
  markers.length = 0;
  pointIndex = 1;
  updateCount();
});

window.removeMarker = function (idx) {
  if (markers[idx]) {
    map.removeLayer(markers[idx]);
    markers.splice(idx, 1);
    updateCount();
  }
};

// Centrer sur position GPS du téléphone si disponible
if (navigator.geolocation) {
  navigator.geolocation.getCurrentPosition(function (pos) {
    map.setView([pos.coords.latitude, pos.coords.longitude], 12);
  }, function () {});
}
