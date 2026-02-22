from fastapi import APIRouter, Depends
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
    return db.query(models.Business).all()