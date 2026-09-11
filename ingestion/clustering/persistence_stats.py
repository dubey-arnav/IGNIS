import sys
import os
import pandas as pd
from sqlalchemy import text

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from database.db_connect import engine

df = pd.read_csv("data/thermal_events_clustered.csv")

# Drop noise points (-1) — they're one-off events, not persistent clusters
clustered = df[df["cluster_label"] != -1].copy()
clustered["event_date"] = pd.to_datetime(clustered["event_date"])

insert_sql = text("""
    INSERT INTO fire_clusters
        (geom, first_detection, last_detection, total_detections,
        active_days, mean_frp, max_frp, persistence_score)
    VALUES
        (ST_SetSRID(ST_MakePoint(:lon, :lat), 4326),
        :first_detection, :last_detection, :total_detections,
        :active_days, :mean_frp, :max_frp, :persistence_score)
""")

rows_inserted = 0

with engine.begin() as conn:
    for cluster_id, group in clustered.groupby("cluster_label"):
        center_lat = group["latitude"].mean()
        center_lon = group["longitude"].mean()

        first_detection = group["event_date"].min().date()
        last_detection = group["event_date"].max().date()
        total_detections = len(group)
        active_days = group["event_date"].dt.date.nunique()
        mean_frp = group["frp"].mean()
        max_frp = group["frp"].max()

        # Simple prototype persistence score: how many distinct active days,
        # relative to the full time span the cluster has been observed over.
        time_span_days = max((last_detection - first_detection).days, 1)
        persistence_score = round(active_days / time_span_days, 4)

        conn.execute(insert_sql, {
            "lat": float(center_lat),
            "lon": float(center_lon),
            "first_detection": first_detection,
            "last_detection": last_detection,
            "total_detections": total_detections,
            "active_days": active_days,
            "mean_frp": float(mean_frp),
            "max_frp": float(max_frp),
            "persistence_score": persistence_score,
        })
        rows_inserted += 1

print(f"Inserted {rows_inserted} rows into fire_clusters")