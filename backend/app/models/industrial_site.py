from sqlalchemy import BigInteger, Column, DateTime, Float, Integer, String
from sqlalchemy.dialects.postgresql import JSONB

from app.database import Base


class IndustrialSite(Base):
    __tablename__ = "industrial_sites"

    id = Column(Integer, primary_key=True)
    osm_id = Column(BigInteger)
    name = Column(String(255))
    type = Column(String(100))
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    tags = Column(JSONB)
    source = Column(String(20))
    created_at = Column(DateTime)