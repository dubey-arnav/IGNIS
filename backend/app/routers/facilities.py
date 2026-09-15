from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories import facility_repository
from app.routers.events import parse_bbox
from app.services import facility_service

router = APIRouter(prefix="/api/facilities", tags=["facilities"])


@router.get("")
def list_facilities(bbox: Optional[str] = None, type: Optional[str] = None,
                    q: Optional[str] = None,
                    limit: int = Query(200, ge=1, le=2000),
                    db: Session = Depends(get_db)):
    return facility_service.list_facilities(
        db, bbox=parse_bbox(bbox), type_=type, q=q, limit=limit)


@router.get("/types")
def types(db: Session = Depends(get_db)):
    return {"items": [dict(r) | {"count": int(r["count"])}
                      for r in facility_repository.facility_types(db)]}


@router.get("/{facility_id}")
def get_facility(facility_id: int, db: Session = Depends(get_db)):
    d = facility_service.get_facility_detail(db, facility_id)
    if d is None:
        raise HTTPException(404, f"Facility {facility_id} not found")
    return d