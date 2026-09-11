import os
import requests
from dotenv import load_dotenv

load_dotenv()
MAP_KEY = os.getenv("FIRMS_MAP_KEY")

  # Adjust this bounding box to your real area of interest: west,south,east,north
bbox = "68,6,97,37"      # example: roughly all of India
days = "5"               # NRT area API allows up to 5 days per request
source = "VIIRS_SNPP_NRT"

url = f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{MAP_KEY}/{source}/{bbox}/{days}"

response = requests.get(url)
response.raise_for_status()  # stops the script with a clear error if the request failed

os.makedirs("data", exist_ok=True)
out_path = "data/firms_raw.csv"
with open(out_path, "w", encoding="utf-8") as f:
      f.write(response.text)

print(f"Saved {out_path} ({len(response.text)} characters)")
