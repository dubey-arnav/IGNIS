from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import events, health, map_data

app = FastAPI(
    title="IGNIS API",
    description="Industrial thermal anomaly classification and monitoring.",
    version="1.0.0",
)

# Browsers block a React app on port 5173 from calling an API on port 8000
# unless the API explicitly allows it. That permission is called CORS.
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


@app.get("/")
def root():
    return {"name": "IGNIS API", "docs": "/docs", "health": "/api/health"}