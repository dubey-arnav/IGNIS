import sys
import os
import pandas as pd
from sqlalchemy import text

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from database.db_connect import engine

# 1. Base thermal event data
with engine.connect() as conn:
    events = pd.read_sql(text("""
        SELECT id AS event_id, latitude, longitude, event_date, event_time,
                confidence, bright_ti4, bright_ti5, frp, daynight, cluster_id
        FROM thermal_events
    """), conn)

print(f"Base events: {len(events)}")

# 2. Facility features (Step 40b's output)
facility = pd.read_csv("data/facility_features.csv")
merged = events.merge(facility, on="event_id", how="left")

# 3. Cluster/persistence features — join via cluster_id
with engine.connect() as conn:
    clusters = pd.read_sql(text("""
        SELECT id AS cluster_id, total_detections, active_days,
                mean_frp AS cluster_mean_frp, max_frp AS cluster_max_frp,
                persistence_score
        FROM fire_clusters
    """), conn)
merged = merged.merge(clusters, on="cluster_id", how="left")

# Events with no cluster (one-off detections) get sensible defaults instead of NaN
merged["persistence_score"] = merged["persistence_score"].fillna(0)
merged["total_detections"] = merged["total_detections"].fillna(1)
merged["active_days"] = merged["active_days"].fillna(1)

# 4. Sentinel-2 features — should now genuinely exist since Steps 33-39 are done
sentinel_path = "data/sentinel_features.csv"
if os.path.exists(sentinel_path):
    sentinel = pd.read_csv(sentinel_path)
    merged = merged.merge(sentinel, on="event_id", how="left")
    print("Sentinel-2 features merged in.")
    missing_sentinel = merged["ndvi_mean"].isna().sum()
    print(f"({missing_sentinel} events have no Sentinel-2 data — likely cloud cover or not yet processed)")
else:
    for col in ["ndvi_mean", "ndbi_mean", "ndwi_mean", "swir1_mean", "swir2_mean"]:
        merged[col] = None
    print("WARNING: data/sentinel_features.csv not found — check Step 39 ran with the LIMIT removed.")

print(f"\nFinal feature dataset: {len(merged)} rows, {len(merged.columns)} columns")
print(merged.columns.tolist())

os.makedirs("data", exist_ok=True)
merged.to_csv("data/ml_feature_dataset.csv", index=False)
print("Saved data/ml_feature_dataset.csv")