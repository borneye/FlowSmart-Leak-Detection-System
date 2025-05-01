import random
import sqlite3
from pathlib import Path
import time

DB_FOLDER = Path("data")
DB_FOLDER.mkdir(parents=True, exist_ok=True)
DB_PATH = DB_FOLDER / "users.db"

def initialize_sensor_database():
    """Creates the sensor_data table if it doesn't exist."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS sensor_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            pressure REAL NOT NULL,
            flow REAL NOT NULL,
            leak_status TEXT NOT NULL
        )""")
        conn.commit()

def insert_sensor_data(pressure, flow, leak_status):
    """Inserts a new sensor data record into the database."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
        INSERT INTO sensor_data (pressure, flow, leak_status)
        VALUES (?, ?, ?)
        """, (pressure, flow, leak_status))
        conn.commit()

def get_latest_sensor_data():
    """Fetches the most recent sensor data entry."""
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("""
        SELECT timestamp, pressure, flow, leak_status FROM sensor_data
        ORDER BY timestamp DESC LIMIT 1
        """)
        result = cur.fetchone()
        if result:
            return result
        else:
            return ("No Data", 0.0, 0.0, "No Leak")

def check_leak_resolution():
    """Checks if the leak is resolved (i.e., no leak detected in the latest readings)."""
    timestamp, pressure, flow, leak_status = get_latest_sensor_data()
    
    # Here, consider a resolved leak if the status is "No Leak Detected" and 
    # readings are within acceptable range
    if leak_status == "No Leak Detected" and pressure >= 45.0 and flow <= 10.0:
        return True  # Leak resolved
    return False  # Leak still unresolved

def generate_dummy_sensor_data():
    """Simulates realistic sensor readings with equal chances for 'Leak Detected' and 'No Leak'."""
    pressure = round(random.uniform(40.0, 100.0), 2)  # Pressure in PSI
    flow = round(random.uniform(1.0, 20.0), 2)  # Flow rate in L/min
    
    # Set the probability for leak detection to 50/50
    leak_prob = 0.5  # 50% chance of a leak, 50% chance of no leak
    leak_status = "Leak Detected" if random.random() < leak_prob else "No Leak"
    
    # Insert the generated data into the database
    insert_sensor_data(pressure, flow, leak_status)
    print(f"Inserted: Pressure={pressure}, Flow={flow}, Leak={leak_status}")

def resolve_leak():
    """Manually resolve a detected leak by maintenance."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
        UPDATE sensor_data SET leak_status = 'No Leak Detected' 
        WHERE leak_status = 'Leak Detected'
        ORDER BY timestamp DESC LIMIT 1
        """)
        conn.commit()

# Run this script to initialize the database and generate dummy data continuously
if __name__ == "__main__":
    initialize_sensor_database()
    while True:
        generate_dummy_sensor_data()  # Simulate and insert data every 10 seconds
        time.sleep(10)  # Adjust the sleep time for 10-second intervals

def get_sensor_history(limit=100):
    """Fetches historical sensor readings up to a specified limit."""
    with sqlite3.connect(DB_PATH) as conn:
        return conn.execute(
            "SELECT timestamp, pressure, flow FROM sensor_data ORDER BY timestamp DESC LIMIT ?",
            (limit,)
        ).fetchall()
