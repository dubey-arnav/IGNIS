from sqlalchemy import text
from sqlalchemy.orm import Session


def classification_counts(db: Session):
    return db.execute(text("""
        SELECT predicted_label,
               COUNT(*) AS count,
               ROUND(AVG(risk_score)::numeric, 1) AS avg_risk
        FROM risk_scores
        GROUP BY predicted_label
        ORDER BY count DESC
    """)).mappings().all()


def tier_counts(db: Session):
    return db.execute(text("""
        SELECT risk_tier, COUNT(*) AS count
        FROM risk_scores
        GROUP BY risk_tier
    """)).mappings().all()


def headline(db: Session):
    return db.execute(text("""
        SELECT
          (SELECT COUNT(*) FROM thermal_events)        AS total_events,
          (SELECT COUNT(*) FROM fire_clusters)         AS total_clusters,
          (SELECT COUNT(*) FROM industrial_sites)      AS total_facilities,
          (SELECT MIN(event_date) FROM thermal_events) AS first_date,
          (SELECT MAX(event_date) FROM thermal_events) AS last_date
    """)).mappings().one()


def timeline(db: Session, start_date=None, end_date=None):
    return db.execute(text("""
        SELECT t.event_date, r.predicted_label, COUNT(*) AS count
        FROM thermal_events t
        JOIN risk_scores r ON r.event_id = t.id
        WHERE (CAST(:start_date AS date) IS NULL OR t.event_date >= :start_date)
          AND (CAST(:end_date AS date)   IS NULL OR t.event_date <= :end_date)
        GROUP BY t.event_date, r.predicted_label
        ORDER BY t.event_date
    """), {"start_date": start_date, "end_date": end_date}).mappings().all()


def by_facility_type(db: Session):
    """For each industrial-classified event, which facility type is nearest.

    LATERAL means 'for each row on the left, run this small query'.
    The <-> operator is PostGIS index-assisted nearest-neighbour search."""
    return db.execute(text("""
        SELECT f.type AS facility_type, r.predicted_label, COUNT(*) AS count
        FROM thermal_events t
        JOIN risk_scores r ON r.event_id = t.id
        JOIN LATERAL (
            SELECT s.type
            FROM industrial_sites s
            WHERE ST_DWithin(s.geom::geography, t.geom::geography, 5000)
            ORDER BY s.geom <-> t.geom
            LIMIT 1
        ) f ON TRUE
        WHERE r.predicted_label IN
              ('Industrial Fire', 'Persistent Industrial Thermal Source')
        GROUP BY f.type, r.predicted_label
        ORDER BY count DESC
        LIMIT 20
    """)).mappings().all()


def distance_profile(db: Session):
    """How each class distributes across distance-to-facility buckets.

    This is the query that visually proves the model's core logic."""
    return db.execute(text("""
        WITH d AS (
          SELECT r.predicted_label,
                 (SELECT MIN(ST_Distance(s.geom::geography, t.geom::geography))
                  FROM industrial_sites s
                  WHERE ST_DWithin(s.geom::geography, t.geom::geography, 10000)
                 ) AS dist_m
          FROM thermal_events t
          JOIN risk_scores r ON r.event_id = t.id
        )
        SELECT predicted_label,
          CASE WHEN dist_m IS NULL THEN '>10km'
               WHEN dist_m < 500   THEN '0-500m'
               WHEN dist_m < 1500  THEN '500-1500m'
               WHEN dist_m < 5000  THEN '1.5-5km'
               ELSE '5-10km' END AS bucket,
          COUNT(*) AS count
        FROM d
        GROUP BY 1, 2
        ORDER BY 1, 2
    """)).mappings().all()