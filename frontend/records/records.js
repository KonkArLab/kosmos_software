let serverUrl = location.protocol === "https:" ? location.origin : "http://10.42.0.1:5000";

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

async function populateTable() {
  const fileTable = document.getElementById("fileTable");
  const records = await fetchData();

  while (fileTable.rows.length > 1) {
    fileTable.deleteRow(1);
  }

  records.reverse().forEach((record) => {
    const row = fileTable.insertRow();
    row.insertCell().textContent = record.fileName;
    row.insertCell().textContent = record.size;
    const timeCell = row.insertCell();
    timeCell.textContent = `${record.time} ${record.day} ${record.month}`;
  });
}

populateTable();
