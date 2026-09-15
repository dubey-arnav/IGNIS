from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.common import Paginated
from app.schemas.event import EventDetail, EventSummary
from app.services import event_service

router = APIRouter(prefix="/api/events", tags=["events"])


def parse_bbox(bbox: Optional[str]):
    """bbox=west,south,east,north  (same order as the FIRMS API)."""
    if not bbox:
        return None
    try:
        w, s, e, n = [float(x) for x in bbox.split(",")]
        return (w, s, e, n)
    except ValueError:
        raise HTTPException(400, "bbox must be 'west,south,east,north'")


@router.get("", response_model=Paginated[EventSummary])
def list_events(
    classification: Optional[List[str]] = Query(None),
    tier: Optional[List[str]] = Query(None),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    min_frp: Optional[float] = None,
    bbox: Optional[str] = None,
    cluster_id: Optional[int] = None,
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    return event_service.list_events(
        db, classification=classification, tier=tier, start_date=start_date,
        end_date=end_date, min_frp=min_frp, bbox=parse_bbox(bbox),
        cluster_id=cluster_id, limit=limit, offset=offset)


@router.get("/{event_id}", response_model=EventDetail)
def get_event(event_id: int, db: Session = Depends(get_db)):
    detail = event_service.get_event_detail(db, event_id)
    if detail is None:
        raise HTTPException(404, f"Event {event_id} not found")
    return detail