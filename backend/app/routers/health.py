from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db

router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health")
def health(db: Session = Depends(get_db)):
    checks = {"api": "ok"}
    try:
        db.execute(text("SELECT 1"))
        checks["database"] = "ok"
        counts = db.execute(text("""
            SELECT
              (SELECT COUNT(*) FROM thermal_events)   AS events,
              (SELECT COUNT(*) FROM industrial_sites) AS facilities,
              (SELECT COUNT(*) FROM fire_clusters)    AS clusters,
              (SELECT COUNT(*) FROM risk_scores)      AS classified
        """)).mappings().one()
        checks["row_counts"] = dict(counts)
    except Exception as exc:
        checks["database"] = f"error: {exc}"
    return checks