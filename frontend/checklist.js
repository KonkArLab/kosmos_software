// This variable holds the URL of the server where the backend is hosted
let serverUrl = "http://10.42.0.1:5000";
// Alternative server URL (commented out)
// let serverUrl = "http://10.29.225.198:5000";

// Variable to store configuration data fetched from the server
let listData; 

// Function to fetch the list
function fetchList() {
  try {
    const myList = document.querySelector("section");

      fetch("list.json")
	.then((response) => {
	  if (!response.ok) {
	    throw new Error(`HTTP error, status = ${response.status}`);
	  }
	  return response.json();
	})
	.then ((data) => {
	  for (let element of data.materiel) {
	    let listItem = document.createElement("ul");
	    
	    let input = document.createElement("input");
	    input.setAttribute("type", "checkbox");
	    input.setAttribute("id", element);
	    input.setAttribute("name", "materiel");
	    input.classList.add("list-element");
	    input.value = myList[element];
	    
	    let label = document.createElement("label");
	    label.setAttribute("for", "materiel" + element);
	    label.classList.add("list-element");
	    label.textContent = element;
	    
	    listItem.append(
			    input,
			    label
			    )
	    
	    myList.appendChild(listItem);
	    listData = myList;
	    listItem='';
	
	    }
	    
	    //bouton reset	
	    const resetButton = document.createElement("button");
	    resetButton.setAttribute("id", "resetButton");
	    resetButton.setAttribute("type", "button");
	    resetButton.textContent = "Reset";
	    resetButton.classList.add("reboot");
	    resetButton.addEventListener("click", function (event) {
	      console.log("reset ok");
	      event.preventDefault(); // Prevent the default form submission behavior
	      localStorage.clear();
	      window.location.reload();
	      
	    });
	    myList.appendChild(resetButton);
	    
	    change();
	    	  
	  })
	    
	}

  catch(error){
    const p = document.createElement("p");
    p.appendChild(document.createTextNode(`Error: ${error.message}`));
    document.body.insertBefore(p, myList);
  }
}

function change(){
  var box = document.querySelectorAll("input[type='checkbox']");
  var selectbox = [];
  var savebox = localStorage.getItem('selectbox');
  
  //vérification si il y a des cases cochées en mémoire
  if (savebox) {
    selectbox.push(...JSON.parse(savebox));
    }
    
  //mise à jour des états en fonction des cases en mémoire
  box.forEach(box => {
    if (selectbox.includes(box.id)){
      box.checked = true;
    }
  });
    
  box.forEach(box => {
    box.addEventListener('change', () => {
      if(box.checked) {
	console.log("change ok");
	selectbox.push(box.id);
      } else {
	var indexSelectbox = selectbox.indexOf(box.id)
	if (indexSelectbox !== -1){
	  selectbox.splice(indexSelectbox, 1);
	}
      }
      localStorage.setItem('selectbox', JSON.stringify(selectbox));
      console.log("selectbox", selectbox);
      console.log("savebox", savebox);
    });
  });
}


// Fetch the list when the page loads
fetchList();
