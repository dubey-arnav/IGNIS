from fastapi import APIRouter, HTTPException

from app.config import settings
from app.ml import model_loader, predictor
from app.schemas.prediction import PredictionRequest, PredictionResponse

router = APIRouter(prefix="/api", tags=["ml"])


@router.get("/model-info")
def model_info():
    try:
        state = model_loader.load()
        cfg = state["feature_config"]
        return {"loaded": True, "version": settings.MODEL_VERSION,
                "classes": state["class_names"],
                "n_features": len(cfg["categorical"]) + len(cfg["numeric"]),
                "categorical": cfg["categorical"], "numeric": cfg["numeric"]}
    except Exception as exc:
        return {"loaded": False, "error": str(exc),
                "expected_path": str(settings.MODEL_PATH)}


@router.post("/predict", response_model=PredictionResponse)
def predict(body: PredictionRequest):
    try:
        result = predictor.predict(body.model_dump())
    except Exception as exc:
        raise HTTPException(500, f"Prediction failed: {exc}")
    return PredictionResponse(**result, model_version=settings.MODEL_VERSION)