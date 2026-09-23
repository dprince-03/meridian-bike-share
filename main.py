from fastapi import FastAPI, HTTPException
from datetime import datetime
from database import get_connection
from models import create_tables
from fastapi.staticfiles import StaticFiles


app = FastAPI(title="Meridian Bike Share API")
app.mount("/static", StaticFiles(directory="static", html=True), name="static")

create_tables()

@app.get("/stations")
def get_stations():
    conn = get_connection()
    stations = conn.execute("SELECT * FROM stations").fetchall()
    result = []
    for s in stations:
        free_bikes = conn.execute(
            "SELECT COUNT(*) FROM bikes WHERE station_id = ? AND status = 'available'",
            (s["id"],)
        ).fetchone()[0]
        result.append({"id": s["id"], "name": s["name"], "capacity": s["capacity"], "free_bikes": free_bikes})
    conn.close()
    return result

@app.get("/stations/{station_id}/bikes")
def get_station_bikes(station_id: int):
    conn = get_connection()
    bikes = conn.execute("SELECT * FROM bikes WHERE station_id = ?", (station_id,)).fetchall()
    conn.close()
    return [dict(b) for b in bikes]

@app.post("/rentals")
def start_rental(bike_id: int, start_station_id: int):
    conn = get_connection()
    bike = conn.execute("SELECT * FROM bikes WHERE id = ?", (bike_id,)).fetchone()
    if not bike:
        conn.close()
        raise HTTPException(status_code=404, detail="Bike not found")
    if bike["status"] != "available":
        conn.close()
        raise HTTPException(status_code=409, detail="Bike already out")

    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO rentals (bike_id, start_station_id, start_time) VALUES (?, ?, ?)",
        (bike_id, start_station_id, datetime.utcnow().isoformat())
    )
    cursor.execute("UPDATE bikes SET status = 'out' WHERE id = ?", (bike_id,))
    conn.commit()
    rental_id = cursor.lastrowid
    conn.close()
    return {"rental_id": rental_id, "bike_id": bike_id, "status": "started"}

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

    cursor = conn.cursor()
    cursor.execute(
        "UPDATE rentals SET end_station_id = ?, end_time = ? WHERE id = ?",
        (end_station_id, datetime.utcnow().isoformat(), rental_id)
    )
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
    return {"message": "Meridian Bike Share API", "docs": "/docs"}