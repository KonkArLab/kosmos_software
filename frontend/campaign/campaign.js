document.addEventListener("DOMContentLoaded", function () {
    // Select the main form by its ID
    const form = document.getElementById("campaignForm");

    // Define the form fields with their properties like ID, placeholder, type, etc.
    const fields = [
        { id: "date", placeholder: "", type: "date", label: "Date", tabIndex: 1,  isDate:true },
        { id: "region", placeholder: "ATL", type: "text", label: "Région", tabIndex: 2, maxlength: "100" },
        { id: "zone", placeholder: "BR", type: "text", label: "Zone", tabIndex: 3, maxlength: "3"},
        { id: "type", placeholder: "SVR", type: "text", label: "Type", tabIndex: 4, maxlength: "3" },
        { id: "boat", placeholder: "PEQUOD", type: "text", label: "Bateau", tabIndex: 5, maxlength: "100" },
        { id: "pilot", placeholder: "Capitaine ACHAB", type: "text", label: "Pilote", tabIndex: 6, maxlength: "100" },
        { id: "crew", placeholder: "C.H., J.C.", type: "text", label: "Equipage", tabIndex: 7, maxlength: "100" },
        { id: "partners", placeholder: "Ifremer, KAL", type: "text", label: "Partenaires", tabIndex: 8, maxlength: "200" }
    ];

    const campaignFinal = {
        zoneDict: {
            zone: String,
            region: String,
            type: String
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
        const group = document.createElement("div");
        group.className = "form-group";

        const label = document.createElement("label");
        label.setAttribute("for", field.id);
        label.textContent = field.label;

        const input = document.createElement("input");
        input.id = field.id;
        input.placeholder = field.placeholder;
        input.type = field.type;
        input.tabIndex = field.tabIndex;
        input.maxLength = field.maxlength;

        group.appendChild(label);
        group.appendChild(input);
        form.appendChild(group);
    });

    // Fix iOS Safari date input overflow
    window.addEventListener('load', () => {
        const dateInput = document.getElementById("date");
        if (!dateInput) return;
        const container = document.querySelector('.container');
        if (!container) return;
        const cs = getComputedStyle(container);
        const w = container.clientWidth
                  - parseFloat(cs.paddingLeft)
                  - parseFloat(cs.paddingRight);
        dateInput.style.setProperty('width', w + 'px', 'important');
        dateInput.style.setProperty('max-width', w + 'px', 'important');
    });

    // Add "Save" and "Reset" buttons to the form
    const actions = document.createElement("div");
    actions.className = "form-actions";

    const saveButton = document.createElement("button");
    saveButton.type = "submit";
    saveButton.textContent = "Save";

    const resetButton = document.createElement("button");
    resetButton.type = "reset";
    resetButton.textContent = "Reset";
    resetButton.id = "campaignResetButton";

    actions.appendChild(saveButton);
    actions.appendChild(resetButton);
    form.appendChild(actions);

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

        campaignFinal.zoneDict.type = formData.type;
        campaignFinal.zoneDict.region = formData.region;
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
