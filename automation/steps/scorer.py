# automation/steps/scorer.py
"""
Loads the EXISTING trained model exactly once per process (not per event)
and exposes a predict() function. This is the "packaged scoring logic"
the ML handoff report (17.10.6) identified as missing.
"""
import json
import logging
import pandas as pd
import xgboost as xgb

logger = logging.getLogger("ignis.automation.scorer")


class FireClassifier:
    def __init__(
        self,
        model_path: str = "ml/models/xgb_fire_classifier.json",
        label_map_path: str = "ml/training/label_mapping.json",
    ):
        self.model = xgb.XGBClassifier()
        self.model.load_model(model_path)
        with open(label_map_path) as f:
            label_map = json.load(f)
        self.class_names = [name for name, _ in sorted(label_map.items(), key=lambda kv: kv[1])]
        logger.info(f"Loaded model from {model_path} with classes: {self.class_names}")

    def predict(self, feature_row: pd.DataFrame) -> dict:
        """
        feature_row: output of feature_builder.build_feature_row() — 1 row,
        correct categorical dtypes already applied.
        Returns: {"predicted_label": str, "class_probabilities": {label: float}}
        """
        proba = self.model.predict_proba(feature_row)[0]
        predicted_index = int(proba.argmax())
        return {
            "predicted_label": self.class_names[predicted_index],
            "class_probabilities": {
                name: round(float(p), 4) for name, p in zip(self.class_names, proba)
            },
        }
