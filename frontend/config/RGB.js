// Set up an interval to periodically fetch and update the RGB information
setInterval(async function () {
  // Fetch the state information from the server
  const response = await fetch(serverUrl + "/rgb");
  const body = await response.json();
  // Update the HTML element with the fetched state information
  document.getElementById("RGB").innerHTML = body.RGB;
}, 2000);
