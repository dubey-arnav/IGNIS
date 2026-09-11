import requests
import json
import os
import time

OVERPASS_URL = "https://overpass.kumi.systems/api/interpreter"

headers = {
    "User-Agent": "IGNIS-hackathon-project (student project, contact: youremail@example.com)",
}

# Full target area: south, west, north, east
FULL_BBOX = (6, 68, 37, 97)  # roughly all of India

# How many pieces to cut the area into, per side (3 = a 3x3 grid = 9 requests)
GRID_SIZE = 4

def make_grid(bbox, grid_size):
    south, west, north, east = bbox
    lat_step = (north - south) / grid_size
    lon_step = (east - west) / grid_size

    boxes = []
    for i in range(grid_size):
        for j in range(grid_size):
            s = south + i * lat_step
            n = south + (i + 1) * lat_step
            w = west + j * lon_step
            e = west + (j + 1) * lon_step
            boxes.append(f"{s},{w},{n},{e}")
    return boxes

def build_query(bbox_str):
    return f"""
    [out:json][timeout:90];
    (
      node["man_made"="works"]({bbox_str});
      way["man_made"="works"]({bbox_str});
      way["landuse"="industrial"]({bbox_str});
      node["power"="plant"]({bbox_str});
      way["power"="plant"]({bbox_str});
      node["man_made"="petroleum_well"]({bbox_str});
      way["man_made"="pipeline"]({bbox_str});
    );
    out center tags;
    """

all_elements = []
boxes = make_grid(FULL_BBOX, GRID_SIZE)

for idx, box in enumerate(boxes):
    print(f"Requesting box {idx + 1}/{len(boxes)}: {box}")
    query = build_query(box)

    response = requests.post(OVERPASS_URL, data={"data": query}, headers=headers)

    if response.status_code != 200:
        print(f"  Skipped — status {response.status_code}")
        continue

    data = response.json()

    if "remark" in data:
        print(f"  Remark: {data['remark']}")
        continue

    elements = data.get("elements", [])
    print(f"  Got {len(elements)} elements")
    all_elements.extend(elements)

    time.sleep(2)  # be polite to the shared public server between requests

print(f"\nTotal elements collected: {len(all_elements)}")

os.makedirs("data", exist_ok=True)
with open("data/osm_raw.json", "w", encoding="utf-8") as f:
    json.dump({"elements": all_elements}, f)

print("Saved data/osm_raw.json")