from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    phone = Column(String, unique=True, index=True, nullable=False)
    role = Column(String, nullable=False)
    language_pref = Column(String, default="en")
    verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Lot(Base):
    __tablename__ = "lots"

    id = Column(Integer, primary_key=True, index=True)
    collector_id = Column(Integer, ForeignKey("users.id"))
    recycler_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    pool_id = Column(Integer, ForeignKey("pools.id"), nullable=True)
    
    material_type = Column(String, nullable=False)
    confidence_score = Column(Float, nullable=True)
    weight_kg = Column(Float, nullable=False)
    condition = Column(String, nullable=False)
    lat = Column(Float, nullable=True)
    lng = Column(Float, nullable=True)
    
    price_min = Column(Float, nullable=True)
    price_max = Column(Float, nullable=True)
    safety_guidance = Column(String, nullable=True)
    photo_url = Column(String, nullable=True)
    status = Column(String, default="created")
    tamper_hash = Column(String, nullable=True)
    offline_client_id = Column(String, nullable=True, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Pool(Base):
    __tablename__ = "pools"

    id = Column(Integer, primary_key=True, index=True)
    material_type = Column(String, nullable=False)
    total_weight_kg = Column(Float, default=0.0)
    target_weight_kg = Column(Float, default=50.0)
    status = Column(String, default="open")
    lat = Column(Float, nullable=True)
    lng = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())