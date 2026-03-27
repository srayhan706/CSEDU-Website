from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from typing import List, Optional
from database import get_db
from models import Award
from pydantic import BaseModel
from dependencies import get_user_from_session
from middleware import permission_required

router = APIRouter(
    prefix="/api/awards",
    tags=["awards"],
    responses={404: {"description": "Not found"}},
)

class AwardSchema(BaseModel):
    id: Optional[int]
    title: str
    description: str
    details: Optional[str] = None
    recipient: str
    recipientType: str  # 'faculty' | 'student'
    year: int
    type: str  # 'award' | 'grant' | ...
    organization: Optional[str] = None
    amount: Optional[int] = None
    department: Optional[str] = None
    duration: Optional[str] = None
    categories: Optional[List[str]] = None
    publications: Optional[List[str]] = None
    link: Optional[str] = None

    class Config:
        orm_mode = True
        fields = {
            'recipientType': 'recipient_type',
        }

@router.get("/", response_model=list)
def get_awards(db: Session = Depends(get_db)):
    awards = db.query(Award).all()
    return [
        AwardSchema(
            id=a.id,
            title=a.title,
            description=a.description,
            details=a.details,
            recipient=a.recipient,
            recipientType=a.recipient_type,
            year=a.year,
            type=a.type,
            organization=a.organization,
            amount=a.amount,
            department=a.department,
            duration=a.duration,
            categories=a.categories,
            publications=a.publications,
            link=a.link
        ) for a in awards
    ]   

@router.post("/", dependencies=[Depends(permission_required("MANAGE_AWARDS"))])
def post_award(award: AwardSchema, db: Session = Depends(get_db)):
    obj = Award(
        title=award.title,
        description=award.description,
        details=award.details,
        recipient=award.recipient,
        recipient_type=award.recipientType,
        year=award.year,
        type=award.type,
        organization=award.organization,
        amount=award.amount,
        department=award.department,
        duration=award.duration,
        categories=award.categories,
        publications=award.publications,
        link=award.link
    )
    db.add(obj)
    db.commit()
    return {"message": "Award added"}
