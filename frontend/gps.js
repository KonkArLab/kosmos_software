// Set up an interval to periodically fetch and update the state information
setInterval(async function () {
  // Fetch the state information from the server
  const response = await fetch(serverUrl + "/gps");
  const body = await response.json();

  // Update the HTML element with the fetched state information
  document.getElementById("latitude").innerHTML = body.latitude;
  document.getElementById("longitude").innerHTML = body.longitude;

}, 2000);
