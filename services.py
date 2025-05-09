import mysql.connector
from collections import Counter
import requests
from app import create_db_connection


weather_api_url = "https://api.openweathermap.org/data/2.5/forecast"  
api_key = "your_api_key"  


def get_unique_locations():
    """
    Fetch unique user locations from the MySQL database. If a location is shared by 10 or more users,
    it will only be queried once for weather data.

    Returns:
        list: A list of unique locations to query for weather data.
    """
    # Connect to the MySQL database
    connection = create_db_connection()
    if not connection:
        print("Failed to connect to the database.")
        return []

    try:
        cursor = connection.cursor()
        # Query to fetch all user locations
        cursor.execute("SELECT location FROM users")  
        user_locations = cursor.fetchall()

        # Flatten the list of tuples into a list of locations
        locations = [location[0] for location in user_locations]

        # Count occurrences of each location
        location_counts = Counter(locations)

        # Filter unique locations (only one query per location if shared by 1 or more users)
        unique_locations = [location for location, count in location_counts.items() if count >= 10]

        return unique_locations

    finally:
        # Close the database connection
        connection.close()


def get_weather_forecast(unique_locations):
    """
    Send unique locations to a weather API and get a one-week weather forecast for each location.

    Args:
        unique_locations (list): List of unique locations.

    Returns:
        dict: A dictionary with locations as keys and their respective weather forecasts as values.
    """

    weather_data = {}

    for location in unique_locations:
        params = {
            "q": location,
            "appid": api_key,
            "units": "metric",  
            "cnt": 7  
        }

        response = requests.get(weather_api_url, params=params)

        if response.status_code == 200:
            weather_data[location] = response.json()
        else:
            print(f"Failed to fetch weather data for {location}. Status code: {response.status_code}")

    return weather_data

