from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.services import analytics_service

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/timeline")
def timeline(start_date: Optional[date] = None, end_date: Optional[date] = None,
             db: Session = Depends(get_db)):
    return analytics_service.timeline(db, start_date, end_date)


@router.get("/by-facility-type")
def by_facility_type(db: Session = Depends(get_db)):
    return analytics_service.by_facility_type(db)


@router.get("/distance-profile")
def distance_profile(db: Session = Depends(get_db)):
    return analytics_service.distance_profile(db)