from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict
from pydantic import BaseModel, Field
from datetime import datetime, date
from models import Exam
from database import get_db
from middleware import permission_required
from models import User
router = APIRouter(prefix="/api/exams", tags=["exams"])

class ExamBase(BaseModel):
    courseCode: str
    courseTitle: str
    semester: int
    batch: str
    examType: str  # "midterm" | "final" | "retake" | "improvement"
    date: date
    startTime: str  # "HH:MM"
    endTime: str    # "HH:MM"
    room: str
    invigilators: List[str]
    status: str     # "scheduled" | "ongoing" | "completed" | "cancelled"
    notes: str = ""

class ExamCreate(ExamBase):
    invigilators: List[int]  # List of user IDs

class ExamResponse(ExamBase):
    id: int
    class Config:
        from_attributes = True

@router.get("", response_model=List[ExamResponse])
def get_exams(db: Session = Depends(get_db)):
    exams = db.query(Exam).all()
    result = []
    
    for e in exams:
        try:
            exam_response = ExamResponse(
                id=e.id,
                courseCode=e.courseCode,
                courseTitle=e.courseTitle,
                semester=e.semester,
                batch=e.batch,
                examType=e.examType,
                date=e.date,
                startTime=e.startTime,
                endTime=e.endTime,
                room=e.room,
                invigilators=e.invigilators,
                status=e.status,
                notes=e.notes if e.notes else ""
            )
            result.append(exam_response)
        except Exception as ex:
            print(f"Error processing exam {e.id}: {ex}")
    
    return result

@router.post("", response_model=ExamResponse)
def create_exam(
    exam: ExamCreate,
    officer: dict = Depends(permission_required("MANAGE_NOTICES")),
    db: Session = Depends(get_db)
):
    # Resolve user IDs to names
    invigilator_names = []
    for user_id in exam.invigilators:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail=f"Invigilator user id {user_id} not found")
        invigilator_names.append(user.name)
    new_exam = Exam(
        courseCode=exam.courseCode,
        courseTitle=exam.courseTitle,
        semester=exam.semester,
        batch=exam.batch,
        examType=exam.examType,
        date=datetime.combine(exam.date, datetime.min.time()),
        startTime=exam.startTime,
        endTime=exam.endTime,
        room=exam.room,
        invigilators=invigilator_names,
        status=exam.status,
        notes=exam.notes
    )
    db.add(new_exam)
    db.commit()
    db.refresh(new_exam)
    return new_exam
