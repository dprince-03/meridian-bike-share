from database import get_connection

def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS stations (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        capacity INTEGER NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS bikes (
        id INTEGER PRIMARY KEY,
        station_id INTEGER NOT NULL,
        status TEXT NOT NULL DEFAULT 'available',
        FOREIGN KEY (station_id) REFERENCES stations(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS rentals (
        id INTEGER PRIMARY KEY,
        bike_id INTEGER NOT NULL,
        start_station_id INTEGER NOT NULL,
        end_station_id INTEGER,
        start_time TEXT NOT NULL,
        end_time TEXT,
        FOREIGN KEY (bike_id) REFERENCES bikes(id),
        FOREIGN KEY (start_station_id) REFERENCES stations(id),
        FOREIGN KEY (end_station_id) REFERENCES stations(id)
    )
    """)

    conn.commit()
    conn.close()