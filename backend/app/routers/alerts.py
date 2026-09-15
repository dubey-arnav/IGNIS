from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.services import event_service

PRIORITY = ["Industrial Fire", "Persistent Industrial Thermal Source"]

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


@router.get("")
def alerts(limit: int = Query(25, ge=1, le=200), db: Session = Depends(get_db)):
    """Derived view, not a table: the most recent industrial-classified events.

    No alert storage exists, so nothing can go stale."""
    result = event_service.list_events(db, classification=PRIORITY, limit=limit)
    return {"count": result["total"], "alerts": result["items"]}