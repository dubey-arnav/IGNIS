from sqlalchemy.orm import Session

from app.repositories import event_repository
from app.repositories import facility_repository as repo
from app.schemas.facility import FacilityDetail, FacilitySummary
from app.services.event_service import _summary


def list_facilities(db: Session, **kw):
    rows = repo.list_facilities(db, **kw)
    return {"count": len(rows), "items": [FacilitySummary(
        id=f.id, osm_id=f.osm_id, name=f.name, type=f.type,
        latitude=f.latitude, longitude=f.longitude) for f in rows]}


def get_facility_detail(db: Session, facility_id: int):
    f = repo.get_facility(db, facility_id)
    if f is None:
        return None
    breakdown = {r["predicted_label"]: int(r["count"])
                 for r in repo.classification_breakdown_near(db, facility_id)}
    near = repo.events_near_facility(db, facility_id, limit=20)
    recent = []
    for n in near:
        row = event_repository.get_event(db, n["id"])
        if row:
            recent.append(_summary(*row))
    return FacilityDetail(
        id=f.id, osm_id=f.osm_id, name=f.name, type=f.type,
        latitude=f.latitude, longitude=f.longitude, tags=f.tags,
        nearby_event_count=sum(breakdown.values()),
        classification_breakdown=breakdown, recent_events=recent)