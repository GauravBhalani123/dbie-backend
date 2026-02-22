from fastapi import APIRouter, Depends
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
    }