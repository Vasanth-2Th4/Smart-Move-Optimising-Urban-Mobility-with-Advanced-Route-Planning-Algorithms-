const express = require('express');
const cors = require('cors');
const fs = require('fs').promises;  // File system module to write files
const app = express();
const port = 5000;

// Enable CORS for all origins
app.use(cors());

// Middleware to parse incoming JSON
app.use(express.json());

// Example route for testing
app.post('/api/optimize-route', async (req, res) => {
    const { startPoint, deliveryPoints } = req.body;
    console.log('Received startPoint:', startPoint);
    console.log('Received deliveryPoints:', deliveryPoints);

    // Save the request data to a file
    const dataToSave = {
        startPoint,
        deliveryPoints,
        timestamp: new Date().toISOString()  // Add a timestamp for when the request was made
    };

    const fileName = 'route_data.json';  // File name to save the data
    const filePath = __dirname + '/' + fileName;  // Get the path where the file will be saved

    try {
        // Write data to the file
        await fs.appendFile(filePath, JSON.stringify(dataToSave, null, 2) + '\n');
        console.log('Data saved successfully to file!');
    } catch (err) {
        console.error('Error writing to file:', err);
        res.status(500).json({ error: 'Failed to save data' });
        return;
    }

    // Dummy response: Just return the points sorted alphabetically
    const optimizedRoute = deliveryPoints.sort();
    res.json(optimizedRoute);
});

// Start the server
app.listen(port, () => {
    console.log(`Server running on http://localhost:${port}`);
});
