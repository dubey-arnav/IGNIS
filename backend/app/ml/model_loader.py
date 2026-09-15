import json
import threading

import xgboost as xgb

from app.config import settings

_lock = threading.Lock()
_state = {"model": None, "feature_config": None, "class_names": None}


def load():
    """Loads the trained model ONCE and caches it in memory.

    Reloading per request would add ~200ms to every call."""
    if _state["model"] is not None:
        return _state
    with _lock:
        if _state["model"] is not None:
            return _state
        model = xgb.XGBClassifier()
        model.load_model(str(settings.MODEL_PATH))
        with open(settings.FEATURE_CONFIG_PATH) as f:
            feature_config = json.load(f)
        with open(settings.LABEL_MAP_PATH) as f:
            label_map = json.load(f)
        _state.update({
            "model": model,
            "feature_config": feature_config,
            "class_names": [n for n, _ in sorted(label_map.items(),
                                                 key=lambda kv: kv[1])],
        })
    return _state


def is_loaded() -> bool:
    return _state["model"] is not None