import json
import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.calibration import CalibratedClassifierCV
from sklearn.utils.class_weight import compute_sample_weight

MODEL_PATH = "ml/models/xgb_fire_classifier.json"
FEATURE_CONFIG_PATH = "ml/models/feature_config.json"
LABEL_MAP_PATH = "ml/training/label_mapping.json"
TRAIN_DATA_PATH = "data/train_dataset.csv"

SEVERITY_WEIGHTS = {
    "Other/Unknown": 0, "Wildfire / Natural Fire": 20,
    "Persistent Industrial Thermal Source": 60, "Industrial Fire": 100,
}
ADJUSTMENT_RANGE = 4


class RiskScorer:
    """Load once (e.g. when the API starts), then call .score_event() many times."""

    def __init__(self):
        with open(FEATURE_CONFIG_PATH) as f:
            config = json.load(f)
        self.categorical = config["categorical"]
        self.numeric = config["numeric"]
        self.features = self.categorical + self.numeric
        self.category_levels = config["category_levels"]

        with open(LABEL_MAP_PATH) as f:
            label_map = json.load(f)
        self.class_names = [n for n, _ in sorted(label_map.items(), key=lambda kv: kv[1])]

        train_df = pd.read_csv(TRAIN_DATA_PATH)
        for col in self.categorical:
            train_df[col] = train_df[col].astype("category")
        X_train, y_train = train_df[self.features], train_df["target"]
        sample_weight = compute_sample_weight("balanced", y_train)

        base_model = xgb.XGBClassifier(
            n_estimators=300, max_depth=5, learning_rate=0.1,
            objective="multi:softprob", num_class=len(self.class_names),
            enable_categorical=True, eval_metric="mlogloss", random_state=42,
        )
        self.model = CalibratedClassifierCV(base_model, method="isotonic", cv=5)
        self.model.fit(X_train, y_train, sample_weight=sample_weight)

    def score_event(self, event: dict) -> dict:
        """event must contain all 19 feature keys (see report Part 17.10.6).
        Cluster-level fields (total_detections, active_days, cluster_mean_frp,
        cluster_max_frp, persistence_score) may be missing for a brand-new,
        unclustered detection -- XGBoost treats missing values natively."""
        df = pd.DataFrame([event])
        for col in self.categorical:
            df[col] = pd.Categorical(df[col], categories=self.category_levels[col])
        X = df[self.features]

        proba = self.model.predict_proba(X)[0]
        predicted_label = self.class_names[int(np.argmax(proba))]

        base_score = sum(proba[i] * SEVERITY_WEIGHTS[name] for i, name in enumerate(self.class_names))

        frp_norm = min(max(event.get("frp", 0), 0), 50) / 50
        persistence_norm = min(max(event.get("active_days", 0) or 0, 0), 30) / 30
        dist = event.get("nearest_facility_distance_m", 5000) or 5000
        proximity_norm = 1 - (min(max(dist, 0), 5000) / 5000)
        intensity = max(0, min(1, 0.4 * frp_norm + 0.3 * persistence_norm + 0.3 * proximity_norm))
        adjustment = ADJUSTMENT_RANGE * (intensity - 0.5) * 2

        risk_score = round(max(0, min(100, base_score + adjustment)), 1)
        risk_tier = "Critical" if risk_score >= 70 else "High" if risk_score >= 40 else "Medium" if risk_score >= 15 else "Low"

        return {
            "predicted_label": predicted_label,
            "class_probabilities": {name: round(float(p), 4) for name, p in zip(self.class_names, proba)},
            "risk_score": risk_score,
            "risk_tier": risk_tier,
        }