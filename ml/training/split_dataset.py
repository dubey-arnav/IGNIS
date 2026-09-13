import json
import pandas as pd
from sklearn.model_selection import StratifiedGroupKFold

# ---- Paths ----
INPUT_PATH = "data/training_dataset.csv"
TRAIN_OUTPUT = "data/train_dataset.csv"
TEST_OUTPUT = "data/test_dataset.csv"
LABEL_MAP_PATH = "ml/training/label_mapping.json"

# ---- Step 1: Load the joined dataset from Milestone 2 ----
df = pd.read_csv(INPUT_PATH)

# ---- Step 2: Build the "group" column ----
# Rows that belong to a real cluster share that cluster as their group.
# Rows with no cluster (one-off events) each get their OWN unique group,
# since there's no sibling row to worry about leaking against.
df["group"] = df["cluster_id"].apply(
    lambda x: f"cluster_{int(x)}" if pd.notna(x) else None
)
missing = df["group"].isna()
df.loc[missing, "group"] = "single_" + df.loc[missing, "event_id"].astype(str)

assert df["group"].isna().sum() == 0, "Every row must have a group."

# ---- Step 3: Turn the text label into a number (the actual target variable) ----
# XGBoost needs numeric class labels, not strings. This mapping is saved to
# disk so every other script (training, evaluation, SHAP) uses the SAME
# numbers for the SAME classes -- never redefine this mapping elsewhere.
LABEL_MAP = {
    "Other/Unknown": 0,
    "Wildfire / Natural Fire": 1,
    "Persistent Industrial Thermal Source": 2,
    "Industrial Fire": 3,
}
df["target"] = df["label"].map(LABEL_MAP)
assert df["target"].isna().sum() == 0, "Found a label not in LABEL_MAP!"

with open(LABEL_MAP_PATH, "w") as f:
    json.dump(LABEL_MAP, f, indent=2)

# ---- Step 4: Grouped, stratified 80/20 split ----
# n_splits=5 just means "cut into 5 roughly-equal chunks"; we only use the
# first chunk as our test set (20%) and everything else as train (80%).
sgkf = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)
train_idx, test_idx = next(
    sgkf.split(X=df.index.values, y=df["target"].values, groups=df["group"].values)
)

train_df = df.iloc[train_idx]
test_df = df.iloc[test_idx]

# ---- Step 5: Safety checks ----
overlap = set(train_df["group"]) & set(test_df["group"])
assert len(overlap) == 0, f"Group leakage! {len(overlap)} groups appear in both sets."

print(f"Train: {train_df.shape[0]} rows, Test: {test_df.shape[0]} rows")
print(f"Train %: {len(train_df)/len(df):.1%}, Test %: {len(test_df)/len(df):.1%}")
print("\nTrain label distribution:")
print(train_df["label"].value_counts(normalize=True).round(3))
print("\nTest label distribution:")
print(test_df["label"].value_counts(normalize=True).round(3))

# ---- Step 6: Save ----
train_df.to_csv(TRAIN_OUTPUT, index=False)
test_df.to_csv(TEST_OUTPUT, index=False)
print(f"\nSaved {TRAIN_OUTPUT} and {TEST_OUTPUT}")