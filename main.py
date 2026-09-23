from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from datetime import datetime, timezone
from pathlib import Path
from database import get_connection
from models import create_tables

# Find the static folder next to this file, no matter where the server is started from.
STATIC_DIR = Path(__file__).parent / "static"

app = FastAPI(title="Meridian Bike Share API")
app.mount("/static", StaticFiles(directory=STATIC_DIR, html=True), name="static")

create_tables()

def now():
    return datetime.now(timezone.utc).isoformat()

@app.get("/stations")
def get_stations():
    conn = get_connection()
    rows = conn.execute("""
        SELECT s.id, s.name, s.capacity, COUNT(b.id) AS free_bikes
        FROM stations s
        LEFT JOIN bikes b ON b.station_id = s.id AND b.status = 'available'
        GROUP BY s.id
        ORDER BY s.id
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]

@app.get("/stations/{station_id}/bikes")
def get_station_bikes(station_id: int):
    conn = get_connection()
    station = conn.execute("SELECT id FROM stations WHERE id = ?", (station_id,)).fetchone()
    if not station:
        conn.close()
        raise HTTPException(status_code=404, detail="Station not found")
    bikes = conn.execute("SELECT * FROM bikes WHERE station_id = ?", (station_id,)).fetchall()
    conn.close()
    return [dict(b) for b in bikes]

@app.get("/rentals")
def get_rentals():
    conn = get_connection()
    rentals = conn.execute("SELECT * FROM rentals ORDER BY id DESC").fetchall()
    conn.close()
    return [dict(r) for r in rentals]

@app.post("/rentals")
def start_rental(bike_id: int, start_station_id: int):
    conn = get_connection()
    bike = conn.execute("SELECT * FROM bikes WHERE id = ?", (bike_id,)).fetchone()
    if not bike:
        conn.close()
        raise HTTPException(status_code=404, detail="Bike not found")

    station = conn.execute("SELECT id FROM stations WHERE id = ?", (start_station_id,)).fetchone()
    if not station:
        conn.close()
        raise HTTPException(status_code=404, detail="Station not found")

    if bike["status"] != "available":
        conn.close()
        raise HTTPException(status_code=409, detail="Bike already out")

    # The rider must take the bike from the station it is actually docked at.
    if bike["station_id"] != start_station_id:
        conn.close()
        raise HTTPException(status_code=409, detail="Bike is not docked at this station")

    cursor = conn.cursor()
    # Only mark the bike as out if it is still available. Doing the check inside the
    # UPDATE means two people can't rent the same bike at the same moment.
    cursor.execute("UPDATE bikes SET status = 'out' WHERE id = ? AND status = 'available'", (bike_id,))
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=409, detail="Bike already out")

    cursor.execute(
        "INSERT INTO rentals (bike_id, start_station_id, start_time) VALUES (?, ?, ?)",
        (bike_id, start_station_id, now())
    )
    conn.commit()
    rental_id = cursor.lastrowid
    conn.close()
    return {"rental_id": rental_id, "bike_id": bike_id, "start_station_id": start_station_id, "status": "started"}

@app.patch("/rentals/{rental_id}/return")
def return_rental(rental_id: int, end_station_id: int):
    conn = get_connection()
    rental = conn.execute("SELECT * FROM rentals WHERE id = ?", (rental_id,)).fetchone()
    if not rental:
        conn.close()
        raise HTTPException(status_code=404, detail="Rental not found")
    if rental["end_time"]:
        conn.close()
        raise HTTPException(status_code=409, detail="Rental already returned")

    station = conn.execute("SELECT * FROM stations WHERE id = ?", (end_station_id,)).fetchone()
    if not station:
        conn.close()
        raise HTTPException(status_code=404, detail="Station not found")

    docked = conn.execute(
        "SELECT COUNT(*) FROM bikes WHERE station_id = ? AND status = 'available'",
        (end_station_id,)
    ).fetchone()[0]
    if docked >= station["capacity"]:
        conn.close()
        raise HTTPException(status_code=409, detail="Station is full")

    cursor = conn.cursor()
    # Only close the rental if it is still open (same idea as in start_rental).
    cursor.execute(
        "UPDATE rentals SET end_station_id = ?, end_time = ? WHERE id = ? AND end_time IS NULL",
        (end_station_id, now(), rental_id)
    )
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=409, detail="Rental already returned")

    cursor.execute("UPDATE bikes SET status = 'available', station_id = ? WHERE id = ?",
                    (end_station_id, rental["bike_id"]))
    conn.commit()
    conn.close()
    return {"rental_id": rental_id, "status": "returned"}

@app.get("/reports/busiest-stations")
def busiest_stations():
    conn = get_connection()
    rows = conn.execute("""
        SELECT s.id, s.name, COUNT(r.id) as rental_count
        FROM stations s
        LEFT JOIN rentals r ON r.start_station_id = s.id
        GROUP BY s.id
        ORDER BY rental_count DESC
        LIMIT 5
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]

@app.get("/")
def root():
    # Send visitors straight to the dashboard.
    return RedirectResponse("/static/")
