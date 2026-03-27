from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import enum

from models import Base, Announcement, AnnouncementType, PriorityLevel
from config import settings

# Create database connection
DATABASE_URL = f"postgresql://{settings.database_username}:{settings.database_password}@localhost:{settings.database_port}/{settings.database_name}"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def setup_database():
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Create a session
    db = SessionLocal()
    
    try:
        # Check if announcements table exists and has data
        existing_announcements = db.query(Announcement).count()
        
        if existing_announcements == 0:
            print("Adding sample announcements...")
            # Add sample announcements
            announcements = [
                Announcement(
                    title="Welcome to the New Department Website",
                    content="We are excited to launch our new Department of Computer Science and Engineering website. This platform will serve as a central hub for all department-related information, announcements, and resources.",
                    date=datetime.utcnow(),
                    type=AnnouncementType.GENERAL,
                    priority=PriorityLevel.HIGH,
                    image="/assets/images/csedu_building.jpg",
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                ),
                Announcement(
                    title="Fall 2023 Registration Open",
                    content="Registration for Fall 2023 semester is now open. Please log in to the student portal to register for your courses. The deadline for registration is August 15, 2023.",
                    date=datetime.utcnow(),
                    type=AnnouncementType.ACADEMIC,
                    priority=PriorityLevel.HIGH,
                    image=None,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                ),
                Announcement(
                    title="Faculty Research Symposium",
                    content="The annual Faculty Research Symposium will be held on September 10, 2023. All faculty members are invited to present their research work. Please submit your abstracts by August 30.",
                    date=datetime.utcnow(),
                    type=AnnouncementType.ACADEMIC,
                    priority=PriorityLevel.MEDIUM,
                    image="/assets/images/research_lab.jpg",
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                ),
                Announcement(
                    title="New GPU Lab Equipment",
                    content="The department has acquired new NVIDIA RTX 4090 GPUs for the AI research lab. Students working on machine learning projects can request access through their supervisors.",
                    date=datetime.utcnow(),
                    type=AnnouncementType.ADMIN,
                    priority=PriorityLevel.MEDIUM,
                    image="/assets/images/lab_equipment.jpg",
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                ),
                Announcement(
                    title="Summer Internship Opportunities",
                    content="Several companies have posted summer internship opportunities for CSE students. Check the career portal for details and application instructions.",
                    date=datetime.utcnow(),
                    type=AnnouncementType.GENERAL,
                    priority=PriorityLevel.LOW,
                    image=None,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
            ]
            
            db.add_all(announcements)
            db.commit()
            print(f"Added {len(announcements)} sample announcements")
        else:
            print(f"Found {existing_announcements} existing announcements, skipping sample data creation")
            
    except Exception as e:
        print(f"Error setting up database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    setup_database()
