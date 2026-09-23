import sqlite3
from pathlib import Path

# Keep the database next to this file, no matter which folder the server is started from.
DB_NAME = Path(__file__).parent / "meridian.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    # SQLite ignores FOREIGN KEY rules unless this is turned on for each connection.
    conn.execute("PRAGMA foreign_keys = ON")
    return conn
