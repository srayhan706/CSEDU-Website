from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from database import get_db
from models import Course, Program
from dependencies import get_user_from_session
from pydantic import BaseModel
from fastapi.responses import FileResponse
import os
import random
from pathlib import Path
import json

router = APIRouter(prefix="/api/student")

class CourseResponse(BaseModel):
    id: int
    code: str
    title: str
    description: str
    credits: int
    semester: int
    year: int
    difficulty: str
    has_syllabus: bool
    duration: str
    rating: float
    enrolled_students: int
    prerequisites: Optional[List[str]] = None
    specialization: Optional[str] = None
    program_name: Optional[str] = None

@router.get("/courses", response_model=List[CourseResponse])
def get_student_courses(
    year: Optional[int] = Query(None, description="Filter by year"),
    semester: Optional[int] = Query(None, description="Filter by semester"),
    db: Session = Depends(get_db),
    user: dict = Depends(get_user_from_session)
):
    """
    Get all courses for students with optional year and semester filtering
    """
    # Join Course with Program to get program information
    query = db.query(Course).join(Program, Course.program_id == Program.id)
    
    # Apply filters if provided
    if year is not None:
        query = query.filter(Course.year == year)
    
    if semester is not None:
        query = query.filter(Course.semester == semester)
    
    # Order by year and semester
    courses = query.order_by(Course.year, Course.semester).all()
    
    # Get all programs for lookup
    programs = {p.id: p.title for p in db.query(Program).all()}
    
    # Check for available syllabi
    syllabi_dir = Path("static/sample_pdfs")
    available_syllabi = [f.stem.split('_')[0] for f in syllabi_dir.glob("*_syllabus.pdf")] if syllabi_dir.exists() else []
    
    # Transform to response model
    result = []
    for course in courses:
        # Handle prerequisites (convert from JSON if needed)
        prerequisites = []
        if course.prerequisites:
            if isinstance(course.prerequisites, str):
                try:
                    prerequisites = json.loads(course.prerequisites)
                except:
                    prerequisites = []
            else:
                prerequisites = course.prerequisites
        
        result.append(
            CourseResponse(
                id=course.id,
                code=course.code,
                title=course.title,
                description=course.description or "",
                credits=course.credits,
                semester=course.semester,
                year=course.year,
                difficulty=course.difficulty,
                has_syllabus=course.code in available_syllabi,  # Check if syllabus exists
                duration=course.duration,
                rating=course.rating,
                enrolled_students=course.enrolled_students,
                prerequisites=prerequisites,
                specialization=course.specialization,
                program_name=programs.get(course.program_id, "")
            )
        )
    
    return result

@router.get("/courses/{course_id}/syllabus")
def download_syllabus(
    course_id: int,
    db: Session = Depends(get_db),
    user: dict = Depends(get_user_from_session)
):
    """
    Download the syllabus for a specific course
    """
    # Check if course exists
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Look for a specific syllabus for this course
    sample_pdfs_dir = Path("static/sample_pdfs")
    specific_syllabus = sample_pdfs_dir / f"{course.code}_syllabus.pdf"
    
    if specific_syllabus.exists():
        # Return the specific syllabus for this course
        return FileResponse(
            path=specific_syllabus,
            filename=f"{course.code}_syllabus.pdf",
            media_type="application/pdf"
        )
    else:
        # If no specific syllabus exists, find any available syllabus
        pdf_files = list(sample_pdfs_dir.glob("*.pdf"))
        if not pdf_files:
            raise HTTPException(status_code=404, detail="No syllabus files available for this course")
        
        # Select a random syllabus as fallback
        selected_pdf = random.choice(pdf_files)
        
        # Return the file as a download
        return FileResponse(
            path=selected_pdf,
            filename=f"{course.code}_syllabus.pdf",
            media_type="application/pdf"
        )
