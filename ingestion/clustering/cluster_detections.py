import sys
import os
import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN
from sqlalchemy import text

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from database.db_connect import engine

# Load ALL thermal events (recent + historical) that you want to cluster.
# For now, pull straight from the database rather than juggling multiple CSVs.
with engine.connect() as conn:
    df = pd.read_sql(text("SELECT id, latitude, longitude, event_date, frp FROM thermal_events"), conn)

print(f"Clustering {len(df)} thermal events...")

# DBSCAN needs coordinates in radians for the haversine (real-earth-distance) metric
coords_rad = np.radians(df[["latitude", "longitude"]].values)

EARTH_RADIUS_KM = 6371.0
eps_km = 1.0  # points within ~1 km of each other are considered "the same cluster"
eps_rad = eps_km / EARTH_RADIUS_KM

db = DBSCAN(eps=eps_rad, min_samples=2, metric="haversine")
df["cluster_label"] = db.fit_predict(coords_rad)

n_clusters = len(set(df["cluster_label"])) - (1 if -1 in df["cluster_label"].values else 0)
n_noise = (df["cluster_label"] == -1).sum()

print(f"Found {n_clusters} clusters")
print(f"{n_noise} events did not belong to any cluster (one-off detections, label = -1)")

os.makedirs("data", exist_ok=True)
df.to_csv("data/thermal_events_clustered.csv", index=False)
print("Saved data/thermal_events_clustered.csv")
