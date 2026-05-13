import sqlite3
import json
import datetime
from dataclasses import dataclass, asdict
from typing import List

# ANSI Color Codes for EPA
GREEN = "\033[32m"
YELLOW = "\033[33m"
LIGHT_RED = "\033[91m"
RED = "\033[31m"
MAGENTA = "\033[35m"
BOLD_RED = "\033[1m\033[31m"
RESET = "\033[0m"

def get_epa_category(aqi_value: float) -> str:
    if aqi_value <= 50:
        return f"{GREEN}Good{RESET}"
    elif aqi_value <= 100:
        return f"{YELLOW}Moderate{RESET}"
    elif aqi_value <= 150:
        return f"{LIGHT_RED}Unhealthy for Sensitive Groups{RESET}"
    elif aqi_value <= 200:
        return f"{RED}Unhealthy{RESET}"
    elif aqi_value <= 300:
        return f"{MAGENTA}Very Unhealthy{RESET}"
    else:
        return f"{BOLD_RED}Hazardous{RESET}"

@dataclass
class CityRecord:
    city_name: str
    aqi_value: float
    timestamp: str

class DatabaseManager:
    def __init__(self, db_name="aqi_data.db"):
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name, check_same_thread=False)
        self._init_db()

    def _init_db(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                city_name TEXT NOT NULL,
                aqi_value REAL NOT NULL,
                timestamp TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                city_name TEXT NOT NULL,
                predicted_aqi REAL NOT NULL,
                prediction_date TEXT NOT NULL,
                target_date TEXT NOT NULL,
                decision_made TEXT NOT NULL
            )
        """)
        self.conn.commit()

    def add_prediction(self, city_name: str, predicted_aqi: float, prediction_date: str, target_date: str, decision_made: str):
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO predictions (city_name, predicted_aqi, prediction_date, target_date, decision_made) VALUES (?, ?, ?, ?, ?)",
            (city_name, predicted_aqi, prediction_date, target_date, decision_made)
        )
        self.conn.commit()

    def add_record(self, record: CityRecord):
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO records (city_name, aqi_value, timestamp) VALUES (?, ?, ?)",
            (record.city_name, record.aqi_value, record.timestamp)
        )
        self.conn.commit()

    def get_all_records(self) -> List[CityRecord]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT city_name, aqi_value, timestamp FROM records")
        rows = cursor.fetchall()
        return [CityRecord(city_name=row[0], aqi_value=row[1], timestamp=row[2]) for row in rows]

    def get_average_aqi(self) -> float:
        cursor = self.conn.cursor()
        cursor.execute("SELECT AVG(aqi_value) FROM records")
        result = cursor.fetchone()[0]
        if result is None:
            return 0.0
        return float(result)

    def get_city_with_highest_aqi(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT city_name, aqi_value FROM records ORDER BY aqi_value DESC LIMIT 1")
        result = cursor.fetchone()
        return result

    def export_to_json(self) -> str:
        records = self.get_all_records()
        records_dict = [asdict(record) for record in records]
        timestamp_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"aqi_export_{timestamp_str}.json"
        with open(filename, "w") as json_file:
            json.dump(records_dict, json_file, indent=4)
        return filename
