let calls = []; // Define calls as a global variable

// Function to fetch calls data from the local caller_entries.json file
function getCallsFromS3() {
    const url = 'https://hackharvardq11.s3.amazonaws.com/messages/caller_entries.json'; // Local file path for the uploaded JSON file

    return new Promise((resolve, reject) => {
        fetch(url)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                resolve(data);
            })
            .catch(error => {
                console.error("Error fetching data from local JSON", error);
                reject(error);
            });
    });
}

// Function to fetch data and update the table
function updateCallDataFromLocal() {
    getCallsFromS3()
        .then(fetchedCalls => {
            const tableBody = document.getElementById('call-data');
            const totalCalls = document.getElementById('total-calls');

            // Modify the data structure to fit the current script
            calls = fetchedCalls.map(call => ({
                time: call.Time,
                address: call.Address,
                description: call.Description,
                priority: parseInt(call["Priority Ranking"]), // Convert percentage to an integer
                name: call["Caller Name"],  // Use "Caller Name" from the JSON
                phone: call["Caller Phone"]  // Use "Caller Phone" from the JSON
            }));

            // Sort calls by priority before displaying
            const sortedCalls = sortByPriorityDescending(calls);
            const duplicateIncidents = groupIncidents(sortedCalls);

            displayDuplicateIncidents(duplicateIncidents);

            tableBody.innerHTML = '';  // Clear existing rows

            sortedCalls.forEach((call, index) => {
                let priorityClass = call.priority > 3 ? 'high' : 'low';
                tableBody.innerHTML += `
                    <tr>
                        <td>${call.time || null}</td>
                        <td>${call.address || null}</td>
                        <td>${call.description || null}</td>
                        <td class="priority ${priorityClass}">${call.priority || null}</td>
                        <td>${call.name || null}</td>
                        <td>${call.phone || null}</td>
                        <td><button onclick="removeCallRow(${index})">−</button></td>
                    </tr>
                `;
            });

            totalCalls.innerText = sortedCalls.length;
        })
        .catch(err => {
            console.error('Error loading call data from local JSON:', err);
        });
}

// Function to remove a call row
function removeCallRow(index) {
    const confirmed = confirm('Are you sure you want to remove this call?');
    if (confirmed) {
        calls.splice(index, 1); // Remove the call from the array
        updateCallData(); // Re-render the table with updated data
        alert('Call removed successfully');
    }
}

// Function to populate the call data table
function updateCallData() {
    const tableBody = document.getElementById('call-data');
    const totalCalls = document.getElementById('total-calls');

    // Sort calls by priority before displaying
    const sortedCalls = sortByPriorityDescending(calls);
    const duplicateIncidents = groupIncidents(sortedCalls);

    displayDuplicateIncidents(duplicateIncidents);

    tableBody.innerHTML = '';  // Clear existing rows

    sortedCalls.forEach((call, index) => {
        let priorityClass = call.priority > 3 ? 'high' : 'low';
        tableBody.innerHTML += `
            <tr>
                <td>${call.time || null}</td>
                <td>${call.address || null}</td>
                <td>${call.description || null}</td>
                <td class="priority ${priorityClass}">${call.priority || null}</td>
                <td>${call.name || null}</td>
                <td>${call.phone || null}</td>
                <td><button onclick="removeCallRow(${index})">−</button></td>
            </tr>
        `;
    });

    totalCalls.innerText = sortedCalls.length;
}

updateCallDataFromLocal();


// Function to sort calls by priority in descending order
function sortByPriorityDescending(calls) {
    return calls.sort((a, b) => b.priority - a.priority);
}

// Function to group and count duplicate incidents
function groupIncidents(calls) {
    let incidentMap = {};
    let duplicateIncidents = [];

    calls.forEach(call => {
        const key = `${call.address || null}-${call.description || null}`;  // Group by address and description
        if (incidentMap[key]) {
            incidentMap[key].count++;
            incidentMap[key].calls.push(call);
        } else {
            incidentMap[key] = { count: 1, calls: [call] };
        }
    });

    // Get only duplicates (3 or more)
    for (let key in incidentMap) {
        if (incidentMap[key].count >= 3) {
            duplicateIncidents.push(incidentMap[key]);
        }
    }

    return duplicateIncidents;
}

// Function to display duplicate incidents in multiple full-on boxes
function displayDuplicateIncidents(duplicateIncidents) {
    const incidentContainer = document.getElementById('incident-container');
    incidentContainer.innerHTML = '';  
    incidentContainer.style.display = 'flex'; 
    incidentContainer.style.flexWrap = 'wrap'; 
    incidentContainer.style.gap = '10px'; 

    duplicateIncidents.forEach(group => {
        let incidentBox = document.createElement('div');
        incidentBox.className = 'incident-box';
        incidentBox.style.border = '1px solid black';
        incidentBox.style.padding = '10px';
        incidentBox.style.width = '500px'; 
        incidentBox.style.boxSizing = 'border-box'; 

        let incidentDetails = `<h3>Possible Major Incident: ${group.calls[0].description || null}</h3>`;
        incidentDetails += '<ul>';

        group.calls.forEach(call => {
            incidentDetails += `<li>Address: ${call.address ||  null}, Time: ${call.time || null}, Caller: ${call.name || null}, Phone: ${call.phone || null}</li>`;
        });

        incidentDetails += '</ul>';
        incidentBox.innerHTML = incidentDetails;
        incidentContainer.appendChild(incidentBox);
    });

    // Show the container if we have duplicates
    if (duplicateIncidents.length > 0) {
        incidentContainer.style.display = 'flex';
    } else {
        incidentContainer.style.display = 'none';
    }
}

setInterval(fetchAndUpdateData, 500); 

fetchAndUpdateData();
