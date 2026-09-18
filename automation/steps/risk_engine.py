# automation/steps/risk_engine.py
"""
Reuses the EXACT formula from the existing risk_score.py (Part 17.8):
severity weights, ADJUSTMENT_RANGE=4, tier thresholds. Loads the
pre-fit calibrated model (see fit_and_save_calibrated_model.py) instead
of re-fitting it on every run.
"""
import json
import joblib
import pandas as pd

SEVERITY_WEIGHTS = {
    "Other/Unknown": 0,
    "Wildfire / Natural Fire": 20,
    "Persistent Industrial Thermal Source": 60,
    "Industrial Fire": 100,
}
ADJUSTMENT_RANGE = 4  # final tuned value, Decision E in the ML report


class RiskEngine:
    def __init__(
        self,
        calibrated_model_path: str = "ml/models/calibrated_risk_model.joblib",
        class_names: list[str] = None,
    ):
        self.model = joblib.load(calibrated_model_path)
        if class_names is None:
            with open("ml/training/label_mapping.json") as f:
                label_map = json.load(f)
            self.class_names = [name for name, _ in sorted(label_map.items(), key=lambda kv: kv[1])]
        else:
            self.class_names = class_names

    def score(self, feature_row: pd.DataFrame, raw_event: dict) -> dict:
        proba = self.model.predict_proba(feature_row)[0]
        base_score = sum(p * SEVERITY_WEIGHTS.get(name, 0) for p, name in zip(proba, self.class_names))

        frp_val = raw_event.get("frp")
        frp_norm = min(max((float(frp_val) if frp_val is not None else 0.0) / 50.0, 0.0), 1.0)

        active_days_val = raw_event.get("active_days")
        persistence_norm = min(max((float(active_days_val) if active_days_val is not None else 0.0) / 30.0, 0.0), 1.0)

        distance = raw_event.get("nearest_facility_distance_m")
        proximity_norm = 1.0 - min(max((float(distance) if distance is not None else 5000.0) / 5000.0, 0.0), 1.0)

        intensity = 0.4 * frp_norm + 0.3 * persistence_norm + 0.3 * proximity_norm
        adjustment = ADJUSTMENT_RANGE * (intensity - 0.5) * 2

        risk_score = float(round(min(max(base_score + adjustment, 0.0), 100.0), 1))
        predicted_label = self.class_names[int(proba.argmax())]

        if risk_score >= 70:
            tier = "Critical"
        elif risk_score >= 40:
            tier = "High"
        elif risk_score >= 15:
            tier = "Medium"
        else:
            tier = "Low"

        return {
            "predicted_label": predicted_label,
            "risk_score": risk_score,
            "risk_tier": tier,
        }
