from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from typing import List, Optional
from database import get_db
from models import AdmissionStats, AdmissionDeadline, AdmissionFAQ, User
from pydantic import BaseModel
from dependencies import get_user_from_session
from middleware import permission_required
from datetime import datetime, date

router = APIRouter(
    prefix="/api/admissions",
    tags=["admissions"],
    responses={404: {"description": "Not found"}},
)

# Pydantic Schemas
class AdmissionStatsSchema(BaseModel):
    nextDeadline: str
    programsOffered: int
    applicationTime: str
    acceptanceRate: str

class AdmissionDeadlineSchema(BaseModel):
    program: str
    level: str
    date: date
    requirements: str
    notes: Optional[str] = None

    class Config:
        from_attributes = True

class AdmissionFAQSchema(BaseModel):
    question: str
    answer: str
    category: str

# GET endpoints (open to all)
@router.get("/stats", response_model=AdmissionStatsSchema)
def get_stats(db: Session = Depends(get_db)):
    stats = db.query(AdmissionStats).first()
    if not stats:
        raise HTTPException(status_code=404, detail="No stats found")
    return AdmissionStatsSchema(
        nextDeadline=stats.next_deadline,
        programsOffered=stats.programs_offered,
        applicationTime=stats.application_time,
        acceptanceRate=stats.acceptance_rate
    )

@router.get("/deadlines", response_model=List[AdmissionDeadlineSchema])
def get_deadlines(db: Session = Depends(get_db)):
    deadlines = db.query(AdmissionDeadline).all()
    return [AdmissionDeadlineSchema(
        program=d.program,
        level=d.level,
        date=d.date.strftime("%Y-%m-%d"),
        requirements=d.requirements,
        notes=d.notes
    ) for d in deadlines]

@router.get("/faqs", response_model=List[AdmissionFAQSchema])
def get_faqs(db: Session = Depends(get_db)):
    faqs = db.query(AdmissionFAQ).all()
    return [AdmissionFAQSchema(
        question=f.question,
        answer=f.answer,
        category=f.category
    ) for f in faqs]

# POST endpoints (OFFICER only)
@router.post("/stats", dependencies=[Depends(permission_required("MANAGE_ADMISSIONS"))])
def post_stats(stats: AdmissionStatsSchema, db: Session = Depends(get_db)):
    obj = db.query(AdmissionStats).first()
    if obj:
        obj.next_deadline = stats.nextDeadline
        obj.programs_offered = stats.programsOffered
        obj.application_time = stats.applicationTime
        obj.acceptance_rate = stats.acceptanceRate
    else:
        obj = AdmissionStats(
            next_deadline=stats.nextDeadline,
            programs_offered=stats.programsOffered,
            application_time=stats.applicationTime,
            acceptance_rate=stats.acceptanceRate
        )
        db.add(obj)
    db.commit()
    return {"message": "Stats updated"}

@router.post("/deadlines", dependencies=[Depends(permission_required("MANAGE_ADMISSIONS"))])
def post_deadline(deadline: AdmissionDeadlineSchema, db: Session = Depends(get_db)):
    obj = AdmissionDeadline(
        program=deadline.program,
        level=deadline.level,
        date=deadline.date,  # Already a date object from Pydantic
        requirements=deadline.requirements,
        notes=deadline.notes
    )
    db.add(obj)
    db.commit()
    return {"message": "Deadline added"}

@router.post("/faqs", dependencies=[Depends(permission_required("MANAGE_ADMISSIONS"))])
def post_faq(faq: AdmissionFAQSchema, db: Session = Depends(get_db)):
    obj = AdmissionFAQ(
        question=faq.question,
        answer=faq.answer,
        category=faq.category
    )
    db.add(obj)
    db.commit()
    return {"message": "FAQ added"}
