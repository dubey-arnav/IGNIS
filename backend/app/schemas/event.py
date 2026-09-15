from datetime import date, time
from typing import List, Optional

from pydantic import BaseModel

from app.schemas.common import ClassificationOut, RiskOut


class EventSummary(BaseModel):
    event_id: int
    latitude: float
    longitude: float
    event_date: date
    event_time: Optional[time] = None
    frp: Optional[float] = None
    sensor_confidence: Optional[str] = None
    daynight: Optional[str] = None
    cluster_id: Optional[int] = None
    classification: ClassificationOut
    risk: RiskOut


class NearbyFacility(BaseModel):
    id: int
    name: Optional[str] = None
    type: Optional[str] = None
    latitude: float
    longitude: float
    distance_m: float


class ClusterHistory(BaseModel):
    cluster_id: int
    first_detection: Optional[date] = None
    last_detection: Optional[date] = None
    total_detections: Optional[int] = None
    active_days: Optional[int] = None
    mean_frp: Optional[float] = None
    max_frp: Optional[float] = None
    persistence_score: Optional[float] = None


class EventDetail(EventSummary):
    satellite: Optional[str] = None
    instrument: Optional[str] = None
    bright_ti4: Optional[float] = None
    bright_ti5: Optional[float] = None
    model_version: Optional[str] = None
    cluster: Optional[ClusterHistory] = None
    nearby_facilities: List[NearbyFacility] = []