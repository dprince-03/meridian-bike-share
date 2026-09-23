# Meridian Bike Share API

A REST API and admin dashboard for Meridian Bike Share, a fictional public
cycle-hire operator with docking stations, bikes, and rentals. Built for
the Adeptbloc Software/Web Development Team Case Study, Phase 1.

## Team
- Adedayo Adejare
- Iboro Sampson
- Chinonso Ejiaku

## Tech Stack
- **Python 3** with **FastAPI** for the REST API
- **SQLite** for the relational database
- **Uvicorn** as the ASGI server
- Plain HTML/CSS/JavaScript for the admin page (no framework)

## Project Structure
```
meridian-bike-share/
├── main.py            # FastAPI app and route definitions
├── database.py        # SQLite connection helper
├── models.py          # Table creation (schema)
├── seed.py            # Loads sample data into the database
├── static/
│   └── index.html     # One-page admin view
├── requirements.txt
└── README.md
```

## Setup and Running Locally

This project requires no manual installation if run in GitHub Codespaces
(recommended). Steps below work identically in Codespaces or any Python 3
environment.

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Create tables and load seed data**
   ```bash
   python seed.py
   ```

3. **Start the server**
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```

4. **Open the API**
   - Interactive API docs (Swagger UI): `/docs`
   - Admin page: `/static/index.html`

In GitHub Codespaces, the forwarded port URL is generated automatically
and shown in the "Ports" tab.

## Data Model

Three tables model the core relationships of the system:

### `stations`
| Column     | Type    | Notes            |
|------------|---------|------------------|
| id         | INTEGER | Primary key      |
| name       | TEXT    | Station name     |
| capacity   | INTEGER | Max bike docks   |

### `bikes`
| Column      | Type    | Notes                                  |
|-------------|---------|-----------------------------------------|
| id          | INTEGER | Primary key                            |
| station_id  | INTEGER | Foreign key -> stations.id             |
| status      | TEXT    | `available` or `out`                   |

A bike belongs to exactly one station at any given time.

### `rentals`
| Column            | Type    | Notes                                   |
|-------------------|---------|-------------------------------------------|
| id                | INTEGER | Primary key                             |
| bike_id           | INTEGER | Foreign key -> bikes.id                 |
| start_station_id  | INTEGER | Foreign key -> stations.id              |
| end_station_id    | INTEGER | Foreign key -> stations.id (nullable)   |
| start_time        | TEXT    | ISO timestamp                           |
| end_time          | TEXT    | ISO timestamp (nullable until returned) |

A rental links one bike to a start station, an end station, and two
timestamps, so the full round trip of a bike can be reconstructed from
this table alone.

## API Endpoints

| Method | Route                          | Description                                      |
|--------|---------------------------------|---------------------------------------------------|
| GET    | `/stations`                    | List every station with its free-bike count       |
| GET    | `/stations/{id}/bikes`         | List bikes docked at one station                  |
| POST   | `/rentals`                     | Start a rental (`bike_id`, `start_station_id`)     |
| PATCH  | `/rentals/{id}/return`         | End a rental, re-dock the bike (`end_station_id`)  |
| GET    | `/reports/busiest-stations`    | Top 5 stations by rentals started                  |

### Status codes
- `404` if a referenced bike or rental does not exist
- `409` if a bike is already rented out and a new rental is attempted, or
  if a rental has already been returned

All endpoints can be tested interactively at `/docs`.

## Admin Page

`static/index.html` is a plain HTML/CSS/JavaScript page that calls
`GET /stations` on this same API and renders each station's name and
free-bike count. It requires no build step and no external framework.

## Notes on Seed Data

The case brief references seed data "printed on the case slides that
follow," which was not present in the materials we received. We flagged
this with the organizers. In the meantime, this project uses a small,
proportionally reasonable placeholder dataset (5 stations, 12 bikes) so
the API and admin page can be fully built and demonstrated. Data can be
swapped by editing `seed.py`.