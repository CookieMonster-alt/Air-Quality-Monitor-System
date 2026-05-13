import sqlite3
import json
from dataclasses import dataclass, asdict
from typing import List

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

    def export_to_json(self) -> str:
        records = self.get_all_records()
        records_dict = [asdict(record) for record in records]
        return json.dumps(records_dict, indent=4)
