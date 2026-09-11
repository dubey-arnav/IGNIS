import sys
import os
from sqlalchemy import text
import pandas as pd

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from database.db_connect import engine

RADIUS_METERS = 5000  # adjust based on how "nearby" should be defined for this project

match_sql = text("""
    SELECT
        te.id AS event_id,
        isite.id AS site_id,
        isite.name AS site_name,
        isite.type AS site_type,
        ST_Distance(te.geom::geography, isite.geom::geography) AS distance_meters
    FROM thermal_events te
    JOIN industrial_sites isite
        ON ST_DWithin(te.geom::geography, isite.geom::geography, :radius)
    ORDER BY te.id, distance_meters
""")

with engine.connect() as conn:
    result = conn.execute(match_sql, {"radius": RADIUS_METERS})
    df = pd.DataFrame(result.fetchall(), columns=result.keys())

print(f"Found {len(df)} event-facility matches within {RADIUS_METERS} meters")
print(df.head(10))

os.makedirs("data", exist_ok=True)
df.to_csv("data/event_facility_matches.csv", index=False)
print("Saved data/event_facility_matches.csv")
