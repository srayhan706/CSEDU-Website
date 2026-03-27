"""
API Schema:
GET /api/student/exams
Response: [
  {
    id: number,
    title: string,
    course_code: string,
    course_title: string,
    date: string (ISO format),
    start_time: string (HH:MM format),
    end_time: string (HH:MM format),
    location: string,
    type: string (midterm, final, quiz, etc),
    status: string (upcoming, ongoing, completed),
    total_marks: number,
    obtained_marks: number | null,
    instructions: string | null,
    materials_allowed: string[] | null,
    syllabus_topics: string[] | null,
    year: number,
    semester: number
  }
]

GET /api/student/exams/{exam_id}
Response: {
  id: number,
  title: string,
  course_code: string,
  course_title: string,
  date: string (ISO format),
  start_time: string (HH:MM format),
  end_time: string (HH:MM format),
  location: string,
  type: string (midterm, final, quiz, etc),
  status: string (upcoming, ongoing, completed),
  total_marks: number,
  obtained_marks: number | null,
  instructions: string,
  materials_allowed: string[],
  syllabus_topics: string[],
  year: number,
  semester: number
}
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from database import get_db
from models import Exam, Course, User
from dependencies import get_user_from_session
from pydantic import BaseModel
from datetime import datetime, date
import json
from typing import List, Optional

router = APIRouter(prefix="/api/student")

class MaterialsAllowed(BaseModel):
    name: str

class SyllabusTopic(BaseModel):
    topic: str

class ExamResponse(BaseModel):
    id: int
    title: str
    course_code: str
    course_title: str
    date: date
    start_time: str
    end_time: str
    location: str
    type: str
    status: str
    total_marks: int
    obtained_marks: Optional[int] = None
    instructions: Optional[str] = None
    materials_allowed: Optional[List[str]] = None
    syllabus_topics: Optional[List[str]] = None
    year: int
    semester: int

@router.get("/exams", response_model=List[ExamResponse])
def get_student_exams(
    status: Optional[str] = Query(None, description="Filter by status (upcoming, ongoing, completed)"),
    type: Optional[str] = Query(None, description="Filter by exam type (midterm, final, quiz, etc)"),
    db: Session = Depends(get_db),
    user: dict = Depends(get_user_from_session)
):
    """
    Get all exams for the logged-in student with optional filtering
    """
    # Get the user ID from the session
    user_id = user["id"]
    
    # Join Exam with Course to get course information
    # In a real implementation, you would filter exams by the student's enrolled courses
    # For now, we'll return all exams as a demonstration
    query = db.query(Exam).join(Course, Exam.course_id == Course.id)
    
    # Apply filters if provided
    if status:
        # Calculate status based on current date and exam date
        current_datetime = datetime.now()
        
        if status == "upcoming":
            query = query.filter(Exam.date > current_datetime.date())
        elif status == "ongoing":
            query = query.filter(
                Exam.date == current_datetime.date(),
                # This is a simplified check - in reality you'd compare with actual time
                # and consider start_time and end_time
            )
        elif status == "completed":
            query = query.filter(Exam.date < current_datetime.date())
    
    if type:
        query = query.filter(Exam.type == type)
    
    # Order by date (upcoming first)
    exams = query.order_by(Exam.date, Exam.start_time).all()
    
    # Transform to response model
    result = []
    current_datetime = datetime.now()
    
    for exam in exams:
        # Calculate exam status based on current date and time
        status = "upcoming"
        if exam.date < current_datetime.date():
            status = "completed"
        elif exam.date == current_datetime.date():
            # Simple time comparison - could be improved with proper time parsing
            current_time = current_datetime.strftime("%H:%M")
            if current_time >= exam.start_time and current_time <= exam.end_time:
                status = "ongoing"
            elif current_time > exam.end_time:
                status = "completed"
        
        # Parse JSON fields if they're stored as strings
        materials_allowed = []
        if exam.materials_allowed:
            if isinstance(exam.materials_allowed, str):
                try:
                    materials_allowed = json.loads(exam.materials_allowed)
                except:
                    materials_allowed = []
            else:
                materials_allowed = exam.materials_allowed
        
        syllabus_topics = []
        if exam.syllabus_topics:
            if isinstance(exam.syllabus_topics, str):
                try:
                    syllabus_topics = json.loads(exam.syllabus_topics)
                except:
                    syllabus_topics = []
            else:
                syllabus_topics = exam.syllabus_topics
        
        # Get course information
        course = db.query(Course).filter(Course.id == exam.course_id).first()
        
        result.append(
            ExamResponse(
                id=exam.id,
                title=exam.title,
                course_code=course.code if course else "Unknown",
                course_title=course.title if course else "Unknown",
                date=exam.date,
                start_time=exam.start_time,
                end_time=exam.end_time,
                location=exam.location,
                type=exam.type,
                status=status,
                total_marks=exam.total_marks,
                obtained_marks=exam.obtained_marks,
                instructions=exam.instructions,
                materials_allowed=materials_allowed,
                syllabus_topics=syllabus_topics,
                year=course.year if course else 0,
                semester=course.semester if course else 0
            )
        )
    
    return result

@router.get("/exams/{exam_id}", response_model=ExamResponse)
def get_student_exam_details(
    exam_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(get_user_from_session)
):
    """
    Get detailed information about a specific exam
    """
    # Get the exam
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")
    
    # Get course information
    course = db.query(Course).filter(Course.id == exam.course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Calculate exam status
    current_datetime = datetime.now()
    status = "upcoming"
    if exam.date < current_datetime.date():
        status = "completed"
    elif exam.date == current_datetime.date():
        current_time = current_datetime.strftime("%H:%M")
        if current_time >= exam.start_time and current_time <= exam.end_time:
            status = "ongoing"
        elif current_time > exam.end_time:
            status = "completed"
    
    # Parse JSON fields if they're stored as strings
    materials_allowed = []
    if exam.materials_allowed:
        if isinstance(exam.materials_allowed, str):
            try:
                materials_allowed = json.loads(exam.materials_allowed)
            except:
                materials_allowed = []
        else:
            materials_allowed = exam.materials_allowed
    
    syllabus_topics = []
    if exam.syllabus_topics:
        if isinstance(exam.syllabus_topics, str):
            try:
                syllabus_topics = json.loads(exam.syllabus_topics)
            except:
                syllabus_topics = []
        else:
            syllabus_topics = exam.syllabus_topics
    
    return ExamResponse(
        id=exam.id,
        title=exam.title,
        course_code=course.code,
        course_title=course.title,
        date=exam.date,
        start_time=exam.start_time,
        end_time=exam.end_time,
        location=exam.location,
        type=exam.type,
        status=status,
        total_marks=exam.total_marks,
        obtained_marks=exam.obtained_marks,
        instructions=exam.instructions,
        materials_allowed=materials_allowed,
        syllabus_topics=syllabus_topics,
        year=course.year,
        semester=course.semester
    )
