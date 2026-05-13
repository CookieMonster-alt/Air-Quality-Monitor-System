import random
import datetime
from data_manager import DatabaseManager, CityRecord

CITIES = [
    "London", "Paris", "New York", "Tokyo", "Berlin",
    "Madrid", "Rome", "Beijing", "Sydney", "Moscow",
    "Istanbul", "Dubai", "Mumbai", "Singapore", "Hong Kong",
    "Toronto", "Los Angeles", "Chicago", "Sao Paulo", "Mexico City",
    "Seoul", "Jakarta", "Bangkok", "Kuala Lumpur", "Manila",
    "Cairo", "Delhi", "Shanghai", "Taipei", "Osaka",
    "Amsterdam", "Vienna", "Brussels", "Stockholm", "Copenhagen",
    "Oslo", "Helsinki", "Warsaw", "Prague", "Budapest",
    "Athens", "Lisbon", "Dublin", "Buenos Aires", "Rio de Janeiro",
    "Santiago", "Lima", "Bogota", "Caracas", "Johannesburg"
]

def generate_mock_data():
    db = DatabaseManager()
    now = datetime.datetime.now()

    print("Generating mock data...")
    for city in CITIES:
        # Generate random AQI between 0 and 500
        aqi = round(random.uniform(0.0, 500.0), 1)

        # Generate random date within the last 30 days
        days_ago = random.randint(0, 30)
        hours_ago = random.randint(0, 23)
        minutes_ago = random.randint(0, 59)

        past_date = now - datetime.timedelta(days=days_ago, hours=hours_ago, minutes=minutes_ago)
        timestamp = past_date.isoformat(" ", "minutes")

        record = CityRecord(city_name=city, aqi_value=aqi, timestamp=timestamp)
        db.add_record(record)

    print("Successfully generated and inserted 50 mock records into the database.")

if __name__ == "__main__":
    generate_mock_data()
