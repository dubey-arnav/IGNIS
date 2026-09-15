from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.ml import model_loader
from app.routers import (alerts, analytics, classifications, events,
                          facilities, health, map_data, predict)

app = FastAPI(
    title="IGNIS API",
    description="Industrial thermal anomaly classification and monitoring.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(events.router)
app.include_router(map_data.router)
app.include_router(classifications.router)
app.include_router(analytics.router)
app.include_router(alerts.router)
app.include_router(facilities.router)
app.include_router(predict.router)


@app.on_event("startup")
def warm_up():
    try:
        model_loader.load()
        print("[IGNIS] ML model loaded.")
    except Exception as exc:
        print(f"[IGNIS] WARNING: model not loaded: {exc}")


@app.get("/")
def root():
    return {"name": "IGNIS API", "docs": "/docs", "health": "/api/health"}