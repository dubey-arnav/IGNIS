import json
import sys
import os
from sqlalchemy import text

sys.path.append(os.path.join(os.path.dirname(__file__), "..", ".."))
from database.db_connect import engine

with open("data/osm_raw.json", "r", encoding="utf-8") as f:
    data = json.load(f)

def get_coords(element):
    # Nodes have lat/lon directly; ways/relations have a "center" object instead
    if "lat" in element and "lon" in element:
        return element["lat"], element["lon"]
    if "center" in element:
        return element["center"]["lat"], element["center"]["lon"]
    return None, None

def guess_type(tags):
    # Simple priority order to pick one readable category from the raw tags
    if tags.get("power") == "plant":
        return "power_plant"
    if tags.get("man_made") == "works":
        return "industrial_works"
    if tags.get("landuse") == "industrial":
        return "industrial_area"
    if tags.get("man_made") == "petroleum_well":
        return "petroleum_well"
    if tags.get("man_made") == "pipeline":
        return "pipeline"
    return "other"

insert_sql = text("""
    INSERT INTO industrial_sites
        (osm_id, name, type, latitude, longitude, geom, tags, source)
    VALUES
        (:osm_id, :name, :type, :latitude, :longitude,
        ST_SetSRID(ST_MakePoint(:longitude, :latitude), 4326),
        :tags, 'OSM')
""")

rows_inserted = 0
skipped = 0

with engine.begin() as conn:
    for element in data["elements"]:
        lat, lon = get_coords(element)
        if lat is None or lon is None:
            skipped += 1
            continue

        tags = element.get("tags", {})

        conn.execute(insert_sql, {
            "osm_id": element.get("id"),
            "name": tags.get("name"),
            "type": guess_type(tags),
            "latitude": lat,
            "longitude": lon,
            "tags": json.dumps(tags),
        })
        rows_inserted += 1

print(f"Inserted {rows_inserted} rows into industrial_sites")
print(f"Skipped {skipped} elements with no coordinates")