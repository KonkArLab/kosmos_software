// This variable holds the URL of the server where the backend is hosted
let serverUrl = location.protocol === "https:" ? location.origin : "http://10.42.0.1:5000";
// Alternative server URL (commented out)
// let serverUrl = "http://10.29.225.198:5000";

// Function to fetch records data from the server
async function fetchData() {
  try {
    const response = await fetch(serverUrl + "/getRecords");
    const data = await response.json();
    return data.data;
  } catch (error) {
    console.error("Error fetching data:", error);
    return [];
  }
}

// Function to populate the table with records data
async function populateTable() {
  const fileTable = document.getElementById("fileTable");

  // Fetch records data from the API
  const records = await fetchData();

  // Clear existing rows in the table (excluding the header)
  while (fileTable.rows.length > 1) {
    fileTable.deleteRow(1);
  }

  // Reverse the records array before adding rows
  const reversedRecords = records.reverse();

  // Iterate over reversed records and create table rows
  reversedRecords.forEach((record) => {
    const row = fileTable.insertRow();
    row.insertCell().textContent = record.fileName;
    row.insertCell().textContent = record.size;

    // Merge Time, Day, and Month into a single column
    const timeCell = row.insertCell();
    timeCell.textContent = `${record.time} ${record.day} ${record.month}`;
  });
}

// Call the function to populate the table when the page loads
populateTable();

// ── Carte des plongées ────────────────────────────────────────────────────────
const recordsMap = L.map('records-map').setView([47.0, -3.5], 7);

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '© OpenStreetMap contributors',
  maxZoom: 19
}).addTo(recordsMap);

L.control.scale({ imperial: false }).addTo(recordsMap);

async function loadRecordsOnMap() {
  try {
    const resp = await fetch(serverUrl + "/getRecordsGPS");
    const body = await resp.json();
    const points = body.data;
    if (!points || points.length === 0) return;

    const bounds = [];

    points.forEach(function (p) {
      const icon = L.divIcon({
        className: '',
        html: `<div style="
          background:var(--c-primary,#20415D);
          color:#fff;
          border-radius:4px;
          padding:2px 6px;
          font-size:0.7rem;
          font-weight:700;
          white-space:nowrap;
          border:2px solid #fff;
          box-shadow:0 2px 6px rgba(0,0,0,0.35);
        ">${p.name}</div>`,
        iconAnchor: [0, 10]
      });

      L.marker([p.lat, p.lon], { icon: icon })
        .addTo(recordsMap)
        .bindPopup(`<b>${p.name}</b><br>Lat : ${p.lat.toFixed(5)}<br>Lon : ${p.lon.toFixed(5)}`);

      bounds.push([p.lat, p.lon]);
    });

    recordsMap.fitBounds(bounds, { padding: [30, 30] });
  } catch (e) {
    console.error('Erreur chargement GPS records :', e);
  }
}

loadRecordsOnMap();
