import openai  

# Set OpenAI API key
openai.api_key = "your_openai_api_key"  

def get_recommendations_from_openai(weather_data):
    """
    Send weather data to OpenAI API and receive recommendations for each unique location.

    Args:
        weather_data (dict): A dictionary with locations as keys and their respective weather forecasts as values.

    Returns:
        dict: A dictionary with locations as keys and their respective recommendations as values.
    """
    recommendations = {}

    for location, forecast in weather_data.items():
        # prompt for OpenAI
        prompt = f"""
        Based on the following weather forecast for {location}, provide recommendations for activities, precautions, or alerts:
        {forecast}
        """

        try:
            # Send the prompt to OpenAI API
            response = openai.Completion.create(
                engine="text-davinci-003",  # Use the appropriate engine
                prompt=prompt,
                max_tokens=150
            )

            # Extract the recommendation from the response
            recommendations[location] = response.choices[0].text.strip()

        except Exception as e:
            print(f"Failed to get recommendations for {location}. Error: {e}")

    return recommendations