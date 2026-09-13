import json
import numpy as np
import pandas as pd
import xgboost as xgb

FULL_DATA_PATH = "data/training_dataset.csv"
FEATURE_CONFIG_PATH = "ml/models/feature_config.json"
MODEL_PATH = "ml/models/xgb_fire_classifier.json"
LABEL_MAP_PATH = "ml/training/label_mapping.json"
OUTPUT_PATH = "data/risk_scores.csv"

# ---- Step 1: Load model + config ----
model = xgb.XGBClassifier()
model.load_model(MODEL_PATH)

with open(FEATURE_CONFIG_PATH) as f:
    config = json.load(f)
CATEGORICAL, NUMERIC = config["categorical"], config["numeric"]
FEATURES = CATEGORICAL + NUMERIC
CATEGORY_LEVELS = config["category_levels"]

with open(LABEL_MAP_PATH) as f:
    LABEL_MAP = json.load(f)
CLASS_NAMES = [name for name, _ in sorted(LABEL_MAP.items(), key=lambda kv: kv[1])]

# ---- Step 2: Load and score EVERY event (not just the test split) ----
# Note: events that were in the training set will look slightly more
# "confident" than genuinely new data would -- that's expected and fine for
# production scoring. Milestone 5's held-out test numbers remain the honest
# measure of how well this model actually performs.
df = pd.read_csv(FULL_DATA_PATH)
for col in CATEGORICAL:
    df[col] = pd.Categorical(df[col], categories=CATEGORY_LEVELS[col])
X = df[FEATURES]

proba = model.predict_proba(X)  # shape: (n_events, 4)
df["predicted_label"] = [CLASS_NAMES[i] for i in proba.argmax(axis=1)]
for i, name in enumerate(CLASS_NAMES):
    df[f"prob_{name.replace('/', '_').replace(' ', '_')}"] = proba[:, i]

# ---- Step 3: Combine probabilities into one risk score (0-100) ----
SEVERITY_WEIGHTS = {
    "Other/Unknown": 0,
    "Wildfire / Natural Fire": 20,
    "Persistent Industrial Thermal Source": 60,
    "Industrial Fire": 100,
}
risk_score = np.zeros(len(df))
for i, name in enumerate(CLASS_NAMES):
    risk_score += proba[:, i] * SEVERITY_WEIGHTS[name]
df["risk_score"] = risk_score.round(1)

# ---- Step 4: Bucket into tiers a dashboard can color-code directly ----
def tier(score):
    if score >= 70: return "Critical"
    if score >= 40: return "High"
    if score >= 15: return "Medium"
    return "Low"

df["risk_tier"] = df["risk_score"].apply(tier)

# ---- Step 5: Sanity check -- does the risk tier line up with real labels? ----
print("=== Risk tier counts ===")
print(df["risk_tier"].value_counts())
print("\n=== Risk tier vs. true label (sanity cross-check) ===")
print(pd.crosstab(df["label"], df["risk_tier"]))

# ---- Step 6: Save the final scored dataset ----
output_cols = ["event_id", "cluster_id", "latitude", "longitude", "event_date",
               "label", "predicted_label", "risk_score", "risk_tier"]
df[output_cols].to_csv(OUTPUT_PATH, index=False)
print(f"\nSaved {OUTPUT_PATH} ({len(df)} rows)")