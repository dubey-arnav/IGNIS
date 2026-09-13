import json
import pandas as pd
import numpy as np
import xgboost as xgb
import shap

TEST_PATH = "data/test_dataset.csv"
FEATURE_CONFIG_PATH = "ml/models/feature_config.json"
MODEL_PATH = "ml/models/xgb_fire_classifier.json"
LABEL_MAP_PATH = "ml/training/label_mapping.json"

# ---- Step 1: Load model, config, test data (same pattern as evaluate.py) ----
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

test_df = pd.read_csv(TEST_PATH).reset_index(drop=True)
for col in CATEGORICAL:
    test_df[col] = pd.Categorical(test_df[col], categories=CATEGORY_LEVELS[col])
X_test = test_df[FEATURES]

# ---- Step 2: Compute SHAP values ----
# TreeExplainer is the fast, exact method for tree-based models like XGBoost.
explainer = shap.TreeExplainer(model)
shap_values = explainer(X_test)  # shape: (rows, features, classes)

# ---- Step 3: Global importance -- which features matter most overall? ----
mean_abs = np.abs(shap_values.values).mean(axis=0)  # (features, classes)
importance_df = pd.DataFrame(mean_abs, index=FEATURES, columns=CLASS_NAMES)
importance_df["overall"] = importance_df.mean(axis=1)
importance_df = importance_df.sort_values("overall", ascending=False)

print("=== Global feature importance (mean |SHAP value|) ===")
print(importance_df.round(3).head(10))

# ---- Step 4: Explain one specific costly miss from Milestone 5 ----
# event_id 2691 (cluster 514) was truly "Persistent Industrial" but predicted
# "Other/Unknown". Let's see exactly why, in both directions.
target_event = 2691
row_idx = test_df.index[test_df["event_id"] == target_event][0]
print(f"\n=== Explaining event_id {target_event} (true: Persistent Industrial, predicted: Other/Unknown) ===")

for class_idx, class_name in [(0, "Other/Unknown"), (2, "Persistent Industrial")]:
    vals = shap_values.values[row_idx, :, class_idx]
    contributions = pd.Series(vals, index=FEATURES).sort_values(key=abs, ascending=False)
    print(f"\nTop features pushing toward '{class_name}':")
    print(contributions.head(5).round(3))