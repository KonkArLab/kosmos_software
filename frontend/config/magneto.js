// Set up an interval to periodically fetch and update the magneto information
setInterval(async function () {
  // Fetch the state information from the server
  const response = await fetch(serverUrl + "/magneto");
  const body = await response.json();
  // Update the HTML element with the fetched state information
  document.getElementById("magneto").innerHTML = body.magneto;
}, 2000);
