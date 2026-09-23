# Meridian Bike Share API

A REST API and admin dashboard for Meridian Bike Share, a fictional public
cycle-hire operator with docking stations, bikes, and rentals. Built for
the Adeptbloc Software/Web Development Team Case Study, Phase 1.

## Team A

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
│   └── index.html     # Admin dashboard
├── requirements.txt
└── README.md
```

## Setup and Running Locally

The steps below work the same in GitHub Codespaces (recommended) or any
Python 3 environment.

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
4. **Open the app**

   - Admin dashboard: `/` (redirects to `/static/`)
   - Interactive API docs (Swagger UI): `/docs`

`python seed.py` resets all data, so run it again whenever you want a fresh start.

In GitHub Codespaces, the forwarded port URL is generated automatically
and shown in the "Ports" tab.

## Data Model

Three tables model the core relationships of the system:

### `stations`

| Column   | Type    | Notes          |
| -------- | ------- | -------------- |
| id       | INTEGER | Primary key    |
| name     | TEXT    | Station name   |
| capacity | INTEGER | Max bike docks |

### `bikes`

| Column     | Type    | Notes                      |
| ---------- | ------- | -------------------------- |
| id         | INTEGER | Primary key                |
| station_id | INTEGER | Foreign key -> stations.id |
| status     | TEXT    | `available` or `out`   |

A docked bike belongs to exactly one station. While a bike is out, its
`station_id` still points to the station it left from until it is returned.

### `rentals`

| Column           | Type    | Notes                                   |
| ---------------- | ------- | --------------------------------------- |
| id               | INTEGER | Primary key                             |
| bike_id          | INTEGER | Foreign key -> bikes.id                 |
| start_station_id | INTEGER | Foreign key -> stations.id              |
| end_station_id   | INTEGER | Foreign key -> stations.id (nullable)   |
| start_time       | TEXT    | ISO timestamp                           |
| end_time         | TEXT    | ISO timestamp (nullable until returned) |

A rental links one bike to a start station, an end station, and two
timestamps, so the full round trip of a bike can be reconstructed from
this table alone.

## API Endpoints

| Method | Route                       | Description                                         |
| ------ | --------------------------- | --------------------------------------------------- |
| GET    | `/stations`                 | List every station with its free-bike count         |
| GET    | `/stations/{id}/bikes`      | List bikes at one station                           |
| GET    | `/rentals`                  | List all rentals, newest first                      |
| POST   | `/rentals`                  | Start a rental (`bike_id`, `start_station_id`)      |
| PATCH  | `/rentals/{id}/return`      | End a rental, re-dock the bike (`end_station_id`)   |
| GET    | `/reports/busiest-stations` | Top 5 stations by rentals started                   |

Parameters are passed as query strings, e.g.
`POST /rentals?bike_id=3&start_station_id=1`. The API checks that the bike
is actually docked at `start_station_id` before starting the rental.

### Status codes

- `404` if a referenced bike, rental or station does not exist
- `409` if a bike is already rented out, the bike is not docked at the
  given start station, a rental has already been returned, or the return
  station is full

All endpoints can be tested interactively at `/docs`.

## Admin Page

`static/index.html` is a plain HTML/CSS/JavaScript dashboard that calls
this same API. It shows:

- totals for stations, free bikes, bikes out and rentals
- each station's free bikes against its capacity (click a station to see
  and rent its bikes)
- bikes currently out, with a button to return each one to a station
- the busiest stations and the 10 most recent rentals

It refreshes every 15 seconds, follows the system's light or dark mode,
and needs no build step or framework.

## Notes on Seed Data

The case brief references seed data "printed on the case slides that
follow," which was not present in the materials we received. We flagged
this with the organizers. In the meantime, this project uses a small,
proportionally reasonable placeholder dataset (5 stations, 12 bikes) so
the API and admin page can be fully built and demonstrated. Data can be
swapped by editing `seed.py`.
