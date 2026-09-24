# database/seed_initial_data.py
"""
Seeds a fresh database with:
1. Industrial sites from data/osm_raw.json (31,900 locations)
2. Historical thermal events and clusters from data/thermal_events_clustered.csv
3. Risk scores from data/risk_scores.csv
Idempotent: skips tables that already contain data.
"""
import os
import sys
import json
import logging
import pandas as pd
from sqlalchemy import create_engine, text

logging.basicConfig(level="INFO", format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("ignis.seed")

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "IGNIS")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

URL = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(URL, pool_pre_ping=True)


def seed_industrial_sites():
    with engine.connect() as conn:
        count = conn.execute(text("SELECT COUNT(*) FROM industrial_sites")).scalar()
    if count and count > 0:
        logger.info(f"industrial_sites already contains {count} records. Skipping.")
        return

    osm_path = "data/osm_raw.json"
    if not os.path.exists(osm_path):
        logger.warning(f"File {osm_path} not found. Skipping industrial sites seed.")
        return

    logger.info(f"Loading industrial sites from {osm_path}...")
    with open(osm_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    def get_coords(el):
        if "lat" in el and "lon" in el:
            return el["lat"], el["lon"]
        if "center" in el:
            return el["center"]["lat"], el["center"]["lon"]
        return None, None

    def guess_type(tags):
        if tags.get("power") == "plant": return "power_plant"
        if tags.get("man_made") == "works": return "industrial_works"
        if tags.get("landuse") == "industrial": return "industrial_area"
        if tags.get("man_made") == "petroleum_well": return "petroleum_well"
        if tags.get("man_made") == "pipeline": return "pipeline"
        return "other"

    insert_sql = text("""
        INSERT INTO industrial_sites
            (osm_id, name, type, latitude, longitude, geom, tags, source)
        VALUES
            (:osm_id, :name, :type, :latitude, :longitude,
             ST_SetSRID(ST_MakePoint(:longitude, :latitude), 4326),
             :tags, 'OSM')
    """)

    batch = []
    for el in data.get("elements", []):
        lat, lon = get_coords(el)
        if lat is None or lon is None:
            continue
        tags = el.get("tags", {})
        batch.append({
            "osm_id": el.get("id"),
            "name": tags.get("name"),
            "type": guess_type(tags),
            "latitude": lat,
            "longitude": lon,
            "tags": json.dumps(tags),
        })

    with engine.begin() as conn:
        for i in range(0, len(batch), 1000):
            conn.execute(insert_sql, batch[i:i + 1000])

    logger.info(f"Successfully inserted {len(batch)} industrial sites.")


def seed_risk_scores():
    with engine.connect() as conn:
        count = conn.execute(text("SELECT COUNT(*) FROM risk_scores")).scalar()
    if count and count > 0:
        logger.info(f"risk_scores already contains {count} records. Skipping.")
        return

    csv_path = "data/risk_scores.csv"
    if not os.path.exists(csv_path):
        logger.info(f"{csv_path} not found. Skipping risk_scores seed.")
        return

    df = pd.read_csv(csv_path)
    logger.info(f"Backfilling {len(df)} risk scores from {csv_path}...")
    insert_sql = text("""
        INSERT INTO risk_scores (event_id, cluster_id, predicted_label, risk_score, risk_tier, model_version)
        VALUES (:event_id, :cluster_id, :predicted_label, :risk_score, :risk_tier, :model_version)
        ON CONFLICT (event_id) DO UPDATE SET
            predicted_label = EXCLUDED.predicted_label,
            risk_score = EXCLUDED.risk_score,
            risk_tier = EXCLUDED.risk_tier
    """)
    records = []
    for _, row in df.iterrows():
        records.append({
            "event_id": int(row["event_id"]),
            "cluster_id": int(row["cluster_id"]) if pd.notna(row.get("cluster_id")) else None,
            "predicted_label": str(row["predicted_label"]),
            "risk_score": float(row["risk_score"]),
            "risk_tier": str(row["risk_tier"]),
            "model_version": "xgb_v1",
        })

    with engine.begin() as conn:
        for i in range(0, len(records), 1000):
            conn.execute(insert_sql, records[i:i + 1000])
    logger.info(f"Successfully seeded {len(records)} risk scores.")


if __name__ == "__main__":
    logger.info("Starting initial seed process...")
    seed_industrial_sites()
    seed_risk_scores()
    logger.info("Seed process complete.")
