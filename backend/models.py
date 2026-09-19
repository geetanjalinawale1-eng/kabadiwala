from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    phone = Column(String, unique=True, index=True)
    role = Column(String)
    language_pref = Column(String, default="en")
    verified = Column(Boolean, default=False)

class Lot(Base):
    __tablename__ = "lots"
    id = Column(Integer, primary_key=True, index=True)
    collector_id = Column(Integer, ForeignKey("users.id"))
    material_type = Column(String)
    confidence_score = Column(Float, nullable=True)
    weight_kg = Column(Float)
    condition = Column(String)
    photo_url = Column(String, nullable=True)
    status = Column(String, default="created")
    price_min = Column(Float, nullable=True)
    price_max = Column(Float, nullable=True)
    recycler_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
