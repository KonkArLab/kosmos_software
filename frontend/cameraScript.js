// This variable holds the URL of the server where the backend is hosted
let serverUrl = location.protocol === "https:" ? location.origin : "http://10.42.0.1:5000";
// Alternative server URL (commented out)
// let serverUrl = "http://10.29.225.198:5000";

// Element references
const startButton = document.getElementById("startCamera");
const stopButton = document.getElementById("stopCamera");
const shutdownButton = document.getElementById("shutdown");

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
            body: JSON.stringify({ lat: lat, lon: lon })
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
          campaign:  campaignParsed?.zoneDict?.campaign        || "XX",
          zone:      campaignParsed?.zoneDict?.zone            || "ZZ",
          locality:   campaignParsed?.zoneDict?.locality          || "",
          protection: campaignParsed?.zoneDict?.protection       || "",
          boat:      campaignParsed?.deploiementDict?.boat     || "",
          pilot:     campaignParsed?.deploiementDict?.pilot    || "",
          crew:      campaignParsed?.deploiementDict?.crew     || "",
          partners:  campaignParsed?.deploiementDict?.partners || ""
        })
      });
      const body = await response.json();
      // Enable only the stop button for camera
      stopButton.disabled = false;
    } else {
      Swal.fire({
          title: 'Error',
          text: 'Please fill campaign before starting',
          icon: 'error',
          confirmButtonText: 'OK'
        });
      return;
    }
  } catch (error) {
    console.error("Error starting the camera:", error);
  }
}

// Function to send a stop request to the server
async function stop() {
  disableAllButtons();
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
