// This variable holds the URL of the server where the backend is hosted
let serverUrl = "http://10.42.0.1:5000";
// Alternative server URL (commented out)
// let serverUrl = "http://10.29.225.198:5000";

// Variable to store configuration data fetched from the server
let listData;

const materials = [
	"Batterie chargée",
	"Batterie de rechange",
	"Clé USB vide",
	"Flotteur à casier",
	"Bout 5m",
	"Jeu de bout",
	"Gréement",
	"Lunette de Calfat",
	"Tube caméra",
	"Réducteur",
	"Trépied",
	"Fagot de colsons",
	"Plombs (x2)",
	"Pompe à vide",
	"Aimants (x2)",
	"Ardoise et feutre",
	"Serviette microfibre",
	"Fiche terrain",
	"Stylo",
	"GPS",
	"Profondimètre de plongée",
	"Gaffe",
	"Jeu de clés allen",
	"Jeu de clés à cliquet",
	"Clé de 8",
	"Clés de 13 (x2)",
	"Pince plate",
	"Tournevis plat",
	"Vis M5 (x2)",
	"Ecrous M5 (x2)",
	"Rondelle M8",
	"Bouchon du vent",
	"Tube de graisse (silicone)"
];

document.addEventListener("DOMContentLoaded", function () {
  const list = document.getElementById("checkList");

  function initLocalStorage() {
    if (!localStorage.getItem("materials")) {
      localStorage.setItem("materials", JSON.stringify([]));
    }
  }

  function getMaterialsFromLocalStorage() {
    return JSON.parse(localStorage.getItem("materials")) || [];
  }

  function saveMaterialsToLocalStorage(materials) {
    localStorage.setItem("materials", JSON.stringify(materials));
  }

  initLocalStorage();
  let materialsChose = getMaterialsFromLocalStorage();

  materials.forEach((element, index) => {
    let listItem = document.createElement("li");

    let input = document.createElement("input");
    input.setAttribute("type", "checkbox");
    input.setAttribute("id", "material" + index);
    input.setAttribute("name", "material" + index);
    input.value = element;

    let label = document.createElement("label");
    label.setAttribute("for", "material" + index);
    label.textContent = element;

    listItem.append(input, label);
    list.append(listItem);
  });

  const resetButton = document.createElement("button");
  resetButton.setAttribute("id", "resetButton");
  resetButton.setAttribute("type", "reset");
  resetButton.textContent = "Reset";
  resetButton.addEventListener("click", function () {
    localStorage.setItem("materials", JSON.stringify([]));
    materialsChose = [];
  });
  list.appendChild(resetButton);

  const checkboxes = document.querySelectorAll('input[type="checkbox"]');
  checkboxes.forEach(checkbox => {
    if (materialsChose.includes(checkbox.value)) {
      checkbox.checked = true;
    }
  });

  list.addEventListener("change", function (event) {
    if (event.target.type === "checkbox") {
      if (event.target.checked) {
        materialsChose.push(event.target.value);
      } else {
        materialsChose = materialsChose.filter(material => material !== event.target.value);
      }
      saveMaterialsToLocalStorage(materialsChose);
    }
  });
});
