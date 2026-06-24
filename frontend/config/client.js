// This variable holds the URL of the server where the backend is hosted
let serverUrl = location.protocol === "https:" ? location.origin : "http://10.42.0.1:5000";
// Alternative server URL (commented out)
// let serverUrl = "http://10.29.225.198:5000";

// Variable to store configuration data fetched from the server
let configsData;

// Function to fetch the configuration from the server and dynamically generate the form
async function fetchConfig() {
  try {
    const response = await fetch(serverUrl + "/getConfig");
    const data = await response.json();

    // Assuming the response structure is { data: { ... }, status: "ok" }
    if (data.status === "ok") {
      const configContainer = document.getElementById("configForm");
      configsData = data.data;

      configContainer.style.cssText = "display:grid; grid-template-columns:auto 1fr auto; gap:6px 12px; align-items:center;";

      for (const key in configsData) {
        const label = document.createElement("label");
        label.setAttribute("for", key);
        label.textContent = key;
        label.style.cssText = "font-size:0.78rem; font-weight:600; color:#5C7A93; text-transform:uppercase; letter-spacing:0.04em; white-space:nowrap; padding:4px 0;";

        const input = document.createElement("input");
        input.setAttribute("type", "text");
        input.setAttribute("id", key);
        input.setAttribute("readonly", "");
        input.value = configsData[key];
        input.style.cssText = "padding:4px 8px; border:1.5px solid #C8D8E8; border-radius:6px; font-size:0.875rem; width:100%; box-sizing:border-box;";

        const button = document.createElement("button");
        button.setAttribute("type", "button");
        button.setAttribute("id", "but" + key);
        button.textContent = "Modify";
        button.style.cssText = "font-size:0.78rem; padding:4px 12px; white-space:nowrap;";
        button.addEventListener("click", () => modifyParameter("but" + key, key));

        configContainer.appendChild(label);
        configContainer.appendChild(input);
        configContainer.appendChild(button);
      }

      // Add Reboot button after the parameter divs
      const buttonDiv = document.createElement("h3");
      const rebootButton = document.createElement("button");
      rebootButton.setAttribute("id", "rebootButton");
      rebootButton.setAttribute("type", "button");
      rebootButton.textContent = "Reboot"; 
      /*
      const response = await fetch(serverUrl + "/state");
      const body = await response.json();
      if (body.state.substr(body.state.length-7) === "STANDBY") {
         rebootButton.disabled = false;
      } else {
        rebootButton.disabled = true; 
      }
      */
      buttonDiv.appendChild(rebootButton)
      configContainer.appendChild(buttonDiv);
    } else {
      console.error("Failed to fetch configuration:", data.status);
    }
  } catch (error) {
    console.error("Error fetching configuration:", error);
  }

  // Add event listener to the Reboot button
  document
    .getElementById("rebootButton")
    .addEventListener("click", function (event) {
      event.preventDefault(); // Prevent the default form submission behavior
      updateConfigOnServer(configsData);
    });
}

// Fetch the configuration when the page loads
fetchConfig();

// Function to update the configuration on the server
async function updateConfigOnServer(updatedConfig) {
  try { 
    const response2 = await fetch(serverUrl + "/state");
    const body2 = await response2.json();
    if (body2.state.substr(body2.state.length-7) === "STANDBY") {
      const response = await fetch(serverUrl + "/changeConfig", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(updatedConfig),
      });

      const data = await response.json();

      // Assuming the response structure is { status: "ok" }
      if (data.status === "ok") {
        console.log("Configuration updated on the server");
      } else {
        console.error(
          "Failed to update configuration on the server:",
          data.status
        );
      }
    } else {
      Swal.fire({
          title: 'Error',
          text: "Le Reboot n'est possible que dans l'état STANDBY",
          icon: 'error',
          confirmButtonText: 'OK'
        });
        return;
    }
  } catch (error) {
    console.error("Error updating configuration on the server:", error);
  }
}

// Function to enable modification of a configuration parameter
function modifyParameter(buttonId, paramId) {
  const button = document.getElementById(buttonId);
  const input = document.getElementById(paramId);

  if (button.textContent === "Modify") {
    input.readOnly = false;
    button.textContent = "Save";
  } else {
    // Check if the original value is a number
    const originalValue = configsData[paramId];
    const isOriginalValueNumber = !isNaN(originalValue);

    // Check if the new value is a number
    const newValue = input.value;
    const isNewValueNumber = !isNaN(newValue);

    if (isOriginalValueNumber && !isNewValueNumber) {
      // Display an error if the original value is a number and the new value is not
      alert("Error: Please enter a valid number.");
      return; // Exit the function without updating the configuration
    }

    // Update only if the new value is of the same type
    configsData[paramId] = newValue;
    input.readOnly = true;
    button.textContent = "Modify";
    console.log("Configurations updated locally:", configsData);
  }
}
