import json
import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.calibration import CalibratedClassifierCV
from sklearn.utils.class_weight import compute_sample_weight

FULL_DATA_PATH = "data/training_dataset.csv"
TRAIN_DATA_PATH = "data/train_dataset.csv"  # needed to refit calibration
FEATURE_CONFIG_PATH = "ml/models/feature_config.json"
MODEL_PATH = "ml/models/xgb_fire_classifier.json"
LABEL_MAP_PATH = "ml/training/label_mapping.json"
OUTPUT_PATH = "data/risk_scores.csv"

with open(FEATURE_CONFIG_PATH) as f:
    config = json.load(f)
CATEGORICAL, NUMERIC = config["categorical"], config["numeric"]
FEATURES = CATEGORICAL + NUMERIC
CATEGORY_LEVELS = config["category_levels"]

with open(LABEL_MAP_PATH) as f:
    LABEL_MAP = json.load(f)
CLASS_NAMES = [name for name, _ in sorted(LABEL_MAP.items(), key=lambda kv: kv[1])]

# ---- Step 1: Calibrate probabilities ----
# Raw XGBoost probabilities are overconfident (>0.99 for 98% of events).
# Calibration re-maps them to better reflect genuine uncertainty, using the
# training set with 5-fold cross-validation internally.
train_df = pd.read_csv(TRAIN_DATA_PATH)
for col in CATEGORICAL:
    train_df[col] = train_df[col].astype("category")
X_train, y_train = train_df[FEATURES], train_df["target"]
sample_weight = compute_sample_weight("balanced", y_train)

base_model = xgb.XGBClassifier(
    n_estimators=300, max_depth=5, learning_rate=0.1,
    objective="multi:softprob", num_class=len(CLASS_NAMES),
    enable_categorical=True, eval_metric="mlogloss", random_state=42,
)
calibrated_model = CalibratedClassifierCV(base_model, method="isotonic", cv=5)
calibrated_model.fit(X_train, y_train, sample_weight=sample_weight)

# ---- Step 2: Score the full dataset ----
df = pd.read_csv(FULL_DATA_PATH)
for col in CATEGORICAL:
    df[col] = pd.Categorical(df[col], categories=CATEGORY_LEVELS[col])
X = df[FEATURES]
proba = calibrated_model.predict_proba(X)

df["predicted_label"] = [CLASS_NAMES[i] for i in proba.argmax(axis=1)]

# ---- Step 3: Base score from calibrated class probabilities ----
SEVERITY_WEIGHTS = {
    "Other/Unknown": 0,
    "Wildfire / Natural Fire": 20,
    "Persistent Industrial Thermal Source": 60,
    "Industrial Fire": 100,
}
base_score = np.zeros(len(df))
for i, name in enumerate(CLASS_NAMES):
    base_score += proba[:, i] * SEVERITY_WEIGHTS[name]

# ---- Step 4: Continuous intensity adjustment (the actual fix) ----
# Even among events the model is equally sure about, real severity varies.
# This nudges the score within its tier based on raw signal strength:
#   - frp: fire radiative power, capped at 50 MW (a strong detection)
#   - active_days: how long this source has persisted, capped at 30 days
#   - proximity: how close to a facility, capped at 5km
frp_norm = (df["frp"].clip(0, 50) / 50).fillna(0)
persistence_norm = (df["active_days"].clip(0, 30) / 30).fillna(0)
proximity_norm = (1 - (df["nearest_facility_distance_m"].clip(0, 5000) / 5000)).fillna(0)
intensity = (0.4 * frp_norm + 0.3 * persistence_norm + 0.3 * proximity_norm).clip(0, 1)

ADJUSTMENT_RANGE = 4  # max points this can shift the score, either direction
adjustment = ADJUSTMENT_RANGE * (intensity - 0.5) * 2
df["risk_score"] = (base_score + adjustment).clip(0, 100).round(1)

def tier(score):
    if score >= 70: return "Critical"
    if score >= 40: return "High"
    if score >= 15: return "Medium"
    return "Low"
df["risk_tier"] = df["risk_score"].apply(tier)

print("=== Risk tier counts ===")
print(df["risk_tier"].value_counts())
print(f"\nUnique risk score values: {df['risk_score'].nunique()}")
print("\n=== Risk tier vs. true label ===")
print(pd.crosstab(df["label"], df["risk_tier"]))

output_cols = ["event_id", "cluster_id", "latitude", "longitude", "event_date",
               "label", "predicted_label", "risk_score", "risk_tier"]
df[output_cols].to_csv(OUTPUT_PATH, index=False)
print(f"\nSaved {OUTPUT_PATH} ({len(df)} rows)")