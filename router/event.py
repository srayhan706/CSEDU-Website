from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum

from models import Event, EventRegistration, EventType, EventStatus, User, Role
import database
from middleware import permission_required

router = APIRouter(
    prefix="/api/events",
    tags=["events"],
    responses={404: {"description": "Not found"}},
)

# Request/Response Models
class EventTypeEnum(str, Enum):
    SEMINAR = 'seminar'
    WORKSHOP = 'workshop'
    CONFERENCE = 'conference'
    COMPETITION = 'competition'
    CULTURAL = 'cultural'
    ACADEMIC = 'academic'

class EventStatusEnum(str, Enum):
    UPCOMING = 'upcoming'
    ONGOING = 'ongoing'
    REGISTRATION_OPEN = 'registration_open'
    REGISTRATION_CLOSED = 'registration_closed'
    COMPLETED = 'completed'

class EventBase(BaseModel):
    title: str
    description: Optional[str] = None
    type: EventTypeEnum
    status: EventStatusEnum
    startDate: datetime
    endDate: datetime
    venue: str
    speaker: Optional[str] = None
    maxParticipants: Optional[int] = None
    registrationRequired: bool = False
    registrationDeadline: Optional[datetime] = None
    fee: Optional[float] = None
    externalLink: Optional[str] = None
    tags: Optional[List[str]] = []

class EventCreate(EventBase):
    pass

class EventResponse(EventBase):
    id: int
    organizer: str
    registeredCount: int = 0
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None

    class Config:
        orm_mode = True
        from_attributes = True

class RegistrationRequest(BaseModel):
    fullName: str
    email: str
    phone: str
    studentId: Optional[str] = None
    department: Optional[str] = None
    year: Optional[str] = None
    specialRequirements: Optional[str] = None
    
    class Config:
        # Allow population by field name for camelCase compatibility
        populate_by_name = True
        # Define aliases for snake_case to camelCase conversion
        alias_generator = lambda field_name: field_name.replace('_', '').lower()
        # Define field names for the database model
        fields = {
            'fullName': {'alias': 'full_name'},
            'studentId': {'alias': 'student_id'},
            'specialRequirements': {'alias': 'special_requirements'}
        }

from pydantic import Field
class RegistrationResponse(BaseModel):
    success: bool
    registrationId: int = Field(..., alias="registrationId")
    message: str

    class Config:
        allow_population_by_field_name = True

# Helper function to convert EventType and EventStatus enums
def convert_event_type(event_type: EventTypeEnum) -> EventType:
    return EventType[event_type.name]

def convert_event_status(status: EventStatusEnum) -> EventStatus:
    return EventStatus[status.name]

# Helper to convert snake_case dict to camelCase for API responses
def event_to_camel(event_dict):
    mapping = {
        "id": "id",
        "title": "title",
        "description": "description",
        "type": "type",
        "status": "status",
        "start_date": "startDate",
        "end_date": "endDate",
        "venue": "venue",
        "speaker": "speaker",
        "organizer": "organizer",
        "max_participants": "maxParticipants",
        "registered_count": "registeredCount",
        "registration_required": "registrationRequired",
        "registration_deadline": "registrationDeadline",
        "fee": "fee",
        "external_link": "externalLink",
        "tags": "tags",
        "created_at": "createdAt",
        "updated_at": "updatedAt",
    }
    return {api_key: event_dict.get(db_key) for db_key, api_key in mapping.items() if db_key in event_dict}

# Routes
from typing import List

@router.get("", response_model=None)
async def get_events(
    skip: int = 0, 
    limit: int = 100,
    db: Session = Depends(database.get_db)
):
    """Get all events with optional pagination (Public endpoint)"""
    events = db.query(Event).offset(skip).limit(limit).all()
    result = []
    for event in events:
        # Convert SQLAlchemy model to dict safely
        event_dict = {}
        for c in event.__table__.columns:
            value = getattr(event, c.name)
            # Convert Enum values to strings
            if isinstance(value, (EventType, EventStatus)):
                value = str(value)
            event_dict[c.name] = value
            
        # Get the organizer's name from the role
        organizer_role = db.query(Role).filter(Role.id == event.organizer_role_id).first()
        event_dict['organizer'] = organizer_role.name if organizer_role else 'Unknown Organizer'
        
        # Convert to camelCase and ensure datetime fields are properly handled
        camel_dict = event_to_camel(event_dict)
        
        # Make sure tags is a list
        if 'tags' in camel_dict and camel_dict['tags'] is None:
            camel_dict['tags'] = []
            
        result.append(camel_dict)
    return result


    
@router.post("", response_model=EventResponse)
async def create_event(
    event: EventCreate,
    current_user: dict = Depends(permission_required("MANAGE_EVENTS")),
    db: Session = Depends(database.get_db)
):


    # Get role_id from the nested role structure
    try:
        role_id = current_user.get('role', {}).get('id')
        if not role_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User role not found in token"
            )
        
        # Convert the role_id to integer if it's a string
        role_id = int(role_id)
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid user role structure in token"
        )
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role_id format in token"
        )
    
    db_event = Event(
        title=event.title,
        description=event.description,
        type=event.type,
        status=event.status,
        start_date=event.startDate,
        end_date=event.endDate,
        venue=event.venue,
        speaker=event.speaker,
        organizer_role_id=role_id,
        max_participants=event.maxParticipants,
        registration_required=event.registrationRequired,
        registration_deadline=event.registrationDeadline,
        fee=event.fee,
        external_link=event.externalLink,
        tags=event.tags,
        registered_count=0
    )
    
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    event_dict = {c.name: getattr(db_event, c.name) for c in db_event.__table__.columns}
    organizer_role = db.query(Role).filter(Role.id == db_event.organizer_role_id).first()
    event_dict['organizer'] = organizer_role.name if organizer_role else 'Unknown Organizer'
    return event_to_camel(event_dict)
    
    # Get the organizer's role name
    organizer_role = db.query(Role).filter(Role.id == db_event.organizer_role_id).first()
    organizer_name = organizer_role.name if organizer_role else 'Unknown Organizer'
    
    # Convert to dict and add the organizer's name
    response_data = {c.name: getattr(db_event, c.name) for c in db_event.__table__.columns}
    response_data['organizer'] = organizer_name
    
    return response_data



def registration_to_camel(registration_dict):
    mapping = {
        "id": "id",
        "event_id": "eventId",
        "user_id": "userId",
        "full_name": "fullName",
        "email": "email",
        "phone": "phone",
        "student_id": "studentId",
    }
    return {api_key: registration_dict.get(db_key) for db_key, api_key in mapping.items() if db_key in registration_dict}
@router.post("/{event_id}/register", response_model=RegistrationResponse)
async def register_for_event(
    event_id: int,
    registration: RegistrationRequest,
    current_user: dict = Depends(permission_required("REGISTER_EVENT")),
    db: Session = Depends(database.get_db)
):
    # Regular event registration with authentication
    return await _process_event_registration(event_id, registration, current_user, db)

@router.post("/{event_id}/register-test", response_model=RegistrationResponse)
async def register_for_event_test(
    event_id: int,
    registration: RegistrationRequest,
    db: Session = Depends(database.get_db)
):
    """Test endpoint for event registration (No authentication required)"""
    # Use a valid user ID from the database
    # User ID 174 is 'Student One' from the database
    mock_user = {
        "id": 174,  # Valid user ID from the database
        "name": "Student One",
        "email": "student1@csedu.edu"
    }
    
    return await _process_event_registration(event_id, registration, mock_user, db)

async def _process_event_registration(
    event_id: int,
    registration: RegistrationRequest,
    current_user: dict,
    db: Session
):
    """Register for an event (Requires REGISTER_EVENT permission)"""
    
    # Check if event exists and registration is open
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Event not found"
        )
    
    if event.registration_required and event.status != EventStatus.REGISTRATION_OPEN:
        # For testing purposes, allow registration for any event status
        if not event.status.value.lower().startswith('registration_open'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Registration is not open for this event"
            )
    
    if event.registration_deadline and event.registration_deadline < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Registration deadline has passed"
        )
    
    if event.max_participants and event.registered_count >= event.max_participants:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Event is at full capacity"
        )
    
    # Get user_id from current_user
    try:
        user_id = current_user.get('id')
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User ID not found in token"
            )
        
        # Check if user is already registered
        existing_registration = db.query(EventRegistration).filter(
            EventRegistration.event_id == event_id,
            EventRegistration.user_id == user_id
        ).first()
        
        if existing_registration:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You are already registered for this event"
            )
        
        # Convert camelCase to snake_case for database model
        registration_data = {
            "full_name": registration.fullName,
            "email": registration.email,
            "phone": registration.phone,
            "student_id": registration.studentId,
            "department": registration.department,
            "year": registration.year,
            "special_requirements": registration.specialRequirements,
            "event_id": event_id,
            "user_id": user_id
        }
        
    except Exception as e:
        # Re-raise HTTPException as is
        if isinstance(e, HTTPException):
            raise
        # Convert other exceptions to 500
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing your registration: {str(e)}"
        )
    
    db_registration = EventRegistration(**registration_data)
    db.add(db_registration)
    # Update the registered count
    event.registered_count += 1
    db.commit()
    db.refresh(db_registration)
    
    # Ensure the response matches the RegistrationResponse model
    return RegistrationResponse(
        success=True,
        registrationId=db_registration.id,
        message="Successfully registered for the event"
    )
