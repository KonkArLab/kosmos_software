// Set up an interval to periodically fetch and update the gps information
setInterval(async function () {
  // Fetch the state information from the server
  const response = await fetch(serverUrl + "/checkConversion");
  const body = await response.json();
  // Update the HTML element with the fetched state information
  document.getElementById("checkConversion").innerHTML = body.checkConversion;
}, 1000);
