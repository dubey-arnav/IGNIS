import sys
import os
import pandas as pd
from sqlalchemy import text

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from database.db_connect import engine

RADIUS_METERS = 5000

# Step 1: get every event id (so events with zero nearby facilities aren't lost)
with engine.connect() as conn:
    all_events = pd.read_sql(text("SELECT id AS event_id FROM thermal_events"), conn)

print(f"Total events: {len(all_events)}")

# Step 2: ONE spatial join query for every event-facility pair within radius (fast — single indexed join)
pair_query = text("""
    SELECT
        te.id AS event_id,
        isite.type AS facility_type,
        ST_Distance(te.geom::geography, isite.geom::geography) AS distance_m
    FROM thermal_events te
    JOIN industrial_sites isite
        ON ST_DWithin(te.geom, isite.geom, 0.06)
        AND ST_DWithin(te.geom::geography, isite.geom::geography, :radius)
""")

with engine.connect() as conn:
    pairs = pd.read_sql(pair_query, conn, params={"radius": RADIUS_METERS})

print(f"Event-facility pairs found: {len(pairs)}")

# Step 3: collapse to one row per event — nearest distance, count, nearest type
if len(pairs) > 0:
    pairs_sorted = pairs.sort_values("distance_m")
    nearest = pairs_sorted.drop_duplicates(subset="event_id", keep="first")
    nearest = nearest.rename(columns={"distance_m": "nearest_facility_distance_m",
                                       "facility_type": "nearest_facility_type"})
    counts = pairs.groupby("event_id").size().reset_index(name="facilities_within_radius")

    result = all_events.merge(nearest[["event_id", "nearest_facility_distance_m", "nearest_facility_type"]],
                               on="event_id", how="left")
    result = result.merge(counts, on="event_id", how="left")
    result["facilities_within_radius"] = result["facilities_within_radius"].fillna(0).astype(int)
else:
    result = all_events.copy()
    result["nearest_facility_distance_m"] = None
    result["nearest_facility_type"] = None
    result["facilities_within_radius"] = 0

print(f"Computed facility features for {len(result)} events")
print(result.head())

os.makedirs("data", exist_ok=True)
result.to_csv("data/facility_features.csv", index=False)
print("Saved data/facility_features.csv")