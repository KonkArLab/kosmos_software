let serverUrl = "http://10.42.0.1:5000";

const defaultMetaData = {
    video: {
        codeStation: "",
        hourDict: { hour: "", minute: "", second: ""},
        gpsDict: { site: "", latitude: "", longitude: "" },
        ctdDict: { depth: "", temperature: "", salinity: "" },
        astroDict: { moon: "", tide: "", coefficient: "" },
        meteoAirDict: { sky: "", wind: "", direction: "", atmPress: "", tempAir: "" },
        meteoMerDict: { seaState: "", swell: "" },
        analyseDict: { exploitability: "", habitat: "", fauna: "", visibility: "" },
    }
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
  const metaData = defaultMetaData;
  const metaDataValues = loadMetaData().video;
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
      createFormRow(sectionContent, key, "Station Code", metaDataValues[key]);
    } else if (key === "hourDict") {
      createTimeField(sectionContent, metaDataValues[key]);
    } else if (typeof value === "object" && !Array.isArray(value)) {
      Object.entries(value).forEach(([subKey, subValue]) => {
        createFormRow(sectionContent, key, subKey, metaDataValues[key][subKey]);
      });
    } else {
      createFormRow(sectionContent, key, metaDataValues.key);
    }

    table.appendChild(sectionContent);
    document.getElementById("formMetaData").addEventListener("submit", submitForm);
  });
  const inputs = document.querySelectorAll('input[type="number"]');
  const maxDecimals = 7;
  inputs.forEach(inputElement => {
    inputElement.addEventListener('input', function() {
      const value = inputElement.value;
      const decimalPart = value.split('.')[1];
      if(decimalPart && decimalPart.length > maxDecimals) {
        inputElement.value = value.slice(0, value.indexOf('.') + maxDecimals + 1);
      }
    });
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
    inputElement.value = value;
    if(inputElement.type === "number"){
      inputElement.setAttribute("step", "0.0000001");
    }
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

function submitForm(event) {
  event.preventDefault();
  dataFinal = defaultMetaData;
  const video = defaultMetaData.video;
  dataFinal["campaign"] = JSON.parse(localStorage.getItem("campaignData"));
  
  dataFinal["system"] = loadMetaData().system;
  video.codeStation = document.getElementById('Station Code')?.value;

  let time = document.getElementById('timeInformation')?.value;

  video.hourDict.hour = parseInt(time.substr(0,2));
  video.hourDict.minute =  parseInt(time.substr(3,2));
  video.hourDict.second =  parseInt(time.substr(6,2));

  video.gpsDict.site = document.getElementById('site')?.value;
  video.gpsDict.latitude = parseFloat(document.getElementById('latitude')?.value);
  if(video.gpsDict.latitude < limits["latitude"]["min"] || video.gpsDict.latitude > limits["latitude"]["max"]) {
    limitError("latitude", limits["latitude"]["min"], limits["latitude"]["max"]);
    return;
  }
  video.gpsDict.longitude = parseFloat(document.getElementById('longitude')?.value);
  if(video.gpsDict.longitude < limits["longitude"]["min"] || video.gpsDict.longitude > limits["longitude"]["max"]) {
    limitError("longitude", limits["longitude"]["min"], limits["longitude"]["max"]);
    return;
  }

  video.ctdDict.depth = parseFloat(document.getElementById('depth')?.value);
  if(video.gpsDict.depth < limits["depth"]["min"] || video.gpsDict.depth > limits["depth"]["max"]) {
    limitError("depth", limits["depth"]["min"], limits["depth"]["max"]);
    return;
  }
  video.ctdDict.temperature = parseFloat(document.getElementById('temperature')?.value);
  if(video.gpsDict.temperature < limits["temperature"]["min"] || video.gpsDict.temperature > limits["temperature"]["max"]) {
    limitError("temperature", limits["temperature"]["min"], limits["temperature"]["max"]);
    return;
  }
  video.ctdDict.salinity = parseInt(document.getElementById('salinity')?.value);
  if(video.gpsDict.salinity < limits["salinity"]["min"] || video.gpsDict.salinity > limits["salinity"]["max"]) {
    limitError("salinity", limits["salinity"]["min"], limits["salinity"]["max"]);
    return;
  }

  video.astroDict.moon = document.getElementById('moon')?.value;
  video.astroDict.tide = document.getElementById('tide')?.value;
  video.astroDict.coefficient = parseInt(document.getElementById('coefficient')?.value);
  if(video.gpsDict.coefficient < limits["coefficient"]["min"] || video.gpsDict.coefficient > limits["coefficient"]["max"]) {
    limitError("coefficient", limits["coefficient"]["min"], limits["coefficient"]["max"]);
    return;
  }

  video.meteoAirDict.sky = document.getElementById('sky')?.value;
  video.meteoAirDict.wind = parseInt(document.getElementById('wind')?.value);
  if(video.gpsDict.wind < limits["wind"]["min"] || video.gpsDict.wind > limits["wind"]["max"]) {
    limitError("wind", limits["wind"]["min"], limits["wind"]["max"]);
    return;
  }
  video.meteoAirDict.direction = document.getElementById('direction')?.value;
  video.meteoAirDict.atmPress = parseFloat(document.getElementById('atmPress')?.value);
  if(video.gpsDict.atmPress < limits["atmPress"]["min"] || video.gpsDict.atmPress > limits["atmPress"]["max"]) {
    limitError("atmPress", limits["atmPress"]["min"], limits["atmPress"]["max"]);
    return;
  }
  video.meteoAirDict.tempAir = parseFloat(document.getElementById('tempAir')?.value);
  if(video.gpsDict.tempAir < limits["tempAir"]["min"] || video.gpsDict.tempAir > limits["tempAir"]["max"]) {
    limitError("tempAir", limits["tempAir"]["min"], limits["tempAir"]["max"]);
    return;
  }

  video.meteoMerDict.seaState = document.getElementById('seaState')?.value;
  video.meteoMerDict.swell = parseInt(document.getElementById('swell')?.value);
  if(video.gpsDict.swell < limits["swell"]["min"] || video.gpsDict.swell > limits["swell"]["max"]) {
    limitError("swell", limits["swell"]["min"], limits["swell"]["max"]);
    return;
  }

  video.analyseDict.exploitability = document.getElementById('exploitability')?.value;
  video.analyseDict.habitat = document.getElementById('habitat')?.value;
  video.analyseDict.fauna = document.getElementById('fauna')?.value;
  video.analyseDict.visibility = document.getElementById('visibility')?.value;

  dataFinal.video = video;

  if ((isNaN(video.gpsDict.latitude) || isNaN(video.gpsDict.longitude)) || isNaN(video.hourDict.hour)) {
    Swal.fire({
      title: 'Error',
      text: 'Hour and GPS information are mandatory',
      icon: 'error',
      confirmButtonText: 'OK'
    });
    return;
  } else {
    sendToBack(dataFinal);
  }

}

function limitError(key, min, max) {
  Swal.fire({
      title: 'Error',
      text: key + ' has to be between ' + min + ' and ' + max + '.',
      icon: 'error',
      confirmButtonText: 'OK'
    });
}

async function sendToBack(data) {
  try {
    const response = await fetch(serverUrl + "/updateMetadata", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(data),
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
