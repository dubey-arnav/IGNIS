import pandas as pd

df = pd.read_csv("data/firms_raw.csv")

print("Raw rows:", len(df))
print(df.columns.tolist())

  # Drop rows missing essential fields
df = df.dropna(subset=["latitude", "longitude", "acq_date"])

  # Basic sanity range checks for lat/lon
df = df[(df["latitude"].between(-90, 90)) & (df["longitude"].between(-180, 180))]

  # Remove exact duplicate detections
df = df.drop_duplicates()

print("Clean rows:", len(df))

df.to_csv("data/firms_clean.csv", index=False)
print("Saved data/firms_clean.csv")