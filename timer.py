import time
from datetime import datetime
from services import get_unique_locations, get_weather_forecast
from model import get_recommendations_from_google_ai
from notifications import send_recommendations

def send_daily_alerts():
    # 1. Get unique locations from the database
    unique_locations = get_unique_locations()
    if not unique_locations:
        print("No locations found.")
        return

    # 2. Get weather forecast for each location
    weather_data = get_weather_forecast(unique_locations)
    if not weather_data:
        print("No weather data found.")
        return

    # 3. Get recommendations from Gemini AI
    recommendations = get_recommendations_from_google_ai(weather_data)
    if not recommendations:
        print("No recommendations generated.")
        return

    # 4. Send recommendations via SMS and Email
    send_recommendations(recommendations)
    print(f"Sent recommendations to users at {datetime.now()}.")

def run_daily_scheduler(hour=7, minute=0):
    """Run the send_daily_alerts function every day at the specified hour and minute."""
    print(f"Scheduler started. Will send alerts daily at {hour:02d}:{minute:02d}.")
    while True:
        now = datetime.now()
        if now.hour == hour and now.minute == minute:
            send_daily_alerts()
            # Sleep for 61 seconds to avoid running multiple times in the same minute
            time.sleep(61)
        else:
            # Sleep for 30 seconds before checking again
            time.sleep(30)

if __name__ == "__main__":
    run_daily_scheduler(hour=0, minute=2)  # Sends alerts every day at 7:00 AM