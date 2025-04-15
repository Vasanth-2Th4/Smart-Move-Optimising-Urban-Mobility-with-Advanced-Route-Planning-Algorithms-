# Smart-Move-Optimising-Urban-Mobility-with-Advanced-Route-Planning-Algorithms-
Developed Smart Move, an intelligent urban mobility system that leverages Ant Colony Optimization for advanced route planning. It suggests faster, less congested paths to reduce travel time and improve traffic flow for efficient city commuting.

Here’s a detailed and professional `README.md` for your project **"Smart Move – Optimising Urban Mobility with Advanced Route Planning Algorithms"**, based on the structure and functionality of your uploaded files:

---

# 🚦 Smart Move: Optimising Urban Mobility with Advanced Route Planning Algorithms

Smart Move is a full-stack urban mobility solution that leverages **Ant Colony Optimization (ACO)** and real-time **Google Maps** and **weather data** to help users generate optimal delivery or commuting routes. It combines route planning, traffic prediction, and environmental awareness for smarter urban navigation.

---

## 🌐 Live Tech Stack

- **Frontend**: HTML, CSS, JavaScript (Vanilla) with Google Maps API
- **Backend**: Flask (Python) + Express.js (Node.js)
- **Optimization Algorithm**: Ant Colony Optimization (ACO)
- **APIs Used**: 
  - Google Maps Directions & Places
  - OpenWeatherMap API

---

## 🔧 Features

- 🗺️ Auto-suggest start, delivery, and end locations using Google Maps Places
- 📦 Add multiple delivery points dynamically
- 🧠 Calculate route permutations with time, distance, traffic & weather
- 🐜 Optimize the best route using ACO
- 📊 Visual feedback with detailed metrics (time, traffic, weather)
- 📥 Export route details to Excel (via Flask)
- 📝 Save user delivery data server-side (via Express)

---

## 📁 Project Structure

```
📦 Smart-Move
├── app.py                  # Flask server with ACO logic and Excel generation
├── server.js               # Node.js server to log route data
├── index.html              # Main UI page
├── script.js               # Client-side logic to send route data and render results
├── styles.css              # UI styling
├── package.json            # Node dependencies and metadata
├── package-lock.json       # Exact versions for Node packages
```


## 🚀 Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/smart-move.git
cd smart-move
```

### 2. Install Node Dependencies
```bash
npm install
```

### 3. Run the Node.js Backend
```bash
node server.js
# Runs on http://localhost:5000
```

### 4. Run the Flask Backend
```bash
python app.py
# Runs on http://127.0.0.1:5000
```

---

## ✅ How to Use

1. Open `index.html` in your browser.
2. Enter a **Start Point**, one or more **Delivery Points**, and an **End Point**.
3. Click "Generate Route".
4. View:
   - Route with arrows ➔
   - Total distance (km)
   - Real-time traffic and weather conditions
   - Total estimated time
5. Optimized route details will also be saved/exported server-side.

---

## 🧠 Algorithm Insight: Ant Colony Optimization (ACO)

ACO is a biologically inspired algorithm based on how ants find the shortest paths. In this project, it's used to:
- Evaluate multiple delivery point permutations
- Balance traffic time, distance, and real-time conditions
- Determine the most efficient delivery route

---

## 📌 Environment Variables

Make sure to set your own keys:
- Google Maps API Key
- OpenWeatherMap API Key

These are currently hardcoded in `app.py` and `index.html`. For production, move them to a `.env` file or config file.


## 🤝 Contributing

Feel free to fork, open issues, and submit pull requests to improve route efficiency, UI, or integrate public transport APIs!
