"""
Database Initialization and Connection
Handles SQLite setup for the AURA System.
"""

import sqlite3
from pathlib import Path

# Base directory of the backend
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Database file path
DB_PATH = BASE_DIR / "aura_system.db"

# Schema file path
SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"


def get_connection():
    """
    Returns a SQLite database connection.
    WAL mode enabled for concurrency safety.
    """
    
    conn = sqlite3.connect(
        DB_PATH,
        timeout=10,
        check_same_thread=False,
    )
    conn.row_factory = sqlite3.Row

    # 🔒 Enable WAL mode
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    conn.execute("PRAGMA busy_timeout=5000;")

    return conn


def initialize_database():
    """
    Creates database and tables if they do not exist.
    """
    conn = get_connection()
    cursor = conn.cursor()

    with open(SCHEMA_PATH, "r", encoding="utf-8") as schema_file:
        schema_sql = schema_file.read()
        cursor.executescript(schema_sql)

    conn.commit()
    conn.close()
