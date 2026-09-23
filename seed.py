from database import get_connection
from models import create_tables

def seed_data():
    create_tables()
    conn = get_connection()
    cursor = conn.cursor()

    # Clear existing data (safe to rerun)
    cursor.execute("DELETE FROM rentals")
    cursor.execute("DELETE FROM bikes")
    cursor.execute("DELETE FROM stations")

    stations = [
        (1, "Central Park", 20),
        (2, "Riverside", 15),
        (3, "Old Town Square", 25),
        (4, "University Gate", 18),
        (5, "Harbor View", 12),
    ]
    cursor.executemany(
        "INSERT INTO stations (id, name, capacity) VALUES (?, ?, ?)", stations
    )

    bikes = [
        (1, 1, "available"), (2, 1, "available"), (3, 1, "available"),
        (4, 2, "available"), (5, 2, "available"),
        (6, 3, "available"), (7, 3, "available"), (8, 3, "available"),
        (9, 4, "available"), (10, 4, "available"),
        (11, 5, "available"), (12, 5, "available"),
    ]
    cursor.executemany(
        "INSERT INTO bikes (id, station_id, status) VALUES (?, ?, ?)", bikes
    )

    conn.commit()
    conn.close()
    print("Seed data loaded.")

if __name__ == "__main__":
    seed_data()