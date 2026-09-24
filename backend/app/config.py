import os
from pathlib import Path
from dotenv import load_dotenv

# backend/app/config.py -> parents[2] is the project root (IGNIS/)
PROJECT_ROOT = Path(os.getenv("PROJECT_ROOT", str(Path(__file__).resolve().parents[2])))
if (PROJECT_ROOT / ".env").exists():
    load_dotenv(PROJECT_ROOT / ".env")
load_dotenv()


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
    MODEL_PATH = Path(os.getenv("MODEL_PATH", str(PROJECT_ROOT / "ml" / "models" / "xgb_fire_classifier.json")))
    FEATURE_CONFIG_PATH = Path(os.getenv("FEATURE_CONFIG_PATH", str(PROJECT_ROOT / "ml" / "models" / "feature_config.json")))
    LABEL_MAP_PATH = Path(os.getenv("LABEL_MAP_PATH", str(PROJECT_ROOT / "ml" / "training" / "label_mapping.json")))
    MODEL_VERSION = os.getenv("MODEL_VERSION", "xgb_v1")

    _raw_cors = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000,http://localhost:8000,http://127.0.0.1:8000,*"
    )
    CORS_ORIGINS = [o.strip() for o in _raw_cors.split(",") if o.strip()]



settings = Settings()