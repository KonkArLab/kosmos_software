let serverUrl = "http://10.42.0.1:5000";

const fields = [
  { id: "increment", placeholder: "", type: "text", label: "Increment", tabIndex: 1, maxlength: "4", isVisible:false },
  { id: "codestation", placeholder: "", type: "text", label: "Code Station", tabIndex: 2, maxlength: "200", isVisible:true },
  { id: "hour", placeholder: "", type: "time", label: "Hour", tabIndex: 3 , isVisible:true},
  { id: "latitude", placeholder: "", type: "number", label: "Latitude", tabIndex: 4, min: "-90", max: "90" , isVisible:true},
  { id: "longitude", placeholder: "", type: "number", label: "Longitude", tabIndex: 5, min: "-180", max: "180" , isVisible:true},
  { id: "site", placeholder: "", type: "text", label: "Site", tabIndex: 6, maxlength: "200" , isVisible:false},
  { id: "depth", placeholder: "", type: "number", label: "Depth (m)", tabIndex: 7, min: "0", max: "4000", isVisible:false},
  { id: "temperature", placeholder: "", type: "number", label: "Temperature (°C)", tabIndex: 8, min: "-10", max: "60" , isVisible:false},
  { id: "moon", placeholder: "", type: "text", label: "Moon phase", tabIndex: 9, maxlength: "200", choices : true , isVisible:false},
  { id: "tide", placeholder: "", type: "text", label: "Tide", tabIndex: 10, maxlength: "200", choices : true, isVisible:false},
  { id: "coefficient", placeholder: "", type: "number", label: "Tide coefficient", tabIndex: 11, min: "20", max: "120" , isVisible:false},
  { id: "sky", placeholder: "", type: "text", label: "Sky", tabIndex: 12, maxlength: "200" , isVisible:false},
  { id: "wind", placeholder: "", type: "number", label: "Wind (Bft)", tabIndex: 13, min: "0", max: "12" , isVisible:false},
  { id: "direction", placeholder: "", type: "text", label: "Wind direction", tabIndex: 14, maxlength: "200", choices : true, isVisible:false},
  { id: "seaState", placeholder: "", type: "text", label: "Sea state", tabIndex: 15, maxlength: "200", choices : true, isVisible:false },
  { id: "swell", placeholder: "", type: "number", label: "Swell (m)", tabIndex: 16, min: "0", max: "30", isVisible:false},
  { id: "exploitability", placeholder: "", type: "text", label: "Exploitability", tabIndex: 17, maxlength: "200" , isVisible:false},
  { id: "habitat", placeholder: "", type: "text", label: "Habitat", tabIndex: 18, maxlength: "200" , isVisible:false},
  { id: "fauna", placeholder: "", type: "text", label: "Fauna", tabIndex: 19, maxlength: "200" , isVisible:false},
  { id: "visibility", placeholder: "", type: "text", label: "Visibility", tabIndex:20, maxlength: "200" , isVisible:false}
];

// Default metadata object in case no data is available

const defaultMetaData = {
  system: {},
  campaign: {},
  video: {
    stationDict: {codestation:String, increment: String},
    hourDict: { hour: Number, minute: Number, second: Number, hourOS: Number, minuteOS: Number, secondOS: Number },
    gpsDict: { site: String, latitude: Number, longitude: Number },
    ctdDict: { depth: Number, temperature: Number, salinity: String },
    astroDict: { moon: String, tide: String, coefficient: Number },
    meteoAirDict: { sky: String, wind: Number, direction: String, atmPress: Number, tempAir: Number },
    meteoMerDict: { seaState: String, swell: Number },
    analyseDict: { exploitability: String, habitat: String, fauna: String, visibility: String }
  }
};

const dataFinal = {
  system: {},
  campaign: {},
  video: {}
}

// Load metadata from localStorage, or return defaults if not available
function loadMetaData() {
  let metaData;
  try {
    metaData = JSON.parse(localStorage.getItem("metaData"));
  } catch {
    alert("Error reading metaData from localStorage.");
    return defaultMetaData;
  }
  // Validate metadata and load default if invalid
  if (!metaData || !validateMetaData(metaData)) {
    alert("Invalid or missing metaData. Loading default values.");
    return defaultMetaData;
  }
  return metaData;
}

function validateMetaData(data) {
  return data && data.video;
}

const sectionTitles = {
  stationDict: "Station Code",
  gpsDict: "Location",
  meteoAirDict: "Meteorological Air Information",
  meteoMerDict: "Meteorological Sea Information",
  analyseDict: "Analysis",
  hourDict: "Hour",
  ctdDict: "Depth and Temperature",
  astroDict: "Astronomical Information",
};

// List of choices for some metadatas
function getChoicesForField(field) {
  const choicesData = {
    direction: [
      { value: "", label: "" },
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
      { value: "", label: ""},
      { value: "BM", label: "BM (Low Tide)" },
      { value: "BM+1", label: "BM+1" },
      { value: "BM-1", label: "BM-1" },
      { value: "PM", label: "PM (High Tide)" },
      { value: "PM+1", label: "PM+1" },
      { value: "PM-1", label: "PM-1" },
    ],
    moon: [
      { value: "", label: ""},
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
      { value: "", label: "" },
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

function initializeChoices(selectElement, choicesArray) {
  new Choices(selectElement, {
    searchEnabled: true,
    shouldSort: false,
    choices: choicesArray.map(choice => ({ value: choice.value, label: choice.label })),
  });
}

function generateTable() {
  const table = document.getElementById("metadataTable");
  table.innerHTML = ""; // Limpia la tabla existente

  if(localStorage.getItem("pending")) {
    Swal.fire({
      title: 'Alert',
      text: 'You have a previous measure pending. Please fill the information before start a new camera record',
      icon: 'info',
      confirmButtonText: 'OK'
    });
  };

  localStorage.setItem("pending", JSON.stringify("1"));

  const metaDataFromStorage = loadMetaData();
  dataFinal["system"] = metaDataFromStorage.system;
  dataFinal.campaign = JSON.parse(localStorage.getItem("campaignData"));

  const metaDataValues = metaDataFromStorage.video || {};
  
  Object.entries(defaultMetaData.video).forEach(([sectionKey, sectionValue]) => {
    // Crear la fila del título de la sección
    const titleRow = document.createElement("tr");
    const titleCell = document.createElement("td");
    titleCell.colSpan = 2;
    titleCell.textContent = sectionTitles[sectionKey];
    titleCell.classList.add("section-title");

    // Comportamiento de colapsar
    titleCell.addEventListener("click", () => {
      sectionContent.classList.toggle("collapsed");
      titleCell.classList.toggle("collapsed");
    });

    titleRow.appendChild(titleCell);
    table.appendChild(titleRow);

    const sectionContent = document.createElement("tbody");
    sectionContent.classList.add("section-content");

    if (sectionKey === "hourDict") {
      // Agregar los campos de fecha y hora en esta sección
      ["date", "hour"].forEach(subKey => {
        const field = fields.find(f => f.id === subKey);
        if (field && field.isVisible) createFormRowWithButton(sectionContent, field, metaDataValues[subKey]);
      });
    } else if (typeof sectionValue === "object" && !Array.isArray(sectionValue)) {
      // Si es un objeto, iterar por sus claves
      Object.keys(sectionValue).forEach(subKey => {
        const field = fields.find(f => f.id === subKey);
        if (field && field.isVisible) createFormRow(sectionContent, field, metaDataValues[sectionKey][subKey]);
      });
    } else {
      const field = fields.find(f => f.id === sectionKey);
      if (field && field.isVisible) createFormRow(sectionContent, field, metaDataValues[sectionKey]);
    }
    table.appendChild(sectionContent);
    document.getElementById("formMetaData").addEventListener("submit", submitForm);
  });
}

function createFormRowWithButton(container, field, value) {
  const row = document.createElement("tr");

  const labelCell = document.createElement("td");
  const label = document.createElement("label");
  label.textContent = field.label;
  label.setAttribute("for", field.id);
  labelCell.appendChild(label);
  row.appendChild(labelCell);

  const inputCell = document.createElement("td");
  const inputElement = document.createElement("input");
  inputElement.type = field.type;
  inputElement.id = field.id;
  inputElement.placeholder = field.placeholder || "";
  
  const noww = new Date().toTimeString().split(" ")[0];  
  inputElement.value = noww.split(":").slice(0, 2).join(":") || "";
  inputElement.tabIndex = field.tabIndex;
  inputElement.classList.add("form-input");


  const button = document.createElement("button");
  button.type = "button";
  button.textContent = "Set Current";
  button.id = "setHour";
  button.addEventListener("click", () => {
    if (field.type === "time") {
       const now = new Date().toTimeString().split(" ")[0];
       inputElement.value = now.split(":").slice(0, 2).join(":"); 
    }
  });

  inputCell.appendChild(inputElement);
  //inputCell.appendChild(button);
  row.appendChild(inputCell);

  container.appendChild(row);
}

function createFormRow(container, field, value) {
  const row = document.createElement("tr");

  const labelCell = document.createElement("td");
  const label = document.createElement("label");
  label.textContent = field.label;
  label.setAttribute("for", field.id);
  labelCell.appendChild(label);
  row.appendChild(labelCell);

  const inputCell = document.createElement("td");
  let inputElement;

  if (field.choices) {
    inputElement = document.createElement("select");
    inputElement.id = field.id;
    initializeChoices(inputElement, getChoicesForField(field.id));
    if (value && typeof value !== 'function') inputElement.value = value;
  } else {
    inputElement = document.createElement("input");
    inputElement.type = field.type;
    inputElement.id = field.id;
    inputElement.placeholder = field.placeholder || "";
    if (field.type === "number") {
      if (field.min) inputElement.min = field.min;
      if (field.max) inputElement.max = field.max;
      if (field.id === "latitude" || field.id === "longitude" ) inputElement.step = "0.0000001";
      if (field.id === "depth" || field.id === "temperature" ) inputElement.step = "0.1";
      if (field.id === "coefficient" || field.id === "wind" || field.id === "wind" ) inputElement.step = "1";
    }
    if (field.maxlength) inputElement.maxLength = field.maxlength;
    if (value && typeof value !== 'function') inputElement.value = value;
    if (field.id === "codestation") {
      const FormData = JSON.parse(localStorage.getItem("campaignData"));
      const MetaData = JSON.parse(localStorage.getItem("metaData"));
      inputElement.value = FormData.zoneDict.zone+FormData.dateDict.date.split('-')[0].split('20')[1]+MetaData.video.stationDict.increment;
    }
  }

  inputElement.tabIndex = field.tabIndex;
  inputElement.classList.add("form-input");
  inputCell.appendChild(inputElement);
  row.appendChild(inputCell);

  container.appendChild(row);
}

function submitForm(event) {
  event.preventDefault();
   
  dataFinal.video = defaultMetaData.video;

  dataFinal.video.stationDict.codestation = document.getElementById('codestation')?.value;
  dataFinal.video.stationDict.increment = document.getElementById('increment')?.value;

  let time = document.getElementById('hour')?.value;

  if (time) {
    dataFinal.video.hourDict.hour = parseInt(time.substr(0,2));
    dataFinal.video.hourDict.minute =  parseInt(time.substr(3,2));
    dataFinal.video.hourDict.second =  0;
  }
  dataFinal.video.hourDict.hourOS = parseInt(document.getElementById('hourOS')?.value);
  dataFinal.video.hourDict.minuteOS =  parseInt(document.getElementById('minuteOS')?.value);
  dataFinal.video.hourDict.secondOS =  parseInt(document.getElementById('secondOS')?.value);
  dataFinal.video.gpsDict.site = document.getElementById('site')?.value;
  dataFinal.video.gpsDict.latitude = parseFloat(document.getElementById('latitude')?.value);
  dataFinal.video.gpsDict.longitude = parseFloat(document.getElementById('longitude')?.value);
  dataFinal.video.ctdDict.depth = parseFloat(document.getElementById('depth')?.value);
  dataFinal.video.ctdDict.temperature = parseFloat(document.getElementById('temperature')?.value);
  dataFinal.video.ctdDict.salinity = parseFloat(document.getElementById('salinity')?.value);
  dataFinal.video.astroDict.moon = document.getElementById('moon')?.value;
  dataFinal.video.astroDict.tide = document.getElementById('tide')?.value;
  dataFinal.video.astroDict.coefficient = parseInt(document.getElementById('coefficient')?.value);
  dataFinal.video.meteoAirDict.sky = document.getElementById('sky')?.value;
  dataFinal.video.meteoAirDict.wind = parseInt(document.getElementById('wind')?.value);
  dataFinal.video.meteoAirDict.direction = document.getElementById('direction')?.value;
  dataFinal.video.meteoAirDict.atmPress = parseFloat(document.getElementById('atmPress')?.value);
  dataFinal.video.meteoAirDict.tempAir = parseFloat(document.getElementById('tempAir')?.value);
  dataFinal.video.meteoMerDict.seaState = document.getElementById('seaState')?.value;
  dataFinal.video.meteoMerDict.swell = parseInt(document.getElementById('swell')?.value);
  dataFinal.video.analyseDict.exploitability = document.getElementById('exploitability')?.value;
  dataFinal.video.analyseDict.habitat = document.getElementById('habitat')?.value;
  dataFinal.video.analyseDict.fauna = document.getElementById('fauna')?.value;
  dataFinal.video.analyseDict.visibility = document.getElementById('visibility')?.value;

  if ((isNaN(dataFinal.video.gpsDict.latitude) || isNaN(dataFinal.video.gpsDict.longitude)) || 
        isNaN(dataFinal.video.hourDict.hour)) {
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
      localStorage.removeItem("pending");
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
