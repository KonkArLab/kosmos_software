// This variable holds the URL of the server where the backend is hosted
let serverUrl = "http://10.42.0.1:5000";
// Alternative server URL (commented out)
// let serverUrl = "http://10.29.225.198:5000";

// Function to fetch records data from the server
async function fetchData() {
  try {
    const response = await fetch(serverUrl + "/getRecords");
    const data = await response.json();
    return data.data;
  } catch (error) {
    console.error("Error fetching data:", error);
    return [];
  }
}

// Function to populate the table with records data
async function populateTable() {
  const fileTable = document.getElementById("fileTable");

  // Fetch records data from the API
  const records = await fetchData();

  // Clear existing rows in the table (excluding the header)
  while (fileTable.rows.length > 1) {
    fileTable.deleteRow(1);
  }

  // Reverse the records array before adding rows
  const reversedRecords = records.reverse();

  // Iterate over reversed records and create table rows
  reversedRecords.forEach((record) => {
    const row = fileTable.insertRow();
    row.insertCell().textContent = record.fileName;
    row.insertCell().textContent = record.size;

    // Merge Time, Day, and Month into a single column
    const timeCell = row.insertCell();
    timeCell.textContent = `${record.time} ${record.day} ${record.month}`;
  });
}

// Call the function to populate the table when the page loads
populateTable();
