# automation/steps/cluster_update.py
"""
Reuses the existing DBSCAN parameters (eps=1km, min_samples=2, haversine)
from the historical-persistence pipeline, applied to a rolling window
instead of the full table, per the "Clustering is not naturally incremental"
decision at the top of this guide.
"""
import logging
import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN
from sqlalchemy import text

logger = logging.getLogger("ignis.automation.cluster_update")

EPS_KM = 1.0
MIN_SAMPLES = 2
EARTH_RADIUS_KM = 6371.0
ROLLING_WINDOW_DAYS = 90


def update_clusters(engine) -> dict:
    with engine.connect() as conn:
        df = pd.read_sql(
            text("""
                SELECT id, latitude, longitude, event_date, frp
                FROM thermal_events
                WHERE event_date >= CURRENT_DATE - (:days || ' days')::interval
            """),
            conn,
            params={"days": ROLLING_WINDOW_DAYS},
        )

    if df.empty:
        return {"events_considered": 0, "clusters_touched": 0}

    coords = np.radians(df[["latitude", "longitude"]].to_numpy())
    db = DBSCAN(
        eps=EPS_KM / EARTH_RADIUS_KM, min_samples=MIN_SAMPLES, metric="haversine"
    ).fit(coords)
    df["cluster_label"] = db.labels_

    clustered = df[df["cluster_label"] != -1]
    touched = 0

    with engine.begin() as conn:
        for label, group in clustered.groupby("cluster_label"):
            centroid_lat = float(group["latitude"].mean())
            centroid_lon = float(group["longitude"].mean())
            first_detection = group["event_date"].min()
            last_detection = group["event_date"].max()
            total_detections = int(len(group))
            active_days = int(group["event_date"].nunique())
            time_span_days = max(
                (pd.to_datetime(last_detection) - pd.to_datetime(first_detection)).days,
                1,
            )
            persistence_score = round(active_days / time_span_days, 4)
            mean_frp = float(group["frp"].mean()) if group["frp"].notna().any() else None
            max_frp = float(group["frp"].max()) if group["frp"].notna().any() else None

            # Reconcile against an existing cluster centroid within 1km if one
            # already exists (so we UPDATE, not duplicate, a cluster that
            # simply gained a new detection).
            existing = conn.execute(
                text("""
                    SELECT id FROM fire_clusters
                    WHERE ST_DWithin(
                        geom::geography,
                        ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)::geography,
                        1000)
                    LIMIT 1
                """),
                {"lon": centroid_lon, "lat": centroid_lat},
            ).fetchone()

            if existing:
                cluster_id = existing[0]
                conn.execute(
                    text("""
                        UPDATE fire_clusters SET
                            last_detection = :last_detection,
                            total_detections = :total_detections,
                            active_days = :active_days,
                            mean_frp = :mean_frp, max_frp = :max_frp,
                            persistence_score = :persistence_score
                        WHERE id = :id
                    """),
                    {
                        "last_detection": last_detection,
                        "total_detections": total_detections,
                        "active_days": active_days,
                        "mean_frp": mean_frp,
                        "max_frp": max_frp,
                        "persistence_score": persistence_score,
                        "id": cluster_id,
                    },
                )
            else:
                cluster_id = conn.execute(
                    text("""
                        INSERT INTO fire_clusters
                        (geom, first_detection, last_detection, total_detections,
                         active_days, mean_frp, max_frp, persistence_score)
                        VALUES
                        (ST_SetSRID(ST_MakePoint(:lon, :lat), 4326),
                         :first_detection, :last_detection, :total_detections,
                         :active_days, :mean_frp, :max_frp, :persistence_score)
                        RETURNING id
                    """),
                    {
                        "lon": centroid_lon,
                        "lat": centroid_lat,
                        "first_detection": first_detection,
                        "last_detection": last_detection,
                        "total_detections": total_detections,
                        "active_days": active_days,
                        "mean_frp": mean_frp,
                        "max_frp": max_frp,
                        "persistence_score": persistence_score,
                    },
                ).scalar()

            conn.execute(
                text("UPDATE thermal_events SET cluster_id = :cid WHERE id = ANY(:ids)"),
                {"cid": cluster_id, "ids": group["id"].tolist()},
            )
            touched += 1

    logger.info(f"Clustering: considered={len(df)} clusters_touched={touched}")
    return {"events_considered": len(df), "clusters_touched": touched}
