import rasterio
import numpy as np

with rasterio.open("data/sentinel_test.tiff") as src:
    green = src.read(1).astype(float)   # B03
    red   = src.read(2).astype(float)   # B04
    nir   = src.read(3).astype(float)   # B08
    swir1 = src.read(4).astype(float)   # B11
    swir2 = src.read(5).astype(float)   # B12
    scl   = src.read(6).astype(int)     # Scene Classification

# Cloud mask: exclude SCL codes for no-data, saturated, cloud-shadow, cloud, thin-cirrus
cloud_codes = [0, 1, 3, 8, 9, 10]
valid_mask = ~np.isin(scl, cloud_codes)

print(f"Total pixels: {scl.size}, Valid (non-cloud) pixels: {valid_mask.sum()}")

def safe_index(a, b, mask):
    denom = a + b
    denom[denom == 0] = np.nan
    index = (a - b) / denom
    return index[mask]

ndvi_valid = safe_index(nir, red, valid_mask)      # vegetation index
ndbi_valid = safe_index(swir1, nir, valid_mask)    # built-up index
ndwi_valid = safe_index(green, nir, valid_mask)    # water index

features = {
    "ndvi_mean": np.nanmean(ndvi_valid),
    "ndvi_std": np.nanstd(ndvi_valid),
    "ndbi_mean": np.nanmean(ndbi_valid),
    "ndbi_std": np.nanstd(ndbi_valid),
    "ndwi_mean": np.nanmean(ndwi_valid),
    "ndwi_std": np.nanstd(ndwi_valid),
    "swir1_mean": np.nanmean(swir1[valid_mask]),
    "swir2_mean": np.nanmean(swir2[valid_mask]),
    "valid_pixel_fraction": valid_mask.sum() / scl.size,
}

print("\nCalculated features:")
for k, v in features.items():
    print(f"  {k}: {v:.4f}")