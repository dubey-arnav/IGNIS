from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class PredictionRequest(BaseModel):
    confidence: Optional[str] = Field(None, examples=["n"])
    daynight: Optional[str] = Field(None, examples=["D"])
    nearest_facility_type: Optional[str] = Field(None, examples=["power_plant"])
    bright_ti4: Optional[float] = None
    bright_ti5: Optional[float] = None
    frp: Optional[float] = None
    nearest_facility_distance_m: Optional[float] = None
    facilities_within_radius: Optional[int] = None
    total_detections: Optional[int] = None
    active_days: Optional[int] = None
    cluster_mean_frp: Optional[float] = None
    cluster_max_frp: Optional[float] = None
    persistence_score: Optional[float] = None
    ndvi_mean: Optional[float] = None
    ndbi_mean: Optional[float] = None
    ndwi_mean: Optional[float] = None
    swir1_mean: Optional[float] = None
    swir2_mean: Optional[float] = None
    valid_pixel_fraction: Optional[float] = None


class PredictionResponse(BaseModel):
    predicted_label: str
    class_probabilities: Dict[str, float]
    risk_score: float
    risk_tier: str
    missing_features: List[str]
    warnings: List[str]
    model_version: str