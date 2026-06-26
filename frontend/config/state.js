setInterval(async function () {
  try {
    const response = await fetch(serverUrl + "/state");
    const body = await response.json();
    document.getElementById("etat").innerHTML = body.state;
    if (typeof syncTimer === 'function') syncTimer(body);
  } catch {}
}, 1000);
