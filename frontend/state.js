// Set up an interval to periodically fetch and update the state information
setInterval(async function () {
  // Fetch the state information from the server
  const response = await fetch(serverUrl + "/state");
  const body = await response.json();

  // Update the HTML element with the fetched state information
  document.getElementById("etat").innerHTML = body.state;
}, 1000);
