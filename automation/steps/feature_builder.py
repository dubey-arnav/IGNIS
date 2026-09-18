# automation/steps/feature_builder.py
"""
Assembles the 19-feature vector the model was trained on (Part 17.5 of the
handoff report). Column names and order must match ml/models/feature_config.json
exactly — that file is the single source of truth, loaded at runtime rather
than hardcoded here, so if the model is ever retrained with different
features this file does not need to change.
"""
import json
import logging
import pandas as pd

logger = logging.getLogger("ignis.automation.feature_builder")


def build_feature_row(
    event: dict,
    facility_features: dict,
    cluster_features: dict,
    sentinel_features: dict,
    feature_config_path: str = "ml/models/feature_config.json",
) -> pd.DataFrame:
    """
    event: raw thermal_events row (dict) — confidence, daynight, bright_ti4, bright_ti5, frp.
    facility_features: output of Step A4 for this event.
    cluster_features: {"total_detections":..., "active_days":..., "cluster_mean_frp":...,
                       "cluster_max_frp":..., "persistence_score":...} — None for un-clustered events.
    sentinel_features: output of Step A6 for this event.
    Returns a 1-row DataFrame with correct categorical dtypes applied.
    """
    with open(feature_config_path) as f:
        config = json.load(f)

    categorical = config["categorical"]  # ["confidence", "daynight", "nearest_facility_type"]
    numeric = config["numeric"]
    category_levels = config["category_levels"]

    cluster_features = cluster_features or {}
    facility_features = facility_features or {}
    sentinel_features = sentinel_features or {}

    row = {
        "confidence": event.get("confidence"),
        "daynight": event.get("daynight"),
        "nearest_facility_type": facility_features.get("nearest_facility_type"),
        "bright_ti4": float(event["bright_ti4"]) if event.get("bright_ti4") is not None else None,
        "bright_ti5": float(event["bright_ti5"]) if event.get("bright_ti5") is not None else None,
        "frp": float(event["frp"]) if event.get("frp") is not None else None,
        "nearest_facility_distance_m": float(facility_features["nearest_facility_distance_m"]) if facility_features.get("nearest_facility_distance_m") is not None else None,
        "facilities_within_radius": int(facility_features.get("facilities_within_radius") or 0),
        "total_detections": int(cluster_features["total_detections"]) if cluster_features.get("total_detections") is not None else 1,
        "active_days": int(cluster_features["active_days"]) if cluster_features.get("active_days") is not None else 1,
        "cluster_mean_frp": float(cluster_features["cluster_mean_frp"]) if cluster_features.get("cluster_mean_frp") is not None else None,
        "cluster_max_frp": float(cluster_features["cluster_max_frp"]) if cluster_features.get("cluster_max_frp") is not None else None,
        "persistence_score": float(cluster_features["persistence_score"]) if cluster_features.get("persistence_score") is not None else 0.0,
        "ndvi_mean": float(sentinel_features["ndvi_mean"]) if sentinel_features.get("ndvi_mean") is not None else None,
        "ndbi_mean": float(sentinel_features["ndbi_mean"]) if sentinel_features.get("ndbi_mean") is not None else None,
        "ndwi_mean": float(sentinel_features["ndwi_mean"]) if sentinel_features.get("ndwi_mean") is not None else None,
        "swir1_mean": float(sentinel_features["swir1_mean"]) if sentinel_features.get("swir1_mean") is not None else None,
        "swir2_mean": float(sentinel_features["swir2_mean"]) if sentinel_features.get("swir2_mean") is not None else None,
        "valid_pixel_fraction": float(sentinel_features["valid_pixel_fraction"]) if sentinel_features.get("valid_pixel_fraction") is not None else None,
    }

    missing = [c for c in categorical + numeric if c not in row]
    if missing:
        raise ValueError(f"feature_config.json expects columns not built here: {missing}")

    df = pd.DataFrame([row])[categorical + numeric]

    # CRITICAL — same trap flagged as ML Bug #5: categorical columns must be
    # re-cast against the EXACT levels seen during training, or predictions
    # are silently wrong rather than erroring.
    for col in categorical:
        df[col] = pd.Categorical(df[col], categories=category_levels[col])

    for col in numeric:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df
