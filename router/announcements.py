from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from typing import List, Optional
from database import get_db
from models import Announcement, AnnouncementType, PriorityLevel
from pydantic import BaseModel
from datetime import datetime
from dependencies import get_user_from_session
from middleware import permission_required

router = APIRouter(
    prefix="/api/announcements",
    tags=["announcements"],
    responses={404: {"description": "Not found"}},
)

class AnnouncementSchema(BaseModel):
    id: Optional[int]
    title: str
    content: str
    date: datetime
    type: str  # 'academic' | 'admin' | 'general'
    priority: str  # 'high' | 'medium' | 'low'
    image: Optional[str] = None

    class Config:
        orm_mode = True

@router.get("/", response_model=List[AnnouncementSchema])
def get_announcements(
    type: Optional[str] = None,
    priority: Optional[str] = None,
    limit: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Get all announcements with optional filtering by type and priority.
    """
    query = db.query(Announcement)
    
    # Apply filters if provided
    if type:
        try:
            announcement_type = AnnouncementType[type.upper()]
            query = query.filter(Announcement.type == announcement_type)
        except KeyError:
            raise HTTPException(status_code=400, detail=f"Invalid announcement type: {type}")
    
    if priority:
        try:
            priority_level = PriorityLevel[priority.upper()]
            query = query.filter(Announcement.priority == priority_level)
        except KeyError:
            raise HTTPException(status_code=400, detail=f"Invalid priority level: {priority}")
    
    # Order by date (newest first) and priority
    query = query.order_by(Announcement.date.desc(), Announcement.priority)
    
    # Apply limit if provided
    if limit:
        query = query.limit(limit)
    
    announcements = query.all()
    
    # Convert to response format
    result = []
    for announcement in announcements:
        result.append({
            "id": announcement.id,
            "title": announcement.title,
            "content": announcement.content,
            "date": announcement.date,
            "type": announcement.type.name.lower(),
            "priority": announcement.priority.name.lower(),
            "image": announcement.image
        })
    
    return result

@router.get("/{announcement_id}", response_model=AnnouncementSchema)
def get_announcement(announcement_id: int, db: Session = Depends(get_db)):
    """
    Get a specific announcement by ID.
    """
    announcement = db.query(Announcement).filter(Announcement.id == announcement_id).first()
    
    if not announcement:
        raise HTTPException(status_code=404, detail=f"Announcement with ID {announcement_id} not found")
    
    return {
        "id": announcement.id,
        "title": announcement.title,
        "content": announcement.content,
        "date": announcement.date,
        "type": announcement.type.name.lower(),
        "priority": announcement.priority.name.lower(),
        "image": announcement.image
    }

@router.post("/", response_model=AnnouncementSchema)
def create_announcement(
    announcement_data: AnnouncementSchema,
    db: Session = Depends(get_db),
    current_user = Depends(get_user_from_session)
):
    """
    Create a new announcement (requires admin privileges).
    """
    # Check if user has admin privileges
    if not permission_required(["admin"])(current_user):
        raise HTTPException(status_code=403, detail="Not authorized to create announcements")
    
    try:
        announcement_type = AnnouncementType[announcement_data.type.upper()]
        priority_level = PriorityLevel[announcement_data.priority.upper()]
    except KeyError:
        raise HTTPException(status_code=400, detail="Invalid announcement type or priority level")
    
    new_announcement = Announcement(
        title=announcement_data.title,
        content=announcement_data.content,
        date=announcement_data.date,
        type=announcement_type,
        priority=priority_level,
        image=announcement_data.image
    )
    
    db.add(new_announcement)
    db.commit()
    db.refresh(new_announcement)
    
    return {
        "id": new_announcement.id,
        "title": new_announcement.title,
        "content": new_announcement.content,
        "date": new_announcement.date,
        "type": new_announcement.type.name.lower(),
        "priority": new_announcement.priority.name.lower(),
        "image": new_announcement.image
    }
