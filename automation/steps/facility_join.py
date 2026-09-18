# automation/steps/facility_join.py
"""
Reuses the spatial-matching approach from ingestion/features/facility_features.py
(ST_DWithin pre-filter + precise geography distance), scoped to a list of new
event IDs instead of the full historical table.
"""
import logging
from sqlalchemy import text

logger = logging.getLogger("ignis.automation.facility_join")

# Same 0.06-degree pre-filter used in the existing pipeline to avoid a full
# seq-scan join (Part 16 of the handoff report).
PRE_FILTER_DEGREES = 0.06


def compute_facility_features(engine, event_ids: list[int]) -> dict:
    """
    Returns {event_id: {"nearest_facility_distance_m": ..., "nearest_facility_type": ...,
                        "facilities_within_radius": ...}}
    """
    if not event_ids:
        return {}

    with engine.connect() as conn:
        rows = conn.execute(
            text("""
                SELECT
                    t.id AS event_id,
                    (SELECT s.type
                     FROM industrial_sites s
                     WHERE ST_DWithin(t.geom, s.geom, :pre_filter)
                     ORDER BY t.geom <-> s.geom
                     LIMIT 1) AS nearest_facility_type,
                    (SELECT ST_Distance(t.geom::geography, s.geom::geography)
                     FROM industrial_sites s
                     WHERE ST_DWithin(t.geom, s.geom, :pre_filter)
                     ORDER BY t.geom <-> s.geom
                     LIMIT 1) AS nearest_facility_distance_m,
                    (SELECT COUNT(*)
                     FROM industrial_sites s
                     WHERE ST_DWithin(t.geom, s.geom, :pre_filter)
                       AND ST_DWithin(t.geom::geography, s.geom::geography, 5000)) AS facilities_within_radius
                FROM thermal_events t
                WHERE t.id = ANY(:ids)
            """),
            {"pre_filter": PRE_FILTER_DEGREES, "ids": event_ids},
        ).mappings().all()

    result = {r["event_id"]: dict(r) for r in rows}
    logger.info(f"Computed facility features for {len(result)} new events.")
    return result
