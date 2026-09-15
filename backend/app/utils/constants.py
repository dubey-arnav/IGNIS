# The four classes the trained model actually predicts.
MODELLED_CLASSES = [
    "Industrial Fire",
    "Persistent Industrial Thermal Source",
    "Wildfire / Natural Fire",
    "Other/Unknown",
]

# Agricultural Burning is a project category but is NOT predicted by the
# current model (it was never assigned by the labeling script). It is exposed
# with modelled=False so the UI can show it honestly instead of hiding it.
CLASSIFICATIONS = {
    "Industrial Fire": {
        "code": "industrial_fire",
        "color": "#E03131",
        "modelled": True,
        "priority": 1,
        "description": "A transient burn event at or very near a known industrial facility.",
    },
    "Persistent Industrial Thermal Source": {
        "code": "persistent_industrial",
        "color": "#F76707",
        "modelled": True,
        "priority": 2,
        "description": "A location detected burning or glowing repeatedly over many distinct days, close to an industrial facility.",
    },
    "Wildfire / Natural Fire": {
        "code": "wildfire",
        "color": "#F59F00",
        "modelled": True,
        "priority": 3,
        "description": "No industrial facility nearby, short-lived, high peak radiative power.",
    },
    "Agricultural Burning": {
        "code": "agricultural_burning",
        "color": "#66A80F",
        "modelled": False,
        "priority": 4,
        "description": "Crop residue burning. Defined as a project category but not predicted by the current model.",
    },
    "Other/Unknown": {
        "code": "other_unknown",
        "color": "#868E96",
        "modelled": True,
        "priority": 5,
        "description": "Insufficient evidence to classify confidently.",
    },
}

RISK_TIERS = {
    "Critical": {"color": "#C92A2A", "min_score": 70},
    "High": {"color": "#E8590C", "min_score": 40},
    "Medium": {"color": "#F08C00", "min_score": 15},
    "Low": {"color": "#ADB5BD", "min_score": 0},
}

SEVERITY_WEIGHTS = {
    "Other/Unknown": 0,
    "Wildfire / Natural Fire": 20,
    "Persistent Industrial Thermal Source": 60,
    "Industrial Fire": 100,
}

FIRMS_CONFIDENCE = {"l": "low", "n": "nominal", "h": "high"}


def classification_meta(label: str) -> dict:
    return CLASSIFICATIONS.get(label, CLASSIFICATIONS["Other/Unknown"])


def tier_for_score(score: float) -> str:
    if score >= 70:
        return "Critical"
    if score >= 40:
        return "High"
    if score >= 15:
        return "Medium"
    return "Low"