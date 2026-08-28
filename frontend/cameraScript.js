// This variable holds the URL of the server where the backend is hosted
let serverUrl = location.protocol === "https:" ? location.origin : "http://10.42.0.1:5000";
// Alternative server URL (commented out)
// let serverUrl = "http://10.29.225.198:5000";

// Element references
const startButton = document.getElementById("startCamera");
const stopButton = document.getElementById("stopCamera");
const shutdownButton = document.getElementById("shutdown");
const timerEl = document.getElementById("recording-timer");

// ── Compteur d'enregistrement ────────────────────────────────────────────────
let _timerInterval = null;
let _recordingStartMs = null;  // Date.now() équivalent au début de l'enregistrement

function _formatElapsed(ms) {
  const s = Math.floor(ms / 1000);
  const h = Math.floor(s / 3600).toString().padStart(2, '0');
  const m = Math.floor((s % 3600) / 60).toString().padStart(2, '0');
  const sec = (s % 60).toString().padStart(2, '0');
  return `⏱ ${h}:${m}:${sec}`;
}

function startTimer(serverStartUnix) {
  _recordingStartMs = serverStartUnix * 1000;
  timerEl.style.display = 'block';
  timerEl.textContent = _formatElapsed(Date.now() - _recordingStartMs);
  if (_timerInterval) return;
  _timerInterval = setInterval(function () {
    timerEl.textContent = _formatElapsed(Date.now() - _recordingStartMs);
  }, 1000);
}

function stopTimer() {
  clearInterval(_timerInterval);
  _timerInterval = null;
  _recordingStartMs = null;
  timerEl.style.display = 'none';
  timerEl.textContent = '';
}

// Appelé par state.js à chaque poll — resynchronise si connexion retrouvée
function syncTimer(body) {
  const isWorking = body.state && body.state.endsWith('WORKING');
  if (isWorking && body.recording_start) {
    startTimer(body.recording_start);  // startTimer ignore si déjà actif, recale sinon
  } else if (!isWorking) {
    stopTimer();
  }
}
// ─────────────────────────────────────────────────────────────────────────────

// Initial setup: disable stop buttons and enable shutdown
stopButton.disabled = true;
shutdownButton.disabled = false;
startButton.disabled = false;

majStateButton();

async function majStateButton() {
  try {
    const response = await fetch(serverUrl + "/state");
    const body = await response.json();
    if (body.state.substr(body.state.length-7) === "WORKING") {
      stopButton.disabled = false;
      startButton.disabled = true;
      shutdownButton.disabled = true;
    } else {
      resetButtonState()
    }
  } finally {}
}

async function askPhoneGPS() {
  // Toujours réinitialiser les valeurs précédentes
  try {
    await fetch(serverUrl + "/resetPhoneGPS", { method: "POST" });
  } catch {}

  try {
    const r = await fetch(serverUrl + "/gpsStatus");
    const data = await r.json();
    if (data.has_fix) return;
  } catch { return; }

  if (!navigator.geolocation) return;

  const result = await Swal.fire({
    title: 'GPS non disponible',
    text: 'Aucune coordonnée GPS détectée. Utiliser le GPS du téléphone ?',
    icon: 'question',
    showCancelButton: true,
    confirmButtonText: 'Oui, utiliser mon GPS',
    cancelButtonText: 'Non, continuer sans GPS'
  });
  if (!result.isConfirmed) return;

  await new Promise(function(resolve) {
    navigator.geolocation.getCurrentPosition(
      async function(pos) {
        const lat = pos.coords.latitude.toFixed(6);
        const lon = pos.coords.longitude.toFixed(6);
        try {
          await fetch(serverUrl + "/setPhoneGPS", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: { lat: lat, lon: lon }
          });
        } catch {}
        resolve();
      },
      function() { resolve(); },
      { enableHighAccuracy: true, timeout: 10000 }
    );
  });
}

// Function to send a start request to the server
async function start() {
  try {
    const response2 = await fetch(serverUrl + "/checkConversion");
    const body2 = await response2.json();
    if (body2.checkConversion === "Conversion en cours") {
      Swal.fire({
          title: 'Error',
          text: 'Conversion en cours, veuillez attendre avant de relancer une vidéo',
          icon: 'error',
          confirmButtonText: 'OK'
        });
      return;
    } else {
      if (localStorage.getItem("pending")) {
        window.location.href = "./metadata/metadata.html";
      }
      const storedData = localStorage.getItem("campaignData");
      if (storedData) {
        await askPhoneGPS();
        disableAllButtons();
        const campaignParsed = JSON.parse(storedData);
        const response = await fetch(serverUrl + "/start", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            region:    campaignParsed?.zoneDict?.region        || "", 
            zone:      campaignParsed?.zoneDict?.zone            || "",
            type:   campaignParsed?.zoneDict?.type          || "",
            protection: campaignParsed?.zoneDict?.protection       || "",
            boat:      campaignParsed?.deploiementDict?.boat     || "",
            pilot:     campaignParsed?.deploiementDict?.pilot    || "",
            crew:      campaignParsed?.deploiementDict?.crew     || "",
            partners:  campaignParsed?.deploiementDict?.partners || ""
          })
        });
        const body = await response.json();
        stopButton.disabled = false;
        if (body.recording_start) startTimer(body.recording_start);
      } else {
        Swal.fire({
            title: 'Error',
            text: 'Please fill campaign before starting',
            icon: 'error',
            confirmButtonText: 'OK'
          });
        return;
      }
    }      
  } catch (error) {
    console.error("Error starting the camera:", error);
  }
}

// Function to send a stop request to the server
async function stop() {
  disableAllButtons();
  stopTimer();
  try {
    const response = await fetch(serverUrl + "/stop");
    const body = await response.json();
    /////////////
    localStorage.setItem("metaData", JSON.stringify(body.metadata));
    //window.location.href = "./metadata/metadata.html";
    //localStorage.setItem("metaData", JSON.stringify(body.metadata));
    submitForm()
  } catch (error) {
    console.error("Error stopping the camera:", error);
  } finally {
    // Enable only start buttons and shutdown after stop
    startButton.disabled = false;
    shutdownButton.disabled = false;
  }
}

// Function to send a shutdown request to the server
async function shutdown() {
  disableAllButtons();
  try {
    const response2 = await fetch(serverUrl + "/checkConversion");
    const body2 = await response2.json();
    if (body2.checkConversion === "Conversion en cours") {
      Swal.fire({
          title: 'Error',
          text: 'Conversion en cours, veuillez attendre avant le SHUTDOWN',
          icon: 'error',
          confirmButtonText: 'OK'
        });
      return;
    } else {
      const response = await fetch(serverUrl + "/shutdown");
      const body = await response.json();
      console.log(body);
    }
  } catch (error) {
    console.error("Error shutting down:", error);
  } finally {
    // Enable shutdown only after shutdown completes
    shutdownButton.disabled = false;
    startButton.disabled = false;
  }
}


// Helper function to disable all buttons
function disableAllButtons() {
  startButton.disabled = true;
  stopButton.disabled = true;
  shutdownButton.disabled = true;
}

// Helper function to reset buttons to their initial state
function resetButtonState() {
  startButton.disabled = false;
  stopButton.disabled = true;
  shutdownButton.disabled = false;
}
