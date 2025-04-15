from flask import Flask, request, jsonify
from flask_cors import CORS
import itertools
import requests
import openpyxl
import googlemaps
import pandas as pd
import numpy as np
import random
from datetime import timedelta

app = Flask(__name__)
CORS(app)

# Initialize Google Maps client
#gmaps = googlemaps.Client(key='AIzaSyChnZ0SRYEPh-jMrS8AdqGJdNxUX-Nu6Do')     #remove hastag
weather_api_key = 'f30b257a86c037d7047ee7b0fcbce704'

# ACO Parameters
num_ants = 5
num_iterations = 30
pheromone_evaporation_coefficient = 0.7
pheromone_constant = 1000
pheromone_importance = 1
distance_importance = 1

# Adjusted `calculate_distance_matrix`
def calculate_distance_matrix(points):
    n = len(points)
    distance_matrix = np.zeros((n, n))

    for i in range(n):
        for j in range(i + 1, n):
            try:
                directions = gmaps.directions(points[i], points[j], departure_time='now')
                if directions and directions[0]['legs']:
                    distance = directions[0]['legs'][0].get('distance', {}).get('value', 1e6)  # Fallback distance
                    distance_matrix[i][j] = distance_matrix[j][i] = distance
                else:
                    distance_matrix[i][j] = distance_matrix[j][i] = 1e6
            except Exception as e:
                print(f"Error getting directions from {points[i]} to {points[j]}: {e}")
                distance_matrix[i][j] = distance_matrix[j][i] = 1e6

    return distance_matrix


def get_weather_conditions(location):
    """Fetch weather conditions for a given location using the OpenWeatherMap API."""
    url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={weather_api_key}&units=metric"
    try:
        response = requests.get(url)
        data = response.json()
        if response.status_code == 200:
            weather_description = data['weather'][0]['description']
            temperature = data['main']['temp']
            return f"{weather_description}, {temperature}°C"
        else:
            return "Weather data not available"
    except Exception as e:
        print(f"Error fetching weather data for {location}: {e}")
        return "Weather data error"

def ant_colony_optimization(distance_matrix, start_index, end_index):
    """ACO algorithm to find the optimized route."""
    num_points = len(distance_matrix)
    pheromones = np.ones((num_points, num_points))

    best_route = None
    best_distance = float('inf')

    for iteration in range(num_iterations):
        all_routes = []
        print(f"\n--- Iteration {iteration + 1} ---")  # Print the iteration number

        for ant in range(num_ants):
            route = [start_index]
            total_distance = 0

            while len(route) < num_points:
                current = route[-1]
                probabilities = []

                for next_point in range(num_points):
                    if next_point not in route:
                        # Calculate the transition probability
                        pheromone_level = pheromones[current][next_point] ** pheromone_importance
                        distance_level = (1.0 / distance_matrix[current][next_point]) ** distance_importance
                        probabilities.append((next_point, pheromone_level * distance_level))

                # Select the next point based on probabilities
                if probabilities:
                    total = sum([prob[1] for prob in probabilities])
                    probabilities = [(point, prob / total) for point, prob in probabilities]
                    next_point = random.choices(
                        [prob[0] for prob in probabilities],
                        [prob[1] for prob in probabilities]
                    )[0]
                    route.append(next_point)
                    total_distance += distance_matrix[current][next_point]

            # Add the distance from the last point to the endpoint
            total_distance += distance_matrix[route[-1]][end_index]
            route.append(end_index)
            all_routes.append((route, total_distance))

            # Update best route if this route is shorter
            if total_distance < best_distance:
                best_distance = total_distance
                best_route = route

            # Print the route of the current ant and its total distance
            print(f"Ant {ant + 1}: Route = {route}, Total Distance = {total_distance}")

        # Update pheromones based on routes
        pheromones *= (1 - pheromone_evaporation_coefficient)
        for route, distance in all_routes:
            for i in range(len(route) - 1):
                pheromones[route[i]][route[i + 1]] += pheromone_constant / distance

        # Print pheromone matrix after each iteration
        print(f"Pheromone Matrix after iteration {iteration + 1}:")
        print(pheromones)

    # Return the best route and its total distance
    return best_route, best_distance


@app.route('/api/generate-route', methods=['POST'])
def generate_route():
    try:
        data = request.get_json()
        if not data:
            raise ValueError("No JSON data received")
        
        # Check if the required keys are in the data
        if 'startPoint' not in data or 'deliveryPoints' not in data or 'endPoint' not in data:
            return jsonify({'error': 'Invalid data format. Missing startPoint, deliveryPoints, or endPoint.'}), 400

        start_point = data['startPoint']
        delivery_points = data['deliveryPoints']
        end_point = data['endPoint']

        # Get all permutations of the delivery points
        routes = list(itertools.permutations(delivery_points))

        all_routes = []
        for route in routes:
            route_info = get_route_info(start_point, route, end_point)
            all_routes.append(route_info)

        # Generate Excel file
        generate_excel(all_routes)

        return jsonify(all_routes)
    except Exception as e:
        print(f"Error: {e}")  # Logs the error to the server console
        return jsonify({'error': str(e)}), 500


def get_weather_conditions(lat, lon):
    """Fetch weather conditions for a given location."""
    weather_url = f'http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={weather_api_key}'
    response = requests.get(weather_url)
    if response.status_code == 200:
        weather_data = response.json()
        main_weather = weather_data['weather'][0]['main']
        description = weather_data['weather'][0]['description']
        temp = weather_data['main']['temp'] - 273.15  # Convert from Kelvin to Celsius
        return f"{main_weather}, {description}, {temp:.1f}°C"
    else:
        return "Weather data not available"

def classify_traffic_condition(distance, duration_in_traffic, average_speed=40):
    expected_time = (distance / average_speed) * 3600  # Expected time in seconds

    if duration_in_traffic and expected_time > 0:
        delay_percentage = ((duration_in_traffic - expected_time) / expected_time) * 100
    else:
        delay_percentage = 0

    if delay_percentage <= 20:
        return "Low"
    elif delay_percentage <= 50:
        return "Medium"
    else:
        return "Heavy"

def parse_time_condition(time_str):
    """Parse a time string like '1 hour 30 mins' into total minutes."""
    hours = 0
    minutes = 0
    if 'hour' in time_str:
        hours = int(time_str.split('hour')[0].strip())
        if 'mins' in time_str:
            minutes = int(time_str.split('hour')[1].split('mins')[0].strip())
    elif 'mins' in time_str:
        minutes = int(time_str.split('mins')[0].strip())
    return hours * 60 + minutes

def calculate_total_time(time_conditions):
    """Calculate total time from a list of time condition strings."""
    total_minutes = sum(parse_time_condition(time) for time in time_conditions if time != 'unknown')
    
    # Convert total minutes into hours and minutes
    hours = total_minutes // 60
    minutes = total_minutes % 60
    total_time_formatted = f"{hours} hrs {minutes} mins" if hours > 0 else f"{minutes} mins"
    return total_time_formatted

def get_route_info(start_point, route, end_point):
    points = [start_point] + list(route) + [end_point]
    total_distance = 0
    total_time_seconds = 0  # Initialize total time in seconds
    traffic_conditions = []
    time_conditions = []
    weather_conditions = []

    print(f"Calculating route info for: {points}")

    for i in range(len(points) - 1):
        try:
            directions = gmaps.directions(points[i], points[i + 1], departure_time='now')
            # Distance in km
            distance = directions[0]['legs'][0]['distance']['value'] / 1000  
            total_distance += distance

            # Duration in traffic (in seconds) if available
            duration_in_traffic = directions[0]['legs'][0].get('duration_in_traffic', {}).get('value', None)
            
            if duration_in_traffic:
                total_time_seconds += duration_in_traffic  # Add time in seconds for the segment
                time_conditions.append(directions[0]['legs'][0].get('duration_in_traffic', {}).get('text', 'unknown'))
            else:
                time_conditions.append('unknown')

            # Traffic condition based on distance and traffic duration
            traffic_condition = classify_traffic_condition(distance, duration_in_traffic)
            traffic_conditions.append(traffic_condition)

            # Fetch weather data for the starting point of the segment
            location = gmaps.geocode(points[i])[0]['geometry']['location']
            weather = get_weather_conditions(location['lat'], location['lng'])
            weather_conditions.append(weather)
            print(f"Weather for {points[i]}: {weather}")

        except Exception as e:
            traffic_conditions.append('error')
            time_conditions.append('error')
            weather_conditions.append('error')
            print(f"Error getting directions or weather for {points[i]}: {e}")

    # Calculate total time in a formatted string from the time_conditions list
    total_time_formatted = calculate_total_time(time_conditions)

    return {
        'route': points,
        'total_distance': total_distance,
        'traffic_conditions': traffic_conditions,
        'time_conditions': time_conditions,
        'weather_conditions': weather_conditions,
        'total_time': total_time_formatted  # This will now show total time
    }




def generate_excel(routes):
    df = pd.DataFrame(routes)
    df.to_excel('routes.xlsx', index=False)

@app.route('/api/optimize-route', methods=['POST'])
def optimize_route():
    try:
        data = request.get_json()
        
        # Check if the required keys are in the data
        if 'startPoint' not in data or 'deliveryPoints' not in data or 'endPoint' not in data:
            return jsonify({'error': 'Invalid data format. Missing startPoint, deliveryPoints, or endPoint.'}), 400

        start = data['startPoint']
        delivery_points = data['deliveryPoints']
        end = data['endPoint']

        # Combine all points for distance matrix calculation
        all_points = [start] + delivery_points + [end]
        distance_matrix = calculate_distance_matrix(all_points)

        # Apply ACO to find the best route with fewer iterations and ants
        start_index = 0
        end_index = len(all_points) - 1
        best_route, best_distance = ant_colony_optimization(distance_matrix, start_index, end_index)

        # Map indices back to point names
        optimized_route = [all_points[i] for i in best_route]
        
        return jsonify({"optimized_route": optimized_route, "best_distance": best_distance})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
