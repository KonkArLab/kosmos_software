// This variable holds the URL of the server where the backend is hosted
let serverUrl = location.protocol === "https:" ? location.origin : "http://10.42.0.1:5000";
// Alternative server URL (commented out)
// let serverUrl = "http://10.29.225.198:5000";

// This variable tracks the state of live video streaming
let live = false;

// Element references
const testLumenButton = document.getElementById("testLumen");

const testIPButton = document.getElementById("testIP");
const changeIPButton = document.getElementById("changeIP");

const startLiveButton = document.getElementById("startLive");
const stopLiveButton = document.getElementById("stopLive");

const testSensorsButton = document.getElementById("testSensors");
const initSensorsButton = document.getElementById("initSensors");

const motorPlusButton = document.getElementById("motorPlus");
const motorMinusButton = document.getElementById("motorMinus");

// Initial setup: disable stop buttons and enable shutdown
testLumenButton.disabled = false;

testSensorsButton.disabled = false;
initSensorsButton.disabled = false;

motorPlusButton.disabled = false;
motorMinusButton.disabled = false;

stopLiveButton.disabled = true;
startLiveButton.disabled = false;

majStateButton();

async function majStateButton() {
  try {
    const response = await fetch(serverUrl + "/state");
    const body = await response.json();
    if (body.state.substr(body.state.length-7) === "WORKING") {
      testLumenButton.disabled = true;
      
      testSensorsButton.disabled = true;
      initSensorsButton.disabled = true;

      motorPlusButton.disabled = true;
      motorMinusButton.disabled = true;

      stopLiveButton.disabled = true;
      startLiveButton.disabled = true;
    } else {
      resetButtonState()
    }
  } finally {}
}

// Avance et recul moteur
document.getElementById("motorPlus").addEventListener("click", rotatePlus);
async function rotatePlus() {
  try {
    const response = await fetch(serverUrl + "/state");
    const body = await response.json();
    if (body.state.substr(body.state.length-7) === "STANDBY") {
        const motorresponse = await fetch(serverUrl + "/motorPlus");
        const motorbody = await motorresponse.json();
        document.getElementById("motor").textContent = motorbody.motor;
        setTimeout(() => {
          document.getElementById("motor").textContent = "";
        }, 1000);
    } else {
      resetButtonState()
    }
  } finally {}
}

document.getElementById("motorMinus").addEventListener("click", rotateMinus);
async function rotateMinus() {
  try {
    const response = await fetch(serverUrl + "/state");
    const body = await response.json();
    if (body.state.substr(body.state.length-7) === "STANDBY") {
        const motorresponse = await fetch(serverUrl + "/motorMinus");
        const motorbody = await motorresponse.json();
        document.getElementById("motor").textContent = motorbody.motor;
        setTimeout(() => {
          document.getElementById("motor").textContent = "";
        }, 1000);
    } else {
      resetButtonState()
    }
  } finally {}
}



// Test de l'éclairage
document.getElementById("testLumen").addEventListener("click", lumen);
async function lumen() {
  try {
    const response = await fetch(serverUrl + "/state");
    const body = await response.json();
    if (body.state.substr(body.state.length-7) === "STANDBY") {
        const lightresponse = await fetch(serverUrl + "/testLumen");
        const lightbody = await lightresponse.json();
        document.getElementById("light").textContent = lightbody.light;
        setTimeout(() => {
          document.getElementById("light").textContent = "";
        }, 2000);
    } else {
      resetButtonState()
    }
  } finally {}
}

// Test de l'ip
document.getElementById("testIP").addEventListener("click", IP);
async function IP() {
  try {
    const response = await fetch(serverUrl + "/state");
    const body = await response.json();
    if (body.state.substr(body.state.length-7) === "STANDBY") {
        const ipresponse = await fetch(serverUrl + "/testIP");
        const ipbody = await ipresponse.json();
        document.getElementById("ip").textContent = ipbody.ip;
        setTimeout(() => {
          document.getElementById("ip").textContent = "";
        }, 2000);
    } else {
      resetButtonState()
    }
  } finally {}
}

// Changement de l'ip
document.getElementById("changeIP").addEventListener("click", changeIP);
async function changeIP() {
  try {
    const response = await fetch(serverUrl + "/state");
    const body = await response.json();
    if (body.state.substr(body.state.length-7) === "STANDBY") {
        const cipresponse = await fetch(serverUrl + "/changeIP");
        const cipbody = await cipresponse.json();
        document.getElementById("ip").textContent = cipbody.ip;
        setTimeout(() => {
          document.getElementById("ip").textContent = "";
        }, 2000);
    } else {
      resetButtonState()
    }
  } finally {}
}

// Test des capteurs
document.getElementById("testSensors").addEventListener("click", sensors);
async function sensors() {
  try {
    const responseState = await fetch(serverUrl + "/state");
    const stateBody = await responseState.json();
    if (stateBody.state.endsWith("STANDBY")) {
      const response = await fetch(serverUrl + "/sensors");
      const Body = await response.json();
      document.getElementById("RGB").textContent = Body.RGB;
      document.getElementById("tp").textContent = "Pression " + Body.pression + " hPa  Température" + "   " + Body.temperature + " °C" ;
      const lat = Body.latitude;
      const lon = Body.longitude;
      document.getElementById("gps").textContent = "Latitude " + lat + "°  Longitude " + lon + "°";
      document.getElementById("magneto").textContent = "Cap " + Body.magneto ;
      document.getElementById("RTC").textContent = Body.rtc ;
      document.getElementById("time").textContent = Body.time ;

      const gpsAbsent = isNaN(parseFloat(lat)) || isNaN(parseFloat(lon));
      document.getElementById("usePhoneGPS").style.display = gpsAbsent ? "inline-block" : "none";

      setTimeout(() => {
        document.getElementById("RGB").textContent = "";
        document.getElementById("tp").textContent = "";
        document.getElementById("gps").textContent = "";
        document.getElementById("magneto").textContent = "";
        document.getElementById("RTC").textContent = "";
        document.getElementById("time").textContent = "";
        document.getElementById("usePhoneGPS").style.display = "none";
      }, 7000);
    } else {
      resetButtonState();
    }
  } catch (err) {
    console.error(err);
  } finally{testSensorsButton.disabled = false};
}

// Initialisation des capteurs

document.getElementById("initSensors").addEventListener("click", initSensors);
async function initSensors() {
  try {
    const responseState = await fetch(serverUrl + "/state");
    const stateBody = await responseState.json();
    if (stateBody.state.endsWith("STANDBY")) {
      const responseinit = await fetch(serverUrl + "/initSensors");
      const initBody = await responseinit.json();
      document.getElementById("init").textContent = initBody.init;
      setTimeout(() => {
        document.getElementById("init").textContent = "";
      }, 5000);
    } else {
      resetButtonState();
    }
  } catch (err) {
    console.error(err);
  } finally{sensors()};
}

// Function to set the live streaming state based on camera state
async function setLive(state) {
  try {
    const response = await fetch(serverUrl + "/state");
    const body = await response.json();
    if (state) {
      console.log(body.state.substr(body.state.length-7))
      if (body.state.substr(body.state.length-7) === "STANDBY") {
        live = true;
        const frameEl = document.getElementById("frame");
        frameEl.style.display = "block";
        frameEl.style.maxWidth = "240px";
        frameEl.style.height = "auto";
        frameEl.style.borderRadius = "6px";
        frameLoop();
        stopLiveButton.disabled = false;
        startLiveButton.disabled = true;
      } else {
        alert(
          "Cannot start live video while the camera is not in STANDBY state."
        );
      }
    } else {
      live = false;
      document.getElementById("frame").style.display = "none";
      stopLiveButton.disabled = true;
      startLiveButton.disabled = false;
    }
  } catch (error) {
    console.error("Error fetching camera state:", error);
  }
}

// Function to fetch an image from the server and display it
async function getImage() {
  const response = await fetch(serverUrl + "/frame");
  const imageBlob = await response.blob();
  const imageObjectURL = URL.createObjectURL(imageBlob);
  const image = document.getElementById("frame");
  image.src = imageObjectURL;
}

// Function to continuously fetch and display frames in a loop
async function frameLoop() {
  while (live) {
    await getImage();
  }
}

// Helper function to disable all buttons
function disableAllButtons() {
  testLumenButton.disabled = true;
  
  testSensorsButton.disabled = true;
  initSensorsButton.disabled = true;
  
  motorPlusButton.disabled = true;
  motorMinusButton.disabled = true;
  
  stopLiveButton.disabled = true;
  startLiveButton.disabled = true;
}

// GPS du téléphone comme fallback
document.getElementById("usePhoneGPS").addEventListener("click", function () {
  if (!navigator.geolocation) {
    alert("La géolocalisation n'est pas supportée par ce navigateur.");
    return;
  }
  const btn = document.getElementById("usePhoneGPS");
  btn.disabled = true;
  btn.textContent = "Localisation…";
  navigator.geolocation.getCurrentPosition(
    function (pos) {
      const lat = pos.coords.latitude.toFixed(6);
      const lon = pos.coords.longitude.toFixed(6);
      document.getElementById("gps").textContent = "Latitude " + lat + "°  Longitude " + lon + "° (téléphone)";
      btn.style.display = "none";
      btn.disabled = false;
      btn.textContent = "Utiliser le GPS du téléphone ?";
      // Envoyer au backend pour l'écriture dans le CSV/JSON
      fetch(serverUrl + "/setPhoneGPS", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ lat: lat, lon: lon })
      }).catch(function () {});
    },
    function (err) {
      let msg;
      if (location.protocol !== "https:") {
        msg = "La géolocalisation nécessite HTTPS.\nConnectez-vous en https://10.42.0.1";
      } else if (err.code === 1) {
        msg = "Permission refusée. Autorisez la localisation dans les réglages du navigateur.";
      } else {
        msg = "Impossible d'obtenir la position : " + err.message;
      }
      alert(msg);
      btn.disabled = false;
      btn.textContent = "Utiliser le GPS du téléphone ?";
    },
    { enableHighAccuracy: true, timeout: 10000 }
  );
});

// Helper function to reset buttons to their initial state
function resetButtonState() {
  testLumenButton.disabled = false;
  
  testSensorsButton.disabled = false;
  initSensorsButton.disabled = false;
  
  stopLiveButton.disabled = true;
  startLiveButton.disabled = false;
  
  motorPlusButton.disabled = false;
  motorMinusButton.disabled = false;
}
