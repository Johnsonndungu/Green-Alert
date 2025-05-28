import requests
import os

# Set your Google AI Studio API key
GOOGLE_AI_API_KEY = "your_google_ai_api_key"
GOOGLE_AI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"

def get_recommendations_from_google_ai(weather_data):
    """
    Send weather data to Google AI Studio API and receive recommendations for each unique location.

    Args:
        weather_data (dict): A dictionary with locations as keys and their respective weather forecasts as values.

    Returns:
        dict: A dictionary with locations as keys and their respective recommendations as values.
    """
    recommendations = {}

    for location, forecast in weather_data.items():
        prompt = f"Based on the following weather forecast for {location}, provide recommendations for activities, precautions, or alerts:\n{forecast}"

        headers = {
            "Content-Type": "application/json"
        }
        params = {
            "key": GOOGLE_AI_API_KEY
        }
        data = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt}
                    ]
                }
            ]
        }

        try:
            response = requests.post(GOOGLE_AI_API_URL, headers=headers, params=params, json=data)
            if response.status_code == 200:
                result = response.json()
                # Extract the generated text from the response
                recommendation = result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                recommendations[location] = recommendation.strip()
            else:
                print(f"Failed to get recommendations for {location}. Status code: {response.status_code}")
        except Exception as e:
            print(f"Failed to get recommendations for {location}. Error: {e}")

    return recommendations