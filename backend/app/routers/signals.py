from fastapi import APIRouter, Depends
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
    return {"message": "Signal added and business re-analyzed"}