document.addEventListener("DOMContentLoaded", function () {
    // Select the main form by its ID
    const form = document.getElementById("campaignForm");

    // Define the form fields with their properties like ID, placeholder, type, etc.
    const fields = [
        { id: "date", placeholder: "", type: "date", label: "Date", tabIndex: 1,  isDate:true },
        { id: "campaign", placeholder: "ATL", type: "text", label: "Campaign", tabIndex: 2, maxlength: "3"},
        { id: "zone", placeholder: "BR", type: "text", label: "Zone", tabIndex: 3, maxlength: "3"},
        { id: "locality", placeholder: "Illien", type: "text", label: "Location", tabIndex: 4, maxlength: "100" },
        { id: "protection", placeholder: "Parc naturel marin d'iroise", type: "text", label: "Protection", tabIndex: 5, maxlength: "100" },
        { id: "boat", placeholder: "Beneteau Capelan", type: "text", label: "Boat", tabIndex: 6, maxlength: "100" },
        { id: "pilot", placeholder: "Olivier F.", type: "text", label: "Pilot", tabIndex: 7, maxlength: "100" },
        { id: "crew", placeholder: "C.H., J.C.", type: "text", label: "Crew", tabIndex: 8, maxlength: "100" },
        { id: "partners", placeholder: "Ifremer RDT, Ifremer Halgo", type: "text", label: "Partners", tabIndex: 9, maxlength: "200" }
    ];

    const campaignFinal = {
        zoneDict: {
            campaign: String,
            zone: String,
            locality: String,
            protection: String
        },
        dateDict:
        {
            date: Date
        },
        deploiementDict: {
            boat: String,
            pilot: String,
            crew: String,
            partners: String
        }
    }

    // Object to store instances of Choices.js
    

    // Dynamically create form fields
    fields.forEach(field => {
        const ligneH3 = document.createElement("h3");
        const label = document.createElement("label");
        label.setAttribute("for", field.id);
        label.textContent = field.label + ": ";
        
        const input = document.createElement("input");
        input.id = field.id;
        input.placeholder = field.placeholder;
        input.type = field.type;
        input.tabIndex = field.tabIndex;
        input.maxLength = field.maxlength;
        
        ligneH3.appendChild(label);
        ligneH3.appendChild(input);
        form.appendChild(ligneH3);
         
    });

    // Add "Save" and "Reset" buttons to the form
    const saveButton = document.createElement("button");
    saveButton.type = "submit";
    saveButton.textContent = "Save";

    const resetButton = document.createElement("button");
    resetButton.type = "reset";
    resetButton.textContent = "Reset";
    resetButton.id = "campaignResetButton"

    form.appendChild(saveButton);
    form.appendChild(resetButton);

    // Set automaticaly the date in the corresponding field
    fields.forEach(field => {
            let value = null;
            if (field.id === 'date') {
                value = new Date().toISOString().split("T")[0] 
            } 
            if (value) {
                const element = document.getElementById(field.id);
                if (element) {
                    element.value = value;
                }
            }
        });
    
    // Load previously saved data from localStorage
    const storedData = localStorage.getItem("campaignData");
    if (storedData) {
        const formData = JSON.parse(storedData);

        fields.forEach(field => {
            let value = null;
            if (field.id in formData.zoneDict) {
                value = formData.zoneDict[field.id];
            } else if (field.id in formData.deploiementDict) {
                value = formData.deploiementDict[field.id];
            } else if (field.id in formData.dateDict) { // on ne se fie pas à la date RTC mais à celle pré-rentrée si elle existe
                value = formData.dateDict[field.id];
            }
            if (value) {
                const element = document.getElementById(field.id);
                if (element) {
                    element.value = value;
                }         
            }
        });
    }

    // Handle form submission event
    form.addEventListener("submit", function (event) {
        event.preventDefault(); // Prevent page reload

        const formData = {};
        let allFieldsFilled = true; // Check that all fields are filled

        fields.forEach(field => {
            const value = document.getElementById(field.id).value;
            formData[field.id] = value;
            if (!value) {
                allFieldsFilled = false;
            }
        });

        const storedDataParsed = storedData ? JSON.parse(storedData) : null;
       
        // Alert if there is no new information to save
       if (JSON.stringify(storedDataParsed) === JSON.stringify(formData)) {
           Swal.fire({
               title: 'Alert',
               text: 'There is not new information to save',
               icon: 'info',
               confirmButtonText: 'OK'
             });
           return;
       }

       // Alert if some fields are empty
        if (!allFieldsFilled) {
            Swal.fire({
                title: 'Error',
                text: 'Fill all inputs',
                icon: 'error',
                confirmButtonText: 'OK'
            });
            return;
        }
        
        campaignFinal.dateDict.date = formData.date;

        campaignFinal.deploiementDict.boat = formData.boat;
        campaignFinal.deploiementDict.crew = formData.crew;
        campaignFinal.deploiementDict.partners = formData.partners;
        campaignFinal.deploiementDict.pilot = formData.pilot;

        campaignFinal.zoneDict.campaign = formData.campaign;
        campaignFinal.zoneDict.locality = formData.locality;
        campaignFinal.zoneDict.protection = formData.protection;
        campaignFinal.zoneDict.zone = formData.zone;
        
        // Save the data to localStorage
        localStorage.setItem("campaignData", JSON.stringify(campaignFinal));
        Swal.fire({
            title: 'Success',
            text: 'Information saved',
            icon: 'success',
            confirmButtonText: 'OK'
        });
    });
});
