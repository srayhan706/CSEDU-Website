
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import json
import os
from pydantic import BaseModel

from database import get_db
from middleware import permission_required

router = APIRouter(
    prefix="/api/schedule",
    tags=["schedule"],
)

# Pydantic models for response
class ClassScheduleResponse(BaseModel):
    id: str
    courseCode: str
    courseName: str
    type: str
    batch: str
    semester: str
    day: str
    startTime: str
    endTime: str
    room: str
    instructorId: int
    instructorName: str
    instructorDesignation: str
    status: str

class ClassesListResponse(BaseModel):
    classes: List[ClassScheduleResponse]
    batches: List[str]
    semesters: List[str]
    rooms: List[str]


@router.get("", response_model=ClassesListResponse)
async def get_classes(
    db: Session = Depends(get_db),
    batch: Optional[str] = None,
    semester: Optional[str] = None,
    room: Optional[str] = None,
    day: Optional[str] = None,
    status: Optional[str] = None
):
    """Get all class schedules with optional filtering"""
    # Load mock data from file
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        mock_data_path = os.path.join(parent_dir, "mock_schedule_data.json")
        
        with open(mock_data_path, "r") as f:
            data = json.load(f)
    except Exception as e:
        # If file doesn't exist, return empty data
        return ClassesListResponse(
            classes=[],
            batches=[],
            semesters=[],
            rooms=[]
        )
    
    # Apply filters if provided
    classes = data["classes"]
    if batch:
        classes = [c for c in classes if c["batch"] == batch]
    if semester:
        classes = [c for c in classes if c["semester"] == semester]
    if room:
        classes = [c for c in classes if c["room"] == room]
    if day:
        classes = [c for c in classes if c["day"] == day]
    if status:
        classes = [c for c in classes if c["status"] == status]
    
    return ClassesListResponse(
        classes=classes,
        batches=data["batches"],
        semesters=data["semesters"],
        rooms=data["rooms"]
    )
