from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime
from pydantic import BaseModel, Field

import models
import database
from .event import permission_required

router = APIRouter(prefix="/api", tags=["labs"])

# -------------------
# Pydantic Schemas
# -------------------
class LabTimeSlotResponse(BaseModel):
    id: int
    day: str
    startTime: str = Field(..., alias="startTime", validation_alias="start_time")
    endTime: str = Field(..., alias="endTime", validation_alias="end_time")
    class Config:
        from_attributes = True
        orm_mode = True  # Keep for backward compatibility
        allow_population_by_field_name = True

class LabResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    location: str
    capacity: int
    facilities: Optional[List[str]]
    image: Optional[str]
    availableTimeSlots: List[LabTimeSlotResponse]
    class Config:
        from_attributes = True
        orm_mode = True  # Keep for backward compatibility
        allow_population_by_field_name = True

class LabCreate(BaseModel):
    name: str
    description: Optional[str]
    location: str
    capacity: int
    facilities: Optional[List[str]] = None
    image: Optional[str] = None
    timeSlots: List[dict]  # [{day, startTime, endTime}]

class LabBookingResponse(BaseModel):
    id: int
    labId: int = Field(..., alias="labId", validation_alias="lab_id")
    userId: int = Field(..., alias="userId", validation_alias="user_id")
    timeSlotId: int = Field(..., alias="timeSlotId", validation_alias="time_slot_id")
    date: date
    purpose: Optional[str]
    status: str
    createdAt: datetime = Field(..., alias="createdAt", validation_alias="created_at")
    updatedAt: datetime = Field(..., alias="updatedAt", validation_alias="updated_at")
    class Config:
        from_attributes = True
        orm_mode = True  # Keep for backward compatibility
        allow_population_by_field_name = True

class LabBookingCreate(BaseModel):
    labId: int
    timeSlotId: int
    date: date
    purpose: Optional[str] = None

# -------------------
# GET /api/labs
# -------------------
@router.get("/labs", response_model=List[LabResponse])
def get_labs(db: Session = Depends(database.get_db)):
    labs = db.query(models.Lab).all()
    result = []
    for lab in labs:
        slots = [LabTimeSlotResponse.from_orm(slot) for slot in lab.time_slots]
        result.append(LabResponse(
            id=lab.id,
            name=lab.name,
            description=lab.description,
            location=lab.location,
            capacity=lab.capacity,
            facilities=lab.facilities,
            image=lab.image,
            availableTimeSlots=slots
        ))
    return result

# -------------------
# POST /api/labs (officer only)
# -------------------
@router.post("/labs", response_model=LabResponse)
def create_lab(
    lab: LabCreate,
    current_user: dict = Depends(permission_required("CREATE_LAB")),
    db: Session = Depends(database.get_db)
):
    db_lab = models.Lab(
        name=lab.name,
        description=lab.description,
        location=lab.location,
        capacity=lab.capacity,
        facilities=lab.facilities,
        image=lab.image
    )
    db.add(db_lab)
    db.commit()
    db.refresh(db_lab)
    # Add time slots
    for slot in lab.timeSlots:
        db_slot = models.LabTimeSlot(
            lab_id=db_lab.id,
            day=slot["day"],
            start_time=slot["startTime"],
            end_time=slot["endTime"]
        )
        db.add(db_slot)
    db.commit()
    db.refresh(db_lab)
    # Use model_validate instead of from_orm for Pydantic v2 compatibility
    slots = [LabTimeSlotResponse.model_validate(slot) for slot in db_lab.time_slots]
    # Use model_validate for the entire response
    return LabResponse.model_validate({
        "id": db_lab.id,
        "name": db_lab.name,
        "description": db_lab.description,
        "location": db_lab.location,
        "capacity": db_lab.capacity,
        "facilities": db_lab.facilities,
        "image": db_lab.image,
        "availableTimeSlots": slots
    })

# -------------------
# GET /api/lab-bookings (students, faculty, chairman)
# -------------------
@router.get("/lab-bookings", response_model=List[LabBookingResponse])
def get_lab_bookings(
    current_user: dict = Depends(permission_required("VIEW_EQUIPMENT_BOOKINGS")),
    db: Session = Depends(database.get_db)
):
    bookings = db.query(models.LabBooking).all()
    return [LabBookingResponse.model_validate(b) for b in bookings]

# -------------------
# POST /api/lab-bookings (faculty, chairman, students)
# -------------------
@router.post("/lab-bookings", response_model=LabBookingResponse)
def create_lab_booking(
    booking: LabBookingCreate,
    current_user: dict = Depends(permission_required("BOOK_LAB")),
    db: Session = Depends(database.get_db)
):
    user_id = current_user.get("id")
    db_booking = models.LabBooking(
        lab_id=booking.labId,
        user_id=user_id,
        time_slot_id=booking.timeSlotId,
        date=booking.date,
        purpose=booking.purpose,
        status="pending"
    )
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    return LabBookingResponse.model_validate(db_booking)
