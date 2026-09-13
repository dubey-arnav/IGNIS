import json
import pandas as pd
import xgboost as xgb
from sklearn.utils.class_weight import compute_sample_weight
from sklearn.metrics import classification_report

# ---- Paths ----
TRAIN_PATH = "data/train_dataset.csv"
TEST_PATH = "data/test_dataset.csv"
LABEL_MAP_PATH = "ml/training/label_mapping.json"
MODEL_PATH = "ml/models/xgb_fire_classifier.json"
FEATURE_CONFIG_PATH = "ml/models/feature_config.json"

# ---- Step 1: Load data ----
train_df = pd.read_csv(TRAIN_PATH)
test_df = pd.read_csv(TEST_PATH)

with open(LABEL_MAP_PATH) as f:
    LABEL_MAP = json.load(f)
CLASS_NAMES = [name for name, _ in sorted(LABEL_MAP.items(), key=lambda kv: kv[1])]

# ---- Step 2: Define feature columns ----
CATEGORICAL = ["confidence", "daynight", "nearest_facility_type"]
NUMERIC = [
    "bright_ti4", "bright_ti5", "frp", "nearest_facility_distance_m",
    "facilities_within_radius", "total_detections", "active_days",
    "cluster_mean_frp", "cluster_max_frp", "persistence_score",
    "ndvi_mean", "ndbi_mean", "ndwi_mean", "swir1_mean", "swir2_mean",
    "valid_pixel_fraction",
]
FEATURES = CATEGORICAL + NUMERIC

# ---- Step 3: Convert categorical columns properly ----
# XGBoost can use text categories natively (no manual one-hot encoding needed),
# but train and test MUST use the exact same category list, fitted on train only,
# or a category XGBoost never saw in training will break/mismatch at test time.
category_levels = {}
for col in CATEGORICAL:
    train_df[col] = train_df[col].astype("category")
    category_levels[col] = train_df[col].cat.categories.tolist()
    test_df[col] = pd.Categorical(test_df[col], categories=train_df[col].cat.categories)

X_train, y_train = train_df[FEATURES], train_df["target"]
X_test, y_test = test_df[FEATURES], test_df["target"]

# ---- Step 4: Handle class imbalance ----
# Other/Unknown is ~74% of the data. Without correction, XGBoost would be
# tempted to just predict that class most of the time and still look "accurate".
# compute_sample_weight("balanced") gives rare classes proportionally more
# weight during training so mistakes on them count more.
sample_weight = compute_sample_weight("balanced", y_train)

# ---- Step 5: Train ----
model = xgb.XGBClassifier(
    n_estimators=300,
    max_depth=5,
    learning_rate=0.1,
    objective="multi:softprob",
    num_class=len(CLASS_NAMES),
    enable_categorical=True,
    eval_metric="mlogloss",
    random_state=42,
)
model.fit(X_train, y_train, sample_weight=sample_weight)

# ---- Step 6: Quick sanity-check evaluation (full evaluation is Milestone 5) ----
y_pred = model.predict(X_test)
print(classification_report(y_test, y_pred, target_names=CLASS_NAMES, digits=3))

# ---- Step 7: Save the model + the exact feature config used to build it ----
model.save_model(MODEL_PATH)
with open(FEATURE_CONFIG_PATH, "w") as f:
    json.dump(
        {"categorical": CATEGORICAL, "numeric": NUMERIC, "category_levels": category_levels},
        f, indent=2,
    )
print(f"\nSaved model to {MODEL_PATH}")
print(f"Saved feature config to {FEATURE_CONFIG_PATH}")