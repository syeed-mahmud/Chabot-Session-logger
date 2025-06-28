import sqlite3
import os
from typing import Optional

# Database configuration - using SQLite for better compatibility
DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'chatbot.db')

def get_db_connection():
    """Get SQLite database connection"""
    try:
        connection = sqlite3.connect(DB_PATH)
        connection.row_factory = sqlite3.Row  # Enable column access by name
        return connection
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def init_database():
    """Initialize SQLite database and create tables"""
    try:
        connection = sqlite3.connect(DB_PATH)
        cursor = connection.cursor()
        
        # Create sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create chat_messages table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS chat_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES chat_sessions(session_id)
            )
        """)
        
        connection.commit()
        cursor.close()
        connection.close()
        
        print("Database initialized successfully!")
        return True
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        return False 