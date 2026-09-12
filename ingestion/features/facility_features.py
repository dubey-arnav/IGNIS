import sys
import os
import pandas as pd
from sqlalchemy import text

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from database.db_connect import engine

RADIUS_METERS = 5000

query = text("""
    SELECT
        te.id AS event_id,
        MIN(ST_Distance(te.geom::geography, isite.geom::geography)) AS nearest_facility_distance_m,
        COUNT(isite.id) AS facilities_within_radius,
        (ARRAY_AGG(isite.type ORDER BY ST_Distance(te.geom::geography, isite.geom::geography)))[1]
            AS nearest_facility_type
    FROM thermal_events te
    LEFT JOIN industrial_sites isite
        ON ST_DWithin(te.geom::geography, isite.geom::geography, :radius)
    GROUP BY te.id
""")

with engine.connect() as conn:
    df = pd.read_sql(query, conn, params={"radius": RADIUS_METERS})

print(f"Computed facility features for {len(df)} events")
print(df.head())

os.makedirs("data", exist_ok=True)
df.to_csv("data/facility_features.csv", index=False)
print("Saved data/facility_features.csv")