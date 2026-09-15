from sqlalchemy import Column, DateTime, Float, Integer, String

from app.database import Base


class RiskScore(Base):
    """Stores the model's CLASSIFICATION (predicted_label) plus the secondary
    risk score. The table name is historical; the API exposes it as
    classification-first."""

    __tablename__ = "risk_scores"

    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, nullable=False, index=True)
    cluster_id = Column(Integer)
    predicted_label = Column(String(50), nullable=False)
    risk_score = Column(Float, nullable=False)
    risk_tier = Column(String(10), nullable=False)
    model_version = Column(String(50))
    scored_at = Column(DateTime)