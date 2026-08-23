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
const majButton = document.getElementById("maj");

const startLiveButton = document.getElementById("startLive");
const stopLiveButton = document.getElementById("stopLive");

const testSensorsButton = document.getElementById("testSensors");
const initSensorsButton = document.getElementById("initSensors");

const motorPlusButton = document.getElementById("motorPlus");

// Initial setup: disable stop buttons and enable shutdown
testLumenButton.disabled = false;

testSensorsButton.disabled = false;
initSensorsButton.disabled = false;

motorPlusButton.disabled = false;

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

      stopLiveButton.disabled = true;
      startLiveButton.disabled = true;
    } else {
      resetButtonState()
    }
  } finally {}
}

// Avance moteur
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

// Maj logiciel
document.getElementById("maj").addEventListener("click", maj);
async function maj() {
  try {
    const response = await fetch(serverUrl + "/state");
    const body = await response.json();
    if (body.state.substr(body.state.length-7) === "STANDBY") {
        const majresponse = await fetch(serverUrl + "/maj");
        const majbody = await majresponse.json();
        document.getElementById("maj_txt").textContent = majbody.maj_txt;
        setTimeout(() => {
          document.getElementById("maj_txt").textContent = "";
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
      
      //const gpsAbsent = isNaN(parseFloat(lat)) || isNaN(parseFloat(lon));
      //document.getElementById("usePhoneGPS").style.display = gpsAbsent ? "inline-block" : "none";

      setTimeout(() => {
        document.getElementById("RGB").textContent = "";
        document.getElementById("tp").textContent = "";
        document.getElementById("gps").textContent = "";
        document.getElementById("magneto").textContent = "";
        document.getElementById("RTC").textContent = "";
        document.getElementById("time").textContent = "";

        //document.getElementById("usePhoneGPS").style.display = "none";
      }, 7000);
    } else {
      resetButtonState();
    }
  } catch (err) {
    console.error(err);
  } finally{testSensorsButton.disabled = false};
}

// Synchronisation de l'heure du Rpi sur celle du téléphone
document.getElementById("syncTime").addEventListener("click", syncTime);
async function syncTime() {
  const btn = document.getElementById("syncTime");
  const msgEl = document.getElementById("syncTimeMsg");
  btn.disabled = true;
  try {
    const now = new Date();
    const pad = n => String(n).padStart(2, '0');
    const formatted = `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())} ${pad(now.getHours())}:${pad(now.getMinutes())}:${pad(now.getSeconds())}`;
    const response = await fetch(serverUrl + "/setTime", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ datetime: formatted })
    });
    const body = await response.json();
    msgEl.textContent = body.status === "ok" ? "Heure synchronisée ✓" : "Erreur : " + body.message;
  } catch (err) {
    msgEl.textContent = "Erreur de synchronisation";
  } finally {
    btn.disabled = false;
    setTimeout(() => { msgEl.textContent = ""; }, 4000);
  }
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
      if (body.state.substr(body.state.length-7) === "STANDBY") {
        live = true;
        const framesDiv = document.getElementById("live-frames");
        framesDiv.style.display = "flex";

        // Caméra 2 uniquement si stéréo
        const frame2El = document.getElementById("frame2");
        if (body.stereo) {
          frame2El.style.display = "block";
          frameLoop2();
        } else {
          frame2El.style.display = "none";
        }

        frameLoop();
        stopLiveButton.disabled = false;
        startLiveButton.disabled = true;
      } else {
        alert("Cannot start live video while the camera is not in STANDBY state.");
      }
    } else {
      live = false;
      document.getElementById("live-frames").style.display = "none";
      stopLiveButton.disabled = true;
      startLiveButton.disabled = false;
    }
  } catch (error) {
    console.error("Error fetching camera state:", error);
  }
}


// Fetch et affiche un frame pour une caméra donnée
async function getImage(endpoint, imgId) {
  const response = await fetch(serverUrl + endpoint);
  const blob = await response.blob();
  const url = URL.createObjectURL(blob);
  const img = document.getElementById(imgId);
  if (img.src) URL.revokeObjectURL(img.src);
  img.src = url;
}

async function frameLoop() {
  while (live) { await getImage("/frame", "frame"); }
}

async function frameLoop2() {
  while (live) { await getImage("/frame2", "frame2"); }
}

// Helper function to disable all buttons
function disableAllButtons() {
  testLumenButton.disabled = true;
  
  testSensorsButton.disabled = true;
  initSensorsButton.disabled = true;
  
  motorPlusButton.disabled = true;
  
  stopLiveButton.disabled = true;
  startLiveButton.disabled = true;
}


/*
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
*/



// Helper function to reset buttons to their initial state
function resetButtonState() {
  testLumenButton.disabled = false;
  
  testSensorsButton.disabled = false;
  initSensorsButton.disabled = false;
  
  stopLiveButton.disabled = true;
  startLiveButton.disabled = false;
  
  motorPlusButton.disabled = false;
}
