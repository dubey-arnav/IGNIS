# automation/steps/fit_and_save_calibrated_model.py
"""
The existing risk_score.py re-fits CalibratedClassifierCV from scratch on
every run (documented technical debt, Part 17.10.2). We fit it ONE TIME
here and save it, so the scheduled pipeline only ever loads it.
Reuses the exact same hyperparameters and class-weight approach as the
existing risk_score.py — this is a packaging change, not a formula change.
"""
import json
import joblib
import pandas as pd
import xgboost as xgb
from sklearn.calibration import CalibratedClassifierCV
from sklearn.utils.class_weight import compute_sample_weight


def fit_and_save(
    feature_config_path: str = "ml/models/feature_config.json",
    train_data_path: str = "data/train_dataset.csv",
    output_path: str = "ml/models/calibrated_risk_model.joblib",
):
    with open(feature_config_path) as f:
        config = json.load(f)
    categorical = config["categorical"]
    numeric = config["numeric"]
    features = categorical + numeric

    train_df = pd.read_csv(train_data_path)
    for col in categorical:
        train_df[col] = train_df[col].astype("category")

    X_train, y_train = train_df[features], train_df["target"]
    sample_weight = compute_sample_weight("balanced", y_train)

    num_class = int(train_df["target"].nunique())
    base_model = xgb.XGBClassifier(
        n_estimators=300,
        max_depth=5,
        learning_rate=0.1,
        objective="multi:softprob",
        num_class=num_class,
        enable_categorical=True,
        eval_metric="mlogloss",
        random_state=42,
    )
    calibrated_model = CalibratedClassifierCV(base_model, method="isotonic", cv=5)
    calibrated_model.fit(X_train, y_train, sample_weight=sample_weight)

    joblib.dump(calibrated_model, output_path)
    print(f"Saved {output_path}")


if __name__ == "__main__":
    fit_and_save()
