from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from enum import Enum
import json

from database import get_db
from models import Course, Program
from middleware import permission_required

# Course schemas
class CourseLevel(str, Enum):
    UNDERGRADUATE = "Undergraduate"
    GRADUATE = "Graduate"

class CourseTag(BaseModel):
    name: str

class CourseResponse(BaseModel):
    id: str
    courseCode: str
    title: str
    description: str
    credits: int
    department: str
    level: CourseLevel
    semester: int
    prerequisites: List[str] = []
    instructors: List[str] = []
    syllabus: str
    tags: List[str] = []

    class Config:
        from_attributes = True
        populate_by_name = True

class CoursesResponse(BaseModel):
    courses: List[CourseResponse]
    departments: List[str]
    levels: List[str]
    semesters: List[int]

# Mock data for development
mock_courses = [
    {
        "id": "CSE101",
        "courseCode": "CSE101",
        "title": "Introduction to Computer Science",
        "description": "An introductory course covering the basics of computer science, programming concepts, and problem-solving techniques.",
        "credits": 3,
        "department": "Computer Science",
        "level": "Undergraduate",
        "semester": 1,
        "prerequisites": [],
        "instructors": ["Dr. Mahmuda Naznin"],
        "syllabus": "Introduction to programming, basic algorithms, data structures, and computer organization.",
        "tags": ["Programming", "Algorithms", "Beginner"]
    },
    {
        "id": "CSE203",
        "courseCode": "CSE203",
        "title": "Data Structures",
        "description": "Study of data organization, management, and storage formats that enable efficient access and modification.",
        "credits": 4,
        "department": "Computer Science",
        "level": "Undergraduate",
        "semester": 2,
        "prerequisites": ["CSE101"],
        "instructors": ["Dr. Sadia Sharmin"],
        "syllabus": "Arrays, linked lists, stacks, queues, trees, graphs, sorting and searching algorithms.",
        "tags": ["Programming", "Algorithms", "Data Structures"]
    },
    {
        "id": "CSE307",
        "courseCode": "CSE307",
        "title": "Software Engineering",
        "description": "Principles and practices of software development and project management.",
        "credits": 3,
        "department": "Software Engineering",
        "level": "Undergraduate",
        "semester": 5,
        "prerequisites": ["CSE203"],
        "instructors": ["Dr. Kazi Muheymin-Us-Sakib"],
        "syllabus": "Software development lifecycle, requirements engineering, design patterns, testing, maintenance.",
        "tags": ["Software Development", "Project Management"]
    },
    {
        "id": "CSE401",
        "courseCode": "CSE401",
        "title": "Computer Networks",
        "description": "Study of computer network architecture, protocols, and applications.",
        "credits": 3,
        "department": "Computer Science",
        "level": "Undergraduate",
        "semester": 4,
        "prerequisites": ["CSE203"],
        "instructors": ["Dr. Muhammad Masroor Ali"],
        "syllabus": "Network models, TCP/IP, routing, network security, wireless networks.",
        "tags": ["Networks", "Protocols", "Security"]
    },
    {
        "id": "CSE503",
        "courseCode": "CSE503",
        "title": "Advanced Machine Learning",
        "description": "Advanced techniques in machine learning and deep learning.",
        "credits": 4,
        "department": "Computer Science",
        "level": "Graduate",
        "semester": 2,
        "prerequisites": ["CSE309", "CSE317"],
        "instructors": ["Dr. Abu Sayed Md. Latiful Hoque"],
        "syllabus": "Deep neural networks, reinforcement learning, generative models, and applications.",
        "tags": ["AI", "Machine Learning", "Deep Learning", "Advanced"]
    }
]

# Extract unique departments, levels, and semesters from mock data
departments = list(set(course["department"] for course in mock_courses))
levels = list(set(course["level"] for course in mock_courses))
semesters = sorted(list(set(course["semester"] for course in mock_courses)))

router = APIRouter(
    prefix="/api/courses",
    tags=["courses"],
    responses={404: {"description": "Not found"}}
)

@router.get("", response_model=CoursesResponse)
async def get_courses(db: Session = Depends(get_db)):
    """
    Get all courses with filter options
    """
    # Query the database for courses
    db_courses = db.query(Course).all()
    
    # Transform database courses to response format
    courses = []
    departments = set()
    levels = set()
    semesters = set()
    
    for course in db_courses:
        # Get program details
        program = db.query(Program).filter(Program.id == course.program_id).first()
        if program:
            department = program.title.split(' in ')[-1] if ' in ' in program.title else "Computer Science"
            level = program.level
            departments.add(department)
            levels.add(level)
            semesters.add(course.semester)
            
            # Parse prerequisites from JSON string
            prerequisites = json.loads(course.prerequisites) if course.prerequisites else []
            
            # Create course response object
            course_response = {
                "id": course.code,
                "courseCode": course.code,
                "title": course.title,
                "description": course.description,
                "credits": course.credits,
                "department": department,
                "level": level,
                "semester": course.semester,
                "prerequisites": prerequisites,
                "instructors": [], # We don't have instructor data yet
                "syllabus": f"Syllabus for {course.title}",
                "tags": [course.specialization] if course.specialization else []
            }
            courses.append(course_response)
    
    return {
        "courses": courses,
        "departments": list(departments),
        "levels": list(levels),
        "semesters": sorted(list(semesters))
    }

@router.get("/{course_id}", response_model=CourseResponse)
async def get_course(course_id: str, db: Session = Depends(get_db)):
    """
    Get a specific course by ID
    """
    # Query the database for the course
    db_course = db.query(Course).filter(Course.code == course_id).first()
    
    if not db_course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course with ID {course_id} not found"
        )
    
    # Get program details
    program = db.query(Program).filter(Program.id == db_course.program_id).first()
    
    if not program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Program for course {course_id} not found"
        )
    
    # Extract department from program title
    department = program.title.split(' in ')[-1] if ' in ' in program.title else "Computer Science"
    
    # Parse prerequisites from JSON string
    prerequisites = json.loads(db_course.prerequisites) if db_course.prerequisites else []
    
    # Create course response object
    course_response = {
        "id": db_course.code,
        "courseCode": db_course.code,
        "title": db_course.title,
        "description": db_course.description,
        "credits": db_course.credits,
        "department": department,
        "level": program.level,
        "semester": db_course.semester,
        "prerequisites": prerequisites,
        "instructors": [], # We don't have instructor data yet
        "syllabus": f"Syllabus for {db_course.title}",
        "tags": [db_course.specialization] if db_course.specialization else []
    }
    
    return course_response
