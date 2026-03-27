from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, case, or_
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime

from models import Announcement, AnnouncementType, User, Role
import database

# Create router
router = APIRouter(
    prefix="/api",
    tags=["announcements"],
    responses={404: {"description": "Not found"}},
)

# Pydantic models for request/response validation
class StatsResponse(BaseModel):
    students: int
    faculty: int
    programs: int
    research: int

class OverviewResponse(BaseModel):

    stats: StatsResponse

from models import PriorityLevel
from models import AnnouncementType
from models import Announcement
from middleware import permission_required
from database import get_db



class AnnouncementCreate(BaseModel):
    title: str
    content: str
    date: Optional[datetime] = None
    type: AnnouncementType
    priority: PriorityLevel
    image: Optional[str] = None

class AnnouncementResponse(BaseModel):
    id: int
    title: str
    content: str
    date: datetime
    type: str
    priority: str
    image: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Routes


from fastapi import Body

@router.post("/announcements", response_model=AnnouncementResponse)
def create_announcement(
    announcement: AnnouncementCreate = Body(...),
    officer: dict = Depends(permission_required("MANAGE_NOTICES")),
    db: Session = Depends(get_db)
):
    new_announcement = Announcement(
        title=announcement.title,
        content=announcement.content,
        date=announcement.date or datetime.utcnow(),
        type=announcement.type,
        priority=announcement.priority,
        image=announcement.image,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(new_announcement)
    db.commit()
    db.refresh(new_announcement)
    return new_announcement

@router.get("/overview", response_model=OverviewResponse)
async def get_overview(db: Session = Depends(database.get_db)):
    """
    Get overview statistics for the home page.
    
    Returns:
    - title: Page title
    - description: Page description
    - stats: Object containing various statistics
      - students: Number of students
      - faculty: Number of faculty members
      - programs: Number of programs
      - research: Number of research projects
    - heroImage: URL for the hero image
    """
    try:
        # Count students (users with 'student' in their role name)
        student_count = db.query(User).join(Role).filter(
            or_(
                func.lower(Role.name).ilike('%student%'),
                func.lower(Role.name).ilike('%learner%')
            )
        ).count()
        
        # Count faculty (users with 'faculty' or 'professor' in their role name)
        faculty_count = db.query(User).join(Role).filter(
            or_(
                func.lower(Role.name).ilike('%faculty%'),
                func.lower(Role.name).ilike('%professor%'),
                func.lower(Role.name).ilike('%teacher%'),
                func.lower(Role.name).ilike('%instructor%')
            )
        ).count()
        
        # For demo purposes - in a real app, you'd query these from your database
        programs_count = 12  # Replace with actual query if you have a programs table
        research_count = 25  # Replace with actual query if you have a research table
        
        return {
            "stats": {
                "students": student_count,
                "faculty": faculty_count,
                "programs": programs_count,
                "research": research_count
            },
        }
        
    except Exception as e:
        # Log the error for debugging
        print(f"Error fetching overview data: {str(e)}")
        # Return default values in case of error
        return {
 
            "stats": {
                "students": 0,
                "faculty": 0,
                "programs": 0,
                "research": 0
            },

        }


@router.get("/announcements", response_model=List[AnnouncementResponse])
async def get_announcements(
    limit: int = Query(10, description="Number of announcements to return"),
    type: Optional[str] = Query(None, description="Filter by announcement type"),
    priority: Optional[str] = Query(None, description="Filter by priority level"),
    db: Session = Depends(database.get_db)
):
    """
    Get a list of announcements.
    
    This endpoint returns a paginated list of announcements, with optional filtering by type and priority.
    The announcements are ordered by date in descending order (newest first).
    
    Parameters:
    - limit: Maximum number of announcements to return (default: 10)
    - type: Filter by announcement type (e.g., 'academic', 'admin', 'general')
    - priority: Filter by priority level (e.g., 'high', 'medium', 'low')
    
    Returns:
    - List of announcement objects
    """
    try:
        query = db.query(Announcement)
        
        # Apply filters if provided
        if type:
            query = query.filter(Announcement.type == type)
        if priority:
            query = query.filter(Announcement.priority == priority)
        
        # Get most recent announcements first
        announcements = query.order_by(Announcement.date.desc()).limit(limit).all()
        return announcements
        
    except Exception as e:
        # Log the error for debugging
        print(f"Error fetching announcements: {str(e)}")
        # Return empty list if there's an error (e.g., table doesn't exist)
        return []


