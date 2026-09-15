from sqlalchemy.orm import Session

from app.repositories import analytics_repository as repo
from app.utils.constants import CLASSIFICATIONS, RISK_TIERS


def classifications(db: Session):
    """Returns ALL FIVE project categories. Unmodelled ones report count 0
    rather than vanishing — the UI stays honest about scope."""
    counts = {r["predicted_label"]: r for r in repo.classification_counts(db)}
    out = []
    for label, meta in sorted(CLASSIFICATIONS.items(), key=lambda kv: kv[1]["priority"]):
        row = counts.get(label)
        out.append({
            "label": label,
            "code": meta["code"],
            "color": meta["color"],
            "modelled": meta["modelled"],
            "description": meta["description"],
            "count": int(row["count"]) if row else 0,
            "avg_risk_score": float(row["avg_risk"]) if row else None,
        })
    total = sum(c["count"] for c in out)
    for c in out:
        c["percentage"] = round(100 * c["count"] / total, 1) if total else 0.0
    return {"total_classified": total, "classifications": out}


def dashboard_summary(db: Session):
    head = dict(repo.headline(db))
    cls = classifications(db)
    tiers = {r["risk_tier"]: int(r["count"]) for r in repo.tier_counts(db)}
    industrial = sum(c["count"] for c in cls["classifications"]
                     if c["code"] in ("industrial_fire", "persistent_industrial"))
    return {
        "coverage": {
            "total_events": int(head["total_events"]),
            "total_clusters": int(head["total_clusters"]),
            "total_facilities": int(head["total_facilities"]),
            "date_range": {"from": head["first_date"], "to": head["last_date"]},
        },
        # Classification block first — it is the primary objective.
        "classification": {
            "total_classified": cls["total_classified"],
            "industrial_related": industrial,
            "breakdown": cls["classifications"],
        },
        "risk": {
            "tiers": [{"tier": t, "count": tiers.get(t, 0),
                       "color": RISK_TIERS[t]["color"]}
                      for t in ["Critical", "High", "Medium", "Low"]],
        },
        "model": {
            "version": "xgb_v1",
            "classes": 4,
            "test_accuracy": 0.986,
            "note": "Accuracy reflects consistency with rule-based labels, "
                    "not independent validation.",
        },
    }


def timeline(db: Session, start_date=None, end_date=None):
    rows = repo.timeline(db, start_date, end_date)
    by_date = {}
    for r in rows:
        d = r["event_date"].isoformat()
        by_date.setdefault(d, {"date": d, "total": 0, "counts": {}})
        by_date[d]["counts"][r["predicted_label"]] = int(r["count"])
        by_date[d]["total"] += int(r["count"])
    return {"series": sorted(by_date.values(), key=lambda x: x["date"])}


def by_facility_type(db: Session):
    return {"items": [dict(r) | {"count": int(r["count"])}
                      for r in repo.by_facility_type(db)]}


def distance_profile(db: Session):
    return {"items": [dict(r) | {"count": int(r["count"])}
                      for r in repo.distance_profile(db)]}