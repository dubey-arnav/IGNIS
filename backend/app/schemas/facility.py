from typing import List, Optional

from pydantic import BaseModel

from app.schemas.event import EventSummary


class FacilitySummary(BaseModel):
    id: int
    osm_id: Optional[int] = None
    name: Optional[str] = None
    type: Optional[str] = None
    latitude: float
    longitude: float


class FacilityDetail(FacilitySummary):
    tags: Optional[dict] = None
    nearby_event_count: int
    classification_breakdown: dict
    recent_events: List[EventSummary] = []