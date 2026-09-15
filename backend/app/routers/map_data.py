from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories import event_repository as repo
from app.routers.events import parse_bbox
from app.utils.constants import RISK_TIERS, classification_meta

router = APIRouter(prefix="/api/map-data", tags=["map"])


@router.get("")
def map_data(
    classification: Optional[List[str]] = Query(None),
    tier: Optional[List[str]] = Query(None),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    min_frp: Optional[float] = None,
    bbox: Optional[str] = None,
    limit: int = Query(5000, ge=1, le=20000),
    db: Session = Depends(get_db),
):
    """GeoJSON FeatureCollection — the format Leaflet consumes natively."""
    rows = repo.map_points(db, classification=classification, tier=tier,
                           start_date=start_date, end_date=end_date,
                           min_frp=min_frp, bbox=parse_bbox(bbox), limit=limit)

    features = []
    for r in rows:
        meta = classification_meta(r.predicted_label)
        features.append({
            "type": "Feature",
            # GeoJSON is ALWAYS [longitude, latitude]. Reversing this is the
            # single most common Leaflet bug.
            "geometry": {"type": "Point", "coordinates": [r.longitude, r.latitude]},
            "properties": {
                "event_id": r.id,
                "classification": r.predicted_label,
                "classification_code": meta["code"],
                "color": meta["color"],
                "frp": r.frp,
                "event_date": r.event_date.isoformat() if r.event_date else None,
                "risk_score": r.risk_score,
                "risk_tier": r.risk_tier,
                "tier_color": RISK_TIERS.get(r.risk_tier, RISK_TIERS["Low"])["color"],
            },
        })
    return {"type": "FeatureCollection", "count": len(features), "features": features}