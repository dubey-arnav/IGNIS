# IGNIS Backend

FastAPI backend for the IGNIS industrial thermal anomaly classification system.

## Setup

1. Install dependencies:
2. Configure environment variables. Copy the example file to the project root:   Then edit `.env` and fill in your actual `DB_PASSWORD`.

3. Run the server:
4. Open the interactive docs: http://127.0.0.1:8000/docs

## Endpoints

| Endpoint | Purpose |
|---|---|
| GET /api/health | Server and database status |
| GET /api/classifications | The 5 classification categories with counts |
| GET /api/events | Paginated, filterable event list |
| GET /api/events/{id} | Full event detail with cluster + nearby facilities |
| GET /api/map-data | GeoJSON for the Leaflet map |
| GET /api/dashboard-summary | Headline dashboard numbers |
| GET /api/analytics/timeline | Daily detection counts by class |
| GET /api/analytics/by-facility-type | Industrial events by facility type |
| GET /api/analytics/distance-profile | Class distribution by distance to facility |
| GET /api/facilities | Facilities, filterable by bbox/type/name |
| GET /api/facilities/types | Ranked facility type counts |
| GET /api/facilities/{id} | Facility detail with nearby events |
| GET /api/alerts | Recent Industrial Fire / Persistent events |
| GET /api/model-info | ML model status and feature list |
| POST /api/predict | Live classification of a new detection |

## Model accuracy note

The trained model reports 98.6% test accuracy. This reflects consistency with
the rule-based labels used to generate ground truth, not independent
validation against unseen fire patterns. See the ML handoff report, Part 17.6,
for the full explanation.