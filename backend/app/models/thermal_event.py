from sqlalchemy import Column, Date, DateTime, Float, Integer, String, Time

from app.database import Base


class ThermalEvent(Base):
    __tablename__ = "thermal_events"

    id = Column(Integer, primary_key=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    event_date = Column(Date, nullable=False)
    event_time = Column(Time)
    satellite = Column(String(20))
    instrument = Column(String(20))
    confidence = Column(String(10))
    bright_ti4 = Column(Float)
    bright_ti5 = Column(Float)
    frp = Column(Float)
    daynight = Column(String(1))
    source = Column(String(20))
    cluster_id = Column(Integer)
    created_at = Column(DateTime)