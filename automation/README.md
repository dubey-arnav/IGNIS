# IGNIS — Phase 3: Automation / Near-Real-Time Pipeline

This folder houses the orchestration layer that connects NASA FIRMS detection fetching, deduplication, spatial processing, persistence clustering, ML feature engineering, model inference, risk scoring, and database upserts.

## Architecture

1. **`fetch_firms.py` (Step A2)**: Fetches rolling NASA FIRMS VIIRS detections via Area API.
2. **`dedupe_and_insert.py` (Step A3)**: Generates a deterministic `firms_uid` hash and idempotently inserts new detections into `thermal_events` via `ON CONFLICT (firms_uid) DO NOTHING RETURNING id`.
3. **`facility_join.py` (Step A4)**: PostGIS spatial join calculating proximity to industrial sites and facility counts within 5km for new detections.
4. **`cluster_update.py` (Step A5)**: Rolling-window DBSCAN clustering (1km, 2 min_samples) reconciling clusters against `fire_clusters`.
5. **`sentinel_context.py` (Step A6)**: Sentinel-2 spectral indices context provider with graceful fallback.
6. **`feature_builder.py` (Step A7)**: Assembles the 19-column ML feature vector matching `feature_config.json` with categorical levels.
7. **`scorer.py` (Step A8)**: Packaged `FireClassifier` wrapper loading the trained XGBoost classifier.
8. **`risk_engine.py` (Step A9)**: Computes risk scores and risk tiers using the calibrated probability model.
9. **`db_writer.py` (Step A10)**: Idempotent upsert into `risk_scores` via `ON CONFLICT (event_id) DO UPDATE`.
10. **`run_pipeline.py` (Step A11)**: Orchestrator running the complete pipeline with per-event error isolation and logging.
11. **`scheduler.py` (Step A12)**: Continuous in-process scheduler running periodically (every 30 minutes).

## Usage

### Run Pipeline Once (Manual / Cron)
```bash
python automation/run_pipeline.py
```

### Run Continuous In-Process Scheduler
```bash
python automation/scheduler.py
```
