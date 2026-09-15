from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class ClassificationOut(BaseModel):
    label: str
    code: str
    color: str
    modelled: bool
    description: Optional[str] = None


class RiskOut(BaseModel):
    score: float
    tier: str
    tier_color: str


class Paginated(BaseModel, Generic[T]):
    total: int
    limit: int
    offset: int
    items: List[T]