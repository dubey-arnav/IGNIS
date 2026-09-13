import pandas as pd

# ---- Paths ----
FEATURES_PATH = "data/ml_feature_dataset.csv"
LABELS_PATH = "data/labeling_candidates.csv"
OUTPUT_PATH = "data/training_dataset.csv"

# ---- Decisions made here (Section 6 of the handoff report) ----
# 1. Events with no cluster_id (one-off detections) are labeled "Other/Unknown".
# 2. "Other/Unknown" is kept as a real 4th class the model will predict.
# Rationale: matches real-world deployment (most raw detections ARE noise),
# at the cost of a heavily imbalanced training set (~74% Other/Unknown).
# We'll handle that imbalance explicitly at training time (class weights).

# ---- Step 1: Load both files ----
features = pd.read_csv(FEATURES_PATH)
labels_raw = pd.read_csv(LABELS_PATH)

# ---- Step 2: De-duplicate labels to one row per cluster ----
# labeling_candidates.csv has multiple rows per cluster when several
# facilities are within radius (fan-out). The label itself never differs
# across those duplicate rows, so it's safe to just keep the first one.
labels = labels_raw.drop_duplicates(subset="cluster_id", keep="first")[
    ["cluster_id", "suggested_label"]
]
assert labels["cluster_id"].is_unique, "labels still has duplicate cluster_ids!"

# ---- Step 3: Join event-level features to cluster-level labels ----
merged = features.merge(labels, on="cluster_id", how="left")

# Safety check: the join must not have multiplied any rows.
assert len(merged) == len(features), (
    f"Row count changed after merge! {len(features)} -> {len(merged)}. "
    "The label file probably wasn't deduplicated correctly."
)

# ---- Step 4: Apply Decision 1 — one-off events become "Other/Unknown" ----
merged["suggested_label"] = merged["suggested_label"].fillna("Other/Unknown")
merged = merged.rename(columns={"suggested_label": "label"})

# ---- Step 5: Final sanity checks ----
assert merged["label"].isna().sum() == 0, "Some rows are still unlabeled!"
print("Label distribution:")
print(merged["label"].value_counts())
print(f"\nTotal rows: {len(merged)} (should be 11441)")

# ---- Step 6: Save ----
merged.to_csv(OUTPUT_PATH, index=False)
print(f"\nSaved joined training dataset to {OUTPUT_PATH}")