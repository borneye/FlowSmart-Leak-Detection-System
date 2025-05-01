# database.py
import sqlite3
from pathlib import Path
import streamlit as st
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(
    filename='db.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

DB_PATH = Path(__file__).parent / "data/users.db"

def get_db_connection():
    """Create and return a database connection"""
    try:
        # Ensure directory exists
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(DB_PATH)
        conn.execute("PRAGMA foreign_keys = ON")
        logging.info(f"Database connection established at {DB_PATH}")
        return conn
    except Exception as e:
        logging.error(f"Connection failed: {str(e)}")
        st.error("Database connection error")
        raise

def init_db():
    """Initialize database tables"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Users table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Password reset table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS password_reset (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token TEXT UNIQUE NOT NULL,
            expires_at TIMESTAMP NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
        """)
        
        conn.commit()
        logging.info("Database tables initialized")
        return True
        
    except Exception as e:
        logging.error(f"Initialization failed: {str(e)}")
        st.error("Database initialization error")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

def verify_db():
    """Verify database structure"""
    required_tables = ['users', 'password_reset']
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        existing_tables = [table[0] for table in cursor.fetchall()]
        
        missing_tables = [t for t in required_tables if t not in existing_tables]
        if missing_tables:
            logging.warning(f"Missing tables: {missing_tables}")
            return False
            
        return True
    except Exception as e:
        logging.error(f"Verification failed: {str(e)}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()