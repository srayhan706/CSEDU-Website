from database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, DateTime, Text, Time, Date
from sqlalchemy.orm import relationship
from datetime import datetime, time
from sqlalchemy import Float

from sqlalchemy import Table, Enum
from sqlalchemy.dialects.postgresql import JSON, ARRAY
from enum import Enum as PyEnum
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, DateTime, Boolean, Float, ForeignKey, Enum, JSON, Date
)

class EquipmentCategory(Base):
    __tablename__ = 'equipment_categories'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    icon = Column(String, nullable=True)
    description = Column(String, nullable=True)
    equipment = relationship('Equipment', back_populates='category')

class Equipment(Base):
    __tablename__ = 'equipment'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    category_id = Column(Integer, ForeignKey('equipment_categories.id'), nullable=False)
    specifications = Column(String, nullable=True)
    quantity = Column(Integer, nullable=False)
    available = Column(Integer, nullable=False)
    image = Column(String, nullable=True)
    location = Column(String, nullable=True)
    requires_approval = Column(Boolean, nullable=False, default=False)
    category = relationship('EquipmentCategory', back_populates='equipment')
    bookings = relationship('EquipmentBooking', back_populates='equipment')

class EquipmentBooking(Base):
    __tablename__ = 'equipment_bookings'
    id = Column(Integer, primary_key=True, autoincrement=True)
    equipment_id = Column(Integer, ForeignKey('equipment.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    user_name = Column(String, nullable=False)
    user_role = Column(String, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    purpose = Column(String, nullable=True)
    status = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    rejection_reason = Column(String, nullable=True)
    equipment = relationship('Equipment', back_populates='bookings')
    user = relationship('User', back_populates='bookings')

class EventType(str, PyEnum):
    SEMINAR = 'seminar'
    WORKSHOP = 'workshop'
    CONFERENCE = 'conference'
    COMPETITION = 'competition'
    CULTURAL = 'cultural'
    ACADEMIC = 'academic'

class EventStatus(str, PyEnum):
    UPCOMING = 'upcoming'
    ONGOING = 'ongoing'
    REGISTRATION_OPEN = 'registration_open'
    REGISTRATION_CLOSED = 'registration_closed'
    COMPLETED = 'completed'


class AdmissionStats(Base):
    __tablename__ = "admission_stats"
    id = Column(Integer, primary_key=True, index=True)
    next_deadline = Column(String, nullable=False)
    programs_offered = Column(Integer, nullable=False)
    application_time = Column(String, nullable=False)
    acceptance_rate = Column(String, nullable=False)

class AdmissionDeadline(Base):
    __tablename__ = "admission_deadlines"
    id = Column(Integer, primary_key=True, index=True)
    program = Column(String, nullable=False)
    level = Column(String, nullable=False)  # Undergraduate/Graduate/Postgraduate
    date = Column(DateTime, nullable=False)
    requirements = Column(String, nullable=False)
    notes = Column(String, nullable=True)

class AdmissionFAQ(Base):
    __tablename__ = "admission_faqs"
    id = Column(Integer, primary_key=True, index=True)
    question = Column(String, nullable=False)
    answer = Column(String, nullable=False)
    category = Column(String, nullable=False)

class Award(Base):
    __tablename__ = "awards"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    details = Column(String, nullable=True)
    recipient = Column(String, nullable=False)
    recipient_type = Column(String, nullable=False)  # 'faculty' | 'student'
    year = Column(Integer, nullable=False)
    type = Column(String, nullable=False)  # 'award' | 'grant' | ...
    organization = Column(String, nullable=True)
    amount = Column(Integer, nullable=True)
    department = Column(String, nullable=True)
    duration = Column(String, nullable=True)
    categories = Column(JSON, nullable=True)
    publications = Column(JSON, nullable=True)
    link = Column(String, nullable=True)


class Session(Base):
    __tablename__ = "sessions"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    expires = Column(Float, nullable=False)


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)

    users = relationship("User", back_populates="role")
    permissions = relationship("RolePermission", back_populates="role")
    events = relationship("Event", back_populates="organizer_role")


class Permission(Base):
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    category = Column(String, nullable=False)

    roles = relationship("RolePermission", back_populates="permission")


class RolePermission(Base):
    __tablename__ = "roles_permissions"

    id = Column(Integer, primary_key=True, index=True)
    role_id = Column(Integer, ForeignKey("roles.id"))
    permission_id = Column(Integer, ForeignKey("permissions.id"))

    role = relationship("Role", back_populates="permissions")
    permission = relationship("Permission", back_populates="roles")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"))

    username = Column(String, nullable=True)
    contact = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    role = relationship("Role", back_populates="users")
    bookings = relationship('EquipmentBooking', back_populates='user')



class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    type = Column(Enum(EventType), nullable=False)
    status = Column(Enum(EventStatus), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    venue = Column(String, nullable=False)
    speaker = Column(String, nullable=True)
    organizer_role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    max_participants = Column(Integer, nullable=True)
    registered_count = Column(Integer, default=0)
    registration_required = Column(Boolean, default=False)
    registration_deadline = Column(DateTime, nullable=True)
    fee = Column(Float, nullable=True)
    external_link = Column(String, nullable=True)
    tags = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    organizer_role = relationship("Role", back_populates="events")
    registrations = relationship("EventRegistration", back_populates="event")




class EventRegistration(Base):
    __tablename__ = "event_registrations"
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    full_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    student_id = Column(String, nullable=True)
    department = Column(String, nullable=True)
    year = Column(String, nullable=True)
    special_requirements = Column(String, nullable=True)
    registration_date = Column(DateTime, default=datetime.utcnow)
    
    event = relationship("Event", back_populates="registrations")
    user = relationship("User")


class Lab(Base):
    __tablename__ = "labs"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    location = Column(String, nullable=False)
    capacity = Column(Integer, nullable=False)
    facilities = Column(JSON, nullable=True)
    image = Column(String, nullable=True)
    time_slots = relationship("LabTimeSlot", back_populates="lab", cascade="all, delete-orphan")
    bookings = relationship("LabBooking", back_populates="lab", cascade="all, delete-orphan")

class LabTimeSlot(Base):
    __tablename__ = "lab_time_slots"
    id = Column(Integer, primary_key=True, index=True)
    lab_id = Column(Integer, ForeignKey("labs.id"), nullable=False)
    day = Column(String, nullable=False)
    start_time = Column(String, nullable=False)  # e.g., '09:00'
    end_time = Column(String, nullable=False)    # e.g., '11:00'
    lab = relationship("Lab", back_populates="time_slots")
    bookings = relationship("LabBooking", back_populates="time_slot", cascade="all, delete-orphan")


class LabBooking(Base):
    __tablename__ = "lab_bookings"
    id = Column(Integer, primary_key=True, index=True)
    lab_id = Column(Integer, ForeignKey("labs.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    time_slot_id = Column(Integer, ForeignKey("lab_time_slots.id"), nullable=False)
    date = Column(Date, nullable=False)
    purpose = Column(String, nullable=True)
    status = Column(String, nullable=False, default="pending") # approved, pending, rejected
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    lab = relationship("Lab", back_populates="bookings")
    time_slot = relationship("LabTimeSlot", back_populates="bookings")

class ForgotPassword(Base):
    __tablename__ = "forgot_password"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    token = Column(String, nullable=False)
    expires = Column(Float, nullable=False)


class FacultyDesignation(str, PyEnum):
    PROFESSOR = "Professor"
    ASSOCIATE_PROFESSOR = "Associate Professor"
    ASSISTANT_PROFESSOR = "Assistant Professor"
    LECTURER = "Lecturer"


class AnnouncementType(str, PyEnum):
    ACADEMIC = 'academic'
    ADMIN = 'admin'
    GENERAL = 'general'

class PriorityLevel(str, PyEnum):
    HIGH = 'high'
    MEDIUM = 'medium'
    LOW = 'low'

class Announcement(Base):
    __tablename__ = "announcements"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    type = Column(Enum(AnnouncementType), nullable=False)
    priority = Column(Enum(PriorityLevel), nullable=False)
    image = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Faculty(Base):
    __tablename__ = "faculty"

    id = Column(Integer,  ForeignKey("users.id"), primary_key=True, index=True, autoincrement=True)
    designation = Column(Enum(FacultyDesignation), nullable=False)
    department = Column(String, nullable=False)
    expertise = Column(JSON, nullable=False)
    office = Column(String, nullable=True)
    image = Column(String, nullable=True)
    website = Column(String, nullable=True)
    publications = Column(Integer, default=0)
    experience = Column(Integer, default=0)  # years of experience
    rating = Column(Float, default=0.0)
    is_chairman = Column(Boolean, default=False)
    bio = Column(Text, nullable=True)
    short_bio = Column(Text, nullable=True)
    education = Column(JSON, nullable=True)  # List of degrees
    courses = Column(JSON, nullable=True)    # List of courses taught
    research_interests = Column(JSON, nullable=True)  # List of research interests
    recent_publications = Column(JSON, nullable=True)  # List of publications
    awards = Column(JSON, nullable=True)  # List of awards
    office_hours = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)



class Exam(Base):
    __tablename__ = "exams"
    id = Column(Integer, primary_key=True, autoincrement=True)
    courseCode = Column(String, nullable=False)
    courseTitle = Column(String, nullable=False)
    semester = Column(Integer, nullable=False)
    batch = Column(String, nullable=False)
    examType = Column(String, nullable=False)  # "midterm" | "final" | "quiz" | "retake" | "improvement"
    date = Column(Date, nullable=False)  # Changed from DateTime to Date
    startTime = Column(String, nullable=False)  # "HH:MM"
    endTime = Column(String, nullable=False)    # "HH:MM"
    room = Column(String, nullable=False)
    invigilators = Column(JSON, nullable=False) # List of names
    status = Column(String, nullable=False)     # "scheduled" | "ongoing" | "completed" | "cancelled"
    notes = Column(String, nullable=True)  # Additional notes


class Assignment(Base):
    __tablename__ = "assignments"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    courseCode = Column(String, nullable=False)
    courseTitle = Column(String, nullable=False)
    semester = Column(Integer, nullable=False)
    batch = Column(String, nullable=False)
    deadline = Column(DateTime, nullable=False)
    description = Column(Text, nullable=False)
    attachments = Column(JSON, nullable=True)  # List of file paths or URLs
    submissionType = Column(String, nullable=False)  # "file" | "link" | "text"
    status = Column(String, nullable=False)  # "active" | "past" | "draft"
    facultyId = Column(Integer, ForeignKey("users.id"), nullable=False)
    facultyName = Column(String, nullable=False)
    createdAt = Column(DateTime, default=datetime.utcnow)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    faculty = relationship("User", foreign_keys=[facultyId])
    submissions = relationship("AssignmentSubmission", back_populates="assignment", cascade="all, delete-orphan")


class AssignmentSubmission(Base):
    __tablename__ = "assignment_submissions"
    id = Column(Integer, primary_key=True, autoincrement=True)
    assignmentId = Column(Integer, ForeignKey("assignments.id"), nullable=False)
    studentId = Column(Integer, ForeignKey("users.id"), nullable=False)
    submissionContent = Column(Text, nullable=False)  # file path, link URL, or text content
    submissionType = Column(String, nullable=False)  # "file" | "link" | "text"
    submittedAt = Column(DateTime, default=datetime.utcnow)
    status = Column(String, nullable=False, default="submitted")  # "submitted" | "graded" | "late"
    grade = Column(Float, nullable=True)
    feedback = Column(Text, nullable=True)
    gradedAt = Column(DateTime, nullable=True)
    
    assignment = relationship("Assignment", back_populates="submissions")
    student = relationship("User", foreign_keys=[studentId])


# Removed ProgramLevel enum - using string directly


class CourseDifficulty(PyEnum):
    BEGINNER = "Beginner"
    INTERMEDIATE = "Intermediate"
    ADVANCED = "Advanced"


class Program(Base):
    __tablename__ = "programs"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    level = Column(String, nullable=False)
    duration = Column(String, nullable=False)
    total_students = Column(Integer, default=0)
    total_courses = Column(Integer, default=0)
    total_credits = Column(Integer, default=0)
    short_description = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    specializations = Column(JSON, nullable=True)  # Array of strings
    learning_objectives = Column(JSON, nullable=True)  # Array of strings
    career_prospects = Column(JSON, nullable=True)  # Array of objects
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    courses = relationship("Course", back_populates="program")


class Course(Base):
    __tablename__ = "courses"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, nullable=False, unique=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    credits = Column(Integer, nullable=False)
    duration = Column(String, nullable=False)
    difficulty = Column(String, nullable=False, default="Intermediate")
    rating = Column(Float, default=0.0)
    enrolled_students = Column(Integer, default=0)
    prerequisites = Column(JSON, nullable=True)  # Array of strings
    specialization = Column(String, nullable=True)
    semester = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)
    program_id = Column(Integer, ForeignKey("programs.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    program = relationship("Program", back_populates="courses")


class ProjectCategory(str, PyEnum):
    MACHINE_LEARNING = "machine_learning"
    WEB_DEVELOPMENT = "web_development"
    MOBILE_APP = "mobile_app"
    ALGORITHMS = "algorithms"
    IOT = "iot"
    SECURITY = "security"
    ROBOTICS = "robotics"
    GRAPHICS = "graphics"


class ProjectType(str, PyEnum):
    STUDENT = "student"
    FACULTY = "faculty"


class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    summary = Column(String, nullable=False)
    abstract = Column(Text, nullable=False)
    supervisor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    year = Column(Integer, nullable=False)
    category = Column(String, nullable=False)
    type = Column(String, nullable=False)
    tags = Column(JSON, nullable=True)
    team = Column(JSON, nullable=True)  # Array of {name: string, role?: string}
    course = Column(String, nullable=True)
    team_size = Column(Integer, nullable=True)
    completion_date = Column(DateTime, nullable=False)
    technologies = Column(JSON, nullable=True)  # Array of strings
    key_features = Column(JSON, nullable=True)  # Array of strings
    achievements = Column(JSON, nullable=True)  # Array of strings
    demo_link = Column(String, nullable=True)
    github_link = Column(String, nullable=True)
    paper_link = Column(String, nullable=True)
    contact_email = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    supervisor = relationship("User", primaryjoin="Project.supervisor_id == User.id")


class ClassType(str, PyEnum):
    LECTURE = "Lecture"
    LAB = "Lab"
    TUTORIAL = "Tutorial"


class ClassStatus(str, PyEnum):
    IN_PROGRESS = "In Progress"
    UPCOMING = "Upcoming"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"


class ClassSchedule(Base):
    __tablename__ = "class_schedules"
    id = Column(Integer, primary_key=True, index=True)
    course_code = Column(String, ForeignKey("courses.code"), nullable=False)
    course_name = Column(String, nullable=False)
    type = Column(Enum(ClassType), nullable=False)
    batch = Column(String, nullable=False)
    semester = Column(String, nullable=False)
    day = Column(String, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    room = Column(String, nullable=False)
    instructor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    instructor_name = Column(String, nullable=False)
    instructor_designation = Column(String, nullable=False)
    status = Column(Enum(ClassStatus), nullable=False, default=ClassStatus.UPCOMING)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    course = relationship("Course", foreign_keys=[course_code], primaryjoin="ClassSchedule.course_code == Course.code")
    instructor = relationship("User", foreign_keys=[instructor_id])


class MeetingType(PyEnum):
    ADVISING = "ADVISING"
    THESIS = "THESIS"
    PROJECT = "PROJECT"
    GENERAL = "GENERAL"
    OTHER = "OTHER"


class MeetingStatus(PyEnum):
    SCHEDULED = "SCHEDULED"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"


class RSVPStatus(PyEnum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    TENTATIVE = "TENTATIVE"
    DECLINED = "DECLINED"


class Meeting(Base):
    __tablename__ = "meetings"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    faculty_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(Date, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    location = Column(String, nullable=True)
    meeting_type = Column(Enum(MeetingType), nullable=False, default=MeetingType.GENERAL)
    status = Column(Enum(MeetingStatus), nullable=False, default=MeetingStatus.SCHEDULED)
    rsvp_status = Column(Enum(RSVPStatus), nullable=False, default=RSVPStatus.PENDING)
    rsvp_notes = Column(Text, nullable=True)
    rsvp_deadline = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    faculty = relationship("User", foreign_keys=[faculty_id], backref="faculty_meetings")
    student = relationship("User", foreign_keys=[student_id], backref="student_meetings")


# Fee Management Models
class FeeStatus(PyEnum):
    PAID = "PAID"
    PENDING = "PENDING"
    OVERDUE = "OVERDUE"

class TransactionStatus(PyEnum):
    COMPLETED = "COMPLETED"
    PENDING = "PENDING"
    FAILED = "FAILED"

class PaymentMethod(PyEnum):
    ONLINE_BANKING = "ONLINE_BANKING"
    MOBILE_BANKING = "MOBILE_BANKING"
    CARD = "CARD"
    CASH = "CASH"
    OTHER = "OTHER"

class FeeCategory(Base):
    __tablename__ = "fee_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    fees = relationship("Fee", back_populates="category")

class Fee(Base):
    __tablename__ = "fees"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    description = Column(Text, nullable=True)
    deadline = Column(DateTime, nullable=False)
    status = Column(Enum(FeeStatus), nullable=False, default=FeeStatus.PENDING)
    semester = Column(String, nullable=False)
    batch = Column(String, nullable=False)
    category_id = Column(Integer, ForeignKey("fee_categories.id"), nullable=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    paid_date = Column(DateTime, nullable=True)
    paid_amount = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    category = relationship("FeeCategory", back_populates="fees")
    student = relationship("User", backref="fees")
    transactions = relationship("Transaction", back_populates="fee")

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, default=datetime.utcnow)
    amount = Column(Float, nullable=False)
    description = Column(Text, nullable=True)
    payment_method = Column(Enum(PaymentMethod), nullable=False)
    status = Column(Enum(TransactionStatus), nullable=False, default=TransactionStatus.PENDING)
    receipt_url = Column(String, nullable=True)
    transaction_id = Column(String, nullable=True, unique=True)
    fee_id = Column(Integer, ForeignKey("fees.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    fee = relationship("Fee", back_populates="transactions")
    student = relationship("User", backref="transactions")
