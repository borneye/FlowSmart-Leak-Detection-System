import sqlite3

DB_PATH = "data/users.db"  # Make sure the path is correct

# Connect to the database
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Check if 'role' column exists
cursor.execute("PRAGMA table_info(users);")
columns = [col[1] for col in cursor.fetchall()]

if "role" not in columns:
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN role TEXT NOT NULL DEFAULT 'User';")
        conn.commit()
        print("✅ Column 'role' added successfully!")
    except sqlite3.OperationalError as e:
        print(f"❌ Error: {e}")
else:
    print("ℹ️ Column 'role' already exists.")

# Close connection
conn.close()
