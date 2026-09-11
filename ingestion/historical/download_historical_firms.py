import os
import time
import requests
import pandas as pd
from datetime import date, timedelta
from dotenv import load_dotenv

load_dotenv()
MAP_KEY = os.getenv("FIRMS_MAP_KEY")

bbox = "68,6,97,37"          # same real area you've been using — keep it consistent!
source = "VIIRS_SNPP_NRT"    # NRT only covers roughly the last ~2 months of history
chunk_days = 5               # the real API limit you discovered earlier
total_days_back = 60         # how far back in total you want to look

base_url = "https://firms.modaps.eosdis.nasa.gov/api/area/csv/{key}/{source}/{bbox}/{days}/{date}"

all_frames = []
today = date.today()

start = 0
while start < total_days_back:
    chunk_start_date = today - timedelta(days=start + chunk_days - 1)
    date_str = chunk_start_date.strftime("%Y-%m-%d")

    url = base_url.format(key=MAP_KEY, source=source, bbox=bbox, days=chunk_days, date=date_str)
    print(f"Requesting {chunk_days} days starting {date_str} ...")

    response = requests.get(url)
    if response.status_code != 200:
        print(f"  Skipped — status {response.status_code}: {response.text[:150]}")
        start += chunk_days
        time.sleep(1)
        continue

    # Turn the CSV text into a DataFrame directly, skip if it's just an empty header
    from io import StringIO
    chunk_df = pd.read_csv(StringIO(response.text))
    print(f"  Got {len(chunk_df)} rows")
    all_frames.append(chunk_df)

    start += chunk_days
    time.sleep(1)  # be polite to the shared API between requests

combined = pd.concat(all_frames, ignore_index=True)
combined = combined.drop_duplicates()

print(f"\nTotal historical rows (after removing duplicates): {len(combined)}")

os.makedirs("data", exist_ok=True)
combined.to_csv("data/firms_historical_raw.csv", index=False)
print("Saved data/firms_historical_raw.csv")
