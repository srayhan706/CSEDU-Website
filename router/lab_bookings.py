from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from models import LabBooking, Lab, LabTimeSlot
from pydantic import BaseModel
from datetime import datetime, date
from typing import List, Optional

# Pydantic models for request and response
class LabBookingBase(BaseModel):
    lab_id: int
    user_id: int
    user_name: str
    user_role: str
    time_slot_id: int
    date: date
    purpose: Optional[str] = None

class LabBookingResponse(LabBookingBase):
    id: int
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class LabBookingCreate(LabBookingBase):
    pass

class LabBookingUpdate(BaseModel):
    status: str

# Router
router = APIRouter(
    prefix="/api/lab-bookings",
    tags=["lab-bookings"],
    responses={404: {"description": "Not found"}},
)

@router.get("/", response_model=List[LabBookingResponse])
def get_lab_bookings(
    skip: int = 0, 
    limit: int = 100,
    lab_id: Optional[int] = None,
    user_id: Optional[int] = None,
    status: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """
    Get all lab bookings with optional filtering
    """
    try:
        query = db.query(LabBooking)
        
        # Apply filters if provided
        if lab_id:
            query = query.filter(LabBooking.lab_id == lab_id)
        if user_id:
            query = query.filter(LabBooking.user_id == user_id)
        if status:
            query = query.filter(LabBooking.status == status)
        if date_from:
            query = query.filter(LabBooking.date >= date_from)
        if date_to:
            query = query.filter(LabBooking.date <= date_to)
            
        bookings = query.order_by(LabBooking.date.desc(), LabBooking.created_at.desc()).offset(skip).limit(limit).all()
        result = []
        
        for booking in bookings:
            try:
                booking_response = {
                    "id": booking.id,
                    "lab_id": booking.lab_id,
                    "user_id": booking.user_id,
                    "user_name": booking.user_name,
                    "user_role": booking.user_role,
                    "time_slot_id": booking.time_slot_id,
                    "date": booking.date,
                    "purpose": booking.purpose,
                    "status": booking.status,
                    "created_at": booking.created_at,
                    "updated_at": booking.updated_at
                }
                result.append(booking_response)
            except Exception as ex:
                print(f"Error processing booking {booking.id}: {ex}")
        
        return result
    except Exception as e:
        print(f"Error in get_lab_bookings: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/{booking_id}", response_model=LabBookingResponse)
def get_lab_booking(booking_id: int, db: Session = Depends(get_db)):
    """
    Get a specific lab booking by ID
    """
    booking = db.query(LabBooking).filter(LabBooking.id == booking_id).first()
    if booking is None:
        raise HTTPException(status_code=404, detail="Lab booking not found")
    return booking

@router.post("/", response_model=LabBookingResponse, status_code=status.HTTP_201_CREATED)
def create_lab_booking(booking: LabBookingCreate, db: Session = Depends(get_db)):
    """
    Create a new lab booking
    """
    # Check if lab exists
    lab = db.query(Lab).filter(Lab.id == booking.lab_id).first()
    if not lab:
        raise HTTPException(status_code=404, detail="Lab not found")
    
    # Check if time slot exists
    time_slot = db.query(LabTimeSlot).filter(LabTimeSlot.id == booking.time_slot_id).first()
    if not time_slot:
        raise HTTPException(status_code=404, detail="Time slot not found")
    
    # Check if time slot belongs to the specified lab
    if time_slot.lab_id != booking.lab_id:
        raise HTTPException(status_code=400, detail="Time slot does not belong to the specified lab")
    
    # Check if there's already a booking for this time slot on this date
    existing_booking = db.query(LabBooking).filter(
        LabBooking.time_slot_id == booking.time_slot_id,
        LabBooking.date == booking.date,
        LabBooking.status.in_(["approved", "pending"])
    ).first()
    
    if existing_booking:
        raise HTTPException(status_code=400, detail="This time slot is already booked for the specified date")
    
    # Create new booking with pending status
    db_booking = LabBooking(
        **booking.dict(),
        status="pending",
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    return db_booking

@router.put("/{booking_id}", response_model=LabBookingResponse)
def update_lab_booking_status(
    booking_id: int, 
    booking_update: LabBookingUpdate, 
    db: Session = Depends(get_db)
):
    """
    Update a lab booking status (admin only)
    """
    # TODO: Add admin check
    booking = db.query(LabBooking).filter(LabBooking.id == booking_id).first()
    if booking is None:
        raise HTTPException(status_code=404, detail="Lab booking not found")
    
    # Validate status
    if booking_update.status not in ["approved", "pending", "rejected"]:
        raise HTTPException(status_code=400, detail="Invalid status. Must be 'approved', 'pending', or 'rejected'")
    
    # Update booking status
    booking.status = booking_update.status
    booking.updated_at = datetime.now()
    
    db.commit()
    db.refresh(booking)
    return booking

@router.delete("/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_lab_booking(booking_id: int, db: Session = Depends(get_db)):
    """
    Delete a lab booking (admin or booking owner only)
    """
    # TODO: Add admin or owner check
    booking = db.query(LabBooking).filter(LabBooking.id == booking_id).first()
    if booking is None:
        raise HTTPException(status_code=404, detail="Lab booking not found")
    
    db.delete(booking)
    db.commit()
    return None
