# automation/run_pipeline.py
import logging
import os
import sys
import time
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from automation.steps.fetch_firms import fetch_recent_firms
from automation.steps.dedupe_and_insert import compute_firms_uid, insert_new_events
from automation.steps.facility_join import compute_facility_features
from automation.steps.cluster_update import update_clusters
from automation.steps.sentinel_context import get_sentinel_context
from automation.steps.feature_builder import build_feature_row
from automation.steps.scorer import FireClassifier
from automation.steps.risk_engine import RiskEngine
from automation.steps.db_writer import ensure_schema, upsert_risk_score

load_dotenv()

os.makedirs("automation/logs", exist_ok=True)

logging.basicConfig(
    level=os.getenv("AUTOMATION_LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(f"automation/logs/run_{datetime.now():%Y%m%d_%H%M%S}.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("ignis.automation.pipeline")


def get_engine():
    db_user = os.getenv("DB_USER", "postgres")
    db_pass = os.getenv("DB_PASSWORD", "")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    db_name = os.getenv("DB_NAME", "IGNIS")
    url = f"postgresql+psycopg2://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
    return create_engine(url, pool_pre_ping=True)


def run() -> dict:
    start = time.time()
    logger.info("=== IGNIS automation run started ===")
    engine = get_engine()
    ensure_schema(engine)
    stats = {"fetched": 0, "inserted": 0, "duplicates": 0, "scored": 0, "failed": 0}

    # --- Step A2: fetch ---
    bbox = os.getenv("FIRMS_BBOX", "68,6,97,37")
    days = int(os.getenv("AUTOMATION_LOOKBACK_DAYS", "2"))
    try:
        df = fetch_recent_firms(bbox=bbox, days=days)
        stats["fetched"] = len(df)
    except Exception as e:
        logger.error(f"FIRMS fetch failed, aborting this run: {e}")
        return stats

    if df.empty:
        logger.info("No FIRMS data returned. Nothing to process. Run complete.")
        return stats

    # --- Step A3: dedupe + insert ---
    insert_stats = insert_new_events(engine, df)
    stats.update({"inserted": insert_stats["inserted"], "duplicates": insert_stats["duplicates"]})
    inserted_ids = insert_stats.get("inserted_ids", [])

    # Check for any events matching this batch that need scoring
    uids = df.apply(compute_firms_uid, axis=1).tolist()
    with engine.connect() as conn:
        unscored_count = conn.execute(
            text("""
                SELECT COUNT(*) FROM thermal_events t
                LEFT JOIN risk_scores rs ON rs.event_id = t.id
                WHERE t.firms_uid = ANY(:uids) AND rs.id IS NULL
            """),
            {"uids": uids},
        ).scalar()

    if insert_stats["inserted"] == 0 and unscored_count == 0:
        logger.info("All fetched rows were duplicates and already scored. Nothing new to score. Run complete.")
        elapsed = time.time() - start
        logger.info(
            f"=== Run complete in {elapsed:.1f}s | fetched={stats['fetched']} "
            f"inserted={stats['inserted']} duplicates={stats['duplicates']} "
            f"scored={stats['scored']} failed={stats['failed']} ==="
        )
        return stats

    # --- Step A5: clustering (affects the whole rolling window, not just new IDs) ---
    try:
        update_clusters(engine)
    except Exception as e:
        logger.error(f"Clustering step failed (continuing with stale cluster data): {e}")

    # --- Fetch events needing scoring back out for scoring ---
    with engine.connect() as conn:
        new_events = conn.execute(
            text("""
                SELECT t.id, t.latitude, t.longitude, t.event_date, t.event_time,
                       t.confidence, t.bright_ti4, t.bright_ti5, t.frp, t.daynight,
                       t.cluster_id,
                       fc.total_detections, fc.active_days, fc.mean_frp AS cluster_mean_frp,
                       fc.max_frp AS cluster_max_frp, fc.persistence_score
                FROM thermal_events t
                LEFT JOIN fire_clusters fc ON fc.id = t.cluster_id
                LEFT JOIN risk_scores rs ON rs.event_id = t.id
                WHERE t.firms_uid = ANY(:uids) AND (t.id = ANY(:inserted_ids) OR rs.id IS NULL)
            """),
            {"uids": uids, "inserted_ids": inserted_ids},
        ).mappings().all()

    if not new_events:
        logger.info("No events pending scoring. Run complete.")
        elapsed = time.time() - start
        logger.info(
            f"=== Run complete in {elapsed:.1f}s | fetched={stats['fetched']} "
            f"inserted={stats['inserted']} duplicates={stats['duplicates']} "
            f"scored={stats['scored']} failed={stats['failed']} ==="
        )
        return stats

    try:
        classifier = FireClassifier("ml/models/xgb_fire_classifier.json", "ml/training/label_mapping.json")
        risk_engine = RiskEngine("ml/models/calibrated_risk_model.joblib", classifier.class_names)
    except Exception as e:
        logger.error(f"Failed to load ML models, aborting scoring: {e}")
        return stats

    event_ids = [e["id"] for e in new_events]
    all_facility_features = compute_facility_features(engine, event_ids)

    for event in new_events:
        event = dict(event)
        try:
            facility_features = all_facility_features.get(event["id"], {})
            cluster_features = {
                "total_detections": event.get("total_detections"),
                "active_days": event.get("active_days"),
                "cluster_mean_frp": event.get("cluster_mean_frp"),
                "cluster_max_frp": event.get("cluster_max_frp"),
                "persistence_score": event.get("persistence_score"),
            }
            sentinel_features = get_sentinel_context(event)
            feature_row = build_feature_row(
                event,
                facility_features,
                cluster_features,
                sentinel_features,
                feature_config_path="ml/models/feature_config.json",
            )
            merged_for_risk = {**event, **facility_features}
            result = risk_engine.score(feature_row, merged_for_risk)
            upsert_risk_score(
                engine,
                event_id=event["id"],
                cluster_id=event.get("cluster_id"),
                result=result,
            )
            stats["scored"] += 1
        except Exception as e:
            # PER-EVENT isolation: one bad record must not kill the whole run.
            logger.error(f"Failed to process event_id={event.get('id')}: {e}", exc_info=True)
            stats["failed"] += 1
            continue

    elapsed = time.time() - start
    logger.info(
        f"=== Run complete in {elapsed:.1f}s | fetched={stats['fetched']} "
        f"inserted={stats['inserted']} duplicates={stats['duplicates']} "
        f"scored={stats['scored']} failed={stats['failed']} ==="
    )
    return stats


if __name__ == "__main__":
    run()
