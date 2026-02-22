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
    status: Optional[str] = "Pending"

class SignalBase(BaseModel):
    signal_type: str
    value: str
    weight: Optional[int] = 1
    source: Optional[str] = None

class SignalCreate(SignalBase):
    business_id: int

class SignalResponse(SignalCreate):
    id: int
    created_at: datetime
    class Config:
        from_attributes = True

class LeadScoreResponse(BaseModel):
    industry_score: float
    asset_score: float
    digital_score: float
    operational_score: float
    need_score: float
    close_probability: float
    category: str
    recommendation: str
    product_matched: Optional[str] = None

class BusinessResponse(BusinessCreate):
    id: int
    created_at: datetime
    scores: Optional[LeadScoreResponse] = None
    signals: Optional[List[SignalResponse]] = []
    class Config:
        from_attributes = True

class AnalyzeProductRequest(BaseModel):
    product_name: str
    business: BusinessCreate
    signals: List[SignalBase]

class AnalyzeProductResponse(BaseModel):
    business_name: str
    asset_presence: float
    digital_maturity: float
    operational_complexity: float
    product_need_probability: float
    close_probability: float
    lead_category: str
    inference_reason: str
    recommended_sales_action: str