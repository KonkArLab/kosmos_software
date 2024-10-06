//JSON file location where default metadata is stored
const testUrl = "./test.json"; 

//Import Icons
const icons = ['', 'icons/reset.png'];

// Function to fetch metadata from the local JSON file
async function fetchMetadata() {
  try {
    const response = await fetch(testUrl); // Fetching the local JSON file
    const data = await response.json(); // Parsing the JSON data
    return data.campagne; // Return the parsed data
  } catch (error) {
    console.error("Error fetching metadata:", error);
    return null;
  }
}

// Function to populate the table with metadata and make cells editable
async function populateMetadataTable() {
  
  const fileTable = document.getElementsByTagName("table")[0];
  let metadata = JSON.parse(localStorage.getItem('metadata'));
  if(!metadata) {
    // Fetch metadata from the JSON file
    metadata = await fetchMetadata();
    localStorage.setItem('metadata', JSON.stringify(metadata));
  }

  if(metadata) {
    // loop on each property
    for (const [key, value] of Object.entries(metadata)) {
      //Add property
      let row = fileTable.insertRow();
      let keyCell = row.insertCell(); // First column with name
      keyCell.textContent = key; 
      let valueCell = row.insertCell(); // Second column with value
      valueCell.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: center; width: 100%;">
          <!-- Conteneur pour la valeur de la propriété -->
          <span>${Array.isArray(value) ? value.map((partner) => `<span>${partner}</span><br>`).join("") : value}</span>
        
          <!-- Conteneur pour les boutons -->
          <div>
            <button class="modify" >
              <img src="icons/modify.png" alt="modify" width="30" height="30" />
            </button> 
            <button class="reset" >
              <img src="icons/reset.png" alt="reset" width="30" height="30" />
            </button>
          </div>
        </div>
      `;
    };
    addModifyListener(metadata);
    addResetListener(metadata);
  } 
}

function addModifyListener(metadata) {
  const modifyButtons = Array.from(document.getElementsByClassName("modify"));

  modifyButtons.forEach(butt => {
    butt.addEventListener("click", (event) => {
      // Remove the edition button 
      const buttonElement = event.target.closest("button");
      buttonElement.style.display = "none";

      // get the parent container of the button
      const parentDiv = event.target.closest("div");
      
      // get the <span> of the value
      const span = parentDiv.previousElementSibling;

      // Create an input with the same value of the span
      const input = document.createElement("input");
      input.type = "text";

      if(span.children.length > 0 && Array.from(span.children).some(child => child instanceof HTMLSpanElement)) {
        Array.from(span.children).forEach((child) => {
          if(child instanceof HTMLSpanElement) {
            input.value += child.textContent+", ";
          }
        })
        input.value = input.value.slice(0, -2);
      } else {
        input.value = span.textContent;
      }

      input.style.width = "100%"; 
      input.style.margin= "5px";

      // replace the span with the input
      span.replaceWith(input);

      // add an event blur on the input to get to span mode 
      input.addEventListener("blur", async () => {
        //update value in the shared json 
        const propertyKey = parentDiv.parentElement.parentElement.previousElementSibling.textContent;
        metadata[propertyKey] = input.value;
        localStorage.setItem('metadata', JSON.stringify(metadata));

        // Create a new span with the same value of the input
        const newSpan = document.createElement("span");
        if(propertyKey == "partenaires") {
          partners = input.value.split(",").map(partner => partner.trim());
          partners.forEach((partner) => {
            if (partner) { // Vérifier que le partenaire n'est pas une chaîne vide
              newSpan.innerHTML += `<span>${partner}</span><br>`;
            }
          })
        } else {
          newSpan.textContent = input.value;
        }

        // replace the input with the new span
        input.replaceWith(newSpan);
        // redisplay modify button
        buttonElement.style.display = "inline-block";
      });

      // focus on the input while editing
      input.focus();
    });
  }); 
}

function addResetListener(metadata) {
  const resetButtons = Array.from(document.getElementsByClassName("reset"))
  resetButtons.forEach(butt => {
    butt.addEventListener("click", async (event) => {
      const defaultJSON = await fetchMetadata(); 

      // get the parent container of the button
      const parentDiv = event.target.closest("div");

      //update value in the shared json 
      const propertyKey = parentDiv.parentElement.parentElement.previousElementSibling.textContent;
      metadata[propertyKey] = defaultJSON[propertyKey];
      localStorage.setItem('metadata', JSON.stringify(metadata));
      
      // get the <span> of the value
      const span = parentDiv.previousElementSibling;

      if(propertyKey == "partenaires") {
        span.innerHTML = ``;
        defaultJSON[propertyKey].forEach((partner) => {
          if (partner) { // Vérifier que le partenaire n'est pas une chaîne vide
            span.innerHTML += `<span>${partner}</span><br>`;
          }
        })
      } else {
        span.textContent = defaultJSON[propertyKey];
      }
    })
  }); 
} 

// Call the function to populate the table when the page loads
populateMetadataTable();