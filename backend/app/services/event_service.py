from typing import Optional

from sqlalchemy.orm import Session

from app.repositories import event_repository as repo
from app.schemas.common import ClassificationOut, RiskOut
from app.schemas.event import (ClusterHistory, EventDetail, EventSummary,
                               NearbyFacility)
from app.utils.constants import RISK_TIERS, classification_meta


def _classification(label: str) -> ClassificationOut:
    m = classification_meta(label)
    return ClassificationOut(label=label, code=m["code"], color=m["color"],
                             modelled=m["modelled"], description=m["description"])


def _risk(score: float, tier: str) -> RiskOut:
    return RiskOut(score=score, tier=tier,
                   tier_color=RISK_TIERS.get(tier, RISK_TIERS["Low"])["color"])


def _summary(ev, rs) -> EventSummary:
    return EventSummary(
        event_id=ev.id, latitude=ev.latitude, longitude=ev.longitude,
        event_date=ev.event_date, event_time=ev.event_time, frp=ev.frp,
        sensor_confidence=ev.confidence, daynight=ev.daynight,
        cluster_id=ev.cluster_id,
        classification=_classification(rs.predicted_label),
        risk=_risk(rs.risk_score, rs.risk_tier),
    )


def list_events(db: Session, **kwargs):
    limit = kwargs.pop("limit", 100)
    offset = kwargs.pop("offset", 0)
    total, rows = repo.list_events(db, limit=limit, offset=offset, **kwargs)
    return {"total": total, "limit": limit, "offset": offset,
            "items": [_summary(ev, rs) for ev, rs in rows]}


def get_event_detail(db: Session, event_id: int) -> Optional[EventDetail]:
    row = repo.get_event(db, event_id)
    if row is None:
        return None
    ev, rs = row

    cluster = None
    if ev.cluster_id is not None:
        c = repo.get_cluster(db, ev.cluster_id)
        if c:
            cluster = ClusterHistory(
                cluster_id=c.id, first_detection=c.first_detection,
                last_detection=c.last_detection, total_detections=c.total_detections,
                active_days=c.active_days, mean_frp=c.mean_frp, max_frp=c.max_frp,
                persistence_score=c.persistence_score)

    facilities = [NearbyFacility(**dict(f))
                  for f in repo.nearby_facilities(db, ev.latitude, ev.longitude)]

    return EventDetail(**_summary(ev, rs).model_dump(),
                       satellite=ev.satellite, instrument=ev.instrument,
                       bright_ti4=ev.bright_ti4, bright_ti5=ev.bright_ti5,
                       model_version=rs.model_version,
                       cluster=cluster, nearby_facilities=facilities)