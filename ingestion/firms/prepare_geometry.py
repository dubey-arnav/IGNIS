import pandas as pd
from shapely.geometry import Point
import geopandas as gpd

df = pd.read_csv("data/firms_clean.csv")

geometry = [Point(xy) for xy in zip(df["longitude"], df["latitude"])]
gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")

print(gdf.head())
print("Rows with geometry:", len(gdf))

gdf.to_file("data/firms_geo.geojson", driver="GeoJSON")
print("Saved data/firms_geo.geojson")