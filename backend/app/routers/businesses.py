from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import schemas, models
from ..database import get_db
from ..scoring_engine import analyze_universal_need

router = APIRouter()

@router.post("/analyze-product", response_model=schemas.AnalyzeProductResponse)
def analyze_product(request: schemas.AnalyzeProductRequest, db: Session = Depends(get_db)):
    biz_data = request.business.model_dump()
    sig_data = [s.model_dump() for s in request.signals]
    
    # 4-Layer Scoring Logic
    result = analyze_universal_need(request.product_name, biz_data, sig_data)
    
    # Check if business exists, else create
    db_biz = db.query(models.Business).filter(models.Business.name == biz_data['name']).first()
    if not db_biz:
        db_biz = models.Business(**biz_data)
        db.add(db_biz)
        db.commit()
        db.refresh(db_biz)
    
    # Add Signals
    for s in request.signals:
        db_sig = models.Signal(**s.model_dump(), business_id=db_biz.id)
        db.add(db_sig)
    
    # Add or Update LeadScore
    score = db.query(models.LeadScore).filter(models.LeadScore.business_id == db_biz.id).first()
    score_data = {
        "business_id": db_biz.id,
        "industry_score": result.get("industry_match", 50.0), # mapped from old logic if needed
        "asset_score": result["asset_presence"],
        "digital_score": result["digital_maturity"],
        "operational_score": result["operational_complexity"],
        "need_score": result["product_need_probability"],
        "close_probability": result["close_probability"],
        "category": result["lead_category"],
        "recommendation": result["recommended_sales_action"],
        "product_matched": request.product_name
    }
    
    if score:
        for k, v in score_data.items():
            setattr(score, k, v)
    else:
        score = models.LeadScore(**score_data)
        db.add(score)
    
    # Set Status mapped to category
    if result["lead_category"] == "Hot":
        db_biz.status = "Follow-up"
    
    db.commit()
    return result