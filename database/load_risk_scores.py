import os
import pandas as pd
import psycopg2
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv("DB_HOST", "localhost"),
    port=os.getenv("DB_PORT", "5432"),
    dbname=os.getenv("DB_NAME", "IGNIS"),
    user=os.getenv("DB_USER", "postgres"),
    password=os.getenv("DB_PASSWORD"),
)
cur = conn.cursor()

df = pd.read_csv("data/risk_scores.csv")

# IMPORTANT: pandas gives us numpy float64/int64 types, which psycopg2
# cannot insert directly -- this is the exact bug flagged in the report.
# Every numeric value must be wrapped in float()/int() (or None for nulls)
# before it goes into the SQL insert.

inserted = 0
for _, row in df.iterrows():
    cluster_id = int(row["cluster_id"]) if pd.notna(row["cluster_id"]) else None
    cur.execute(
        """
        INSERT INTO risk_scores (event_id, cluster_id, predicted_label, risk_score, risk_tier, model_version)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (
            int(row["event_id"]),
            cluster_id,
            str(row["predicted_label"]),
            float(row["risk_score"]),
            str(row["risk_tier"]),
            "xgb_v1_calibrated",
        ),
    )
    inserted += 1

conn.commit()
print(f"Inserted {inserted} rows into risk_scores")

cur.close()
conn.close()