from datetime import date
from typing import List, Optional, Tuple

from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from app.models import FireCluster, RiskScore, ThermalEvent


def _apply_filters(stmt, classification, tier, start_date, end_date,
                   min_frp, bbox, cluster_id):
    """Shared filter logic so /events and /map-data can never diverge."""
    if classification:
        stmt = stmt.where(RiskScore.predicted_label.in_(classification))
    if tier:
        stmt = stmt.where(RiskScore.risk_tier.in_(tier))
    if start_date:
        stmt = stmt.where(ThermalEvent.event_date >= start_date)
    if end_date:
        stmt = stmt.where(ThermalEvent.event_date <= end_date)
    if min_frp is not None:
        stmt = stmt.where(ThermalEvent.frp >= min_frp)
    if cluster_id is not None:
        stmt = stmt.where(ThermalEvent.cluster_id == cluster_id)
    if bbox:
        west, south, east, north = bbox
        stmt = stmt.where(
            ThermalEvent.longitude.between(west, east),
            ThermalEvent.latitude.between(south, north),
        )
    return stmt


def list_events(db: Session, *, classification: Optional[List[str]] = None,
                tier: Optional[List[str]] = None, start_date: Optional[date] = None,
                end_date: Optional[date] = None, min_frp: Optional[float] = None,
                bbox: Optional[Tuple[float, float, float, float]] = None,
                cluster_id: Optional[int] = None,
                limit: int = 100, offset: int = 0):
    base = select(ThermalEvent, RiskScore).join(
        RiskScore, RiskScore.event_id == ThermalEvent.id
    )
    base = _apply_filters(base, classification, tier, start_date, end_date,
                          min_frp, bbox, cluster_id)

    count_stmt = select(func.count()).select_from(base.subquery())
    total = db.execute(count_stmt).scalar_one()

    rows = db.execute(
        base.order_by(RiskScore.risk_score.desc(), ThermalEvent.event_date.desc())
            .limit(limit).offset(offset)
    ).all()
    return total, rows


def get_event(db: Session, event_id: int):
    return db.execute(
        select(ThermalEvent, RiskScore)
        .join(RiskScore, RiskScore.event_id == ThermalEvent.id)
        .where(ThermalEvent.id == event_id)
    ).first()


def get_cluster(db: Session, cluster_id: int):
    return db.get(FireCluster, cluster_id)


def nearby_facilities(db: Session, lat: float, lon: float,
                      radius_m: int = 5000, limit: int = 5):
    """PostGIS: true metres-on-the-ground distance, not degrees.

    ::geography casts lat/lon to a spherical type measured in metres.
    ST_DWithin uses the GIST index first, so only a few rows get measured."""
    sql = text("""
        SELECT id, name, type, latitude, longitude,
               ST_Distance(geom::geography,
                           ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)::geography)
                   AS distance_m
        FROM industrial_sites
        WHERE ST_DWithin(geom::geography,
                         ST_SetSRID(ST_MakePoint(:lon, :lat), 4326)::geography,
                         :radius)
        ORDER BY distance_m
        LIMIT :limit
    """)
    return db.execute(sql, {"lat": lat, "lon": lon,
                            "radius": radius_m, "limit": limit}).mappings().all()


def map_points(db: Session, **filters):
    """Minimal columns only — a map with 11k markers must not ship 25 fields each."""
    stmt = select(
        ThermalEvent.id, ThermalEvent.latitude, ThermalEvent.longitude,
        ThermalEvent.frp, ThermalEvent.event_date,
        RiskScore.predicted_label, RiskScore.risk_score, RiskScore.risk_tier,
    ).join(RiskScore, RiskScore.event_id == ThermalEvent.id)
    stmt = _apply_filters(stmt, filters.get("classification"), filters.get("tier"),
                          filters.get("start_date"), filters.get("end_date"),
                          filters.get("min_frp"), filters.get("bbox"), None)
    return db.execute(stmt.limit(filters.get("limit", 5000))).all()