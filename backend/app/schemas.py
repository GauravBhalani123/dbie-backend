from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class ProductCreate(BaseModel):
    name: str
    category: str
    target_industry: str
    description: Optional[str] = None

class ProductResponse(ProductCreate):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True

class BusinessCreate(BaseModel):
    name: str
    industry: str
    location: str
    website: Optional[str] = None
    employee_size: Optional[str] = None
    description: Optional[str] = None

class SignalCreate(BaseModel):
    business_id: int
    signal_type: str
    value: str
    weight: Optional[int] = 1
    source: Optional[str] = None

class LeadScoreResponse(BaseModel):
    industry_score: float
    asset_score: float
    digital_score: float
    operational_score: float
    need_score: float
    close_probability: float
    category: str
    recommendation: str

class BusinessResponse(BusinessCreate):
    id: int
    created_at: datetime
    scores: Optional[LeadScoreResponse] = None
    class Config:
        from_attributes = True

class SignalResponse(SignalCreate):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True