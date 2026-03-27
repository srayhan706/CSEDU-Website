from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, Lab, LabTimeSlot, LabBooking
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from config import settings

# Load environment variables
load_dotenv()

# Database connection
DATABASE_URL = f"postgresql://{settings.database_username}:{settings.database_password}@localhost:{settings.database_port}/{settings.database_name}"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def setup_labs_table():
    # Create the labs table
    Base.metadata.create_all(bind=engine)
    
    # Create a session
    db = SessionLocal()
    
    try:
        # Check if we already have labs data
        existing_labs = db.query(Lab).count()
        
        if existing_labs == 0:
            print("Adding sample labs data...")
            
            # Sample labs data
            labs = [
                Lab(
                    name="AI & Machine Learning Lab",
                    description="Equipped with high-performance GPUs and specialized hardware for AI research and development",
                    location="Building A, Room 301",
                    capacity=30,
                    facilities=["NVIDIA RTX 4090 GPUs", "TensorFlow Workstations", "Deep Learning Servers", "Neural Network Visualization Tools"],
                    image="/assets/images/labs/ai-lab.jpg"
                ),
                Lab(
                    name="Software Engineering Lab",
                    description="Modern software development environment with industry-standard tools and collaboration spaces",
                    location="Building B, Room 201",
                    capacity=40,
                    facilities=["Development Workstations", "Agile Project Boards", "Collaboration Spaces", "Version Control Systems"],
                    image="/assets/images/labs/software-lab.jpg"
                ),
                Lab(
                    name="Networking & Security Lab",
                    description="Specialized lab for network configuration, security testing, and penetration testing exercises",
                    location="Building A, Room 205",
                    capacity=25,
                    facilities=["Cisco Networking Equipment", "Security Testing Tools", "Firewall Systems", "Network Simulation Software"],
                    image="/assets/images/labs/network-lab.jpg"
                ),
                Lab(
                    name="Graphics & Multimedia Lab",
                    description="Creative space with high-end graphics workstations and multimedia production equipment",
                    location="Building C, Room 102",
                    capacity=20,
                    facilities=["Graphics Workstations", "3D Modeling Software", "Animation Tools", "Video Editing Suites"],
                    image="/assets/images/labs/graphics-lab.jpg"
                ),
                Lab(
                    name="IoT & Embedded Systems Lab",
                    description="Workspace for developing and testing IoT devices and embedded systems projects",
                    location="Building B, Room 305",
                    capacity=25,
                    facilities=["Arduino Kits", "Raspberry Pi Stations", "Sensor Arrays", "IoT Development Platforms"],
                    image="/assets/images/labs/iot-lab.jpg"
                )
            ]
            
            db.add_all(labs)
            db.commit()
            
            # Refresh labs to get their IDs
            for lab in labs:
                db.refresh(lab)
            
            print("Sample labs data added successfully!")
            
            # Add time slots for each lab
            print("Adding sample lab time slots...")
            
            days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
            time_slots = [
                {"start": "09:00", "end": "11:00"},
                {"start": "11:30", "end": "13:30"},
                {"start": "14:00", "end": "16:00"},
                {"start": "16:30", "end": "18:30"}
            ]
            
            all_time_slots = []
            
            for lab in labs:
                for day in days_of_week:
                    for slot in time_slots:
                        time_slot = LabTimeSlot(
                            lab_id=lab.id,
                            day=day,
                            start_time=slot["start"],
                            end_time=slot["end"]
                        )
                        all_time_slots.append(time_slot)
            
            db.add_all(all_time_slots)
            db.commit()
            
            print("Sample lab time slots added successfully!")
            
            # Add some sample bookings
            print("Adding sample lab bookings...")
            
            # Get some time slots to mark as booked
            sample_time_slots = db.query(LabTimeSlot).limit(10).all()
            
            # Get time slots for bookings
            # No need to mark as booked as the field doesn't exist
            
            # Create sample bookings
            sample_bookings = [
                LabBooking(
                    lab_id=sample_time_slots[0].lab_id,
                    user_id=1,  # Assuming user with ID 1 exists
                    user_name="Dr. Palash Roy",
                    user_role="faculty",
                    time_slot_id=sample_time_slots[0].id,
                    date=datetime.now().date() + timedelta(days=2),
                    purpose="AI Research Project Meeting",
                    status="approved",
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                ),
                LabBooking(
                    lab_id=sample_time_slots[1].lab_id,
                    user_id=2,  # Assuming user with ID 2 exists
                    user_name="Tanvir Ahmed",
                    user_role="student",
                    time_slot_id=sample_time_slots[1].id,
                    date=datetime.now().date() + timedelta(days=3),
                    purpose="Thesis Project Work",
                    status="pending",
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                ),
                LabBooking(
                    lab_id=sample_time_slots[2].lab_id,
                    user_id=3,  # Assuming user with ID 3 exists
                    user_name="Dr. Ismat Rahman",
                    user_role="faculty",
                    time_slot_id=sample_time_slots[2].id,
                    date=datetime.now().date() + timedelta(days=1),
                    purpose="Research Group Meeting",
                    status="approved",
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                ),
                LabBooking(
                    lab_id=sample_time_slots[3].lab_id,
                    user_id=4,  # Assuming user with ID 4 exists
                    user_name="Anika Rahman",
                    user_role="student",
                    time_slot_id=sample_time_slots[3].id,
                    date=datetime.now().date() + timedelta(days=4),
                    purpose="Final Year Project Work",
                    status="rejected",
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                ),
                LabBooking(
                    lab_id=sample_time_slots[4].lab_id,
                    user_id=5,  # Assuming user with ID 5 exists
                    user_name="Dr. Farhan Ahmed",
                    user_role="faculty",
                    time_slot_id=sample_time_slots[4].id,
                    date=datetime.now().date() + timedelta(days=5),
                    purpose="Network Security Workshop",
                    status="approved",
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
            ]
            
            db.add_all(sample_bookings)
            db.commit()
            
            print("Sample lab bookings added successfully!")
        else:
            print("Labs table already has data. Skipping sample data creation.")
            
    except Exception as e:
        print(f"Error setting up labs table: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    setup_labs_table()
