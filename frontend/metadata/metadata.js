let serverUrl = "http://10.42.0.1:5000";

const defaultMetaData = {
    video: {
        codeStation: "",
        hourDict: { hour: 0, minute: 0, second: 0 },
        gpsDict: { site: "", latitude: 0.0, longitude: 0.0 },
        ctdDict: { depth: 0.0, temperature: 0.0, salinity: 0 },
        astroDict: { moon: "NL", tide: "BM", coefficient: 20 },
        meteoAirDict: { sky: "", wind: 0, direction: "N", atmPress: 1013.0, tempAir: 0.0 },
        meteoMerDict: { seaState: "", swell: 0 },
        analyseDict: { exploitability: "", habitat: "", fauna: "", visibility: "" },
    },
    system: {}
};

function loadMetaData() {
  let metaData;
  try {
    metaData = JSON.parse(localStorage.getItem("metaData"));
    defaultMetaData.system = metaData.system;
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
      inputElement.setAttribute("step", "0.1");
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

const fieldsToFill = ["gpsDict"];
const limits = {
  "latitude": {"min": -90, "max": 90},
  "longitude": {"min": -180, "max": 180},
  "coefficient": {"min": 20, "max": 120},
  "wind": {"min": 0, "max": 12},
  "depth": {"min": 0, "max": 4000},
  "temperature": {"min": -10, "max": 60},
  "salinity": {"min": 0, "max": 50},
  "atmPress": {"min": 900, "max": 1100},
  "tempAir": {"min": -90, "max": 90} ,
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
  dataFinal = defaultMetaData;
  const video = defaultMetaData.video;
  dataFinal["campaign"] = JSON.parse(localStorage.getItem("campaignData"));

  video.codeStation = document.getElementById('codeStation')?.value;

  video.hourDict.hour = parseInt(document.getElementById('hour')?.value);
  video.hourDict.minute = parseInt(document.getElementById('minute')?.value);
  video.hourDict.second = parseInt(document.getElementById('second')?.value);

  video.gpsDict.site = document.getElementById('site')?.value;
  video.gpsDict.latitude = parseFloat(document.getElementById('latitude')?.value);
  video.gpsDict.longitude = parseFloat(document.getElementById('longitude')?.value);

  video.ctdDict.depth = parseFloat(document.getElementById('depth')?.value);
  video.ctdDict.temperature = parseFloat(document.getElementById('temperature')?.value);
  video.ctdDict.salinity = parseInt(document.getElementById('salinity')?.value);

  video.astroDict.moon = document.getElementById('moon')?.value;
  video.astroDict.tide = document.getElementById('tide')?.value;
  video.astroDict.coefficient = parseInt(document.getElementById('coefficient')?.value);

  video.meteoAirDict.sky = document.getElementById('sky')?.value;
  video.meteoAirDict.wind = parseInt(document.getElementById('wind')?.value);
  video.meteoAirDict.direction = document.getElementById('direction')?.value;
  video.meteoAirDict.atmPress = parseFloat(document.getElementById('atmPress')?.value);
  video.meteoAirDict.tempAir = parseFloat(document.getElementById('tempAir')?.value);

  video.meteoMerDict.seaState = document.getElementById('seaState')?.value;
  video.meteoMerDict.swell = parseInt(document.getElementById('swell')?.value);

  video.analyseDict.exploitability = document.getElementById('exploitability')?.value;
  video.analyseDict.habitat = document.getElementById('habitat')?.value;
  video.analyseDict.fauna = document.getElementById('fauna')?.value;
  video.analyseDict.visibility = document.getElementById('visibility')?.value;

  if (!(video.gpsDict.latitude || video.gpsDict.longitude || video.hourDict.hour || video.hourDict.minute || video.hourDict.second)) {
    Swal.fire({
      title: 'Error',
      text: 'Hour and GPS information are mandatory',
      icon: 'error',
      confirmButtonText: 'OK'
    });
    return;
  }

  try {
    const response = await fetch(serverUrl + "/updateMetadata", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(dataFinal),
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
