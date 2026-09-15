from typing import Optional, Tuple

from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.models import IndustrialSite


def list_facilities(db: Session, bbox: Optional[Tuple] = None,
                    type_: Optional[str] = None, q: Optional[str] = None,
                    limit: int = 200):
    stmt = select(IndustrialSite)
    if bbox:
        w, s, e, n = bbox
        stmt = stmt.where(IndustrialSite.longitude.between(w, e),
                          IndustrialSite.latitude.between(s, n))
    if type_:
        stmt = stmt.where(IndustrialSite.type == type_)
    if q:
        stmt = stmt.where(IndustrialSite.name.ilike(f"%{q}%"))
    return db.execute(stmt.limit(limit)).scalars().all()


def get_facility(db: Session, facility_id: int):
    return db.get(IndustrialSite, facility_id)


def events_near_facility(db: Session, facility_id: int, radius_m: int = 5000,
                         limit: int = 20):
    return db.execute(text("""
        SELECT t.id, r.predicted_label,
               ST_Distance(t.geom::geography, s.geom::geography) AS distance_m
        FROM industrial_sites s
        JOIN thermal_events t
          ON ST_DWithin(t.geom::geography, s.geom::geography, :radius)
        JOIN risk_scores r ON r.event_id = t.id
        WHERE s.id = :fid
        ORDER BY t.event_date DESC
        LIMIT :limit
    """), {"fid": facility_id, "radius": radius_m, "limit": limit}).mappings().all()


def classification_breakdown_near(db: Session, facility_id: int,
                                  radius_m: int = 5000):
    return db.execute(text("""
        SELECT r.predicted_label, COUNT(*) AS count
        FROM industrial_sites s
        JOIN thermal_events t
          ON ST_DWithin(t.geom::geography, s.geom::geography, :radius)
        JOIN risk_scores r ON r.event_id = t.id
        WHERE s.id = :fid
        GROUP BY r.predicted_label
    """), {"fid": facility_id, "radius": radius_m}).mappings().all()


def facility_types(db: Session):
    return db.execute(text("""
        SELECT type, COUNT(*) AS count
        FROM industrial_sites
        GROUP BY type
        ORDER BY count DESC
    """)).mappings().all()