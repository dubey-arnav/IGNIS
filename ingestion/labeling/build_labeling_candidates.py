import sys
import os
import pandas as pd
from sqlalchemy import text

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from database.db_connect import engine

# For each cluster, find the nearest industrial facility (if any within 5km)
query = text("""
    SELECT
        fc.id AS cluster_id,
        ST_X(fc.geom) AS longitude,
        ST_Y(fc.geom) AS latitude,
        fc.first_detection,
        fc.last_detection,
        fc.total_detections,
        fc.active_days,
        fc.mean_frp,
        fc.max_frp,
        fc.persistence_score,
        isite.name AS nearest_facility_name,
        isite.type AS nearest_facility_type,
        MIN(ST_Distance(fc.geom::geography, isite.geom::geography)) AS distance_to_facility_m
    FROM fire_clusters fc
    LEFT JOIN industrial_sites isite
        ON ST_DWithin(fc.geom::geography, isite.geom::geography, 5000)
    GROUP BY fc.id, fc.geom, fc.first_detection, fc.last_detection,
            fc.total_detections, fc.active_days, fc.mean_frp, fc.max_frp,
            fc.persistence_score, isite.name, isite.type
    ORDER BY fc.persistence_score DESC
""")

with engine.connect() as conn:
    df = pd.read_sql(query, conn)

# Add an empty column for a human to fill in
df["suggested_label"] = ""
df["label_reasoning"] = ""

os.makedirs("data", exist_ok=True)
df.to_csv("data/labeling_candidates.csv", index=False)
print(f"Saved {len(df)} clusters to data/labeling_candidates.csv for manual review")