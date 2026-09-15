import numpy as np
import pandas as pd

from app.ml.model_loader import load
from app.utils.constants import SEVERITY_WEIGHTS, tier_for_score

ADJUSTMENT_RANGE = 4  # Decision E from the ML report. Do not change casually.


def predict(payload: dict) -> dict:
    state = load()
    model = state["model"]
    cfg = state["feature_config"]
    class_names = state["class_names"]

    categorical, numeric = cfg["categorical"], cfg["numeric"]
    features = categorical + numeric
    levels = cfg["category_levels"]

    df = pd.DataFrame([{f: payload.get(f) for f in features}])

    # CRITICAL (ML bug #5): categorical columns must be re-cast with the exact
    # category levels seen during training. Skip this and you get silently
    # WRONG predictions, not an error. An unseen category becomes NaN, which
    # XGBoost handles natively as missing.
    for col in categorical:
        df[col] = pd.Categorical(df[col], categories=levels[col])
    for col in numeric:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    proba = model.predict_proba(df[features])[0]
    idx = int(np.argmax(proba))
    label = class_names[idx]
    probabilities = {n: round(float(p), 4) for n, p in zip(class_names, proba)}

    base = sum(float(p) * SEVERITY_WEIGHTS[n] for n, p in zip(class_names, proba))

    def norm(v, lo, hi):
        if v is None or (isinstance(v, float) and np.isnan(v)):
            return 0.0
        return float(np.clip((float(v) - lo) / (hi - lo), 0, 1))

    intensity = (0.4 * norm(payload.get("frp"), 0, 50)
                 + 0.3 * norm(payload.get("active_days"), 0, 30)
                 + 0.3 * (1 - norm(payload.get("nearest_facility_distance_m"), 0, 5000)))
    score = float(np.clip(base + ADJUSTMENT_RANGE * (intensity - 0.5) * 2, 0, 100))
    score = round(score, 1)

    missing = [f for f in features if payload.get(f) is None]
    return {
        "predicted_label": label,
        "class_probabilities": probabilities,
        "risk_score": score,
        "risk_tier": tier_for_score(score),
        "missing_features": missing,
        "warnings": _warnings(missing),
    }


def _warnings(missing):
    w = []
    cluster_feats = {"total_detections", "active_days", "cluster_mean_frp",
                     "cluster_max_frp", "persistence_score"}
    if cluster_feats & set(missing):
        w.append("Cluster-level features are missing. These describe a cluster of "
                 "detections, not a single new one, and active_days is the second "
                 "most important feature. Prediction quality degrades without them.")
    w.append("Probabilities here are uncalibrated and tend to be overconfident. "
             "Stored historical scores used isotonic calibration.")
    return w