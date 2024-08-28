// This variable holds the URL of the server where the backend is hosted
let serverUrl = "http://10.42.0.1:5000";
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
      const configContainer = document.getElementById("container");
      configsData = data.data;

      // Loop through each configuration parameter and create corresponding form elements
      for (const key in configsData) {
        const parameterDiv = document.createElement("div");
        parameterDiv.classList.add("parameter");

        const label = document.createElement("label");
        label.setAttribute("for", "param" + key);
        label.classList.add("parameter-element");
        label.textContent = key;

        const input = document.createElement("input");
        input.setAttribute("type", "text");
        input.setAttribute("id", key);
        input.setAttribute("readonly", "");
        input.classList.add("parameter-element");
        input.value = configsData[key];

        const button = document.createElement("button");
        button.setAttribute("type", "button");
        button.setAttribute("id", "but" + key);
        button.classList.add("parameter-element");
        button.textContent = "Modify";
        button.addEventListener("click", () =>
          modifyParameter("but" + key, key)
        );

        parameterDiv.appendChild(label);
        parameterDiv.appendChild(input);
        parameterDiv.appendChild(button);
        configContainer.appendChild(parameterDiv);
      }

      // Add Reboot button after the parameter divs
      const rebootButton = document.createElement("button");
      rebootButton.setAttribute("id", "rebootButton");
      rebootButton.setAttribute("type", "button");
      rebootButton.textContent = "Reboot";
      rebootButton.classList.add("reboot");
      configContainer.appendChild(rebootButton);
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
