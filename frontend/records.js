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

  // Iterate over records and create table rows
  records.forEach((record) => {
    const row = fileTable.insertRow();
    row.insertCell().textContent = record.fileName;
    row.insertCell().textContent = record.size;

    // Merge Time, Day, and Month into a single column
    const timeCell = row.insertCell();
    timeCell.textContent = `${record.time} h - ${record.day} ${record.month}`;
  });

  // Get all rows, excluding the header
  const rows = Array.from(fileTable.getElementsByTagName("tr")).slice(1);

  // Reverse the order of rows
  rows.reverse();

  // Clear existing rows in the table
  while (fileTable.rows.length > 1) {
    fileTable.deleteRow(1);
  }

  // Reinsert rows in reverse order
  rows.forEach((row) => {
    fileTable.appendChild(row);
  });
}

// Call the function to populate the table when the page loads
populateTable();
