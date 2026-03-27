from database import Base, engine
from models import Course, Program
from sqlalchemy.orm import sessionmaker
import json

# Create all tables
Base.metadata.create_all(bind=engine)

# Create a session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
db = SessionLocal()

# Check if we already have programs
existing_programs = db.query(Program).count()
if existing_programs == 0:
    # Add sample programs
    programs = [
        {
            "title": "Bachelor of Science in Computer Science and Engineering",
            "level": "Undergraduate",
            "duration": "4 years",
            "total_students": 120,
            "total_courses": 40,
            "total_credits": 160,
            "short_description": "A comprehensive program covering all aspects of computer science and engineering."
        },
        {
            "title": "Master of Science in Computer Science",
            "level": "Graduate",
            "duration": "2 years",
            "total_students": 45,
            "total_courses": 12,
            "total_credits": 36,
            "short_description": "An advanced program focusing on specialized areas of computer science."
        }
    ]
    
    program_objects = []
    for program in programs:
        program_obj = Program(**program)
        db.add(program_obj)
        program_objects.append(program_obj)
    
    db.commit()
    
    # Refresh to get the IDs
    for program_obj in program_objects:
        db.refresh(program_obj)
    
    print(f"Added {len(programs)} programs")

# Check if we already have courses
existing_courses = db.query(Course).count()
if existing_courses == 0:
    # Get program IDs
    undergrad_program = db.query(Program).filter(Program.level == "Undergraduate").first()
    grad_program = db.query(Program).filter(Program.level == "Graduate").first()
    
    if not undergrad_program or not grad_program:
        print("Programs not found. Please ensure programs are created first.")
        exit(1)
    
    # Add sample courses
    courses = [
        {
            "code": "CSE101",
            "title": "Introduction to Computer Science",
            "description": "An introductory course covering the basics of computer science, programming concepts, and problem-solving techniques.",
            "credits": 3,
            "duration": "1 semester",
            "difficulty": "Beginner",
            "prerequisites": json.dumps(["None"]),
            "semester": 1,
            "year": 1,
            "program_id": undergrad_program.id,
            "specialization": "Core"
        },
        {
            "code": "CSE203",
            "title": "Data Structures",
            "description": "Study of data organization, management, and storage formats that enable efficient access and modification.",
            "credits": 4,
            "duration": "1 semester",
            "difficulty": "Intermediate",
            "prerequisites": json.dumps(["CSE101"]),
            "semester": 2,
            "year": 1,
            "program_id": undergrad_program.id,
            "specialization": "Core"
        },
        {
            "code": "CSE307",
            "title": "Software Engineering",
            "description": "Principles and practices of software development and project management.",
            "credits": 3,
            "duration": "1 semester",
            "difficulty": "Intermediate",
            "prerequisites": json.dumps(["CSE203"]),
            "semester": 5,
            "year": 3,
            "program_id": undergrad_program.id,
            "specialization": "Software Engineering"
        },
        {
            "code": "CSE401",
            "title": "Computer Networks",
            "description": "Study of computer network architecture, protocols, and applications.",
            "credits": 3,
            "duration": "1 semester",
            "difficulty": "Intermediate",
            "prerequisites": json.dumps(["CSE203"]),
            "semester": 4,
            "year": 2,
            "program_id": undergrad_program.id,
            "specialization": "Networking"
        },
        {
            "code": "CSE503",
            "title": "Advanced Machine Learning",
            "description": "Advanced techniques in machine learning and deep learning.",
            "credits": 4,
            "duration": "1 semester",
            "difficulty": "Advanced",
            "prerequisites": json.dumps(["CSE309", "CSE317"]),
            "semester": 2,
            "year": 1,
            "program_id": grad_program.id,
            "specialization": "AI"
        }
    ]
    
    for course in courses:
        course_obj = Course(**course)
        db.add(course_obj)
    
    db.commit()
    print(f"Added {len(courses)} courses")

print("Database initialization completed successfully!")
