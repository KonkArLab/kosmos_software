// This variable holds the URL of the server where the backend is hosted
let serverUrl = "http://10.42.0.1:5000";
// Alternative server URL (commented out)
// let serverUrl = "http://10.29.225.198:5000";

// This variable tracks the state of live video streaming
let live = false;

// Element references
const startButton = document.getElementById("startCamera");
const stopButton = document.getElementById("stopCamera");
const startLiveButton = document.getElementById("startLive");
const stopLiveButton = document.getElementById("stopLive");
const shutdownButton = document.getElementById("shutdown");

// Initial setup: disable stop buttons and enable shutdown
stopButton.disabled = true;
stopLiveButton.disabled = true;
shutdownButton.disabled = false;

majStateButton();

async function majStateButton() {
  try {
    const response = await fetch(serverUrl + "/state");
    const body = await response.json();
    if (body.state.substr(body.state.length-7) === "WORKING") {
      stopButton.disabled = false;
      startButton.disabled = true;
      startLiveButton.disabled = true;
      shutdownButton.disabled = true;
    } else {
      resetButtonState()
    }
  } finally {}
}

// Function to send a start request to the server
async function start() {
  try {
    if (localStorage.getItem("pending")) {
      window.location.href = "./metadata/metadata.html";
    }
    const storedData = localStorage.getItem("campaignData");
    if (storedData) {
      disableAllButtons();
      const response = await fetch(serverUrl + "/start");
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
    //localStorage.setItem("metaData", JSON.stringify(body.metadata));
    //window.location.href = "./metadata/metadata.html";
  } catch (error) {
    console.error("Error stopping the camera:", error);
  } finally {
    // Enable only start buttons and shutdown after stop
    startButton.disabled = false;
    startLiveButton.disabled = false;
    shutdownButton.disabled = false;
  }
}

// Function to send a shutdown request to the server
async function shutdown() {
  disableAllButtons();
  try {
    const response = await fetch(serverUrl + "/shutdown");
    const body = await response.json();
    console.log(body);
  } catch (error) {
    console.error("Error shutting down:", error);
  } finally {
    // Enable shutdown only after shutdown completes
    shutdownButton.disabled = false;
  }
}

// Function to set the live streaming state based on camera state
async function setLive(state) {
  disableAllButtons();
  try {
    const response = await fetch(serverUrl + "/state");
    const body = await response.json();

    if (state) {
      console.log(body.state.substr(body.state.length-7))
      if (body.state.substr(body.state.length-7) === "STANDBY") {
        live = true;
        frameLoop();
        stopLiveButton.disabled = false; // Enable only the stop live button
      } else {
        alert(
          "Cannot start live video while the camera is not in STANDBY state."
        );
        resetButtonState();
      }
    } else {
      live = false;
      resetButtonState();
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
  startButton.disabled = true;
  stopButton.disabled = true;
  startLiveButton.disabled = true;
  stopLiveButton.disabled = true;
  shutdownButton.disabled = true;
}

// Helper function to reset buttons to their initial state
function resetButtonState() {
  startButton.disabled = false;
  startLiveButton.disabled = false;
  stopButton.disabled = true;
  stopLiveButton.disabled = true;
  shutdownButton.disabled = false;
}
