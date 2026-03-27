from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, EmailStr
from database import get_db
from models import Event, EventRegistration, EventType, EventStatus, User
from datetime import datetime
from sqlalchemy import desc

router = APIRouter(
    prefix="/api/events",
    tags=["events"],
    responses={404: {"description": "Not found"}},
)

# Pydantic models for request and response
class EventResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    type: str
    status: str
    startDate: datetime
    endDate: datetime
    venue: str
    speaker: Optional[str] = None
    organizer: str
    maxParticipants: Optional[int] = None
    registeredCount: Optional[int] = None
    registrationRequired: bool
    registrationDeadline: Optional[datetime] = None
    fee: Optional[float] = None
    externalLink: Optional[str] = None
    tags: List[str] = []
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    
    class Config:
        orm_mode = True
        from_attributes = True

class EventRegistrationRequest(BaseModel):
    fullName: str
    email: EmailStr
    phone: str
    studentId: Optional[str] = None
    department: Optional[str] = None
    year: Optional[str] = None
    specialRequirements: Optional[str] = None

class EventRegistrationResponse(BaseModel):
    success: bool
    registrationId: str
    message: str

@router.get("", response_model=None)
def get_events(
    type: Optional[str] = None,
    status: Optional[str] = None,
    month: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Get all events with optional filtering
    """
    query = db.query(Event)
    
    if type:
        query = query.filter(Event.type == type)
    
    if status:
        query = query.filter(Event.status == status)
    
    if month:
        # Filter by month
        query = query.filter(db.extract('month', Event.start_date) == month)
    
    # Order by start date, most recent first
    query = query.order_by(desc(Event.start_date))
    
    events_db = query.all()
    
    # Format events for response
    events = []
    for event in events_db:
        # Get organizer role name
        organizer_role = db.query(Event.organizer_role).filter(Event.id == event.id).first()
        organizer = organizer_role.name if organizer_role else "Department of CSE"
        
        events.append({
            "id": event.id,
            "title": event.title,
            "description": event.description,
            "type": str(event.type),
            "status": str(event.status),
            "startDate": event.start_date,
            "endDate": event.end_date,
            "venue": event.venue,
            "speaker": event.speaker,
            "organizer": organizer,
            "maxParticipants": event.max_participants,
            "registeredCount": event.registered_count,
            "registrationRequired": event.registration_required,
            "registrationDeadline": event.registration_deadline,
            "fee": event.fee,
            "externalLink": event.external_link,
            "tags": event.tags if event.tags else []
            # Omitting createdAt and updatedAt as they're causing validation issues
        })
    
    return events

@router.get("/{event_id}", response_model=EventResponse)
def get_event(event_id: int, db: Session = Depends(get_db)):
    """
    Get a specific event by ID
    """
    event = db.query(Event).filter(Event.id == event_id).first()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event with ID {event_id} not found"
        )
    
    # Get organizer role name
    organizer_role = db.query(Event.organizer_role).filter(Event.id == event.id).first()
    organizer = organizer_role.name if organizer_role else "Department of CSE"
    
    # Create response
    response = {
        "id": event.id,
        "title": event.title,
        "description": event.description,
        "type": event.type,
        "status": event.status,
        "startDate": event.start_date,
        "endDate": event.end_date,
        "venue": event.venue,
        "speaker": event.speaker,
        "organizer": organizer,
        "maxParticipants": event.max_participants,
        "registeredCount": event.registered_count,
        "registrationRequired": event.registration_required,
        "registrationDeadline": event.registration_deadline,
        "fee": event.fee,
        "externalLink": event.external_link,
        "tags": event.tags if event.tags else []
    }
    
    return response

@router.post("/{event_id}/register", response_model=EventRegistrationResponse)
def register_for_event(
    event_id: int, 
    registration: EventRegistrationRequest = Body(...),
    db: Session = Depends(get_db)
):
    """
    Register for an event
    """
    # Check if event exists
    event = db.query(Event).filter(Event.id == event_id).first()
    
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Event with ID {event_id} not found"
        )
    
    # Check if registration is open
    if event.status != EventStatus.REGISTRATION_OPEN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Registration is not open for this event"
        )
    
    # Check if event is full
    if event.max_participants and event.registered_count >= event.max_participants:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Event is already full"
        )
    
    # Check if registration deadline has passed
    if event.registration_deadline and event.registration_deadline < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Registration deadline has passed"
        )
    
    # Check if user is already registered
    existing_registration = db.query(EventRegistration).filter(
        EventRegistration.event_id == event_id,
        EventRegistration.email == registration.email
    ).first()
    
    if existing_registration:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are already registered for this event"
        )
    
    # Get user by email if exists
    user = db.query(User).filter(User.email == registration.email).first()
    user_id = user.id if user else None
    
    # Create registration
    new_registration = EventRegistration(
        event_id=event_id,
        user_id=user_id,
        full_name=registration.fullName,
        email=registration.email,
        phone=registration.phone,
        student_id=registration.studentId,
        department=registration.department,
        year=registration.year,
        special_requirements=registration.specialRequirements
    )
    
    db.add(new_registration)
    
    # Update event registered count
    event.registered_count += 1
    
    db.commit()
    db.refresh(new_registration)
    
    return {
        "success": True,
        "registrationId": str(new_registration.id),
        "message": "You have successfully registered for this event"
    }
