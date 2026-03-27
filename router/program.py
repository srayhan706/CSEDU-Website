from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime
from enum import Enum

from database import get_db
from models import Program, Course

from middleware import permission_required
# Program schemas
# Valid program levels
VALID_PROGRAM_LEVELS = ["Undergraduate", "Graduate", "Postgraduate"]


class CareerProspect(BaseModel):
    title: str
    description: str
    salary_range: Optional[str] = None
    companies: Optional[List[str]] = None


class ProgramBase(BaseModel):
    title: str
    level: str
    duration: str
    short_description: str
    description: Optional[str] = None
    specializations: Optional[List[str]] = None
    learning_objectives: Optional[List[str]] = None
    career_prospects: Optional[List[CareerProspect]] = None
    
    @validator('level')
    def validate_level(cls, v):
        if v not in VALID_PROGRAM_LEVELS:
            raise ValueError(f"Level must be one of {VALID_PROGRAM_LEVELS}")
        return v


class ProgramCreate(ProgramBase):
    pass


class CareerProspectResponse(BaseModel):
    title: str
    description: str
    avgSalary: str
    
    model_config = {
        "from_attributes": True,
        "populate_by_name": True
    }

class ProgramResponse(BaseModel):
    id: str
    title: str
    level: str
    duration: str
    totalStudents: int
    totalCourses: int
    totalCredits: int
    shortDescription: str
    description: str
    specializations: List[str]
    learningObjectives: List[str]
    careerProspects: List[CareerProspectResponse]
    
    model_config = {
        "from_attributes": True,
        "populate_by_name": True
    }
        
    @classmethod
    def from_orm(cls, db_obj):
        # Convert database object to response model
        career_prospects = []
        try:
            if db_obj.career_prospects:
                for cp in db_obj.career_prospects:
                    try:
                        # Handle career prospects as dictionaries
                        if isinstance(cp, dict):
                            # Ensure we have a string value for avgSalary
                            salary = cp.get('salary_range')
                            if salary is None:
                                salary = 'N/A'
                                
                            career_prospects.append(CareerProspectResponse(
                                title=cp.get('title', ''),
                                description=cp.get('description', ''),
                                avgSalary=str(salary)  # Ensure it's a string
                            ))
                        else:
                            # Handle as objects if they are
                            # Ensure we have a string value for avgSalary
                            try:
                                salary = cp.salary_range
                                if salary is None:
                                    salary = 'N/A'
                            except AttributeError:
                                salary = 'N/A'
                                
                            try:
                                title = cp.title
                            except AttributeError:
                                title = ''
                                
                            try:
                                description = cp.description
                            except AttributeError:
                                description = ''
                                
                            career_prospects.append(CareerProspectResponse(
                                title=title,
                                description=description,
                                avgSalary=str(salary)  # Ensure it's a string
                            ))
                    except Exception:
                        # Skip any problematic career prospect
                        continue
        except Exception:
            # If any error occurs with career_prospects, just use an empty list
            pass
                    
        return cls(
            id=str(db_obj.id),
            title=db_obj.title,
            level=db_obj.level,
            duration=db_obj.duration,
            totalStudents=db_obj.total_students,
            totalCourses=db_obj.total_courses,
            totalCredits=db_obj.total_credits,
            shortDescription=db_obj.short_description,
            description=db_obj.description or "",
            specializations=db_obj.specializations or [],
            learningObjectives=db_obj.learning_objectives or [],
            careerProspects=career_prospects
        )


# Course schemas
# Valid course difficulty levels
VALID_COURSE_DIFFICULTIES = ["Beginner", "Intermediate", "Advanced"]


class CourseBase(BaseModel):
    code: str
    title: str
    description: Optional[str] = None
    credits: int
    duration: str
    difficulty: str = "Intermediate"
    
    @validator('difficulty')
    def validate_difficulty(cls, v):
        if v not in VALID_COURSE_DIFFICULTIES:
            raise ValueError(f"Difficulty must be one of {VALID_COURSE_DIFFICULTIES}")
        return v
    prerequisites: Optional[List[str]] = None
    specialization: Optional[str] = None
    semester: int
    year: int
    program_id: int


class CourseCreate(CourseBase):
    pass


class CourseResponse(BaseModel):
    id: str
    code: str
    title: str
    description: str
    credits: int
    duration: str
    difficulty: str
    rating: float
    enrolledStudents: int
    prerequisites: List[str]
    specialization: str
    semester: int
    year: int
    
    model_config = {
        "from_attributes": True,
        "populate_by_name": True
    }
        
    @classmethod
    def from_orm(cls, db_obj):
        # Convert database object to response model with robust error handling
        try:
            # Safely handle prerequisites - ensure it's a list of strings
            prerequisites = []
            try:
                if db_obj.prerequisites:
                    if isinstance(db_obj.prerequisites, list):
                        for prereq in db_obj.prerequisites:
                            try:
                                if isinstance(prereq, str):
                                    prerequisites.append(prereq)
                                elif isinstance(prereq, dict) and 'code' in prereq:
                                    prerequisites.append(prereq['code'])
                                else:
                                    prerequisites.append(str(prereq))
                            except Exception:
                                # Skip any problematic prerequisite
                                continue
                    else:
                        # Handle case where prerequisites might not be a list
                        prerequisites = [str(db_obj.prerequisites)]
            except Exception:
                # If any error with prerequisites, use empty list
                prerequisites = []
                
            # Get all required fields with safe defaults
            return cls(
                id=str(db_obj.id),
                code=getattr(db_obj, 'code', ''),
                title=getattr(db_obj, 'title', ''),
                description=getattr(db_obj, 'description', '') or "",
                credits=getattr(db_obj, 'credits', 0),
                duration=getattr(db_obj, 'duration', ''),
                difficulty=getattr(db_obj, 'difficulty', 'Intermediate'),
                rating=getattr(db_obj, 'rating', 0.0),
                enrolledStudents=getattr(db_obj, 'enrolled_students', 0),
                prerequisites=prerequisites,
                specialization=getattr(db_obj, 'specialization', '') or "",
                semester=getattr(db_obj, 'semester', 1),
                year=getattr(db_obj, 'year', 2025)
            )
        except Exception as e:
            # If anything fails, return a minimal valid object
            return cls(
                id=str(getattr(db_obj, 'id', 0)),
                code=getattr(db_obj, 'code', ''),
                title=getattr(db_obj, 'title', ''),
                description="",
                credits=0,
                duration="",
                difficulty="Intermediate",
                rating=0.0,
                enrolledStudents=0,
                prerequisites=[],
                specialization="",
                semester=1,
                year=2025
            )

program_router = APIRouter(
    prefix="/api/programs",
    tags=["programs"],
    responses={404: {"description": "Not found"}},
)

course_router = APIRouter(
    prefix="/api/courses",
    tags=["courses"],
    responses={404: {"description": "Not found"}},
)


@program_router.get("", response_model=Dict[str, List[ProgramResponse]])
async def get_programs(db: Session = Depends(get_db)):
    """
    Get all academic programs
    """
    programs = db.query(Program).all()
    return {"programs": [ProgramResponse.from_orm(p) for p in programs]}


@program_router.post("", response_model=ProgramResponse, status_code=status.HTTP_201_CREATED)
async def create_program(
    program: ProgramBase,
    db: Session = Depends(get_db),
    current_user: dict = Depends(permission_required("MANAGE_COURSE_PROGRAMS"))
):

    """
    Create a new academic program (requires MANAGE_COURSE_PROGRAMS permission)
    """
    # Convert career_prospects to dict before saving to database

    career_prospects_data = None
    if program.career_prospects:
        career_prospects_data = [cp.model_dump() for cp in program.career_prospects]
    
    # No need for special handling anymore - level is a simple string
    
    # Create the program with all fields - level is now just a string
    db_program = Program(
        title=program.title,
        level=program.level,  # Simple string now
        duration=program.duration,
        short_description=program.short_description,
        description=program.description,
        specializations=program.specializations,
        learning_objectives=program.learning_objectives,
        career_prospects=career_prospects_data,
        # Initialize required fields for ProgramResponse
        total_students=0,  # Start with 0 students
        total_courses=0,   # Start with 0 courses
        total_credits=0    # Start with 0 credits
    )
    
    db.add(db_program)
    db.commit()
    
    # Refresh the program using session.refresh instead of raw SQL
    # This should work now that we've set the level correctly
    try:
        db.refresh(db_program)
    except Exception as e:
        # If refresh fails, we'll return the program without refreshing
        # The program has already been committed to the database
        pass
    
    # Convert the database object to the response model format
    return ProgramResponse.from_orm(db_program)


@program_router.get("/{program_id}", response_model=ProgramResponse)
async def get_program(program_id: int, db: Session = Depends(get_db)):
    """
    Get a specific academic program by ID
    """
    program = db.query(Program).filter(Program.id == program_id).first()
    if not program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Program with ID {program_id} not found"
        )
    return ProgramResponse.from_orm(program)


@program_router.put("/{program_id}", response_model=ProgramResponse)
async def update_program(
    program_id: int,
    program_update: ProgramCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(permission_required("MANAGE_COURSE_PROGRAMS"))
):
    """
    Update an academic program (requires MANAGE_COURSE_PROGRAMS permission)
    """
    db_program = db.query(Program).filter(Program.id == program_id).first()
    if not db_program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Program with ID {program_id} not found"
        )
    
    # Get the program data - level is already a string from validation
    program_data = program_update.model_dump()
    
    # Special handling for career_prospects
    if 'career_prospects' in program_data and program_data['career_prospects']:
        career_prospects_data = [cp.model_dump() for cp in program_update.career_prospects]
        program_data['career_prospects'] = career_prospects_data
    
    # Update all attributes
    for key, value in program_data.items():
        setattr(db_program, key, value)
    
    # Commit the changes
    db.commit()
    
    # Try to refresh the program
    try:
        db.refresh(db_program)
    except Exception as e:
        # If refresh fails, we'll return the program without refreshing
        # The program has already been committed to the database
        pass
    return ProgramResponse.from_orm(db_program)


@program_router.delete("/{program_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_program(
    program_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(permission_required("MANAGE_COURSE_PROGRAMS"))
):
    """
    Delete an academic program (requires MANAGE_COURSE_PROGRAMS permission)
    """
    db_program = db.query(Program).filter(Program.id == program_id).first()
    if not db_program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Program with ID {program_id} not found"
        )
    
    # Check if there are courses associated with this program
    courses_count = db.query(Course).filter(Course.program_id == program_id).count()
    if courses_count > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete program with ID {program_id} as it has {courses_count} courses associated with it"
        )
    
    db.delete(db_program)
    db.commit()
    return None




# Course endpoints
@course_router.get("", response_model=Dict[str, List[CourseResponse]])
async def get_courses(db: Session = Depends(get_db)):
    """
    Get all courses
    """
    courses = db.query(Course).all()
    return {"courses": [CourseResponse.from_orm(c) for c in courses]}


@course_router.post("", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
async def create_course(
    course: CourseCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(permission_required("MANAGE_COURSE_PROGRAMS"))
):
    """
    Create a new course (requires MANAGE_COURSE_PROGRAMS permission)
    """
    # Check if program exists
    program = db.query(Program).filter(Program.id == course.program_id).first()
    if not program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Program with ID {course.program_id} not found"
        )
    
    # Check if course code already exists
    existing_course = db.query(Course).filter(Course.code == course.code).first()
    if existing_course:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Course with code {course.code} already exists"
        )
    
    db_course = Course(**course.model_dump())
    
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    
    # Update program stats
    program.total_courses += 1
    program.total_credits += course.credits
    db.commit()
    
    return db_course


@course_router.get("/{course_id}", response_model=CourseResponse)
async def get_course(course_id: int, db: Session = Depends(get_db)):
    """
    Get a specific course by ID
    """
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course with ID {course_id} not found"
        )
    return course


@course_router.put("/{course_id}", response_model=CourseResponse)
async def update_course(
    course_id: int,
    course_update: CourseCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(permission_required("MANAGE_COURSE_PROGRAMS"))
):
    """
    Update a course (requires MANAGE_COURSE_PROGRAMS permission)
    """
    db_course = db.query(Course).filter(Course.id == course_id).first()
    if not db_course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course with ID {course_id} not found"
        )
    
    # Check if program exists if program_id is being updated
    if course_update.program_id != db_course.program_id:
        program = db.query(Program).filter(Program.id == course_update.program_id).first()
        if not program:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Program with ID {course_update.program_id} not found"
            )
    
    # Check if course code already exists if code is being updated
    if course_update.code != db_course.code:
        existing_course = db.query(Course).filter(Course.code == course_update.code).first()
        if existing_course:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Course with code {course_update.code} already exists"
            )
    
    # Update course attributes
    for key, value in course_update.model_dump().items():
        setattr(db_course, key, value)
    
    db.commit()
    db.refresh(db_course)
    return db_course


@course_router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(permission_required("MANAGE_COURSE_PROGRAMS"))
):
    """
    Delete a course (requires MANAGE_COURSE_PROGRAMS permission)
    """
    db_course = db.query(Course).filter(Course.id == course_id).first()
    if not db_course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course with ID {course_id} not found"
        )
        
    
    # Update program stats
    program = db.query(Program).filter(Program.id == db_course.program_id).first()
    if program:
        program.total_courses -= 1
        program.total_credits -= db_course.credits
        db.commit()
    
    db.delete(db_course)
    db.commit()
    return None
