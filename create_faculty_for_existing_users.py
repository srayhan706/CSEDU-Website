"""
Script to create faculty records for existing users.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from models import Base, User, Faculty, FacultyDesignation, Role
from config import settings

# Create database connection
DATABASE_URL = settings.database_url
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_faculty_records():
    """Create faculty records for existing users."""
    # Create a session
    db = SessionLocal()
    
    try:
        # Get all users
        users = db.query(User).all()
        
        # Faculty data mapping
        faculty_data = {
            'shoyaib@cse.du.ac.bd': {
                "designation": FacultyDesignation.PROFESSOR,
                "department": "Computer Science and Engineering",
                "expertise": ["Machine Learning", "Artificial Intelligence", "Data Mining", "Computer Vision"],
                "office": "Room 301, CSE Building",
                "image": "/assets/images/faculty/default.jpg",
                "website": "https://example.com/shoyaib",
                "publications": 45,
                "experience": 15,
                "is_chairman": True,
                "bio": "Dr. Mohammad Shoyaib is a Professor and Chairman of the Department of Computer Science and Engineering at the University of Dhaka. He has over 15 years of experience in teaching and research in the field of Artificial Intelligence and Machine Learning.",
                "short_bio": "Leading researcher in machine learning and AI.",
                "education": ["Ph.D. in Computer Science, MIT", "M.Sc. in Computer Science, Stanford University", "B.Sc. in Computer Science, University of Dhaka"],
                "courses": ["CSE 401: Artificial Intelligence", "CSE 402: Machine Learning", "CSE 403: Data Mining"],
                "research_interests": ["Deep Learning", "Computer Vision", "Natural Language Processing", "Pattern Recognition"]
            },
            'mustafiz@cse.du.ac.bd': {
                "designation": FacultyDesignation.ASSOCIATE_PROFESSOR,
                "department": "Computer Science and Engineering",
                "expertise": ["Software Engineering", "Database Systems", "Web Technologies"],
                "office": "Room 302, CSE Building",
                "image": "/assets/images/faculty/default.jpg",
                "website": "https://example.com/mustafiz",
                "publications": 28,
                "experience": 10,
                "is_chairman": False,
                "bio": "Dr. Md. Mustafizur Rahman is an Associate Professor at the Department of Computer Science and Engineering, University of Dhaka. His research focuses on software engineering methodologies and database systems.",
                "short_bio": "Expert in software engineering methodologies and web.",
                "education": ["Ph.D. in Computer Science, University of California", "M.Sc. in Computer Science, University of Dhaka", "B.Sc. in Computer Science, University of Dhaka"],
                "courses": ["CSE 301: Database Systems", "CSE 302: Software Engineering", "CSE 303: Web Technologies"],
                "research_interests": ["Software Testing", "Database Optimization", "Web Security", "Cloud Computing"]
            },
            'anis@cse.du.ac.bd': {
                "designation": FacultyDesignation.ASSISTANT_PROFESSOR,
                "department": "Computer Science and Engineering",
                "expertise": ["Computer Networks", "Cybersecurity", "Internet of Things"],
                "office": "Room 303, CSE Building",
                "image": "/assets/images/faculty/default.jpg",
                "website": "https://example.com/anis",
                "publications": 15,
                "experience": 7,
                "is_chairman": False,
                "bio": "Dr. Anisur Rahman is an Assistant Professor specializing in Computer Networks and Cybersecurity. His current research focuses on securing IoT devices and network protocols.",
                "short_bio": "Specialist in network security and IoT.",
                "education": ["Ph.D. in Computer Networks, ETH Zurich", "M.Sc. in Computer Science, University of Dhaka", "B.Sc. in Computer Science, University of Dhaka"],
                "courses": ["CSE 321: Computer Networks", "CSE 322: Network Security", "CSE 323: Internet of Things"],
                "research_interests": ["Network Security", "IoT Security", "Wireless Networks", "Blockchain"]
            },
            'sadia@cse.du.ac.bd': {
                "designation": FacultyDesignation.LECTURER,
                "department": "Computer Science and Engineering",
                "expertise": ["Human-Computer Interaction", "User Experience", "Mobile Interfaces"],
                "office": "Room 304, CSE Building",
                "image": "/assets/images/faculty/default.jpg",
                "website": "https://example.com/sadia",
                "publications": 5,
                "experience": 3,
                "is_chairman": False,
                "bio": "Dr. Sadia Sharmin is a Lecturer with expertise in Human-Computer Interaction and User Experience Design. She is passionate about creating accessible and intuitive interfaces.",
                "short_bio": "Passionate about UX design and accessibility.",
                "education": ["M.Sc. in Human-Computer Interaction, University of Washington", "B.Sc. in Computer Science, University of Dhaka"],
                "courses": ["CSE 341: Human-Computer Interaction", "CSE 342: User Interface Design", "CSE 343: Mobile Application Development"],
                "research_interests": ["Accessibility", "Mobile UX", "Interaction Design", "Usability Testing"]
            },
            'shariful@cse.du.ac.bd': {
                "designation": FacultyDesignation.PROFESSOR,
                "department": "Computer Science and Engineering",
                "expertise": ["Distributed Systems", "Cloud Computing", "Big Data"],
                "office": "Room 305, CSE Building",
                "image": "/assets/images/faculty/default.jpg",
                "website": "https://example.com/shariful",
                "publications": 38,
                "experience": 12,
                "is_chairman": False,
                "bio": "Dr. Md. Shariful Islam is a Professor specializing in Distributed Systems and Cloud Computing. He has contributed significantly to the field of Big Data processing frameworks.",
                "short_bio": "Expert in distributed systems and cloud computing.",
                "education": ["Ph.D. in Computer Science, University of Toronto", "M.Sc. in Computer Science, University of Dhaka", "B.Sc. in Computer Science, University of Dhaka"],
                "courses": ["CSE 411: Distributed Systems", "CSE 412: Cloud Computing", "CSE 413: Big Data Analytics"],
                "research_interests": ["Distributed Algorithms", "Cloud Security", "Big Data Processing", "Edge Computing"]
            }
        }
        
        # Create faculty records for each user
        for user in users:
            # Check if faculty record already exists
            existing_faculty = db.query(Faculty).filter(Faculty.id == user.id).first()
            if existing_faculty:
                print(f"Faculty record already exists for {user.name}")
                continue
            
            # Get faculty data for this user
            data = faculty_data.get(user.email)
            if not data:
                print(f"No faculty data defined for {user.name} ({user.email})")
                # Create default faculty record
                data = {
                    "designation": FacultyDesignation.LECTURER,
                    "department": "Computer Science and Engineering",
                    "expertise": ["Computer Science"],
                    "office": "CSE Building",
                    "image": "/assets/images/faculty/default.jpg",
                    "website": "",
                    "publications": 0,
                    "experience": 1,
                    "is_chairman": False,
                    "bio": f"{user.name} is a faculty member at the Department of Computer Science and Engineering, University of Dhaka.",
                    "short_bio": "Faculty member at CSE, DU",
                    "education": ["B.Sc. in Computer Science, University of Dhaka"],
                    "courses": [],
                    "research_interests": ["Computer Science"]
                }
            
            # Create faculty record
            faculty = Faculty(
                id=user.id,
                designation=data["designation"],
                department=data["department"],
                expertise=data["expertise"],
                office=data.get("office"),
                image=data.get("image"),
                website=data.get("website"),
                publications=data.get("publications", 0),
                experience=data.get("experience", 0),
                rating=4.5,  # Default rating
                is_chairman=data.get("is_chairman", False),
                bio=data.get("bio"),
                short_bio=data.get("short_bio"),
                education=data.get("education", []),
                courses=data.get("courses", []),
                research_interests=data.get("research_interests", []),
                recent_publications=[],  # Empty list for now
                awards=[],  # Empty list for now
                office_hours="Monday-Thursday: 10:00 AM - 12:00 PM"  # Default office hours
            )
            db.add(faculty)
            print(f"Created faculty record for {user.name}")
        
        db.commit()
        print("Faculty records created successfully")
            
    except Exception as e:
        print(f"Error creating faculty records: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_faculty_records()
