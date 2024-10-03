// Mock JSON file location
const testUrl = "./test.json"; // Ensure this file is placed correctly in your project structure

// Function to fetch metadata from the local mock JSON file
async function fetchMetadata() {
  try {
    const response = await fetch(testUrl); // Fetching the local JSON file
    const data = await response.json(); // Parsing the JSON data
    return data; // Return the parsed data
  } catch (error) {
    console.error("Error fetching mock data:", error);
    return null;
  }
}

// Function to populate the table with metadata and make cells editable (values only)
async function populateMetadataTable() {
  const fileTable = document.getElementById("metadataTable");

  // Fetch metadata from the mock JSON file
  const metadata = await fetchMetadata();

  if (metadata) {
    // Add Code Station row
    let row = fileTable.insertRow();
    row.insertCell().textContent = "Code Station"; // First column with name
    let codeStationCell = row.insertCell(); // Second column with value
    let codeStationInput = document.createElement("input");
    codeStationInput.type = "text";
    codeStationInput.value = metadata.codeStation;
    codeStationCell.appendChild(codeStationInput);

    // Add Heure row
    row = fileTable.insertRow();
    row.insertCell().textContent = "Heure";
    let heureCell = row.insertCell();
    let heureInput = document.createElement("input");
    heureInput.type = "text";
    heureInput.value = `${metadata.heureDict.heure}:${metadata.heureDict.minute}:${metadata.heureDict.seconde}`;
    heureCell.appendChild(heureInput);

    // Add GPS row with latitude and longitude as unchangeable labels
    row = fileTable.insertRow();
    row.insertCell().textContent = "GPS Coordinates";
    let gpsCell = row.insertCell();
    gpsCell.innerHTML = `
      <label>Latitude:</label> <input type="text" value="${metadata.gpsDict.latitude}">
      <label>Longitude:</label> <input type="text" value="${metadata.gpsDict.longitude}">
    `;

    // Add CTD row with profondeur and temperature
    row = fileTable.insertRow();
    row.insertCell().textContent = "CTD (Profondeur / Température)";
    let ctdCell = row.insertCell();
    ctdCell.innerHTML = `
      <label>Profondeur:</label> <input type="text" value="${metadata.ctdDict.profondeur}">
      <label>Température:</label> <input type="text" value="${metadata.ctdDict.temperature}">
    `;

    // Add Astro row
    row = fileTable.insertRow();
    row.insertCell().textContent = "Astro (Lune / Marée)";
    let astroCell = row.insertCell();
    astroCell.innerHTML = `
      <label>Lune:</label> <input type="text" value="${metadata.astroDict.lune}">
      <label>Marée:</label> <input type="text" value="${metadata.astroDict.maree}">
      <label>Coefficient:</label> <input type="text" value="${metadata.astroDict.coefficient}">
    `;

    // Add Météo Air row
    row = fileTable.insertRow();
    row.insertCell().textContent = "Météo Air (Ciel / Vent)";
    let meteoAirCell = row.insertCell();
    meteoAirCell.innerHTML = `
      <label>Ciel:</label> <input type="text" value="${metadata.meteoAirDict.ciel}">
      <label>Vent:</label> <input type="text" value="${metadata.meteoAirDict.vent}">
      <label>Direction:</label> <input type="text" value="${metadata.meteoAirDict.direction}">
      <label>Température:</label> <input type="text" value="${metadata.meteoAirDict.tempAir}">
    `;

    // Add Météo Mer row
    row = fileTable.insertRow();
    row.insertCell().textContent = "Météo Mer (État de la Mer / Houle)";
    let meteoMerCell = row.insertCell();
    meteoMerCell.innerHTML = `
      <label>État Mer:</label> <input type="text" value="${metadata.meteoMerDict.etatMer}">
      <label>Houle:</label> <input type="text" value="${metadata.meteoMerDict.houle}">
    `;

    // Add Analyse row
    row = fileTable.insertRow();
    row.insertCell().textContent = "Analyse (Exploitabilité / Habitat / Faune)";
    let analyseCell = row.insertCell();
    analyseCell.innerHTML = `
      <label>Exploitabilité:</label> <input type="text" value="${metadata.analyseDict.exploitabilite}">
      <label>Habitat:</label> <input type="text" value="${metadata.analyseDict.habitat}">
      <label>Faune:</label> <input type="text" value="${metadata.analyseDict.faune}">
    `;
  } else {
    console.error("No data available to populate the table.");
  }
}

// Call the function to populate the table when the page loads
populateMetadataTable();
