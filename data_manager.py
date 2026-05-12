import sqlite3
import json
from dataclasses import dataclass, asdict
from typing import List

@dataclass
class CityRecord:
    city_name: str
    aqi_value: int
    timestamp: str

class DatabaseManager:
    def __init__(self, db_name="aqi_data.db"):
        self.db_name = db_name
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    city_name TEXT NOT NULL,
                    aqi_value INTEGER NOT NULL,
                    timestamp TEXT NOT NULL
                )
            """)
            conn.commit()

    def add_record(self, record: CityRecord):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO records (city_name, aqi_value, timestamp) VALUES (?, ?, ?)",
                (record.city_name, record.aqi_value, record.timestamp)
            )
            conn.commit()

    def get_all_records(self) -> List[CityRecord]:
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT city_name, aqi_value, timestamp FROM records")
            rows = cursor.fetchall()
            return [CityRecord(city_name=row[0], aqi_value=row[1], timestamp=row[2]) for row in rows]

    def export_to_json(self) -> str:
        records = self.get_all_records()
        records_dict = [asdict(record) for record in records]
        return json.dumps(records_dict, indent=4)
