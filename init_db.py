import sqlite3
from pathlib import Path

# Define database path
DB_FOLDER = Path("data")
DB_PATH = DB_FOLDER / "users.db"

def initialize_database():
    """Create the user and sensor data tables in the database."""
    DB_FOLDER.mkdir(parents=True, exist_ok=True)  # Ensure the data folder exists

    with sqlite3.connect(DB_PATH) as conn:
        # Create the users table if it doesn't exist
        conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('Administrator', 'Maintenance', 'User'))
        )""")
        
        # Create the sensor data table if it doesn't exist
        conn.execute("""
        CREATE TABLE IF NOT EXISTS sensor_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            pressure INTEGER NOT NULL,
            flow INTEGER NOT NULL,
            leak_status TEXT NOT NULL CHECK(leak_status IN ('No Leak', 'Leak Detected'))
        )""")
        conn.commit()

# Run the function when the script is executed
if __name__ == "__main__":
    initialize_database()
    print("Database initialized successfully.")
