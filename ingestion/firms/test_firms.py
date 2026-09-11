import os
import requests
from dotenv import load_dotenv

load_dotenv()
MAP_KEY = os.getenv("FIRMS_MAP_KEY")

  # bounding box: west,south,east,north  (small test area)
bbox = "77,28,78,29"
days = "1"
source = "VIIRS_SNPP_NRT"

url = f"https://firms.modaps.eosdis.nasa.gov/api/area/csv/{MAP_KEY}/{source}/{bbox}/{days}"

response = requests.get(url)
print("Status code:", response.status_code)
print(response.text[:500])  # print first 500 characters only