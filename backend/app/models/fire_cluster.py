from sqlalchemy import Column, Date, DateTime, Float, Integer

from app.database import Base


class FireCluster(Base):
    __tablename__ = "fire_clusters"

    id = Column(Integer, primary_key=True)
    first_detection = Column(Date)
    last_detection = Column(Date)
    total_detections = Column(Integer)
    active_days = Column(Integer)
    mean_frp = Column(Float)
    max_frp = Column(Float)
    persistence_score = Column(Float)
    created_at = Column(DateTime)