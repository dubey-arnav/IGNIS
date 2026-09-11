import pandas as pd
from sqlalchemy import text
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..",".."))
from database.db_connect import engine

def format_acq_time(raw_time):
    if pd.isna(raw_time):
        return None
    t = str(int(raw_time)).zfill(4)   # pad to 4 digits, e.g. "735" -> "0735"
    return f"{t[:2]}:{t[2:]}:00"      # "0735" -> "07:35:00"

df = pd.read_csv("data/firms_clean.csv")

insert_sql = text("""
    INSERT INTO thermal_events
        (latitude, longitude, geom, event_date, event_time, satellite,
        instrument, confidence, bright_ti4, bright_ti5, frp, daynight, source)
    VALUES
        (:latitude, :longitude,
        ST_SetSRID(ST_MakePoint(:longitude, :latitude), 4326),
        :event_date, :event_time, :satellite, :instrument, :confidence,
        :bright_ti4, :bright_ti5, :frp, :daynight, 'FIRMS')
""")

rows_inserted = 0
with engine.begin() as conn:
 for _, row in df.iterrows():
    conn.execute(insert_sql, {
        "latitude": row.get("latitude"),
        "longitude": row.get("longitude"),
        "event_date": row.get("acq_date"),
        "event_time": format_acq_time(row.get("acq_time")),
        "satellite": row.get("satellite"),
        "instrument": row.get("instrument"),
        "confidence": str(row.get("confidence")) if pd.notna(row.get("confidence")) else None,
        "bright_ti4": row.get("bright_ti4"),
        "bright_ti5": row.get("bright_ti5"),
        "frp": row.get("frp"),
        "daynight": row.get("daynight"),
    })
    rows_inserted += 1

print(f"Inserted {rows_inserted} rows into thermal_events")
