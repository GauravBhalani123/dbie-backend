from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    category = Column(String)
    target_industry = Column(String)
    description = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class Business(Base):
    __tablename__ = "businesses"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    industry = Column(String)
    location = Column(String)
    website = Column(String)
    employee_size = Column(String)
    description = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    signals = relationship("Signal", back_populates="business")
    scores = relationship("LeadScore", back_populates="business", uselist=False)

class Signal(Base):
    __tablename__ = "signals"
    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"))
    signal_type = Column(String)
    value = Column(String)
    weight = Column(Integer, default=1)
    source = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    business = relationship("Business", back_populates="signals")

class LeadScore(Base):
    __tablename__ = "lead_scores"
    id = Column(Integer, primary_key=True, index=True)
    business_id = Column(Integer, ForeignKey("businesses.id"), unique=True)
    industry_score = Column(Float)
    asset_score = Column(Float)
    digital_score = Column(Float)
    operational_score = Column(Float)
    need_score = Column(Float)
    close_probability = Column(Float)
    category = Column(String)
    recommendation = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    business = relationship("Business", back_populates="scores")