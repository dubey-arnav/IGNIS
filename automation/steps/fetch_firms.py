# automation/steps/fetch_firms.py
"""
Fetches the most recent window of FIRMS detections.
Reuses the SAME endpoint pattern as ingestion/firms/download_firms.py.
"""
import io
import logging
import os
import pandas as pd
import requests

logger = logging.getLogger("ignis.automation.fetch_firms")

FIRMS_BASE_URL = "https://firms.modaps.eosdis.nasa.gov/api/area/csv"


def fetch_recent_firms(bbox: str = "68,6,97,37", days: int = 2, source: str = "VIIRS_SNPP_NRT") -> pd.DataFrame:
    """
    bbox: "west,south,east,north" — same format used by the existing pipeline.
    days: FIRMS' own valid range is 1-5; we default to 2 for safety margin.
    Returns an empty DataFrame (not an exception) on an empty response,
    so the pipeline can continue instead of crashing on a quiet night.
    """
    map_key = os.getenv("FIRMS_MAP_KEY")
    if not map_key:
        raise RuntimeError("FIRMS_MAP_KEY is not set in the environment (.env)")

    if not (1 <= days <= 5):
        raise ValueError(f"FIRMS day-range must be 1-5, got {days}")

    url = f"{FIRMS_BASE_URL}/{map_key}/{source}/{bbox}/{days}"
    logger.info(f"Requesting FIRMS data: source={source} days={days} bbox={bbox}")

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error(f"FIRMS request failed: {e}")
        raise

    if not response.text.strip():
        logger.warning("FIRMS returned an empty response body.")
        return pd.DataFrame()

    df = pd.read_csv(io.StringIO(response.text))

    if df.empty or "latitude" not in df.columns:
        logger.warning(f"FIRMS returned no usable rows. Raw response head: {response.text[:200]}")
        return pd.DataFrame()

    logger.info(f"Fetched {len(df)} raw FIRMS rows.")
    return df
