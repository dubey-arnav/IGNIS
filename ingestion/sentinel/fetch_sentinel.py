import os
import requests
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("SENTINEL_CLIENT_ID")
CLIENT_SECRET = os.getenv("SENTINEL_CLIENT_SECRET")

TOKEN_URL = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
PROCESS_URL = "https://sh.dataspace.copernicus.eu/process/v1"

def get_token():
    response = requests.post(
        TOKEN_URL,
        data={
            "grant_type": "client_credentials",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        },
    )
    response.raise_for_status()
    return response.json()["access_token"]

# Evalscript: tells Sentinel Hub which bands to return, as raw numbers (not a picture)
evalscript = """
//VERSION=3
function setup() {
return {
    input: [{ bands: ["B03", "B04", "B08", "B11", "B12", "SCL"] }],
    output: { bands: 6, sampleType: "FLOAT32" }
};
}
function evaluatePixel(sample) {
return [sample.B03, sample.B04, sample.B08, sample.B11, sample.B12, sample.SCL];
}
"""

# Small test bbox: west, south, east, north (a few km wide — keep test requests small)
bbox = [77.20, 28.55, 77.25, 28.60]  # example near Delhi — adjust to your real area

payload = {
    "input": {
        "bounds": {
            "bbox": bbox,
            "properties": {"crs": "http://www.opengis.net/def/crs/EPSG/0/4326"},
        },
        "data": [
            {
                "type": "sentinel-2-l2a",
                "dataFilter": {
                    "timeRange": {
                        "from": "2026-08-01T00:00:00Z",
                        "to": "2026-09-01T00:00:00Z",
                    },
                    "maxCloudCoverage": 40,
                },
            }
        ],
    },
    "output": {
        "width": 256,
        "height": 256,
        "responses": [{"identifier": "default", "format": {"type": "image/tiff"}}],
    },
    "evalscript": evalscript,
}

token = get_token()
headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

response = requests.post(PROCESS_URL, headers=headers, json=payload)
response.raise_for_status()

os.makedirs("data", exist_ok=True)
out_path = "data/sentinel_test.tiff"
with open(out_path, "wb") as f:
    f.write(response.content)

print(f"Saved {out_path} ({len(response.content)} bytes)")