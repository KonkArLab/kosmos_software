let serverUrl = "http://10.42.0.1:5000";

const defaultMetaData = {
    video: {
        codeStation: "",
        hourDict: { hour: 0, minute: 0, second: 0 },
        gpsDict: { site: "", latitude: 0.0, longitude: 0.0 },
        ctdDict: { depth: 0.0, temperature: 0.0, salinity: 0 },
        astroDict: { moon: "NL", tide: "BM", coefficient: 20 },
        meteoAirDict: { sky: "", wind: 0, direction: "N", atmPressure: 1013.0, airTemp: 0.0 },
        meteoMerDict: { seaState: "", swell: 0 },
        analyseDict: { exploitability: "", habitat: "", fauna: "", visibility: "" },
    },
};

function loadMetaData() {
  let metaData;
  try {
    metaData = JSON.parse(localStorage.getItem("metaData"));
  } catch {
    alert("Error reading metaData from localStorage.");
    return defaultMetaData;
  }
  
  if (!metaData || !validateMetaData(metaData)) {
    alert("Invalid or missing metaData. Loading default values.");
    return defaultMetaData;
  }
  return metaData;
}


/*
async function loadMetadataFromBackend()
{
    try {
        const response = await fetch("http://0.0.0.0:5000/get_metadata");
        const result = await response.json();
        
        if (result.status === "success") {
            const metadata = result.data;
            localStorage.setItem("metaData", JSON.stringify(metadata));
            console.log("Metadata loaded from backend:", metadata);
            return metadata;
        } else {
            console.warn("Using default metadata due to backend error.");
            return defaultMetaData;
        }

    } catch (error) {
        console.error("Error loading metadata from backend:", error);
        return defaultMetaData;
    }
}
*/


function validateMetaData(data) {
  return data && data.video && data.video.hourDict && data.video.gpsDict;
}

const sectionTitles = {
  codeStation: "Station Code",
  gpsDict: "GPS Coordinates",
  meteoAirDict: "Meteorological Air Information",
  meteoMerDict: "Meteorological Sea Information",
  analyseDict: "Exploitability Information",
  hourDict: "Hour",
  ctdDict: "CTD Information",
  astroDict: "Astronomical Information",
};

function initializeChoices(selectElement, choicesArray) {
  new Choices(selectElement, {
    searchEnabled: true,
    shouldSort: false,
    choices: choicesArray.map(choice => ({ value: choice.value, label: choice.label })),
  });
}

function generateTable() {
  const metaData = loadMetaData();
  const table = document.getElementById("metadataTable");

  Object.entries(metaData.video).forEach(([key, value]) => {
    const sectionTitle = sectionTitles[key] || key;

    const titleRow = document.createElement("tr");
    const titleCell = document.createElement("td");
    titleCell.colSpan = 2;
    titleCell.textContent = sectionTitle;
    titleCell.classList.add("section-title");

    titleCell.addEventListener("click", () => {
      sectionContent.classList.toggle("collapsed");
      titleCell.classList.toggle("collapsed");
    });

    titleRow.appendChild(titleCell);
    table.appendChild(titleRow);

    const sectionContent = document.createElement("tbody");
    sectionContent.classList.add("section-content");

    if (key === "codeStation") {
      createFormRow(sectionContent, key, "Station Code", value);
    } else if (key === "hourDict") {
      createTimeField(sectionContent, value);
    } else if (typeof value === "object" && !Array.isArray(value)) {
      Object.entries(value).forEach(([subKey, subValue]) => {
        createFormRow(sectionContent, key, subKey, subValue);
      });
    } else {
      createFormRow(sectionContent, key, value);
    }

    table.appendChild(sectionContent);

    document.getElementById("formMetaData").addEventListener("submit", submitForm);
  });
}

/*
async function generateTable()
{
    const metaData = await loadMetadataFromBackend();
    const table = document.getElementById("metadataTable");

    Object.entries(metaData.video).forEach(([key, value]) => {
        const sectionTitle = sectionTitles[key] || key;

        const titleRow = document.createElement("tr");
        const titleCell = document.createElement("td");
        titleCell.colSpan = 2;
        titleCell.textContent = sectionTitle;
        titleCell.classList.add("section-title");

        titleCell.addEventListener("click", () => {
            sectionContent.classList.toggle("collapsed");
            titleCell.classList.toggle("collapsed");
        });

        titleRow.appendChild(titleCell);
        table.appendChild(titleRow);

        const sectionContent = document.createElement("tbody");
        sectionContent.classList.add("section-content");

        if (key === "codeStation") {
            createFormRow(sectionContent, key, "Station Code", value);
        } else if (key === "hourDict") {
            createTimeField(sectionContent, value);
        } else if (typeof value === "object" && !Array.isArray(value)) {
            Object.entries(value).forEach(([subKey, subValue]) => {
                createFormRow(sectionContent, key, subKey, subValue);
            });
        } else {
            createFormRow(sectionContent, key, value);
        }

        table.appendChild(sectionContent);
    });

    document.getElementById("formMetaData").addEventListener("submit", submitForm);
}
*/


function createTimeField(container, timeValues) {
  const row = document.createElement("tr");

  const labelCell = document.createElement("td");
  labelCell.textContent = sectionTitles.hourDict;
  row.appendChild(labelCell);

  const inputCell = document.createElement("td");
  const timeInput = document.createElement("input");
  timeInput.type = "time";
  timeInput.step = 1;
  timeInput.value = formatTime(timeValues);
  timeInput.id = "timeInformation";
  inputCell.appendChild(timeInput);
  row.appendChild(inputCell);

  container.appendChild(row);
}

function createFormRow(container, sectionKey, label, value) {
  const row = document.createElement("tr");

  const labelCell = document.createElement("label");
  labelCell.setAttribute("for", label);
  const tdCell = document.createElement("td");
  labelCell.textContent = sectionTitles[label] || label.charAt(0).toUpperCase() + label.slice(1);
  tdCell.appendChild(labelCell);
  row.appendChild(tdCell);

  const inputCell = document.createElement("td");
  let inputElement;

  if (label === "direction" || label === "tide" || label === "moon" || label === "seaState") {
    inputElement = document.createElement("select");
    inputElement.setAttribute("id", label);
    initializeChoices(inputElement, getChoicesForField(label));
    inputElement.value = value;
  } else {
    inputElement = document.createElement("input");
    inputElement.setAttribute("id", label);
    inputElement.type = determineInputType(value);
    if(inputElement.type === "number"){
      inputElement.setAttribute("step", "0.00001");
      inputElement.setAttribute("oninput", "verifierFloat(this)");
    }
    inputElement.value = value;
  }

  inputElement.classList.add("form-input");
  inputCell.appendChild(inputElement);
  row.appendChild(inputCell);

  container.appendChild(row);
}

function getChoicesForField(field) {
  const choicesData = {
    direction: [
      { value: "N", label: "N : Nord" },
      { value: "NE", label: "NE : Nord-Est" },
      { value: "NO", label: "NO : Nord-Ouest" },
      { value: "S", label: "S : Sud" },
      { value: "SE", label: "SE : Sud-Est" },
      { value: "SO", label: "SO : Sud-Ouest" },
      { value: "E", label: "E : Est" },
      { value: "O", label: "O : Ouest" },
    ],
    tide: [
      { value: "BM", label: "BM (Low Tide)" },
      { value: "BM+1", label: "BM+1" },
      { value: "BM-1", label: "BM-1" },
      { value: "PM", label: "PM (High Tide)" },
      { value: "PM+1", label: "PM+1" },
      { value: "PM-1", label: "PM-1" },
    ],
    moon: [
      { value: "NL", label: "NL : Nouvelle Lune (New Moon)" },
      { value: "PC", label: "PC : Premier Croissant (Waxing Crescent)" },
      { value: "PQ", label: "PQ : Premier Quartier (First Quarter)" },
      { value: "GL", label: "GL : Gibbeuse Croissante (Waxing Gibbous)" },
      { value: "PL", label: "PL : Pleine Lune (Full Moon)" },
      { value: "GD", label: "GD : Gibbeuse Décroissante (Waning Gibbous)" },
      { value: "DQ", label: "DQ : Dernier Quartier (Last Quarter)" },
      { value: "DC", label: "DC : Dernier Croissant (Waning Crescent)" },
    ],
    seaState: [
      { value: "Calm", label: "Calme" },
      { value: "Rippled", label: "Ridée" },
      { value: "Smooth", label: "Belle" },
      { value: "Slight", label: "Peu agitée" },
      { value: "Moderate", label: "Agitée" },
      { value: "Rough", label: "Forte" },
      { value: "Very rough", label: "Grosse" },
      { value: "High", label: "Très grosse" },
      { value: "Phenomenal", label: "Énorme" },
    ],  
  };
  return choicesData[field] || [];
}

function determineInputType(value) {
  return typeof value === "number" ? "number" : "text";
}

function verifierFloat(input) {
  const maxDecimals = 5;
  if (!input.checkValidity()) {
    let valeurFloat = parseFloat(input.value);

    if (!isNaN(valeurFloat)) {
      input.value = valeurFloat.toFixed(maxDecimals);
    }
  } 
}

function formatTime(timeDict) {
  const { hour, minute, second } = timeDict;
  return `${String(hour).padStart(2, '0')}:${String(minute).padStart(2, '0')}:${String(second).padStart(2, '0')}`;
}

const fieldsToFill = ["gpsDict", "ctdDict"];
const limits = {
  "latitude": {"min": -90, "max": 90},
  "longitude": {"min": -180, "max": 180},
  "coefficient": {"min": 20, "max": 120},
  "wind": {"min": 0, "max": 12},
  "depth": {"min": 0, "max": 4000},
  "temperature": {"min": -10, "max": 40},
  "salinity": {"min": 0, "max": 50},
  "atmPressure": {"min": 900, "max": 1100},
  "airTemp": {"min": -90, "max": 90} ,
  "swell": {"min": 0, "max": 30} 
}

function validateField(type, key, subKey, value) {
  if (!value && fieldsToFill.includes(key)) {
    return [false, subKey, "Fill at least the four first sections"];
  }
  if (type === "number") {
    if (limits[subKey] && (value < limits[subKey]["min"] || value > limits[subKey]["max"])) {
      return [false, subKey, `The value for ${subKey} must be between ${limits[subKey]["min"]} and ${limits[subKey]["max"]}`];
    }
  }
  return [true, "", ""];
}

async function submitForm(event) {
  event.preventDefault();

  const formData = {};
  let validatedField = [true, "", ""];

  for (const [key, value] of Object.entries(defaultMetaData.video)) {
    if (key === "codeStation") {
      const stationCode = document.getElementById("Station Code").value;
      formData[key] = stationCode;
      if (!stationCode) {
        validatedField = [false, "Station Code", "Fill at least the four first sections"];
        break;
      }
    } else if (key === "heureDict") {
      const time = document.getElementById("timeInformation").value;
      if (time) {
        const [heure, minute, second] = time.split(":").map(Number);
        formData[key] = { heure, minute, second };
      } else {
        validatedField = [false, "timeInformation", "Fill at least the four first sections"];
        break;
      }
    } else if (typeof value === "object" && !Array.isArray(value)) {
      formData[key] = {};
      for (const [subKey, subValue] of Object.entries(value)) {
        const fieldValue = document.getElementById(subKey).value;
        validatedField = validateField(document.getElementById(subKey).type, key, subKey, fieldValue);
        if (!validatedField[0]) {
          break;
        }
        formData[key][subKey] = fieldValue;
      }
      if (!validatedField[0]) {
        break;
      }
    } else {
      const fieldValue = document.getElementById(key).value;
      validatedField = validateField(document.getElementById(key).type, key, key, fieldValue);
      if (!validatedField[0]) {
        break;
      }
      formData[key] = fieldValue;
    }
  }
  
  if (!validatedField[0]) {
    Swal.fire({
      title: 'Error',
      text: validatedField[2],
      icon: 'error',
      confirmButtonText: 'OK'
    }).then(() => {
      document.getElementById(validatedField[1]).focus();
    });
    return;
  }

  //formData["campagne"] = JSON.parse(localStorage.getItem("campagneData"));
  try {
    const response = await fetch("", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(formData),
    });
  
    if (response.ok) {
      Swal.fire({
        title: 'Success',
        text: 'Information saved',
        icon: 'success',
        confirmButtonText: 'OK'
      });
      window.location.href = "../index.html";
    } else {
      Swal.fire({
        title: 'Error',
        text: 'Error occuring while sending data. Retry',
        icon: 'error',
        confirmButtonText: 'OK'
      });
      return;
    }
  } catch (e) {
    Swal.fire({
      title: 'Error',
      text: 'Error occuring while sending data. Retry',
      icon: 'error',
      confirmButtonText: 'OK'
    });
    return;
  }
  
}

document.addEventListener("DOMContentLoaded", generateTable);

/*
async function submitForm(event) 
{
    event.preventDefault();

    const metaData = {};
    const tableRows = document.querySelectorAll("#metadataTable tr");

    tableRows.forEach(row => {
        const inputs = row.querySelectorAll("input, select");
        inputs.forEach(input => {
            if (input.id && input.value) {
                const keys = input.id.split('.');
                let current = metaData;
                keys.forEach((key, index) => {
                    if (index === keys.length - 1) {
                        current[key] = input.value;
                    } else {
                        current[key] = current[key] || {};
                        current = current[key];
                    }
                });
            }
        });
    }); // pas très sur pour cete fonction

    try {
        const response = await fetch("http://0.0.0.0:5000/update_metadata", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(metaData),
        });

        if (response.ok) {
            alert("Metadata saved successfully!");
        } else {
            alert("Error saving metadata.");
        }

    } catch (error) {
        console.error("Failed to save metadata:", error);
        alert("Failed to save metadata.");
    }
}


*/
