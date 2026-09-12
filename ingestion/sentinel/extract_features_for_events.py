import sys
import os
import requests
import rasterio
import numpy as np
import pandas as pd
from io import BytesIO
from dotenv import load_dotenv

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from database.db_connect import engine
from sqlalchemy import text

load_dotenv()
CLIENT_ID = os.getenv("SENTINEL_CLIENT_ID")
CLIENT_SECRET = os.getenv("SENTINEL_CLIENT_SECRET")
TOKEN_URL = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
PROCESS_URL = "https://sh.dataspace.copernicus.eu/process/v1"

evalscript = """
//VERSION=3
function setup() {
return {
    input: [{ bands: ["B03","B04","B08","B11","B12","SCL"] }],
    output: { bands: 6, sampleType: "FLOAT32" }
};
}
function evaluatePixel(sample) {
return [sample.B03, sample.B04, sample.B08, sample.B11, sample.B12, sample.SCL];
}
"""

def get_token():
    r = requests.post(TOKEN_URL, data={
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    })
    r.raise_for_status()
    return r.json()["access_token"]

def buffer_bbox(lat, lon, half_size_deg=0.01):
    return [lon - half_size_deg, lat - half_size_deg, lon + half_size_deg, lat + half_size_deg]

def fetch_and_calc(token, lat, lon):
    payload = {
        "input": {
            "bounds": {
                "bbox": buffer_bbox(lat, lon),
                "properties": {"crs": "http://www.opengis.net/def/crs/EPSG/0/4326"},
            },
            "data": [{
                "type": "sentinel-2-l2a",
                "dataFilter": {
                    "timeRange": {"from": "2026-08-01T00:00:00Z", "to": "2026-09-01T00:00:00Z"},
                    "maxCloudCoverage": 50,
                },
            }],
        },
        "output": {
            "width": 64, "height": 64,
            "responses": [{"identifier": "default", "format": {"type": "image/tiff"}}],
        },
        "evalscript": evalscript,
    }
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    r = requests.post(PROCESS_URL, headers=headers, json=payload)
    if r.status_code != 200:
        return None

    with rasterio.open(BytesIO(r.content)) as src:
        green, red, nir, swir1, swir2, scl = [src.read(i).astype(float) for i in range(1, 7)]
        scl = scl.astype(int)

    valid_mask = ~np.isin(scl, [0, 1, 3, 8, 9, 10])
    if valid_mask.sum() == 0:
        return None

    def idx(a, b):
        d = a + b
        d[d == 0] = np.nan
        return ((a - b) / d)[valid_mask]

    return {
        "ndvi_mean": float(np.nanmean(idx(nir, red))),
        "ndbi_mean": float(np.nanmean(idx(swir1, nir))),
        "ndwi_mean": float(np.nanmean(idx(green, nir))),
        "swir1_mean": float(np.nanmean(swir1[valid_mask])),
        "swir2_mean": float(np.nanmean(swir2[valid_mask])),
        "valid_pixel_fraction": float(valid_mask.sum() / scl.size),
    }

# Pull a small sample of real event locations to test against (limit while testing!)
with engine.connect() as conn:
    result = conn.execute(text("SELECT id, latitude, longitude FROM thermal_events LIMIT 5"))
    events = result.fetchall()

token = get_token()
rows = []
for event_id, lat, lon in events:
    print(f"Fetching Sentinel-2 features for event {event_id} ({lat}, {lon})...")
    feats = fetch_and_calc(token, lat, lon)
    if feats is None:
        print("  No usable data (cloud cover or no scene) — skipped")
        continue
    feats["event_id"] = event_id
    rows.append(feats)

df = pd.DataFrame(rows)
os.makedirs("data", exist_ok=True)
df.to_csv("data/sentinel_features.csv", index=False)
print(f"\nSaved {len(df)} rows to data/sentinel_features.csv")