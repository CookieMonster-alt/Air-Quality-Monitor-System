import sqlite3
import json
import datetime
from dataclasses import dataclass, asdict
from typing import List

def get_epa_color_tag(aqi_value: float) -> str:
    if aqi_value <= 50:
        return "aqi_good"
    elif aqi_value <= 100:
        return "aqi_moderate"
    elif aqi_value <= 150:
        return "aqi_sensitive"
    elif aqi_value <= 200:
        return "aqi_unhealthy"
    elif aqi_value <= 300:
        return "aqi_very_unhealthy"
    else:
        return "aqi_hazardous"

def get_epa_color_hex(aqi_value: float) -> str:
    if aqi_value <= 50:
        return "#00E400"
    elif aqi_value <= 100:
        return "#FFFF00"
    elif aqi_value <= 150:
        return "#FF7E00"
    elif aqi_value <= 200:
        return "#FF0000"
    elif aqi_value <= 300:
        return "#8F3F97"
    else:
        return "#7E0023"

def get_epa_category_raw(aqi_value: float) -> str:
    if aqi_value <= 50:
        return "Good"
    elif aqi_value <= 100:
        return "Moderate"
    elif aqi_value <= 150:
        return "Unhealthy for Sensitive Groups"
    elif aqi_value <= 200:
        return "Unhealthy"
    elif aqi_value <= 300:
        return "Very Unhealthy"
    else:
        return "Hazardous"

def get_epa_category(aqi_value: float) -> str:
    tag = get_epa_color_tag(aqi_value)
    return f"[{tag}]{get_epa_category_raw(aqi_value)}[/]"

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

        # Migration: Clean up any existing duplicates before applying the UNIQUE index
        cursor.execute("""
            DELETE FROM records
            WHERE id NOT IN (
                SELECT MIN(id)
                FROM records
                GROUP BY city_name, timestamp
            )
        """)

        cursor.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS idx_city_date
            ON records(city_name, timestamp)
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

    def add_record(self, record: CityRecord) -> bool:
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT OR IGNORE INTO records (city_name, aqi_value, timestamp) VALUES (?, ?, ?)",
            (record.city_name, record.aqi_value, record.timestamp)
        )
        self.conn.commit()
        return cursor.rowcount > 0

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
