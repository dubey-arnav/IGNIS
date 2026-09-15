from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.services import analytics_service

router = APIRouter(prefix="/api", tags=["classification"])


@router.get("/classifications")
def classifications(db: Session = Depends(get_db)):
    return analytics_service.classifications(db)


@router.get("/dashboard-summary")
def dashboard_summary(db: Session = Depends(get_db)):
    return analytics_service.dashboard_summary(db)