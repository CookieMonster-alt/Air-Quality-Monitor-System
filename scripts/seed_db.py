#!/usr/bin/env python3
import sqlite3
import os

DB_PATH = "data/ailo_db.sqlite"

def seed_database():
    print(f"Creating data directory if it doesn't exist...")
    os.makedirs("data", exist_ok=True)

    print(f"Connecting to {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("Dropping existing air_quality table if it exists...")
    cursor.execute("DROP TABLE IF EXISTS air_quality;")

    print("Creating air_quality table...")
    cursor.execute("""
        CREATE TABLE air_quality (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            location TEXT NOT NULL,
            aqi_level INTEGER NOT NULL,
            temperature REAL NOT NULL
        )
    """)

    print("Inserting dummy realistic data...")
    dummy_data = [
        ("2026-05-29T08:00:00", "London", 45, 15.2),
        ("2026-05-29T09:00:00", "Paris", 65, 18.5),
        ("2026-05-29T10:00:00", "Tokyo", 112, 22.1),
        ("2026-05-29T11:00:00", "New York", 38, 20.0),
        ("2026-05-29T12:00:00", "Los Angeles", 85, 25.4),
        ("2026-05-30T08:00:00", "London", 50, 14.8),
        ("2026-05-30T09:00:00", "Paris", 60, 19.0),
        ("2026-05-30T10:00:00", "Tokyo", 105, 23.0)
    ]

    cursor.executemany("""
        INSERT INTO air_quality (timestamp, location, aqi_level, temperature)
        VALUES (?, ?, ?, ?)
    """, dummy_data)

    conn.commit()
    print(f"Successfully seeded {len(dummy_data)} records.")

    conn.close()
    print("Database seeding complete!")

if __name__ == "__main__":
    seed_database()
