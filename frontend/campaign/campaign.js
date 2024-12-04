document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("campaignForm");

    const fields = [
        { id: "campaign", placeholder: "Sélectionnez un campaign", type: "text", label: "Campaign", tabIndex: 1, isCampaign: true },
        { id: "zone", placeholder: "Sélectionnez une zone", type: "text", label: "Zone", tabIndex: 2, isZone: true },
        { id: "locality", placeholder: "Illien", type: "text", label: "Location", tabIndex: 3, maxlength: "100" },
        { id: "protection", placeholder: "Parc naturel marin d'iroise", type: "text", label: "Protection", tabIndex: 4, maxlength: "100" },
        { id: "boat", placeholder: "Beneteau Capelan", type: "text", label: "Boat", tabIndex: 6, maxlength: "100" },
        { id: "pilot", placeholder: "Olivier F.", type: "text", label: "Pilot", tabIndex: 7, maxlength: "100" },
        { id: "equipment", placeholder: "C.H., J.C.", type: "text", label: "Equipment", tabIndex: 8, maxlength: "100" },
        { id: "partners", placeholder: "Ifremer RDT, Ifremer Halgo", type: "text", label: "Partners", tabIndex: 9, maxlength: "200" }
    ];

    const campaignOptions = [
        { code: "ANT", name: "Antarctique" },
        { code: "ARC", name: "Arctique" },
        { code: "ATL", name: "Atlantique" },
        { code: "IND", name: "Indien" },
        { code: "MED", name: "Méditerranée" },
        { code: "PAC", name: "Pacifique" }
    ];

    const zoneOptions = [
        { code: "AC", name: "Arcachon" },
        { code: "AD", name: "Audierne" },
        { code: "BR", name: "Brest" }
    ];

    let choicesInstances = {};

    fields.forEach(field => {
        const label = document.createElement("label");
        label.setAttribute("for", field.id);
        label.textContent = `${field.label}: `;

        if (field.isCampaign || field.isZone) {
            const select = document.createElement("select");
            select.id = field.id;

            const defaultOption = document.createElement("option");
            defaultOption.value = "";
            defaultOption.textContent = field.placeholder;
            select.appendChild(defaultOption);

            const options = field.isCampaign ? campaignOptions : zoneOptions;

            options.forEach(option => {
                const optionElement = document.createElement("option");
                optionElement.value = option.code;
                optionElement.textContent = `${option.code} - ${option.name}`;
                select.appendChild(optionElement);
            });

            form.appendChild(label);
            form.appendChild(select);

            const choicesInstance = new Choices(select, {
                searchEnabled: true,
                shouldSort: false,
                duplicateItemsAllowed: false,
            });

            // Save instance for later use
            choicesInstances[field.id] = choicesInstance;
        } else {
            const input = document.createElement("input");
            input.id = field.id;
            input.placeholder = field.placeholder;
            input.type = field.type;
            input.maxLength = field.maxlength || "";
            form.appendChild(label);
            form.appendChild(input);
        }
    });

    const saveButton = document.createElement("button");
    saveButton.type = "submit";
    saveButton.textContent = "Save";

    form.appendChild(saveButton);

    const storedData = localStorage.getItem("campaignData");
    if (storedData) {
        const formData = JSON.parse(storedData);

        fields.forEach(field => {
            if (formData[field.id]) {
                if (field.isCampaign || field.isZone) {
                    const choicesInstance = choicesInstances[field.id];
                    if (choicesInstance) {
                        choicesInstance.setChoiceByValue(formData[field.id]);
                    }
                } else {
                    const input = document.getElementById(field.id);
                    if (input) {
                        input.value = formData[field.id];
                    }
                }
            }
        });
    }

    form.addEventListener("submit", function (event) {
        event.preventDefault();

        const formData = {};

        fields.forEach(field => {
            const input = document.getElementById(field.id);
            formData[field.id] = input.value;
        });

        localStorage.setItem("campaignData", JSON.stringify(formData));

        Swal.fire({
            title: 'Success',
            text: 'Information saved',
            icon: 'success',
            confirmButtonText: 'OK'
        });
    });
});
