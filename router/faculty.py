from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Path, status
from sqlalchemy.orm import Session
from models import Faculty, User, FacultyDesignation
import database
from enum import Enum
from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime

from middleware import permission_required

router = APIRouter(
    prefix="/api/faculty",
    tags=["faculty"],
    responses={404: {"description": "Not found"}},
)

# Request/Response Models
class FacultyDesignationEnum(str, Enum):
    PROFESSOR = "Professor"
    ASSOCIATE_PROFESSOR = "Associate Professor"
    ASSISTANT_PROFESSOR = "Assistant Professor"
    LECTURER = "Lecturer"

class FacultyBase(BaseModel):
    designation: FacultyDesignationEnum
    department: str
    expertise: List[str]
    office: Optional[str] = None
    image: Optional[str] = None
    website: Optional[str] = None
    publications: int = 0
    experience: int = 0
    rating: float = 0.0
    is_chairman: bool = False
    bio: Optional[str] = None
    short_bio: Optional[str] = None
    education: Optional[List[str]] = None
    courses: Optional[List[str]] = None
    research_interests: Optional[List[str]] = None
    recent_publications: Optional[List[dict]] = None
    awards: Optional[List[str]] = None
    office_hours: Optional[str] = None

    class Config:
        from_attributes = True

class FacultyCreate(FacultyBase):
    pass

class FacultyUpdate(BaseModel):
    designation: Optional[FacultyDesignationEnum] = None
    department: Optional[str] = None
    expertise: Optional[List[str]] = None
    office: Optional[str] = None
    image: Optional[str] = None
    website: Optional[str] = None
    publications: Optional[int] = None
    experience: Optional[int] = None
    rating: Optional[float] = None
    is_chairman: Optional[bool] = None
    bio: Optional[str] = None
    short_bio: Optional[str] = None
    education: Optional[List[str]] = None
    courses: Optional[List[str]] = None
    research_interests: Optional[List[str]] = None
    recent_publications: Optional[List[dict]] = None
    awards: Optional[List[str]] = None
    office_hours: Optional[str] = None

    class Config:
        from_attributes = True

class FacultyResponse(BaseModel):
    id: int
    name: str
    email: str
    contact: Optional[str] = None
    username: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class FacultyListResponse(BaseModel):
    faculty: List[FacultyResponse]
    roles: List[str]
    expertise_areas: List[str]

    class Config:
        from_attributes = True

class FacultyDetailResponse(BaseModel):
    faculty: Dict[str, Any]

    class Config:
        from_attributes = True

# Routes
# Get courses taught by a faculty member
@router.get("/courses", response_model=Dict[str, Any])
async def get_faculty_courses(
    db: Session = Depends(database.get_db)
):
    """
    Get all courses taught by the authenticated faculty member.
    """
    try:
        # For now, we'll return some mock data since we don't have actual faculty-course relationships
        faculty_courses = [
            {
                "id": "CSE101",
                "courseCode": "CSE101",
                "title": "Introduction to Computer Science",
                "description": "An introductory course covering the basics of computer science, programming concepts, and problem-solving techniques.",
                "credits": 3,
                "department": "Computer Science and Engineering",
                "level": "Undergraduate",
                "semester": 1,
                "students": 45,
                "schedule": "Mon, Wed 10:00-11:30 AM",
                "room": "Room 301"
            },
            {
                "id": "CSE303",
                "courseCode": "CSE303",
                "title": "Database Systems",
                "description": "Introduction to database design, implementation, and management with focus on relational database systems.",
                "credits": 4,
                "department": "Computer Science and Engineering",
                "level": "Undergraduate",
                "semester": 3,
                "students": 38,
                "schedule": "Tue, Thu 1:00-2:30 PM",
                "room": "Room 405"
            },
            {
                "id": "CSE405",
                "courseCode": "CSE405",
                "title": "Artificial Intelligence",
                "description": "Fundamental concepts and techniques in artificial intelligence including knowledge representation, problem solving, search, and machine learning.",
                "credits": 3,
                "department": "Computer Science and Engineering",
                "level": "Undergraduate",
                "semester": 4,
                "students": 32,
                "schedule": "Wed, Fri 3:00-4:30 PM",
                "room": "Room 201"
            }
        ]
        
        return {
            "courses": faculty_courses,
            "total": len(faculty_courses)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching faculty courses: {str(e)}")

@router.get("", response_model=FacultyListResponse)
async def get_faculty(
    department: Optional[str] = None,
    designation: Optional[FacultyDesignationEnum] = None,
    db: Session = Depends(database.get_db)
):
    """
    Get all faculty members with optional filtering by department and designation.
    Public endpoint - no authentication required.
    """
    try:
        # Query faculty records
        query = db.query(Faculty)
        if department:
            query = query.filter(Faculty.department.ilike(f"%{department}%"))
        if designation:
            query = query.filter(Faculty.designation == designation)
        faculty_records = query.all()
        
        # Get all faculty designations for filtering
        roles = [d.value for d in FacultyDesignation]
        expertise_areas = set()
        faculty_list = []
        
        # Process each faculty record
        for f in faculty_records:
            try:
                # Get associated user record
                user = db.query(User).filter(User.id == f.id).first()
                if not user:
                    # Skip faculty records without a corresponding user
                    continue
                
                # Create faculty dictionary with safe access to properties
                faculty_dict = {
                    "id": f.id,
                    "name": user.name if hasattr(user, 'name') else "",
                    "email": user.email if hasattr(user, 'email') else "",
                    "contact": user.contact if hasattr(user, 'contact') and user.contact else "",
                    "username": user.username if hasattr(user, 'username') and user.username else "",
                    "designation": f.designation if f.designation else "",
                    "department": f.department if f.department else "",
                    "expertise": f.expertise if f.expertise else [],
                    "office": f.office if f.office else "",
                    "image": f.image if f.image else "",
                    "website": f.website if f.website else "",
                    "publications": f.publications if f.publications else 0,
                    "experience": f.experience if f.experience else 0,
                    "rating": f.rating if f.rating else 4.0,
                    "is_chairman": f.is_chairman if f.is_chairman is not None else False,
                    "bio": f.bio if f.bio else "",
                    "short_bio": f.short_bio if f.short_bio else "",
                    "education": f.education if f.education else [],
                    "courses": f.courses if f.courses else [],
                    "research_interests": f.research_interests if f.research_interests else [],
                    "recent_publications": f.recent_publications if f.recent_publications else [],
                    "awards": f.awards if f.awards else [],
                    "office_hours": f.office_hours if f.office_hours else "",
                    "created_at": f.created_at,
                    "updated_at": f.updated_at,
                }
                faculty_list.append(faculty_dict)
                
                # Extract expertise areas for filtering
                if f.expertise:
                    if isinstance(f.expertise, list):
                        expertise_areas.update(f.expertise)
                    elif isinstance(f.expertise, str):
                        try:
                            import json
                            expertise_areas.update(json.loads(f.expertise))
                        except Exception:
                            pass
            except Exception as e:
                print(f"Error processing faculty record: {e}")
                continue
        
        return {
            "faculty": faculty_list,
            "roles": sorted(roles),
            "expertise_areas": sorted(list(expertise_areas))
        }
    except Exception as e:
        print(f"Error in get_faculty endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching faculty data: {str(e)}")

@router.get("/{faculty_id}", response_model=Dict[str, Any])
async def get_faculty_by_id(
    faculty_id: str,
    db: Session = Depends(database.get_db)
):
    """Get a single faculty member by ID with detailed information."""
    try:
        # Query the faculty record
        faculty = db.query(Faculty).filter(Faculty.id == faculty_id).first()
        if not faculty:
            raise HTTPException(status_code=404, detail=f"Faculty with ID {faculty_id} not found")
            
        # Get the associated user record
        user = db.query(User).filter(User.id == faculty.id).first()
        if not user:
            raise HTTPException(status_code=404, detail=f"User record for faculty ID {faculty_id} not found")
        
        # Process expertise areas
        expertise = []
        if faculty.expertise:
            if isinstance(faculty.expertise, list):
                expertise = faculty.expertise
            elif isinstance(faculty.expertise, str):
                import json
                try:
                    expertise = json.loads(faculty.expertise)
                except:
                    expertise = [faculty.expertise]
        
        # Construct the response
        faculty_detail = {
            "id": faculty.id,
            "name": user.name,
            "email": user.email,
            "designation": faculty.designation,
            "department": faculty.department,
            "role": faculty.designation,  # Using designation as role
            "expertise": expertise,
            "phone": faculty.phone if hasattr(faculty, 'phone') else "",
            "office": faculty.office if hasattr(faculty, 'office') else "",
            "image": faculty.image if hasattr(faculty, 'image') else "",
            "website": faculty.website if hasattr(faculty, 'website') else "",
            "publications": faculty.publications if hasattr(faculty, 'publications') else 0,
            "experience": faculty.experience if hasattr(faculty, 'experience') else 0,
            "rating": faculty.rating if hasattr(faculty, 'rating') else 4.5,
            "is_chairman": faculty.is_chairman if hasattr(faculty, 'is_chairman') else False,
            "bio": faculty.bio if hasattr(faculty, 'bio') else "",
            "short_bio": faculty.short_bio if hasattr(faculty, 'short_bio') else "",
            "education": faculty.education if hasattr(faculty, 'education') else [],
            "courses": faculty.courses if hasattr(faculty, 'courses') else [],
            "research_interests": faculty.research_interests if hasattr(faculty, 'research_interests') else [],
            "recent_publications": faculty.recent_publications if hasattr(faculty, 'recent_publications') else [],
            "awards": faculty.awards if hasattr(faculty, 'awards') else [],
            "office_hours": faculty.office_hours if hasattr(faculty, 'office_hours') else ""
        }
        
        return {"faculty": faculty_detail}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching faculty detail: {str(e)}")

# Alias for backward compatibility
faculty_router = router
