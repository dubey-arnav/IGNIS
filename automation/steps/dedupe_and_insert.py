# automation/steps/dedupe_and_insert.py
import hashlib
import logging
import pandas as pd
from sqlalchemy import text

logger = logging.getLogger("ignis.automation.dedupe")


def normalize_acq_time(val) -> str:
    """Normalize event time to 4-digit HHMM for deterministic hashing."""
    if pd.isna(val) or val is None or str(val).strip() == "":
        return ""
    s = str(val).strip()
    if ":" in s:
        parts = s.split(":")
        return f"{parts[0].zfill(2)}{parts[1].zfill(2)}"
    try:
        return str(int(float(s))).zfill(4)
    except Exception:
        return s



def format_acq_time(raw_time) -> str | None:
    """Format time string into HH:MM:00 for PostgreSQL TIME column."""
    if pd.isna(raw_time) or raw_time is None or str(raw_time).strip() == "":
        return None
    s = str(raw_time).strip()
    if ":" in s:
        return s
    try:
        t = str(int(float(s))).zfill(4)
        return f"{t[:2]}:{t[2:]}:00"
    except Exception:
        return s


def compute_firms_uid(row: pd.Series) -> str:
    """
    Natural key: same pixel, same date, same time, same satellite platform
    cannot legitimately appear twice in FIRMS. Rounding lat/lon to 4 decimal
    places (~11m) absorbs floating-point noise without merging distinct
    nearby detections.
    """
    key = "|".join([
        f"{round(float(row['latitude']), 4)}",
        f"{round(float(row['longitude']), 4)}",
        str(row.get("acq_date", row.get("event_date"))),
        normalize_acq_time(row.get("acq_time", row.get("event_time"))),
        str(row.get("satellite", "")),
    ])
    return hashlib.md5(key.encode()).hexdigest()


def insert_new_events(engine, df: pd.DataFrame) -> dict:
    """
    Returns counts: {"received": N, "inserted": N, "duplicates": N}
    Uses ON CONFLICT (firms_uid) DO NOTHING so this function is safe to call
    with the exact same rows twice.
    """
    if df.empty:
        return {"received": 0, "inserted": 0, "duplicates": 0}

    df = df.copy()
    df["firms_uid"] = df.apply(compute_firms_uid, axis=1)

    inserted_ids = []
    with engine.begin() as conn:  # one transaction — all-or-nothing per batch
        for _, row in df.iterrows():
            result = conn.execute(
                text("""
                    INSERT INTO thermal_events
                    (latitude, longitude, geom, event_date, event_time,
                    satellite, confidence, bright_ti4, bright_ti5, frp,
                    daynight, source, firms_uid)
                    VALUES
                    (:latitude, :longitude,
                    ST_SetSRID(ST_MakePoint(:longitude, :latitude), 4326),
                    :event_date, :event_time, :satellite, :confidence,
                    :bright_ti4, :bright_ti5, :frp, :daynight,
                    'FIRMS', :firms_uid)
                    ON CONFLICT (firms_uid) DO NOTHING
                    RETURNING id
                """),
                {
                    "latitude": float(row["latitude"]),
                    "longitude": float(row["longitude"]),
                    "event_date": row.get("acq_date", row.get("event_date")),
                    "event_time": format_acq_time(row.get("acq_time", row.get("event_time"))),
                    "satellite": str(row.get("satellite")) if pd.notna(row.get("satellite")) else None,
                    "confidence": str(row.get("confidence")) if pd.notna(row.get("confidence")) else None,
                    "bright_ti4": float(row["bright_ti4"]) if pd.notna(row.get("bright_ti4")) else None,
                    "bright_ti5": float(row["bright_ti5"]) if pd.notna(row.get("bright_ti5")) else None,
                    "frp": float(row["frp"]) if pd.notna(row.get("frp")) else None,
                    "daynight": str(row.get("daynight")) if pd.notna(row.get("daynight")) else None,
                    "firms_uid": row["firms_uid"],
                },
            )
            row_res = result.fetchone()
            if row_res:
                inserted_ids.append(row_res[0])

    duplicates = len(df) - len(inserted_ids)
    logger.info(f"Insert result: received={len(df)} inserted={len(inserted_ids)} duplicates={duplicates}")
    return {"received": len(df), "inserted": len(inserted_ids), "duplicates": duplicates, "inserted_ids": inserted_ids}

