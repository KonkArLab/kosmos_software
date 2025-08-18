// Set up an interval to periodically fetch and update the gps information
setInterval(async function () {
  // Fetch the state information from the server
  const response = await fetch(serverUrl + "/sensors");
  const body = await response.json();
  // Update the HTML element with the fetched state information
  document.getElementById("latitude").innerHTML = body.latitude;
  document.getElementById("longitude").innerHTML = body.longitude;
  //document.getElementById("RGB").innerHTML = body.RGB;
  //document.getElementById("magneto").innerHTML = body.magneto;
  //document.getElementById("pression").innerHTML = body.pression;
  //document.getElementById("temperature").innerHTML = body.temperature;
}, 1000);
