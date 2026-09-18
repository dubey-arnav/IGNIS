# automation/one_time_backfill.py
"""
One-time historical backfill script (only needed if Step A0 found risk_scores empty).
Idempotently ensures the schema and loads rows from data/risk_scores.csv.
"""
import os
import sys
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from automation.steps.db_writer import ensure_schema, upsert_risk_score


load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "IGNIS")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

url = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(url)
ensure_schema(engine)

csv_path = "data/risk_scores.csv"
if os.path.exists(csv_path):
    df = pd.read_csv(csv_path)
    count = 0
    for _, row in df.iterrows():
        upsert_risk_score(
            engine,
            event_id=int(row["event_id"]),
            cluster_id=int(row["cluster_id"]) if pd.notna(row["cluster_id"]) else None,
            result={
                "predicted_label": row["predicted_label"],
                "risk_score": float(row["risk_score"]),
                "risk_tier": row["risk_tier"],
            },
        )
        count += 1
    print(f"Backfilled {count} historical rows.")
else:
    print(f"{csv_path} does not exist. Nothing to backfill.")
