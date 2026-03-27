from sqlalchemy.orm import Session
from database import engine, get_db
from models import Lab, LabTimeSlot
from sqlalchemy import text

def add_lab_time_slots():
    # Get a database session
    db = next(get_db())
    
    try:
        # Get all labs
        labs = db.query(Lab).all()
        
        # Days of the week
        days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
        
        # Time slots
        time_slots = [
            {"start_time": "09:00", "end_time": "11:00"},
            {"start_time": "11:00", "end_time": "13:00"},
            {"start_time": "14:00", "end_time": "16:00"},
            {"start_time": "16:00", "end_time": "18:00"}
        ]
        
        # First, delete existing time slots to avoid duplicates
        db.execute(text("DELETE FROM lab_time_slots"))
        db.commit()
        
        # Add time slots for each lab
        for lab in labs:
            print(f"Adding time slots for lab: {lab.name}")
            
            for day in days:
                for slot in time_slots:
                    # Create a new time slot
                    new_slot = LabTimeSlot(
                        lab_id=lab.id,
                        day=day,
                        start_time=slot["start_time"],
                        end_time=slot["end_time"]
                    )
                    db.add(new_slot)
            
        # Commit all changes
        db.commit()
        print(f"Successfully added time slots for {len(labs)} labs")
        
    except Exception as e:
        db.rollback()
        print(f"Error adding time slots: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    add_lab_time_slots()
