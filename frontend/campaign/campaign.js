document.addEventListener("DOMContentLoaded", function () {
    // Select the main form by its ID
    const form = document.getElementById("campaignForm");

    // Define the form fields with their properties like ID, placeholder, type, etc.
    const fields = [
        { id: "campaign", placeholder: "Sélectionnez un campagne", type: "text", label: "Campaign", tabIndex: 1, isCampaign: true },
        { id: "zone", placeholder: "Sélectionnez une zone", type: "text", label: "Zone", tabIndex: 2, isZone: true },
        { id: "locality", placeholder: "Illien", type: "text", label: "Location", tabIndex: 3, maxlength: "100" },
        { id: "protection", placeholder: "Parc naturel marin d'iroise", type: "text", label: "Protection", tabIndex: 4, maxlength: "100" },
        { id: "boat", placeholder: "Beneteau Capelan", type: "text", label: "Boat", tabIndex: 5, maxlength: "100" },
        { id: "pilot", placeholder: "Olivier F.", type: "text", label: "Pilot", tabIndex: 6, maxlength: "100" },
        { id: "equipment", placeholder: "C.H., J.C.", type: "text", label: "Equipment", tabIndex: 7, maxlength: "100" },
        { id: "partners", placeholder: "Ifremer RDT, Ifremer Halgo", type: "text", label: "Partners", tabIndex: 8, maxlength: "200" }
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
            year: Number,
            month: Number,
            day: Number,
            date: String
        },
        deploiementDict: {
            boat: String,
            pilot: String,
            equipment: String,
            partners: String
        }
    }

    // Available options for campaigns
    const campaignOptions = [
        { code: "ANT", name: "Antarctique" },
        { code: "ARC", name: "Arctique" },
        { code: "ATL", name: "Atlantique" },
        { code: "IND", name: "Indien" },
        { code: "MED", name: "Méditerranée" },
        { code: "PAC", name: "Pacifique" }
    ];

    // Available options for zones
    const zoneOptions = [
        { code: "AC", name: "Arcachon" },
        { code: "AD", name: "Audierne" },
        { code: "AJ", name: "Ajaccio" },
        { code: "AY", name: "Auray" },
        { code: "BA", name: "Bayonne" },
        { code: "BI", name: "Bastia" },
        { code: "BL", name: "Boulogne-sur-Mer" },
        { code: "BR", name: "Brest" },
        { code: "BX", name: "Bordeaux" },
        { code: "BY", name: "Saint-Barthélemy" },
        { code: "CC", name: "Concarneau" },
        { code: "CH", name: "Cherbourg" },
        { code: "CM", name: "Camaret" },
        { code: "CN", name: "Caen" },
        { code: "CY", name: "Cayenne" },
        { code: "DP", name: "Dieppe" },
        { code: "DK", name: "Dunkerque" },
        { code: "DZ", name: "Douarnenez" },
        { code: "FC", name: "Fécamp" },
        { code: "FF", name: "Fort-de-France" },
        { code: "GV", name: "Le Guilvinec" },
        { code: "IO", name: "Île d'Oléron" },
        { code: "LH", name: "Le Havre" },
        { code: "LO", name: "Lorient" },
        { code: "LR", name: "La Rochelle" },
        { code: "LS", name: "Les Sables-d'Olonne" },
        { code: "MA", name: "Marseille" },
        { code: "MN", name: "Marennes" },
        { code: "MT", name: "Martigues" },
        { code: "MX", name: "Morlaix" },
        { code: "NA", name: "Nantes" },
        { code: "NI", name: "Nice" },
        { code: "NO", name: "Noirmoutier" },
        { code: "PL", name: "Paimpol" },
        { code: "PP", name: "Pointe-à-Pitre" },
        { code: "PV", name: "Port-Vendres" },
        { code: "RO", name: "Rouen" },
        { code: "RU", name: "La Réunion" },
        { code: "SB", name: "Saint-Brieuc" },
        { code: "SM", name: "Saint-Malo" },
        { code: "SN", name: "Saint-Nazaire" },
        { code: "SP", name: "Saint-Pierre-et-Miquelon" },
        { code: "ST", name: "Sète" },
        { code: "TL", name: "Toulon" },
        { code: "VA", name: "Vannes" },
        { code: "YE", name: "Île d'Yeu" }
    ];

    // Object to store instances of Choices.js
    const choicesInstances = {};

    // Dynamically create form fields
    fields.forEach(field => {
        const label = document.createElement("label");
        label.setAttribute("for", field.id);
        label.textContent = field.label + ": ";

        if (field.isCampaign || field.isZone) {
            const select = document.createElement("select");
            select.id = field.id;
            select.setAttribute("placeholder", field.placeholder);
            select.setAttribute("name", field.id);

            // Default option
            const defaultOption = document.createElement("option");
            defaultOption.value = "";
            defaultOption.textContent = field.placeholder;
            select.appendChild(defaultOption);

            // Add options
            const options = field.isCampaign ? campaignOptions : zoneOptions;
            options.forEach(option => {
                const optionElement = document.createElement("option");
                optionElement.value = option.code;
                optionElement.textContent = `${option.code} - ${option.name}`;
                select.appendChild(optionElement);
            });

            form.appendChild(label);
            form.appendChild(select);

            // Initialize Choices.js and save instance
            choicesInstances[field.id] = new Choices(select, {
                searchEnabled: true,
                shouldSort: false,
                duplicateItemsAllowed: false
            });
        } else {
            const input = document.createElement("input");
            input.id = field.id;
            input.placeholder = field.placeholder;
            input.type = field.type;
            input.tabIndex = field.tabIndex;
            input.maxLength = field.maxlength;
            form.appendChild(label);
            form.appendChild(input);
        }
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

    // Load previously saved data from localStorage
    const storedData = localStorage.getItem("campaignData");
    if (storedData) {
        const formData = JSON.parse(storedData);

        fields.forEach(field => {
            let value = null;

            if (field.id in formData.zoneDict) {
                value = formData.zoneDict[field.id];
            } else if (field.id in formData.dateDict) {
                value = formData.dateDict[field.id];
            } else if (field.id in formData.deploiementDict) {
                value = formData.deploiementDict[field.id];
            }

            if (value) {
                if ((field.isCampaign || field.isZone) && choicesInstances[field.id]) {
                    choicesInstances[field.id].setChoiceByValue(value);
                } else {
                    const element = document.getElementById(field.id);
                    if (element) {
                        element.value = value;
                    }
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

        campaignFinal.deploiementDict.boat = formData.boat;
        campaignFinal.deploiementDict.equipment = formData.equipment;
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
