import os
import time
import requests
import pandas as pd
from io import StringIO
from datetime import date, timedelta
from dotenv import load_dotenv

load_dotenv()
MAP_KEY = os.getenv("FIRMS_MAP_KEY")

bbox = "68,6,97,37"          # same real area used throughout — keep consistent
source = "VIIRS_SNPP_NRT"
chunk_days = 5                # confirmed real limit for this source
total_days_back = 60          # how far back to try — NRT may not actually go this far

all_frames = []
today = date.today()

start = 0
while start < total_days_back:
    chunk_start_date = today - timedelta(days=start + chunk_days - 1)
    date_str = chunk_start_date.strftime("%Y-%m-%d")

    url = f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{MAP_KEY}/{source}/{bbox}/{chunk_days}/{date_str}"
    print("Requesting URL:", url)

    response = requests.get(url)

    if response.status_code != 200:
        print(f"  Skipped — status {response.status_code}: {response.text[:200]}")
        start += chunk_days
        time.sleep(1)
        continue

    try:
        chunk_df = pd.read_csv(StringIO(response.text))
    except pd.errors.EmptyDataError:
        print("  No data in this window (empty response) — skipped")
        start += chunk_days
        time.sleep(1)
        continue

    print(f"  Got {len(chunk_df)} rows")
    if len(chunk_df) > 0:
        all_frames.append(chunk_df)

    start += chunk_days
    time.sleep(1)

if len(all_frames) == 0:
    print("\nNo historical data was retrieved at all. Check the 'Requesting URL' lines above for clues.")
else:
    combined = pd.concat(all_frames, ignore_index=True)
    combined = combined.drop_duplicates()

    print(f"\nTotal historical rows (after removing duplicates): {len(combined)}")

    os.makedirs("data", exist_ok=True)
    combined.to_csv("data/firms_historical_raw.csv", index=False)
    print("Saved data/firms_historical_raw.csv")