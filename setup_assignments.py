import os
import sys
from datetime import datetime, timedelta
import random

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the models
from database import SessionLocal, engine
from models import Base, Assignment, User

def setup_assignments():
    db = SessionLocal()
    
    # Check if assignments already exist
    existing_assignments = db.query(Assignment).count()
    if existing_assignments > 0:
        print("Assignments already exist. Skipping creation.")
        db.close()
        return
    
    print("Creating sample assignments...")
    
    # Get some faculty users to use as assignment creators
    faculty_users = db.query(User).filter(User.role_id == 2).limit(5).all()  # Assuming role_id 2 is for faculty
    if not faculty_users:
        print("No faculty users found. Creating assignments with placeholder faculty.")
        faculty_users = [{
            "id": 1,
            "name": "Dr. Mahmud Hasan"
        }, {
            "id": 2,
            "name": "Prof. Saifur Rahman"
        }, {
            "id": 3,
            "name": "Dr. Nusrat Jahan"
        }]
    
    # Sample assignment data
    assignments_data = [
        {
            "title": "Implementation of Sorting Algorithms",
            "courseCode": "CSE-205",
            "courseTitle": "Data Structures",
            "semester": 2,
            "batch": "26",
            "deadline": datetime.now() + timedelta(days=7),
            "description": "Implement the following sorting algorithms in C++: Bubble Sort, Insertion Sort, Selection Sort, Merge Sort, and Quick Sort. Compare their time complexities for different input sizes.",
            "attachments": [
                {"name": "Assignment Guidelines.pdf", "url": "/assets/assignments/guidelines.pdf"},
                {"name": "Sample Input Data.txt", "url": "/assets/assignments/sample_data.txt"}
            ],
            "submissionType": "file",
            "status": "active"
        },
        {
            "title": "Database Design Project",
            "courseCode": "CSE-303",
            "courseTitle": "Database Systems",
            "semester": 3,
            "batch": "25",
            "deadline": datetime.now() + timedelta(days=14),
            "description": "Design a relational database for a university management system. Include entity-relationship diagrams, schema definitions, and SQL queries for common operations.",
            "attachments": [
                {"name": "Project Requirements.pdf", "url": "/assets/assignments/db_requirements.pdf"}
            ],
            "submissionType": "file",
            "status": "active"
        },
        {
            "title": "Neural Network Implementation",
            "courseCode": "CSE-401",
            "courseTitle": "Artificial Intelligence",
            "semester": 4,
            "batch": "25",
            "deadline": datetime.now() + timedelta(days=10),
            "description": "Implement a simple feedforward neural network from scratch using Python. Train it on the MNIST dataset and evaluate its performance.",
            "attachments": [],
            "submissionType": "link",
            "status": "active"
        },
        {
            "title": "Operating System Concepts",
            "courseCode": "CSE-307",
            "courseTitle": "Operating Systems",
            "semester": 3,
            "batch": "25",
            "deadline": datetime.now() - timedelta(days=5),
            "description": "Write a comprehensive report on process scheduling algorithms. Include examples, comparisons, and real-world applications.",
            "attachments": [],
            "submissionType": "text",
            "status": "past"
        },
        {
            "title": "Web Application Development",
            "courseCode": "CSE-405",
            "courseTitle": "Software Engineering",
            "semester": 4,
            "batch": "24",
            "deadline": datetime.now() + timedelta(days=21),
            "description": "Develop a full-stack web application using React and Node.js. The application should include user authentication, data persistence, and responsive design.",
            "attachments": [
                {"name": "Project Rubric.pdf", "url": "/assets/assignments/web_rubric.pdf"}
            ],
            "submissionType": "link",
            "status": "active"
        },
        {
            "title": "Computer Networks Lab",
            "courseCode": "CSE-407",
            "courseTitle": "Computer Networks",
            "semester": 4,
            "batch": "24",
            "deadline": datetime.now() - timedelta(days=10),
            "description": "Implement a simple client-server application using socket programming. The application should demonstrate basic network communication principles.",
            "attachments": [],
            "submissionType": "file",
            "status": "past"
        },
        {
            "title": "Compiler Design Project",
            "courseCode": "CSE-409",
            "courseTitle": "Compiler Design",
            "semester": 4,
            "batch": "24",
            "deadline": datetime.now() + timedelta(days=5),
            "description": "Implement a lexical analyzer and parser for a simple programming language. Include documentation on the grammar and parsing techniques used.",
            "attachments": [
                {"name": "Language Specification.pdf", "url": "/assets/assignments/lang_spec.pdf"}
            ],
            "submissionType": "file",
            "status": "active"
        },
        {
            "title": "Machine Learning Algorithms",
            "courseCode": "CSE-501",
            "courseTitle": "Advanced Machine Learning",
            "semester": 5,
            "batch": "23",
            "deadline": datetime.now() + timedelta(days=3),
            "description": "Implement and compare the performance of different classification algorithms on a dataset of your choice. Include a detailed analysis of the results.",
            "attachments": [],
            "submissionType": "link",
            "status": "active"
        },
        {
            "title": "Research Paper Review",
            "courseCode": "CSE-601",
            "courseTitle": "Advanced Algorithms",
            "semester": 6,
            "batch": "23",
            "deadline": datetime.now() + timedelta(days=30),
            "description": "Select a recent research paper on algorithmic advances and write a comprehensive review. Include a summary, critical analysis, and potential applications.",
            "attachments": [
                {"name": "Review Guidelines.pdf", "url": "/assets/assignments/review_guide.pdf"}
            ],
            "submissionType": "text",
            "status": "draft"
        },
        {
            "title": "Introduction to Programming Assignment",
            "courseCode": "CSE-103",
            "courseTitle": "Introduction to Programming",
            "semester": 1,
            "batch": "27",
            "deadline": datetime.now() + timedelta(days=2),
            "description": "Write simple programs in C to demonstrate understanding of basic programming concepts: variables, loops, conditionals, and functions.",
            "attachments": [
                {"name": "Programming Problems.pdf", "url": "/assets/assignments/intro_problems.pdf"}
            ],
            "submissionType": "file",
            "status": "active"
        }
    ]
    
    # Create assignment objects
    assignments = []
    for assignment_data in assignments_data:
        # Select a random faculty user
        if isinstance(faculty_users[0], User):
            faculty = random.choice(faculty_users)
            faculty_id = faculty.id
            faculty_name = faculty.name
        else:
            faculty = random.choice(faculty_users)
            faculty_id = faculty["id"]
            faculty_name = faculty["name"]
        
        assignment = Assignment(
            title=assignment_data["title"],
            courseCode=assignment_data["courseCode"],
            courseTitle=assignment_data["courseTitle"],
            semester=assignment_data["semester"],
            batch=assignment_data["batch"],
            deadline=assignment_data["deadline"],
            description=assignment_data["description"],
            attachments=assignment_data["attachments"],
            submissionType=assignment_data["submissionType"],
            status=assignment_data["status"],
            facultyId=faculty_id,
            facultyName=faculty_name
        )
        assignments.append(assignment)
    
    # Add to database
    db.add_all(assignments)
    db.commit()
    
    print(f"Created {len(assignments)} sample assignments.")
    db.close()

if __name__ == "__main__":
    setup_assignments()
