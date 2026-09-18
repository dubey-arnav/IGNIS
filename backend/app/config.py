import os
from pathlib import Path
from dotenv import load_dotenv

# backend/app/config.py -> parents[2] is the project root (IGNIS/)
PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")


class Settings:
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "IGNIS")

    @property
    def DATABASE_URL(self) -> str:
        return (
            f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    # The backend READS these ML artifacts. It never writes them.
    MODEL_PATH = PROJECT_ROOT / "ml" / "models" / "xgb_fire_classifier.json"
    FEATURE_CONFIG_PATH = PROJECT_ROOT / "ml" / "models" / "feature_config.json"
    LABEL_MAP_PATH = PROJECT_ROOT / "ml" / "training" / "label_mapping.json"
    MODEL_VERSION = "xgb_v1"

    CORS_ORIGINS = list(dict.fromkeys([
        o.strip() for o in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000"
        ).split(",") if o.strip()
    ] + ["http://localhost:5173", "http://127.0.0.1:5173"]))



settings = Settings()