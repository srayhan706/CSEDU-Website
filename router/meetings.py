from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session as SessionType, joinedload
from sqlalchemy import and_, or_, func, text
from datetime import datetime, date, time, timedelta
from typing import List, Optional, Dict, Any, Union, TYPE_CHECKING
from pydantic import BaseModel, ConfigDict, Field

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

# Import models and utilities
from database import get_db
from models import User, Faculty, Meeting, MeetingType, MeetingStatus, RSVPStatus, Session as SessionModel
from dependencies import get_user_from_session
from utils import get_user_by_email

# Pydantic models for request/response
class MeetingBase(BaseModel):
    title: str
    description: Optional[str] = None
    faculty_id: Optional[int] = None
    student_id: Optional[int] = None
    date: str  # YYYY-MM-DD
    start_time: str  # HH:MM
    end_time: str  # HH:MM
    location: str
    meeting_type: str
    status: str = "pending"
    rsvp_status: str = "pending"
    rsvp_deadline: Optional[str] = None
    notes: Optional[str] = None

class MeetingCreate(MeetingBase):
    pass

class MeetingUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    date: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    location: Optional[str] = None
    meeting_type: Optional[str] = None
    status: Optional[str] = None
    rsvp_status: Optional[str] = None
    rsvp_deadline: Optional[str] = None
    notes: Optional[str] = None

class MeetingResponse(MeetingBase):
    id: int
    created_at: datetime
    updated_at: datetime
    faculty: Dict[str, Any]
    student: Dict[str, Any]
    
    model_config = ConfigDict(from_attributes=True)

# Utility function to convert SQLAlchemy model to response model
def meeting_to_response(meeting: Meeting, db: 'SessionType') -> dict:
    try:
        # Safely get faculty information
        faculty_info = None
        if meeting.faculty_id:
            faculty_user = db.query(User).get(meeting.faculty_id)
            faculty = db.query(Faculty).filter(Faculty.id == meeting.faculty_id).first()
            if faculty_user:
                faculty_info = {
                    "id": meeting.faculty_id,
                    "name": faculty_user.name,
                    "email": faculty_user.email,
                    "department": faculty.department if faculty else None
                }
            else:
                faculty_info = {"id": meeting.faculty_id, "name": "Unknown Faculty", "email": None, "department": None}
        
        # Safely get student information
        student_info = None
        if meeting.student_id:
            student_user = db.query(User).get(meeting.student_id)
            if student_user:
                student_info = {
                    "id": meeting.student_id,
                    "name": student_user.name,
                    "email": student_user.email
                }
            else:
                student_info = {"id": meeting.student_id, "name": "Unknown Student", "email": None}
        
        return {
            "id": meeting.id,
            "title": meeting.title,
            "description": meeting.description,
            "faculty_id": meeting.faculty_id,
            "student_id": meeting.student_id,
            "date": meeting.date.isoformat() if meeting.date else None,
            "start_time": str(meeting.start_time) if meeting.start_time else None,
            "end_time": str(meeting.end_time) if meeting.end_time else None,
            "location": meeting.location,
            "meeting_type": meeting.meeting_type,
            "status": meeting.status,
            "rsvp_status": meeting.rsvp_status,
            "rsvp_deadline": meeting.rsvp_deadline.isoformat() if meeting.rsvp_deadline else None,
            "rsvp_notes": meeting.rsvp_notes,
            "created_at": meeting.created_at,
            "updated_at": meeting.updated_at,
            "faculty": faculty_info,
            "student": student_info
        }
    except Exception as e:
        print(f"ERROR in meeting_to_response: {str(e)}")
        # Return a minimal response with just the meeting data, no relations
        return {
            "id": meeting.id,
            "title": meeting.title,
            "description": meeting.description,
            "faculty_id": meeting.faculty_id,
            "student_id": meeting.student_id,
            "date": meeting.date.isoformat() if meeting.date else None,
            "start_time": str(meeting.start_time) if meeting.start_time else None,
            "end_time": str(meeting.end_time) if meeting.end_time else None,
            "location": meeting.location,
            "meeting_type": meeting.meeting_type,
            "status": meeting.status,
            "rsvp_status": meeting.rsvp_status,
            "faculty": {"id": meeting.faculty_id, "name": "Error loading faculty"},
            "student": {"id": meeting.student_id, "name": "Error loading student"}
        }

# Initialize router
router = APIRouter(
    prefix="/api/meetings",
    tags=["meetings"],
    responses={404: {"description": "Not found"}},
)

@router.get("/types", response_model=List[Dict[str, str]])
async def get_meeting_types():
    """Get all available meeting types."""
    return [
        {"value": "advising", "label": "Advising"},
        {"value": "thesis", "label": "Thesis"},
        {"value": "project", "label": "Project"},
        {"value": "general", "label": "General"},
        {"value": "other", "label": "Other"}
    ]

def is_time_slot_available(
    db: SessionType, 
    faculty_id: int, 
    date: date, 
    start_time: str, 
    end_time: str, 
    exclude_meeting_id: Optional[int] = None
) -> bool:
    print(f"Checking availability for faculty {faculty_id} on {date} from {start_time} to {end_time}")
    """
    Check if a time slot is available for a faculty member.
    Returns True if available, False if there's a conflict.
    """
    # Convert string times to time objects for comparison
    start = datetime.strptime(start_time, "%H:%M").time()
    end = datetime.strptime(end_time, "%H:%M").time()
    
    # Query for conflicting meetings
    query = db.query(Meeting).filter(
        Meeting.faculty_id == faculty_id,
        Meeting.date == date,
        Meeting.status != MeetingStatus.CANCELLED
    )
    
    # Debug: Print all meetings on this date
    all_meetings = query.all()
    print(f"Found {len(all_meetings)} existing meetings on {date}")
    for m in all_meetings:
        print(f"  Meeting {m.id}: {m.start_time} - {m.end_time}")
    
    if exclude_meeting_id:
        query = query.filter(Meeting.id != exclude_meeting_id)
    
    # Check each meeting for time overlap
    for meeting in query.all():
        # Handle both string and datetime.time objects
        if isinstance(meeting.start_time, str):
            meeting_start = datetime.strptime(meeting.start_time, "%H:%M").time()
        else:
            meeting_start = meeting.start_time
            
        if isinstance(meeting.end_time, str):
            meeting_end = datetime.strptime(meeting.end_time, "%H:%M").time()
        else:
            meeting_end = meeting.end_time
        
        # Check for time overlap
        if not (end <= meeting_start or start >= meeting_end):
            print(f"  CONFLICT: New meeting {start}-{end} overlaps with existing meeting {meeting_start}-{meeting_end}")
            return False
        else:
            print(f"  NO CONFLICT: New meeting {start}-{end} doesn't overlap with existing meeting {meeting_start}-{meeting_end}")
    
    return True

@router.post("/", response_model=MeetingResponse)
async def create_meeting(
    meeting: MeetingCreate,
    db: 'SessionType' = Depends(get_db),
    current_user: dict = Depends(get_user_from_session)
):
    """
    Create a new meeting.
    Students can create meetings with faculty members.
    Faculty members can create meetings with students.
    """
    # Check if the meeting is in the past
    meeting_date = datetime.strptime(meeting.date, "%Y-%m-%d").date()
    if meeting_date < date.today():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot schedule a meeting in the past"
        )
    
    # Check if start time is before end time
    start_time = datetime.strptime(meeting.start_time, "%H:%M").time()
    end_time = datetime.strptime(meeting.end_time, "%H:%M").time()
    if start_time >= end_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End time must be after start time"
        )
    
    # Debug information
    print(f"Current user: {current_user}")
    print(f"Role name: {current_user['role']['name']}")
    
    # Initialize variables to avoid UnboundLocalError
    student_id = None
    faculty_id = None
    
    # Check if the meeting creator is a student or faculty
    role_name = current_user['role']['name'].lower()
    
    if role_name == 'student':
        student_id = current_user['id']
        faculty_id = meeting.faculty_id
        if not faculty_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Faculty ID is required for student-created meetings"
            )
        # Verify faculty exists
        faculty = db.query(User).filter(User.id == faculty_id).first()
        if not faculty:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Faculty member not found"
            )
    elif role_name == 'faculty':
        # Faculty creating meeting
        faculty_id = current_user['id']
        student_id = meeting.student_id
        if not student_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Student ID is required for faculty-created meetings"
            )
        # Verify student exists
        student = db.query(User).filter(User.id == student_id).first()
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student not found"
            )
    else:
        # Admin or other role creating meeting
        faculty_id = meeting.faculty_id
        student_id = meeting.student_id
        
        if not faculty_id or not student_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Both faculty_id and student_id are required for admin-created meetings"
            )
            
        # Verify faculty exists
        faculty = db.query(User).filter(User.id == faculty_id).first()
        if not faculty:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Faculty member not found"
            )
            
        # Verify student exists
        student = db.query(User).filter(User.id == student_id).first()
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student not found"
            )
    
    # Check for time slot availability
    if not is_time_slot_available(
        db, 
        faculty_id=faculty_id,
        date=meeting_date,
        start_time=meeting.start_time,
        end_time=meeting.end_time
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The selected time slot is not available"
        )
    
    # Create the meeting
    new_meeting = Meeting(
        title=meeting.title,
        description=meeting.description,
        faculty_id=faculty_id,
        student_id=student_id,
        date=meeting_date,
        start_time=meeting.start_time,
        end_time=meeting.end_time,
        location=meeting.location,
        meeting_type=MeetingType(meeting.meeting_type),
        status=MeetingStatus.SCHEDULED,  # Default status
        rsvp_status=RSVPStatus.PENDING,
        rsvp_deadline=meeting.rsvp_deadline,
        rsvp_notes=meeting.rsvp_notes if hasattr(meeting, 'rsvp_notes') else None,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    db.add(new_meeting)
    db.commit()
    db.refresh(new_meeting)
    
    # Load relationships for the response
    db_meeting = (
        db.query(Meeting)
        .options(joinedload(Meeting.faculty), joinedload(Meeting.student))
        .filter(Meeting.id == new_meeting.id)
        .first()
    )
    
    return meeting_to_response(db_meeting, db)

@router.get("/{meeting_id}", response_model=MeetingResponse)
async def get_meeting(
    meeting_id: int,
    db: 'SessionType' = Depends(get_db),
    current_user: dict = Depends(get_user_from_session)
):
    """
    Get meeting details by ID.
    Only the meeting participants (student or faculty) or admins can view the meeting.
    """
    meeting = (
        db.query(Meeting)
        .options(joinedload(Meeting.faculty), joinedload(Meeting.student))
        .filter(Meeting.id == meeting_id)
        .first()
    )
    
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    # Check permissions
    if (current_user['id'] not in [meeting.student_id, meeting.faculty_id] and 
        current_user['role']['name'] != 'admin'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this meeting"
        )
    
    return meeting_to_response(meeting, db)

@router.put("/{meeting_id}", response_model=MeetingResponse)
async def update_meeting(
    meeting_id: int,
    meeting_update: MeetingUpdate,
    db: 'SessionType' = Depends(get_db),
    current_user: dict = Depends(get_user_from_session)
):
    """
    Update a meeting.
    Only the meeting creator (student or faculty) or admins can update the meeting.
    """
    # Get the existing meeting
    meeting = (
        db.query(Meeting)
        .options(joinedload(Meeting.faculty), joinedload(Meeting.student))
        .filter(Meeting.id == meeting_id)
        .first()
    )
    
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    # Check permissions
    if (current_user['id'] != meeting.created_by and 
        current_user['role']['name'] != 'admin'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this meeting"
        )
    
    # Check if the meeting is in the past
    if meeting.date < date.today():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update a past meeting"
        )
    
    # Update fields if provided
    if meeting_update.title is not None:
        meeting.title = meeting_update.title
    if meeting_update.description is not None:
        meeting.description = meeting_update.description
    if meeting_update.location is not None:
        meeting.location = meeting_update.location
    if meeting_update.notes is not None:
        meeting.notes = meeting_update.notes
    if meeting_update.rsvp_deadline is not None:
        meeting.rsvp_deadline = meeting_update.rsvp_deadline
    
    # Handle date and time updates
    new_date = meeting.date
    new_start_time = meeting.start_time
    new_end_time = meeting.end_time
    
    if meeting_update.date is not None:
        new_date = datetime.strptime(meeting_update.date, "%Y-%m-%d").date()
        if new_date < date.today():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot schedule a meeting in the past"
            )
        meeting.date = new_date
    
    if meeting_update.start_time is not None:
        new_start_time = meeting_update.start_time
        meeting.start_time = new_start_time
    
    if meeting_update.end_time is not None:
        new_end_time = meeting_update.end_time
        meeting.end_time = new_end_time
    
    # Validate time if either time was updated
    if (meeting_update.start_time is not None or 
        meeting_update.end_time is not None or
        meeting_update.date is not None):
        
        # Parse times for comparison
        start = datetime.strptime(new_start_time, "%H:%M").time()
        end = datetime.strptime(new_end_time, "%H:%M").time()
        
        if start >= end:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="End time must be after start time"
            )
        
        # Check for time slot availability (excluding the current meeting)
        if not is_time_slot_available(
            db, 
            faculty_id=meeting.faculty_id,
            date=new_date,
            start_time=new_start_time,
            end_time=new_end_time,
            exclude_meeting_id=meeting.id
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The selected time slot is not available"
            )
    
    # Update meeting type if provided
    if meeting_update.meeting_type is not None:
        meeting.meeting_type = MeetingType(meeting_update.meeting_type)
    
    # If the meeting was previously declined, set it back to pending
    if meeting.status == MeetingStatus.CANCELLED and meeting_update.status == MeetingStatus.PENDING:
        meeting.status = MeetingStatus.PENDING
        # Reset RSVP status if needed
        if meeting.rsvp_status == RSVPStatus.DECLINED:
            meeting.rsvp_status = RSVPStatus.PENDING
    
    db.commit()
    db.refresh(meeting)
    
    return meeting_to_response(meeting, db)

@router.delete("/{meeting_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_meeting(
    meeting_id: int,
    db: 'SessionType' = Depends(get_db),
    current_user: dict = Depends(get_user_from_session)
):
    """
    Delete a meeting.
    Only the meeting creator (student or faculty) or admins can delete the meeting.
    """
    meeting = db.query(Meeting).filter(Meeting.id == meeting_id).first()
    
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    
    # Check permissions
    if (current_user['id'] != meeting.created_by and 
        current_user['role']['name'] != 'admin'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this meeting"
        )
    
    db.delete(meeting)
    db.commit()
    
    return None

class MeetingFilter(BaseModel):
    """Filter criteria for listing meetings"""
    start_date: Optional[date] = Field(None, description="Start date for filtering meetings (YYYY-MM-DD)")
    end_date: Optional[date] = Field(None, description="End date for filtering meetings (YYYY-MM-DD)")
    status: Optional[str] = Field(None, description="Filter by meeting status (e.g., 'pending', 'confirmed', 'cancelled')")
    meeting_type: Optional[str] = Field(None, description="Filter by meeting type (e.g., 'advising', 'thesis')")
    search: Optional[str] = Field(None, description="Search term to filter meetings by title or description")
    upcoming: Optional[bool] = Field(None, description="If true, returns only upcoming meetings")
    days: Optional[int] = Field(7, description="Number of days to look ahead for upcoming meetings", ge=1, le=30)

@router.get("/", response_model=List[Dict[str, Any]])
async def list_meetings(
    filters: MeetingFilter = Depends(),
    db: 'SessionType' = Depends(get_db),
    current_user: dict = Depends(get_user_from_session)
):
    """
    List all meetings for the current user with optional filters.
    Students see their own meetings, faculty see their meetings, admins see all.
    """
    try:
        print(f"DEBUG: Received filters: {filters}")
        print(f"DEBUG: Current user: {current_user['id']}, role: {current_user['role']['name']}")
        
        # Base query
        query = db.query(Meeting)
        
        # Apply user-specific filtering
        if current_user['role']['name'].upper() == 'STUDENT':
            print(f"DEBUG: Filtering for student ID {current_user['id']}")
            query = query.filter(Meeting.student_id == current_user['id'])
        elif current_user['role']['name'].upper() == 'FACULTY':
            print(f"DEBUG: Filtering for faculty ID {current_user['id']}")
            query = query.filter(Meeting.faculty_id == current_user['id'])
        # Admins can see all meetings
        
        # Handle upcoming filter (special case)
        if filters.upcoming or (filters.status and filters.status.lower() == 'upcoming'):
            print("DEBUG: Applying upcoming filter")
            today = date.today()
            days = filters.days or 7
            end_date = today + timedelta(days=days)
            print(f"DEBUG: Date range: {today} to {end_date}")
            query = query.filter(
                Meeting.date >= today,
                Meeting.date <= end_date
            )
        else:
            # Apply regular filters
            if filters.start_date:
                query = query.filter(Meeting.date >= filters.start_date)
            if filters.end_date:
                query = query.filter(Meeting.date <= filters.end_date)
            if filters.status and filters.status.lower() != 'upcoming':
                # Use lowercase to match enum values in database
                status_lower = filters.status.lower()
                query = query.filter(Meeting.status == status_lower)
        
        # Apply remaining filters
        if filters.meeting_type:
            # Use the meeting type as provided (should be uppercase)
            query = query.filter(Meeting.meeting_type == filters.meeting_type)
        if filters.search:
            search = f"%{filters.search}%"
            query = query.filter(
                or_(
                    Meeting.title.ilike(search),
                    Meeting.description.ilike(search)
                )
            )
        
        # Order by date and time
        query = query.order_by(Meeting.date.asc(), Meeting.start_time.asc())
        
        # Execute query and format response
        print("DEBUG: Executing query")
        meetings = query.all()
        print(f"DEBUG: Found {len(meetings)} meetings")
        
        result = [meeting_to_response(meeting, db) for meeting in meetings]
        print(f"DEBUG: Returning {len(result)} formatted meetings")
        return result
    except Exception as e:
        print(f"ERROR in list_meetings: {str(e)}")
        import traceback
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/upcoming", response_model=List[Dict[str, Any]])
async def get_upcoming_meetings(
    days: int = Query(7, description="Number of days to look ahead", ge=1, le=30),
    db: 'SessionType' = Depends(get_db),
    current_user: dict = Depends(get_user_from_session)
):
    """
    Get upcoming meetings within the specified number of days.
    """
    today = date.today()
    end_date = today + timedelta(days=days)
    
    query = db.query(Meeting).filter(
        Meeting.date >= today,
        Meeting.date <= end_date,
        or_(
            Meeting.student_id == current_user['id'],
            Meeting.faculty_id == current_user['id']
        )
    ).order_by(Meeting.date.asc(), Meeting.start_time.asc())
    
    meetings = query.all()
    return [meeting_to_response(meeting, db) for meeting in meetings]

# Meeting types endpoint moved to the top of the router

@router.get("/faculty/{faculty_id}/availability")
async def get_faculty_availability(
    faculty_id: int,
    date: str,
    db: 'SessionType' = Depends(get_db),
    current_user: dict = Depends(get_user_from_session)
):
    """
    Get available time slots for a faculty member on a specific date.
    Only the faculty member or admins can view availability.
    """
    # Verify faculty exists
    try:
        parsed_date = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid date format. Use YYYY-MM-DD"
        )
    
    # Check if faculty exists - look in User table instead of Faculty table
    faculty = db.query(User).filter(User.id == faculty_id).first()
    if not faculty:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Faculty member not found"
        )
    
    # Get faculty's booked meetings for the date
    meetings = db.query(Meeting).filter(
        Meeting.faculty_id == faculty_id,
        Meeting.date == parsed_date
    ).all()
    
    # Extract booked time slots
    booked_slots = [
        {
            "start_time": meeting.start_time,
            "end_time": meeting.end_time
        }
        for meeting in meetings
    ]
    
    # Get faculty's working hours (you can customize this based on your requirements)
    # This is a simplified example - you might want to get this from the faculty's profile
    working_hours = {
        "start_time": "09:00",
        "end_time": "17:00"
    }
    
    # Generate available time slots (30-minute intervals)
    available_slots = generate_available_slots(
        working_hours["start_time"],
        working_hours["end_time"],
        booked_slots
    )
    
    return {
        "date": date,
        "faculty_id": faculty_id,
        "available_slots": available_slots
    }

def generate_available_slots(working_start, working_end, booked_slots, interval_minutes=30):
    """Generate available time slots based on working hours and booked meetings."""
    # Convert working hours to datetime objects for easier manipulation
    start_dt = datetime.strptime(working_start, "%H:%M")
    end_dt = datetime.strptime(working_end, "%H:%M")
    
    # Create time slots
    slots = []
    current = start_dt
    
    while current + timedelta(minutes=interval_minutes) <= end_dt:
        slot_start = current.time().strftime("%H:%M")
        slot_end = (current + timedelta(minutes=interval_minutes)).time().strftime("%H:%M")
        
        # Check if this slot is available
        is_available = True
        for booked in booked_slots:
            # Convert booked times to comparable format
            booked_start_str = ""
            booked_end_str = ""
            
            # Handle time objects
            if hasattr(booked["start_time"], "strftime"):
                booked_start_str = booked["start_time"].strftime("%H:%M")
            # Handle string times
            elif isinstance(booked["start_time"], str):
                if len(booked["start_time"]) > 5:  # Format like "10:00:00"
                    booked_start_str = booked["start_time"][:5]  # Take just "10:00"
                else:
                    booked_start_str = booked["start_time"]
            
            # Same for end time
            if hasattr(booked["end_time"], "strftime"):
                booked_end_str = booked["end_time"].strftime("%H:%M")
            elif isinstance(booked["end_time"], str):
                if len(booked["end_time"]) > 5:  # Format like "11:00:00"
                    booked_end_str = booked["end_time"][:5]  # Take just "11:00"
                else:
                    booked_end_str = booked["end_time"]
            
            # Now compare as strings
            if (booked_start_str < slot_end and booked_end_str > slot_start):
                is_available = False
                break
        
        if is_available:
            slots.append({
                "start_time": slot_start,
                "end_time": slot_end
            })
        
        current += timedelta(minutes=interval_minutes)
    
    return slots