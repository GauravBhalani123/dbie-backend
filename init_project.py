import os

# Project structure
files = {
    "backend/Dockerfile": """FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]""",

    "backend/app/main.py": """from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routers import auth, products, businesses, signals, dashboard

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Deep Business Intelligence Engine API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(products.router, prefix="/api/products", tags=["Products"])
app.include_router(businesses.router, prefix="/api/businesses", tags=["Businesses"])
app.include_router(signals.router, prefix="/api/signals", tags=["Signals"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])

@app.get("/")
def read_root():
    return {"message": "Welcome to DBIE API"}""",

    "backend/app/database.py": """from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./dbie.db") # Fallback to sqlite if no URL

if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()""",

    "backend/app/models.py": """from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
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
    business = relationship("Business", back_populates="scores")""",

    "backend/app/schemas.py": """from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

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
        from_attributes = True""",

    "backend/app/auth.py": """from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import os

SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey_change_in_production")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt""",

    "backend/app/scoring_engine.py": """def analyze_business(business, signals):
    industry_score = 50.0  # Base score
    asset_score = 0.0
    digital_score = 100.0  # Assumes High digital capability, subtract based on gaps
    operational_score = 30.0

    keywords = []
    infrastructures = []
    hirings = []
    
    for s in signals:
        val = s.value.lower()
        if s.signal_type == "keyword": keywords.append(val)
        elif s.signal_type == "infrastructure": infrastructures.append(val)
        elif s.signal_type == "hiring": hirings.append(val)
    
    # Asset Detection Logic
    for k in keywords:
        if any(x in k for x in ['weighbridge', 'dharamkanta', 'truck scale', 'ton']):
            asset_score += 30
    for i in infrastructures:
        if any(x in i for x in ['warehouse', 'yard', 'storage']):
            asset_score += 20
    for h in hirings:
        if 'operator' in h:
            asset_score += 15
            
    asset_score = min(100.0, asset_score)

    # Digital Gap Detection
    has_erp = any('erp' in k for k in keywords)
    if business.website and not has_erp:
        digital_score -= 30
    if not business.website:
        digital_score -= 50
        
    for h in hirings:
        if any(x in h for x in ['billing', 'accounting', 'data entry']):
            operational_score += 30
    
    digital_score = max(0.0, digital_score)
    operational_score = min(100.0, operational_score)

    # Need Probability
    need_score = (industry_score * 0.3) + (asset_score * 0.25) + (operational_score * 0.25) + ((100 - digital_score) * 0.2)
    need_score = min(100.0, round(need_score, 2))
    
    close_probability = round(need_score * 0.85, 2)
    
    if need_score >= 75: category = "Hot"
    elif need_score >= 50: category = "Warm"
    else: category = "Cold"
    
    recommendation = "Standard Follow up."
    if category == "Hot":
        recommendation = "High value target. Pitch direct system upgrade."

    return {
        "industry_score": industry_score,
        "asset_score": asset_score,
        "digital_score": digital_score,
        "operational_score": operational_score,
        "need_score": need_score,
        "close_probability": close_probability,
        "category": category,
        "recommendation": recommendation
    }""",

    "backend/app/routers/dashboard.py": """from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from .. import models

router = APIRouter()

@router.get("/")
def get_dashboard_stats(db: Session = Depends(get_db)):
    tot_businesses = db.query(models.Business).count()
    hot_leads = db.query(models.LeadScore).filter(models.LeadScore.category == "Hot").count()
    warm_leads = db.query(models.LeadScore).filter(models.LeadScore.category == "Warm").count()
    cold_leads = db.query(models.LeadScore).filter(models.LeadScore.category == "Cold").count()
    
    return {
        "total_businesses": tot_businesses,
        "leads_breakdown": {
            "hot": hot_leads,
            "warm": warm_leads,
            "cold": cold_leads
        }
    }""",

    "backend/app/routers/auth.py": """from fastapi import APIRouter""",
    "backend/app/routers/products.py": """from fastapi import APIRouter\nrouter = APIRouter()""",
    "backend/app/routers/businesses.py": """from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import schemas, models
from ..database import get_db

router = APIRouter()

@router.post("/", response_model=schemas.BusinessResponse)
def create_business(business: schemas.BusinessCreate, db: Session = Depends(get_db)):
    db_business = models.Business(**business.dict())
    db.add(db_business)
    db.commit()
    db.refresh(db_business)
    return db_business

@router.get("/")
def list_businesses(db: Session = Depends(get_db)):
    return db.query(models.Business).all()""",
    
    "backend/app/routers/signals.py": """from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .. import schemas, models
from ..database import get_db
from ..scoring_engine import analyze_business

router = APIRouter()

@router.post("/")
def add_signal(signal: schemas.SignalCreate, db: Session = Depends(get_db)):
    db_signal = models.Signal(**signal.dict())
    db.add(db_signal)
    db.commit()
    
    # Trigger auto-analyze
    business = db.query(models.Business).filter(models.Business.id == signal.business_id).first()
    signals = db.query(models.Signal).filter(models.Signal.business_id == signal.business_id).all()
    
    scores = analyze_business(business, signals)
    
    existing_score = db.query(models.LeadScore).filter(models.LeadScore.business_id == business.id).first()
    if existing_score:
        for key, value in scores.items():
            setattr(existing_score, key, value)
    else:
        new_score = models.LeadScore(business_id=business.id, **scores)
        db.add(new_score)
        
    db.commit()
    return {"message": "Signal added and business re-analyzed"}""",

    "frontend/Dockerfile": """FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]""",

    "frontend/package.json": """{
  "name": "dbie-frontend",
  "private": true,
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0",
    "chart.js": "^4.4.0",
    "react-chartjs-2": "^5.2.0"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.2.1",
    "vite": "^5.0.0"
  }
}""",

    "frontend/vite.config.js": """import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: true,
    port: 5173
  }
})""",

    "frontend/index.html": """<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>DBIE - Intelligence Engine</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>""",

    "frontend/src/main.jsx": """import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.jsx'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)""",

    "frontend/src/index.css": """body {
  margin: 0;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background-color: #0f172a;
  color: #e2e8f0;
}
.app-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}
.header { border-bottom: 1px solid #334155; padding-bottom: 10px; margin-bottom: 20px;}
.stats-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px;}
.stat-card { background: #1e293b; padding: 20px; border-radius: 8px; text-align: center; }
.stat-card h3 { margin: 0; color: #94a3b8; }
.stat-card.hot { border-left: 4px solid #ef4444; }
.stat-card.warm { border-left: 4px solid #f59e0b; }
.stat-card.cold { border-left: 4px solid #3b82f6; }
.table { width: 100%; border-collapse: collapse; margin-top:20px; }
.table th, .table td { padding: 12px; text-align: left; border-bottom: 1px solid #334155; }
.badge { padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }
.badge-hot { background-color: rgba(239, 68, 68, 0.2); color: #ef4444; }
""",

    "frontend/src/App.jsx": """import { useEffect, useState } from 'react'

function App() {
  const [stats, setStats] = useState(null);
  const [businesses, setBusinesses] = useState([]);

  useEffect(() => {
    fetch('http://localhost:8000/api/dashboard/')
      .then(r => r.json())
      .then(data => setStats(data))
      .catch(e => console.error(e));
      
    fetch('http://localhost:8000/api/businesses/')
      .then(r => r.json())
      .then(data => setBusinesses(data))
      .catch(e => console.error(e));
  }, []);

  return (
    <div className="app-container">
      <div className="header">
        <h1>🚀 Deep Business Intelligence Engine</h1>
      </div>
      
      {stats && (
        <div className="stats-grid">
          <div className="stat-card hot">
            <h3>🔥 Hot Leads</h3>
            <h2>{stats.leads_breakdown.hot}</h2>
          </div>
          <div className="stat-card warm">
            <h3>🌡️ Warm Leads</h3>
            <h2>{stats.leads_breakdown.warm}</h2>
          </div>
          <div className="stat-card cold">
            <h3>❄️ Cold Leads</h3>
            <h2>{stats.leads_breakdown.cold}</h2>
          </div>
        </div>
      )}

      <h2>Recent Intelligences</h2>
      <table className="table">
        <thead>
          <tr>
            <th>Business Name</th>
            <th>Industry</th>
            <th>Location</th>
          </tr>
        </thead>
        <tbody>
          {businesses.map(b => (
            <tr key={b.id}>
              <td>{b.name}</td>
              <td>{b.industry}</td>
              <td>{b.location}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default App
""",
    ".env.example": """DATABASE_URL=postgresql://postgres:password@db:5432/dbie
SECRET_KEY=supersecretkey
JWT_ALGORITHM=HS256""",
    "seed.sql": """-- Insert default user schema etc here.
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";"""
}

def create_project():
    for filepath, content in files.items():
        dir_name = os.path.dirname(filepath)
        if dir_name:
            os.makedirs(dir_name, exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
    print("Project successfully generated!")

if __name__ == "__main__":
    create_project()
