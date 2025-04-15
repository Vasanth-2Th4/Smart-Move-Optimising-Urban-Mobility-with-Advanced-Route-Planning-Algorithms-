// Function to initialize Google Maps Places Autocomplete on input fields
function initializeAutocomplete() {
    const startPoint = new google.maps.places.Autocomplete(document.getElementById('start-point'));
    const endPoint = new google.maps.places.Autocomplete(document.getElementById('end-point'));

    // Event listener to add a new delivery point input field with autocomplete
    document.getElementById('add-point').addEventListener('click', function () {
        const additionalPoints = document.getElementById('additional-points');
        const pointCount = additionalPoints.getElementsByTagName('div').length + 1; // Keeps count for new points

        const newPointDiv = document.createElement('div');
        newPointDiv.classList.add('input-group');
        newPointDiv.innerHTML = `
            <label for="delivery-point-${pointCount}">Delivery Point ${pointCount}:</label>
            <input type="text" id="delivery-point-${pointCount}" name="delivery-point-${pointCount}" required>
        `;
        additionalPoints.appendChild(newPointDiv);

        // Initialize Google Maps Autocomplete for the new input field
        new google.maps.places.Autocomplete(document.getElementById(`delivery-point-${pointCount}`));
    });
}

// Define the calculateRoute function
function calculateRoute() {
    const startPoint = document.getElementById('start-point').value;
    const endPoint = document.getElementById('end-point').value;
    const deliveryPoints = Array.from(document.querySelectorAll('input[id^="delivery-point-"]'))
                                 .map(input => input.value);

    fetch("http://127.0.0.1:5000/api/generate-route", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            startPoint: startPoint,
            deliveryPoints: deliveryPoints,
            endPoint: endPoint
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error("Failed to fetch route data from the server.");
        }
        return response.json();
    })
    .then(data => {
        console.log("Route Data:", data);
        if (Array.isArray(data) && data.length > 0) {
            displayOrderedPoints(data); // Display the data if returned and valid
        } else {
            throw new Error("Unexpected data format received.");
        }
    })
    .catch(error => {
        console.error("Error:", error);
        document.getElementById('result').innerHTML = `<p>Error occurred while calculating the route. Please try again later.</p>`;
    });
}

// Function to display the ordered routes with weather conditions
function displayOrderedPoints(orderedRoutes) {
    // Ensure orderedRoutes is an array before sorting and accessing data
    if (!Array.isArray(orderedRoutes) || orderedRoutes.length === 0) {
        console.error("Invalid orderedRoutes data:", orderedRoutes);
        document.getElementById('result').innerHTML = `<p>Error: No valid route data found.</p>`;
        return;
    }

    // Sort routes by total time taken in ascending order
    orderedRoutes.sort((a, b) => a.total_time - b.total_time);

    // Get the route with the minimum total time
    const optimalRoute = orderedRoutes[0];

    const resultDiv = document.getElementById('result');
    resultDiv.innerHTML = `<h2>Optimized Route:</h2>` + `
        <div>
            <p><strong>Route: ${optimalRoute.route.join(' ➔ ')}</p>
            <p><strong>Total Distance: ${(optimalRoute.total_distance).toFixed(2)} km</p>
            <p><strong>Traffic Conditions: ${optimalRoute.traffic_conditions.join(', ')}</p>
            <p><strong>Time Conditions: ${optimalRoute.time_conditions.join(', ')}</p>
            <p><strong>Weather Conditions: ${optimalRoute.weather_conditions.join(' | ')}</p>
            <p><strong>Total Time Taken:</strong> ${optimalRoute.total_time}</p>
        </div>
    `;
}

// Add event listener to handle form submission and prevent default form action
document.getElementById('delivery-form').addEventListener('submit', function (event) {
    event.preventDefault(); // Prevent form from submitting in the traditional way
    calculateRoute(); // Trigger the route calculation
});
