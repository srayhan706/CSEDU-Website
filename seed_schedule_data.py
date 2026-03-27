import json
from fastapi import FastAPI, APIRouter, Response
from typing import List, Dict, Any

# Create a file with mock data that can be loaded by the API

# Sample data
batches = ["2018", "2019", "2020", "2021", "2022"]
semesters = ["1", "2", "3", "4", "5", "6", "7", "8"]
rooms = ["Room 101", "Room 102", "Room 103", "Room 201", "Room 202", "Lab 1", "Lab 2", "Seminar Room"]
days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday"]
course_codes = [
    "CSE101", "CSE102", "CSE201", "CSE202", "CSE301", "CSE302", "CSE401", "CSE402",
    "CSE303", "CSE304", "CSE305", "CSE306", "CSE307", "CSE308"
]
course_names = [
    "Introduction to Computer Science", "Programming Fundamentals", "Data Structures",
    "Algorithms", "Database Systems", "Operating Systems", "Computer Networks",
    "Software Engineering", "Artificial Intelligence", "Machine Learning",
    "Computer Graphics", "Web Development", "Mobile App Development", "Computer Architecture"
]

# Instructor data
instructors = [
    {"id": 1, "name": "Dr. Md. Shabbir Ahmed", "designation": "Associate Professor"},
    {"id": 2, "name": "Dr. Kazi Muheymin-Us-Sakib", "designation": "Professor"},
    {"id": 3, "name": "Dr. Md. Mustafizur Rahman", "designation": "Assistant Professor"},
    {"id": 4, "name": "Dr. Anindya Iqbal", "designation": "Associate Professor"},
    {"id": 5, "name": "Dr. Md. Abdur Rahman", "designation": "Lecturer"}
]

# Create mock schedule data
def create_mock_schedule_data():
    # Generate class schedules
    class_schedules = []
    
    import random
    from datetime import datetime, timedelta
    
    for i in range(30):  # Create 30 class schedules
        course_idx = i % len(course_codes)
        
        # Create time strings (8 AM to 4 PM)
        hour = random.randint(8, 16)
        minute = random.choice([0, 30])
        
        start_time = f"{hour:02d}:{minute:02d}"
        end_hour = hour + 1 if minute == 0 else hour + 2
        end_minute = minute
        end_time = f"{end_hour:02d}:{end_minute:02d}"
        
        instructor = random.choice(instructors)
        class_type = random.choice(["Lecture", "Lab", "Tutorial"])
        status = random.choice(["In Progress", "Upcoming", "Completed"])
        
        class_schedule = {
            "id": str(i + 1),
            "courseCode": course_codes[course_idx],
            "courseName": course_names[course_idx],
            "type": class_type,
            "batch": random.choice(batches),
            "semester": random.choice(semesters),
            "day": random.choice(days),
            "startTime": start_time,
            "endTime": end_time,
            "room": random.choice(rooms),
            "instructorId": instructor["id"],
            "instructorName": instructor["name"],
            "instructorDesignation": instructor["designation"],
            "status": status
        }
        
        class_schedules.append(class_schedule)
    
    # Create the response structure
    schedule_data = {
        "classes": class_schedules,
        "batches": batches,
        "semesters": semesters,
        "rooms": rooms
    }
    
    # Save to a JSON file
    with open("mock_schedule_data.json", "w") as f:
        json.dump(schedule_data, f, indent=2)
    
    print(f"Created mock schedule data with {len(class_schedules)} class schedules")
    print(f"Batches: {batches}")
    print(f"Semesters: {semesters}")
    print(f"Rooms: {rooms}")

# Now create a function to modify the router/schedule.py file to use the mock data
def create_mock_schedule_router():
    router_code = '''
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import json
import os
from pydantic import BaseModel

from database import get_db
from middleware import permission_required

router = APIRouter(
    prefix="/api/schedule",
    tags=["schedule"],
)

# Pydantic models for response
class ClassScheduleResponse(BaseModel):
    id: str
    courseCode: str
    courseName: str
    type: str
    batch: str
    semester: str
    day: str
    startTime: str
    endTime: str
    room: str
    instructorId: int
    instructorName: str
    instructorDesignation: str
    status: str

class ClassesListResponse(BaseModel):
    classes: List[ClassScheduleResponse]
    batches: List[str]
    semesters: List[str]
    rooms: List[str]


@router.get("", response_model=ClassesListResponse)
async def get_classes(
    db: Session = Depends(get_db),
    batch: Optional[str] = None,
    semester: Optional[str] = None,
    room: Optional[str] = None,
    day: Optional[str] = None,
    status: Optional[str] = None
):
    """Get all class schedules with optional filtering"""
    # Load mock data from file
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(current_dir)
        mock_data_path = os.path.join(parent_dir, "mock_schedule_data.json")
        
        with open(mock_data_path, "r") as f:
            data = json.load(f)
    except Exception as e:
        # If file doesn't exist, return empty data
        return ClassesListResponse(
            classes=[],
            batches=[],
            semesters=[],
            rooms=[]
        )
    
    # Apply filters if provided
    classes = data["classes"]
    if batch:
        classes = [c for c in classes if c["batch"] == batch]
    if semester:
        classes = [c for c in classes if c["semester"] == semester]
    if room:
        classes = [c for c in classes if c["room"] == room]
    if day:
        classes = [c for c in classes if c["day"] == day]
    if status:
        classes = [c for c in classes if c["status"] == status]
    
    return ClassesListResponse(
        classes=classes,
        batches=data["batches"],
        semesters=data["semesters"],
        rooms=data["rooms"]
    )
'''
    
    # Write the router code to a file
    with open("router/schedule.py", "w") as f:
        f.write(router_code)
    
    print("Created mock schedule router")

if __name__ == "__main__":
    create_mock_schedule_data()
    create_mock_schedule_router()
    print("Mock schedule data and router created successfully!")
