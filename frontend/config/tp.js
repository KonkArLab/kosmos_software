// Set up an interval to periodically fetch and update the gps information
setInterval(async function () {
  // Fetch the state information from the server
  const response = await fetch(serverUrl + "/tp");
  const body = await response.json();
  // Update the HTML element with the fetched state information
  document.getElementById("pression").innerHTML = body.pression;
  document.getElementById("temperature").innerHTML = body.temperature;
}, 2000);
