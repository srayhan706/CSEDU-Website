"""
Direct seed script for meetings data with minimal dependencies.
This script directly inserts meetings data into the database.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import random

from models import Base, User, Faculty, Meeting, MeetingType, MeetingStatus, RSVPStatus
from config import settings

# Create database connection
DATABASE_URL = settings.database_url
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def seed_meetings():
    """Seed meetings data directly into the database."""
    # Create a session
    db = SessionLocal()
    
    try:
        # Get all faculty and students
        faculty_list = db.query(Faculty).all()
        
        if not faculty_list:
            print("No faculty found in database. Please run faculty seed script first.")
            return
            
        # Get all users with student role
        student_role = db.query(Role).filter(Role.name == "STUDENT").first()
        if not student_role:
            print("No student role found. Creating...")
            student_role = Role(name="STUDENT")
            db.add(student_role)
            db.commit()
            db.refresh(student_role)
            
        student_list = db.query(User).filter(User.role_id == student_role.id).all()
        if not student_list:
            print("No students found in database. Will create test student.")
            
        print(f"Found {len(faculty_list)} faculty and {len(student_list)} students")
        
        # Create test user for API testing if not exists
        test_student_email = "student2@csedu.edu"
        test_student = db.query(User).filter(User.email == test_student_email).first()
        
        if not test_student:
            print(f"Creating test student user: {test_student_email}")
            from passlib.context import CryptContext
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            
            # Get student role
            student_role = db.query(Role).filter(Role.name == "STUDENT").first()
            if not student_role:
                print("Student role not found. Creating...")
                student_role = Role(name="STUDENT")
                db.add(student_role)
                db.commit()
                db.refresh(student_role)
            
            # Create user
            test_user = User(
                name="Student Two",
                email=test_student_email,
                username="student2",
                password=pwd_context.hash("password123"),
                role_id=student_role.id
            )
            db.add(test_user)
            db.commit()
            db.refresh(test_user)
            
            print(f"Created test student with ID: {test_user.id}")
            
            # Add to student list
            student_list.append(test_user)
        
        # Create test faculty user if not exists
        test_faculty_email = "masroor@csedu.edu"
        test_faculty = db.query(User).filter(User.email == test_faculty_email).first()
        
        if not test_faculty:
            print(f"Creating test faculty user: {test_faculty_email}")
            from passlib.context import CryptContext
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            
            # Get faculty role
            faculty_role = db.query(Role).filter(Role.name == "FACULTY").first()
            if not faculty_role:
                print("Faculty role not found. Creating...")
                faculty_role = Role(name="FACULTY")
                db.add(faculty_role)
                db.commit()
                db.refresh(faculty_role)
            
            # Create user
            test_user = User(
                name="Dr. Muhammad Masroor Ali",
                email=test_faculty_email,
                username="masroor",
                password=pwd_context.hash("password123"),
                role_id=faculty_role.id
            )
            db.add(test_user)
            db.commit()
            db.refresh(test_user)
            
            # Create faculty profile
            from models import FacultyDesignation
            test_faculty_profile = Faculty(
                id=test_user.id,  # Faculty.id is the same as User.id
                designation=FacultyDesignation.PROFESSOR,
                department="Computer Science and Engineering",
                expertise=["Machine Learning", "Artificial Intelligence"],
                office="Room 201, CSE Building"
            )
            db.add(test_faculty_profile)
            db.commit()
            db.refresh(test_faculty_profile)
            print(f"Created test faculty with ID: {test_user.id}")
            
            # Add to faculty list
            faculty_list.append(test_faculty_profile)
        
        # Meeting types from enum
        meeting_types = [MeetingType.ADVISING, MeetingType.THESIS, MeetingType.PROJECT, MeetingType.GENERAL, MeetingType.OTHER]
        
        # Meeting statuses from enum
        statuses = [MeetingStatus.SCHEDULED, MeetingStatus.CONFIRMED, MeetingStatus.COMPLETED, MeetingStatus.CANCELLED]
        
        # RSVP statuses from enum
        rsvp_statuses = [RSVPStatus.PENDING, RSVPStatus.CONFIRMED, RSVPStatus.DECLINED, RSVPStatus.TENTATIVE]
        
        # Generate meetings
        print("Generating meetings...")
        meetings_to_create = []
        
        # Get the test faculty and student for guaranteed meetings
        test_faculty_user = db.query(User).filter(User.email == test_faculty_email).first()
        test_student_user = db.query(User).filter(User.email == test_student_email).first()
        
        if test_faculty_user and test_student_user:
            # Create specific meetings between test faculty and student
            for i in range(1, 6):
                meeting_date = datetime.now() + timedelta(days=i)
                
                meeting_type = meeting_types[i % len(meeting_types)]
                meeting = Meeting(
                    title=f"Meeting {i}: masroor with student2",
                    description=f"This is a {meeting_type.value.upper()} meeting between student and faculty.",
                    faculty_id=test_faculty_user.id,
                    student_id=test_student_user.id,
                    date=meeting_date.date(),
                    start_time=(datetime.min + timedelta(hours=10)).time(),
                    end_time=(datetime.min + timedelta(hours=11)).time(),
                    location=f"Room {100 + i}, CSE Building",
                    meeting_type=meeting_types[i % len(meeting_types)],
                    status=statuses[i % len(statuses)],
                    rsvp_status=rsvp_statuses[i % len(rsvp_statuses)],
                    rsvp_deadline=meeting_date - timedelta(days=1),
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                meetings_to_create.append(meeting)
        
        # Create random meetings
        for i in range(10):
            faculty = random.choice(faculty_list)
            student = random.choice(student_list)
            meeting_date = datetime.now() + timedelta(days=random.randint(1, 30))
            
            faculty_name = faculty.id if hasattr(faculty, 'id') else 'Unknown'
            student_name = student.name if hasattr(student, 'name') else 'Unknown'
            
            meeting_type = random.choice(meeting_types)
            meeting = Meeting(
                title=f"Meeting {i+6}: Faculty {faculty_name} with Student {student_name}",
                description=f"This is a {meeting_type.value.upper()} meeting between student and faculty.",
                faculty_id=faculty.id if hasattr(faculty, 'id') else faculty.user_id,
                student_id=student.id,
                date=meeting_date.date(),
                start_time=(datetime.min + timedelta(hours=random.randint(9, 16))).time(),
                end_time=(datetime.min + timedelta(hours=random.randint(17, 18))).time(),
                location=f"Room {random.randint(100, 500)}, CSE Building",
                meeting_type=random.choice(meeting_types),
                status=random.choice(statuses),
                rsvp_status=random.choice(rsvp_statuses),
                rsvp_deadline=meeting_date - timedelta(days=1),
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            meetings_to_create.append(meeting)
        
        # Add all meetings to database
        db.add_all(meetings_to_create)
        db.commit()
        
        print(f"Successfully created {len(meetings_to_create)} meetings")
        
    except Exception as e:
        print(f"Error seeding meetings: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    # Import here to avoid circular imports
    from models import Role
    seed_meetings()
