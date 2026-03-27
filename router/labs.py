from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from models import Lab, LabTimeSlot
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

# Pydantic models for request and response
class LabTimeSlotBase(BaseModel):
    day: str
    start_time: str
    end_time: str

class LabTimeSlotResponse(LabTimeSlotBase):
    id: int
    lab_id: int

    class Config:
        from_attributes = True

class LabBase(BaseModel):
    name: str
    description: Optional[str] = None
    location: str
    capacity: int
    facilities: Optional[List[str]] = None
    image: Optional[str] = None

class LabResponse(LabBase):
    id: int
    time_slots: List[LabTimeSlotResponse] = []

    class Config:
        from_attributes = True

class LabCreate(LabBase):
    pass

# Router
router = APIRouter(
    prefix="/api/labs",
    tags=["labs"],
    responses={404: {"description": "Not found"}},
)

@router.get("/", response_model=List[LabResponse])
def get_labs(
    skip: int = 0, 
    limit: int = 100,
    name: Optional[str] = None,
    location: Optional[str] = None,
    capacity_min: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Get all labs with optional filtering
    """
    try:
        query = db.query(Lab)
        
        # Apply filters if provided
        if name:
            query = query.filter(Lab.name.ilike(f"%{name}%"))
        if location:
            query = query.filter(Lab.location.ilike(f"%{location}%"))
        if capacity_min:
            query = query.filter(Lab.capacity >= capacity_min)
            
        labs = query.offset(skip).limit(limit).all()
        result = []
        
        for lab in labs:
            try:
                lab_response = {
                    "id": lab.id,
                    "name": lab.name,
                    "description": lab.description,
                    "location": lab.location,
                    "capacity": lab.capacity,
                    "facilities": lab.facilities,
                    "image": lab.image,
                    "time_slots": [{
                        "id": slot.id,
                        "lab_id": slot.lab_id,
                        "day": slot.day,
                        "start_time": slot.start_time,
                        "end_time": slot.end_time
                    } for slot in lab.time_slots]
                }
                result.append(lab_response)
            except Exception as ex:
                print(f"Error processing lab {lab.id}: {ex}")
        
        return result
    except Exception as e:
        print(f"Error in get_labs: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/{lab_id}", response_model=LabResponse)
def get_lab(lab_id: int, db: Session = Depends(get_db)):
    """
    Get a specific lab by ID
    """
    try:
        lab = db.query(Lab).filter(Lab.id == lab_id).first()
        if lab is None:
            raise HTTPException(status_code=404, detail="Lab not found")
        
        lab_response = {
            "id": lab.id,
            "name": lab.name,
            "description": lab.description,
            "location": lab.location,
            "capacity": lab.capacity,
            "facilities": lab.facilities,
            "image": lab.image,
            "time_slots": [{
                "id": slot.id,
                "lab_id": slot.lab_id,
                "day": slot.day,
                "start_time": slot.start_time,
                "end_time": slot.end_time
            } for slot in lab.time_slots]
        }
        
        return lab_response
    except Exception as e:
        print(f"Error in get_lab: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/", response_model=LabResponse, status_code=status.HTTP_201_CREATED)
def create_lab(lab: LabCreate, db: Session = Depends(get_db)):
    """
    Create a new lab (admin only)
    """
    # TODO: Add admin check
    db_lab = Lab(**lab.dict())
    db.add(db_lab)
    db.commit()
    db.refresh(db_lab)
    return db_lab

@router.get("/{lab_id}/time-slots", response_model=List[LabTimeSlotResponse])
def get_lab_time_slots(
    lab_id: int, 
    day: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get all time slots for a specific lab with optional day filter
    """
    query = db.query(LabTimeSlot).filter(LabTimeSlot.lab_id == lab_id)
    
    if day:
        query = query.filter(LabTimeSlot.day == day)
        
    time_slots = query.all()
    return time_slots
