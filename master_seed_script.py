#!/usr/bin/env python3
"""
Master Seed Script for CSEDU Website Database
This script combines all individual seed scripts into one comprehensive script.
Run this script to populate the entire database with sample data.
"""

import os
import sys
import json
import traceback
import psycopg2
from datetime import datetime, time
from dotenv import load_dotenv
import bcrypt

# Load environment variables
load_dotenv()

# Database connection parameters - use environment variables with fallbacks
DB_HOST = os.environ.get("DATABASE_HOSTNAME", "localhost")
DB_PORT = os.environ.get("DATABASE_PORT", "5432")
DB_NAME = os.environ.get("DATABASE_NAME", "csedu")
DB_USER = os.environ.get("DATABASE_USERNAME", "postgres")
DB_PASSWORD = os.environ.get("DATABASE_PASSWORD", "password")  # Default password for development

print(f"Connecting to database {DB_NAME} at {DB_HOST}:{DB_PORT} as {DB_USER}")

# Connect to the database
try:
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    conn.autocommit = False
    cursor = conn.cursor()
    print("Database connection established successfully.")
except Exception as e:
    print(f"Error connecting to the database: {e}")
    sys.exit(1)

# Utility functions
def hash_password(password):
    """Hash a password for storing."""
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

def check_table_exists(table_name):
    """Check if a table exists in the database."""
    cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name = %s
        );
    """, (table_name,))
    return cursor.fetchone()[0]

def get_all_tables():
    """Get all tables in the database."""
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        ORDER BY table_name;
    """)
    return [row[0] for row in cursor.fetchall()]

def clear_table(table_name, cascade=False):
    """Clear all data from a table."""
    try:
        if cascade:
            cursor.execute(f"TRUNCATE TABLE {table_name} CASCADE")
        else:
            cursor.execute(f"DELETE FROM {table_name}")
        print(f"Cleared table: {table_name}")
    except Exception as e:
        print(f"Error clearing table {table_name}: {str(e)}")

def seed_roles_and_permissions():
    """Seed roles and permissions data."""
    print("\nSeeding roles and permissions...")
    
    # Tables are already cleared in main function
    
    # Define roles
    roles = [
        {"name": "ADMIN"},
        {"name": "FACULTY"},
        {"name": "STUDENT"},
        {"name": "STAFF"}
    ]
    
    # Insert roles
    role_ids = {}
    for role in roles:
        cursor.execute(
            "INSERT INTO roles (name) VALUES (%s) RETURNING id",
            (role["name"],)
        )
        role_id = cursor.fetchone()[0]
        role_ids[role["name"]] = role_id
        print(f"Added role: {role['name']} with ID: {role_id}")
    
    # Define permissions by category
    permissions = [
        {"name": "view_faculty", "category": "faculty"},
        {"name": "manage_faculty", "category": "faculty"},
        {"name": "view_courses", "category": "courses"},
        {"name": "manage_courses", "category": "courses"},
        {"name": "view_events", "category": "events"},
        {"name": "manage_events", "category": "events"},
        {"name": "view_projects", "category": "projects"},
        {"name": "manage_projects", "category": "projects"},
        {"name": "view_equipment", "category": "equipment"},
        {"name": "book_equipment", "category": "equipment"},
        {"name": "manage_equipment", "category": "equipment"},
        {"name": "view_labs", "category": "labs"},
        {"name": "book_labs", "category": "labs"},
        {"name": "manage_labs", "category": "labs"},
        {"name": "view_announcements", "category": "announcements"},
        {"name": "manage_announcements", "category": "announcements"},
        {"name": "view_users", "category": "users"},
        {"name": "manage_users", "category": "users"}
    ]
    
    # Insert permissions
    permission_ids = {}
    for permission in permissions:
        cursor.execute(
            "INSERT INTO permissions (name, category) VALUES (%s, %s) RETURNING id",
            (permission["name"], permission["category"])
        )
        permission_id = cursor.fetchone()[0]
        permission_ids[permission["name"]] = permission_id
    
    # Define role-permission mappings
    role_permissions = [
        # Admin has all permissions
        *[(role_ids["ADMIN"], permission_ids[p["name"]]) for p in permissions],
        
        # Faculty permissions
        (role_ids["FACULTY"], permission_ids["view_faculty"]),
        (role_ids["FACULTY"], permission_ids["view_courses"]),
        (role_ids["FACULTY"], permission_ids["manage_courses"]),
        (role_ids["FACULTY"], permission_ids["view_events"]),
        (role_ids["FACULTY"], permission_ids["view_projects"]),
        (role_ids["FACULTY"], permission_ids["manage_projects"]),
        (role_ids["FACULTY"], permission_ids["view_equipment"]),
        (role_ids["FACULTY"], permission_ids["book_equipment"]),
        (role_ids["FACULTY"], permission_ids["view_labs"]),
        (role_ids["FACULTY"], permission_ids["book_labs"]),
        (role_ids["FACULTY"], permission_ids["view_announcements"]),
        
        # Student permissions
        (role_ids["STUDENT"], permission_ids["view_faculty"]),
        (role_ids["STUDENT"], permission_ids["view_courses"]),
        (role_ids["STUDENT"], permission_ids["view_events"]),
        (role_ids["STUDENT"], permission_ids["view_projects"]),
        (role_ids["STUDENT"], permission_ids["view_equipment"]),
        (role_ids["STUDENT"], permission_ids["book_equipment"]),
        (role_ids["STUDENT"], permission_ids["view_labs"]),
        (role_ids["STUDENT"], permission_ids["view_announcements"]),
        
        # Staff permissions
        (role_ids["STAFF"], permission_ids["view_faculty"]),
        (role_ids["STAFF"], permission_ids["view_courses"]),
        (role_ids["STAFF"], permission_ids["view_events"]),
        (role_ids["STAFF"], permission_ids["manage_events"]),
        (role_ids["STAFF"], permission_ids["view_equipment"]),
        (role_ids["STAFF"], permission_ids["manage_equipment"]),
        (role_ids["STAFF"], permission_ids["view_labs"]),
        (role_ids["STAFF"], permission_ids["manage_labs"]),
        (role_ids["STAFF"], permission_ids["view_announcements"]),
        (role_ids["STAFF"], permission_ids["manage_announcements"])
    ]
    
    # Insert role-permission mappings
    for role_id, permission_id in role_permissions:
        cursor.execute(
            "INSERT INTO roles_permissions (role_id, permission_id) VALUES (%s, %s)",
            (role_id, permission_id)
        )
    
    conn.commit()
    print("Roles and permissions seeded successfully.")
    return role_ids

def seed_users(role_ids):
    """Seed user data."""
    print("\nSeeding users...")
    
    # Users table already cleared in main function
    
    # Create admin user
    admin_password = hash_password("admin123")
    cursor.execute(
        """INSERT INTO users 
        (name, email, password, role_id, contact, created_at) 
        VALUES (%s, %s, %s, %s, %s, %s) RETURNING id""",
        ("Admin User", "admin@csedu.edu", admin_password, role_ids["ADMIN"], "+8801700000000", datetime.utcnow())
    )
    admin_id = cursor.fetchone()[0]
    print(f"Created admin user with ID: {admin_id}")
    
    # Create faculty users
    faculty_data = [
        {
            "name": "Dr. Md. Shabbir Ahmed",
            "email": "shabbir@csedu.edu",
            "password": "faculty123",
            "contact": "+8801712345601"
        },
        {
            "name": "Dr. Muhammad Masroor Ali",
            "email": "masroor@csedu.edu",
            "password": "faculty123",
            "contact": "+8801712345602"
        },
        {
            "name": "Dr. Md. Haider Ali",
            "email": "haider@csedu.edu",
            "password": "faculty123",
            "contact": "+8801712345603"
        },
        {
            "name": "Dr. Kazi Muheymin-Us-Sakib",
            "email": "sakib@csedu.edu",
            "password": "faculty123",
            "contact": "+8801712345604"
        },
        {
            "name": "Dr. Md. Abdur Razzaque",
            "email": "razzaque@csedu.edu",
            "password": "faculty123",
            "contact": "+8801712345605"
        },
        {
            "name": "Dr. Md. Mustafizur Rahman",
            "email": "mustafiz@csedu.edu",
            "password": "faculty123",
            "contact": "+8801712345606"
        },
        {
            "name": "Dr. Sarker Tanveer Ahmed Rumee",
            "email": "rumee@csedu.edu",
            "password": "faculty123",
            "contact": "+8801712345607"
        },
        {
            "name": "Dr. Md. Shariful Islam",
            "email": "shariful@csedu.edu",
            "password": "faculty123",
            "contact": "+8801712345608"
        },
        {
            "name": "Dr. Mosaddek Hossain Kamal Tushar",
            "email": "tushar@csedu.edu",
            "password": "faculty123",
            "contact": "+8801712345609"
        },
        {
            "name": "Dr. Md. Mamun-Or-Rashid",
            "email": "mamun@csedu.edu",
            "password": "faculty123",
            "contact": "+8801712345610"
        }
    ]
    
    faculty_ids = {}
    for faculty in faculty_data:
        hashed_password = hash_password(faculty["password"])
        cursor.execute(
            """INSERT INTO users 
            (name, email, password, role_id, contact, created_at) 
            VALUES (%s, %s, %s, %s, %s, %s) RETURNING id""",
            (faculty["name"], faculty["email"], hashed_password, role_ids["FACULTY"], 
             faculty["contact"], datetime.utcnow())
        )
        faculty_id = cursor.fetchone()[0]
        faculty_ids[faculty["name"]] = faculty_id
        print(f"Created faculty user: {faculty['name']} with ID: {faculty_id}")
    
    # Create student users
    student_data = [
        {"name": "Student One", "email": "student1@csedu.edu", "password": "student123", "contact": "+8801812345601"},
        {"name": "Student Two", "email": "student2@csedu.edu", "password": "student123", "contact": "+8801812345602"},
        {"name": "Student Three", "email": "student3@csedu.edu", "password": "student123", "contact": "+8801812345603"},
        {"name": "Student Four", "email": "student4@csedu.edu", "password": "student123", "contact": "+8801812345604"},
        {"name": "Student Five", "email": "student5@csedu.edu", "password": "student123", "contact": "+8801812345605"}
    ]
    
    student_ids = {}
    for student in student_data:
        hashed_password = hash_password(student["password"])
        cursor.execute(
            """INSERT INTO users 
            (name, email, password, role_id, contact, created_at) 
            VALUES (%s, %s, %s, %s, %s, %s) RETURNING id""",
            (student["name"], student["email"], hashed_password, role_ids["STUDENT"], 
             student["contact"], datetime.utcnow())
        )
        student_id = cursor.fetchone()[0]
        student_ids[student["name"]] = student_id
        print(f"Created student user: {student['name']} with ID: {student_id}")
    
    # Create staff users
    staff_data = [
        {"name": "Staff One", "email": "staff1@csedu.edu", "password": "staff123", "contact": "+8801912345601"},
        {"name": "Staff Two", "email": "staff2@csedu.edu", "password": "staff123", "contact": "+8801912345602"}
    ]
    
    staff_ids = {}
    for staff in staff_data:
        hashed_password = hash_password(staff["password"])
        cursor.execute(
            """INSERT INTO users 
            (name, email, password, role_id, contact, created_at) 
            VALUES (%s, %s, %s, %s, %s, %s) RETURNING id""",
            (staff["name"], staff["email"], hashed_password, role_ids["STAFF"], 
             staff["contact"], datetime.utcnow())
        )
        staff_id = cursor.fetchone()[0]
        staff_ids[staff["name"]] = staff_id
        print(f"Created staff user: {staff['name']} with ID: {staff_id}")
    
    conn.commit()
    print("Users seeded successfully.")
    return {"admin": admin_id, "faculty": faculty_ids, "students": student_ids, "staff": staff_ids}

def seed_faculty(faculty_ids):
    """Seed faculty data."""
    print("\nSeeding faculty profiles...")
    
    # Faculty table already cleared in main function
    
    faculty_profiles = [
        {
            "name": "Dr. Md. Shabbir Ahmed",
            "designation": "PROFESSOR",
            "department": "Computer Science and Engineering",
            "expertise": ["Artificial Intelligence", "Machine Learning", "Computer Vision"],
            "office": "Room 401",
            "image": "/assets/teacher/shabbir_ahmed.jpg",
            "website": "https://www.cse.du.ac.bd/faculty/shabbir",
            "publications": 45,
            "experience": 18,
            "rating": 4.8,
            "is_chairman": True,
            "bio": "Dr. Md. Shabbir Ahmed is a Professor and current Chairman of the Department of Computer Science and Engineering at the University of Dhaka. He received his Ph.D. in Computer Science from the University of Tokyo, Japan. His research interests include artificial intelligence, machine learning, and computer vision.",
            "short_bio": "Professor and Chairman with expertise in AI and Machine Learning.",
            "education": json.dumps([
                {"degree": "Ph.D. in Computer Science", "institution": "University of Tokyo", "year": 2005},
                {"degree": "M.Sc. in Computer Science", "institution": "University of Dhaka", "year": 2000},
                {"degree": "B.Sc. in Computer Science", "institution": "University of Dhaka", "year": 1998}
            ]),
            "courses": json.dumps(["CSE401: Artificial Intelligence", "CSE402: Machine Learning", "CSE601: Advanced AI"]),
            "research_interests": json.dumps(["Deep Learning", "Computer Vision", "Natural Language Processing"]),
            "recent_publications": json.dumps([
                {"title": "A Novel Approach to Deep Learning for Image Recognition", "journal": "IEEE Transactions on Pattern Analysis and Machine Intelligence", "year": 2023},
                {"title": "Efficient Neural Network Architectures for Edge Devices", "journal": "Journal of Machine Learning Research", "year": 2022},
                {"title": "Transformer Models for Low-Resource Languages", "journal": "ACL Conference", "year": 2021}
            ]),
            "awards": json.dumps([
                {"title": "Best Paper Award", "organization": "IEEE Conference on Computer Vision", "year": 2022},
                {"title": "Excellence in Teaching", "organization": "University of Dhaka", "year": 2020}
            ]),
            "office_hours": "Sunday, Tuesday: 10:00 AM - 12:00 PM"
        },
        {
            "name": "Dr. Muhammad Masroor Ali",
            "designation": "PROFESSOR",
            "department": "Computer Science and Engineering",
            "expertise": ["Database Systems", "Data Mining", "Big Data Analytics"],
            "office": "Room 402",
            "image": "/assets/teacher/masroor_ali.jpg",
            "website": "https://www.cse.du.ac.bd/faculty/masroor",
            "publications": 38,
            "experience": 16,
            "rating": 4.7,
            "is_chairman": False,
            "bio": "Dr. Muhammad Masroor Ali is a Professor at the Department of Computer Science and Engineering, University of Dhaka. He received his Ph.D. in Computer Science from the National University of Singapore. His research focuses on database systems, data mining, and big data analytics.",
            "short_bio": "Professor with expertise in Database Systems and Data Mining.",
            "education": json.dumps([
                {"degree": "Ph.D. in Computer Science", "institution": "National University of Singapore", "year": 2007},
                {"degree": "M.Sc. in Computer Science", "institution": "University of Dhaka", "year": 2002},
                {"degree": "B.Sc. in Computer Science", "institution": "University of Dhaka", "year": 2000}
            ]),
            "courses": json.dumps(["CSE303: Database Systems", "CSE304: Database Lab", "CSE603: Advanced Database Systems"]),
            "research_interests": json.dumps(["Database Systems", "Data Mining", "Big Data Analytics"]),
            "recent_publications": json.dumps([
                {"title": "Efficient Query Processing in Distributed Databases", "journal": "ACM Transactions on Database Systems", "year": 2023},
                {"title": "A Novel Approach to Data Mining in Healthcare", "journal": "Journal of Biomedical Informatics", "year": 2022}
            ]),
            "awards": json.dumps([
                {"title": "Research Excellence Award", "organization": "University of Dhaka", "year": 2021},
                {"title": "Best Teacher Award", "organization": "CSE Department", "year": 2019}
            ]),
            "office_hours": "Monday, Wednesday: 2:00 PM - 4:00 PM"
        }
    ]
    
    # Add more faculty profiles with minimal data to avoid making the file too large
    additional_faculty = [
        {
            "name": "Dr. Md. Haider Ali",
            "designation": "PROFESSOR",
            "department": "Computer Science and Engineering",
            "expertise": ["Computer Networks", "Wireless Communication", "IoT"],
            "publications": 32,
            "experience": 15,
            "rating": 4.6
        },
        {
            "name": "Dr. Kazi Muheymin-Us-Sakib",
            "designation": "PROFESSOR",
            "department": "Computer Science and Engineering",
            "expertise": ["Software Engineering", "Software Testing", "Software Quality Assurance"],
            "publications": 40,
            "experience": 17,
            "rating": 4.7
        },
        {
            "name": "Dr. Md. Abdur Razzaque",
            "designation": "PROFESSOR",
            "department": "Computer Science and Engineering",
            "expertise": ["Wireless Sensor Networks", "Network Security", "Cyber Security"],
            "publications": 35,
            "experience": 14,
            "rating": 4.5
        },
        {
            "name": "Dr. Md. Mustafizur Rahman",
            "designation": "ASSOCIATE_PROFESSOR",
            "department": "Computer Science and Engineering",
            "expertise": ["Natural Language Processing", "Text Mining", "Information Retrieval"],
            "publications": 25,
            "experience": 10,
            "rating": 4.4
        },
        {
            "name": "Dr. Sarker Tanveer Ahmed Rumee",
            "designation": "ASSOCIATE_PROFESSOR",
            "department": "Computer Science and Engineering",
            "expertise": ["Algorithms", "Computational Complexity", "Graph Theory"],
            "publications": 22,
            "experience": 8,
            "rating": 4.3
        },
        {
            "name": "Dr. Md. Shariful Islam",
            "designation": "ASSISTANT_PROFESSOR",
            "department": "Computer Science and Engineering",
            "expertise": ["Human-Computer Interaction", "User Experience", "Mobile Computing"],
            "publications": 18,
            "experience": 6,
            "rating": 4.2
        },
        {
            "name": "Dr. Mosaddek Hossain Kamal Tushar",
            "designation": "ASSISTANT_PROFESSOR",
            "department": "Computer Science and Engineering",
            "expertise": ["Computer Graphics", "Visualization", "Augmented Reality"],
            "publications": 15,
            "experience": 5,
            "rating": 4.1
        },
        {
            "name": "Dr. Md. Mamun-Or-Rashid",
            "designation": "LECTURER",
            "department": "Computer Science and Engineering",
            "expertise": ["Distributed Systems", "Cloud Computing", "Edge Computing"],
            "publications": 10,
            "experience": 3,
            "rating": 4.0
        }
    ]
    
    # Add additional faculty to the profiles list
    faculty_profiles.extend(additional_faculty)
    
    # Insert faculty profiles
    for profile in faculty_profiles:
        faculty_id = faculty_ids.get(profile["name"])
        if faculty_id:
            # Prepare fields with defaults for missing values
            office = profile.get("office", "TBA")
            image = profile.get("image", None)
            website = profile.get("website", None)
            publications = profile.get("publications", 0)
            experience = profile.get("experience", 0)
            rating = profile.get("rating", 4.0)
            is_chairman = profile.get("is_chairman", False)
            bio = profile.get("bio", None)
            short_bio = profile.get("short_bio", None)
            education = profile.get("education", json.dumps([]))
            courses = profile.get("courses", json.dumps([]))
            research_interests = profile.get("research_interests", json.dumps([]))
            recent_publications = profile.get("recent_publications", json.dumps([]))
            awards = profile.get("awards", json.dumps([]))
            office_hours = profile.get("office_hours", None)
            
            # Insert faculty profile
            cursor.execute(
                """INSERT INTO faculty 
                (id, designation, department, expertise, office, image, website, 
                publications, experience, rating, is_chairman, bio, short_bio, 
                education, courses, research_interests, recent_publications, 
                awards, office_hours, created_at, updated_at) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (faculty_id, profile["designation"], profile["department"], 
                 json.dumps(profile["expertise"]), office, image, website, 
                 publications, experience, rating, is_chairman, bio, short_bio, 
                 education, courses, research_interests, recent_publications, 
                 awards, office_hours, datetime.utcnow(), datetime.utcnow())
            )
            print(f"Created faculty profile for: {profile['name']}")
    
    conn.commit()
    print("Faculty profiles seeded successfully.")
    return faculty_profiles

def seed_courses():
    """Seed courses data."""
    print("\nSeeding courses...")
    
    # Course-related tables already cleared in main function
    
    # Seed programs
    programs = [
        {
            "title": "Bachelor of Science in Computer Science and Engineering", 
            "short_description": "B.Sc. in CSE", 
            "description": "A four-year undergraduate program focusing on computer science and engineering fundamentals.",
            "level": "Undergraduate",
            "duration": "4 years",
            "total_students": 120,
            "total_courses": 40,
            "total_credits": 160,
            "specializations": json.dumps(["Software Engineering", "Artificial Intelligence", "Computer Networks"]),
            "learning_objectives": json.dumps(["Develop problem-solving skills", "Learn programming fundamentals", "Understand computer systems"]),
            "career_prospects": json.dumps(["Software Engineer", "System Analyst", "Database Administrator"])
        },
        {
            "title": "Master of Science in Computer Science and Engineering", 
            "short_description": "M.Sc. in CSE", 
            "description": "A two-year graduate program offering advanced studies in computer science and engineering.",
            "level": "Graduate",
            "duration": "2 years",
            "total_students": 40,
            "total_courses": 12,
            "total_credits": 36,
            "specializations": json.dumps(["Machine Learning", "Data Science", "Cyber Security"]),
            "learning_objectives": json.dumps(["Conduct independent research", "Develop specialized expertise", "Apply advanced concepts"]),
            "career_prospects": json.dumps(["Research Scientist", "Data Scientist", "Security Specialist"])
        },
        {
            "title": "Doctor of Philosophy in Computer Science and Engineering", 
            "short_description": "Ph.D. in CSE", 
            "description": "A research-focused doctoral program in computer science and engineering.",
            "level": "Doctoral",
            "duration": "3-5 years",
            "total_students": 15,
            "total_courses": 6,
            "total_credits": 18,
            "specializations": json.dumps(["Advanced AI", "Theoretical Computer Science", "Distributed Systems"]),
            "learning_objectives": json.dumps(["Contribute original research", "Develop academic expertise", "Advance the field of computer science"]),
            "career_prospects": json.dumps(["Professor", "Research Lead", "Chief Scientist"])
        }
    ]
    
    program_ids = {}
    for program in programs:
        cursor.execute(
            """INSERT INTO programs 
            (title, short_description, description, level, duration, total_students, 
             total_courses, total_credits, specializations, learning_objectives, 
             career_prospects, created_at, updated_at) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id""",
            (program["title"], program["short_description"], program["description"],
             program["level"], program["duration"], program["total_students"],
             program["total_courses"], program["total_credits"], program["specializations"],
             program["learning_objectives"], program["career_prospects"],
             datetime.utcnow(), datetime.utcnow())
        )
        program_id = cursor.fetchone()[0]
        program_ids[program["short_description"]] = program_id
        print(f"Created program: {program['title']} with ID: {program_id}")
    
    # Seed courses
    courses = [
        {
            "code": "CSE101",
            "title": "Introduction to Computer Science",
            "credits": 3,
            "program": "B.Sc. in CSE",
            "semester": 1,
            "year": 1,
            "description": "An introductory course to the field of computer science and programming.",
            "duration": "4 months",
            "difficulty": "Beginner",
            "rating": 4.5,
            "enrolled_students": 120,
            "specialization": "Core",
            "prerequisites": json.dumps([]),
        },
        {
            "code": "CSE102",
            "title": "Programming Language I",
            "credits": 3,
            "program": "B.Sc. in CSE",
            "semester": 1,
            "year": 1,
            "description": "Introduction to programming using a high-level language (C/C++).",
            "duration": "4 months",
            "difficulty": "Beginner",
            "rating": 4.7,
            "enrolled_students": 125,
            "specialization": "Core",
            "prerequisites": json.dumps([])
        },
        {
            "code": "CSE201",
            "title": "Data Structures",
            "credits": 3,
            "program": "B.Sc. in CSE",
            "semester": 2,
            "year": 1,
            "description": "Study of fundamental data structures and their applications.",
            "duration": "4 months",
            "difficulty": "Intermediate",
            "rating": 4.5,
            "enrolled_students": 115,
            "specialization": "Core",
            "prerequisites": json.dumps(["CSE102"])
        },
        {
            "code": "CSE203",
            "title": "Object-Oriented Programming",
            "credits": 3,
            "program": "B.Sc. in CSE",
            "semester": 2,
            "year": 1,
            "description": "Introduction to object-oriented programming concepts using Java.",
            "duration": "4 months",
            "difficulty": "Intermediate",
            "rating": 4.3,
            "enrolled_students": 110,
            "specialization": "Core",
            "prerequisites": json.dumps(["CSE102"])
        },
        {
            "code": "CSE202",
            "title": "Algorithms",
            "credits": 3,
            "program": "B.Sc. in CSE",
            "semester": 2,
            "year": 1,
            "description": "Design and analysis of algorithms.",
            "duration": "4 months",
            "difficulty": "Intermediate",
            "rating": 4.3,
            "enrolled_students": 110,
            "specialization": "Core",
            "prerequisites": json.dumps(["CSE201"])
        },
        {
            "code": "CSE301",
            "title": "Database Systems",
            "credits": 3,
            "program": "B.Sc. in CSE",
            "semester": 3,
            "year": 2,
            "description": "Introduction to database management systems.",
            "duration": "4 months",
            "difficulty": "Intermediate",
            "rating": 4.6,
            "enrolled_students": 105,
            "specialization": "Core",
            "prerequisites": json.dumps(["CSE201"])
        },
        {
            "code": "CSE401",
            "title": "Artificial Intelligence",
            "credits": 3,
            "program": "B.Sc. in CSE",
            "semester": 4,
            "year": 2,
            "description": "Introduction to artificial intelligence concepts and techniques.",
            "duration": "4 months",
            "difficulty": "Advanced",
            "rating": 4.8,
            "enrolled_students": 95,
            "specialization": "AI",
            "prerequisites": json.dumps(["CSE202"])
        },
        {
            "code": "CSE402",
            "title": "Computer Networks",
            "credits": 3,
            "program": "B.Sc. in CSE",
            "semester": 4,
            "year": 2,
            "description": "Fundamentals of computer networking.",
            "duration": "4 months",
            "difficulty": "Intermediate",
            "rating": 4.5,
            "enrolled_students": 98,
            "specialization": "Networking",
            "prerequisites": json.dumps(["CSE302"])
        },
        {
            "code": "CSE501",
            "title": "Advanced Database Systems",
            "credits": 3,
            "program": "M.Sc. in CSE",
            "semester": 1,
            "year": 1,
            "description": "Advanced concepts in database management systems.",
            "duration": "4 months",
            "difficulty": "Advanced",
            "rating": 4.7,
            "enrolled_students": 30,
            "specialization": "Database",
            "prerequisites": json.dumps(["CSE301"])
        },
        {
            "code": "CSE502",
            "title": "Advanced Algorithms",
            "credits": 3,
            "program": "M.Sc. in CSE",
            "semester": 1,
            "year": 1,
            "description": "Advanced algorithmic techniques and analysis.",
            "duration": "4 months",
            "difficulty": "Advanced",
            "rating": 4.6,
            "enrolled_students": 28,
            "specialization": "Theory",
            "prerequisites": json.dumps(["CSE202"])
        },
        {
            "code": "CSE601",
            "title": "Advanced AI",
            "credits": 3,
            "program": "Ph.D. in CSE",
            "semester": 1,
            "year": 1,
            "description": "Advanced topics in artificial intelligence research.",
            "duration": "6 months",
            "difficulty": "Expert",
            "rating": 4.9,
            "enrolled_students": 10,
            "specialization": "AI",
            "prerequisites": json.dumps(["CSE401"])
        },
        {
            "code": "CSE602",
            "title": "Research Methodology",
            "credits": 3,
            "program": "Ph.D. in CSE",
            "semester": 1,
            "year": 1,
            "description": "Research methods and techniques for computer science.",
            "duration": "6 months",
            "difficulty": "Expert",
            "rating": 4.8,
            "enrolled_students": 12,
            "specialization": "Research",
            "prerequisites": json.dumps([])
        }
    ]
    
    course_ids = {}
    for course in courses:
        program_id = program_ids.get(course["program"])
        if program_id:
            # Prepare fields with defaults for missing values
            syllabus = course.get("syllabus", None)
            objectives = course.get("objectives", None)
            references = course.get("references", None)
            
            # Set default values for optional fields
            duration = course.get("duration", "4 months")
            difficulty = course.get("difficulty", "Intermediate")
            rating = course.get("rating", 4.0)
            enrolled_students = course.get("enrolled_students", 50)
            prerequisites = course.get("prerequisites", json.dumps([]))
            specialization = course.get("specialization", "General")
            year = course.get("year", 1)
            
            cursor.execute(
                """INSERT INTO courses 
                (code, title, credits, program_id, semester, year, description, duration, 
                 difficulty, rating, enrolled_students, prerequisites, specialization, 
                 created_at, updated_at) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id""",
                (course["code"], course["title"], course["credits"], program_id, 
                 course["semester"], year, course["description"], duration, difficulty, 
                 rating, enrolled_students, prerequisites, specialization,
                 datetime.utcnow(), datetime.utcnow())
            )
            course_id = cursor.fetchone()[0]
            course_ids[course["code"]] = course_id
            print(f"Created course: {course['code']} - {course['title']} with ID: {course_id}")
    
    # Add course prerequisites
    for course in courses:
        if "prerequisites" in course:
            for prereq_code in course["prerequisites"]:
                if prereq_code in course_ids and course["code"] in course_ids:
                    cursor.execute(
                        """INSERT INTO course_prerequisites 
                        (course_id, prerequisite_id, created_at, updated_at) 
                        VALUES (%s, %s, %s, %s)""",
                        (course_ids[course["code"]], course_ids[prereq_code], 
                         datetime.utcnow(), datetime.utcnow())
                    )
                    print(f"Added prerequisite: {prereq_code} for course: {course['code']}")
    
    conn.commit()
    print("Courses seeded successfully.")
    return {"programs": program_ids, "courses": course_ids}

def seed_projects():
    """Seed projects data."""
    print("\nSeeding projects...")
    
    # Check if the projects table exists
    if not check_table_exists("projects"):
        print("Projects table does not exist. Creating table...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id SERIAL PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            summary VARCHAR(255),
            abstract TEXT,
            supervisor_id INTEGER,
            year INTEGER,
            category VARCHAR(100),
            type VARCHAR(50) NOT NULL,
            tags JSONB,
            team JSONB,
            course VARCHAR(100),
            team_size INTEGER,
            completion_date TIMESTAMP,
            technologies JSONB,
            key_features JSONB,
            achievements JSONB,
            demo_link VARCHAR(255),
            github_link VARCHAR(255),
            paper_link VARCHAR(255),
            contact_email VARCHAR(255),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        print("Projects table created.")
    
    # Check if junction tables exist and create them if needed
    if not check_table_exists("project_faculty"):
        print("Project faculty junction table does not exist. Creating table...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS project_faculty (
            project_id INTEGER REFERENCES projects(id),
            faculty_id INTEGER,
            PRIMARY KEY (project_id, faculty_id)
        );
        """)
        print("Project faculty junction table created.")
    
    if not check_table_exists("project_students"):
        print("Project students junction table does not exist. Creating table...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS project_students (
            project_id INTEGER REFERENCES projects(id),
            student_id INTEGER,
            PRIMARY KEY (project_id, student_id)
        );
        """)
        print("Project students junction table created.")
    
    # Seed projects
    projects = [
        {
            "title": "Smart Traffic Management System using Computer Vision",
            "summary": "AI-powered traffic monitoring and optimization system",
            "type": "faculty",
            "category": "Computer Vision",
            "year": 2023,
            "abstract": "This project aims to develop an intelligent traffic management system using computer vision techniques to monitor and optimize traffic flow in urban areas. The system uses deep learning models to detect and track vehicles, estimate traffic density, and predict congestion patterns.",
            "supervisor_id": None,  # Will be set based on faculty data
            "tags": json.dumps(["AI", "Computer Vision", "Smart City", "Traffic Management"]),
            "team": json.dumps([{"name": "Dr. Md. Shabbir Ahmed", "role": "Principal Investigator"}, {"name": "Dr. Md. Mustafizur Rahman", "role": "Co-Investigator"}, {"name": "Research Assistant 1", "role": "Developer"}, {"name": "Research Assistant 2", "role": "Data Scientist"}]),
            "team_size": 4,
            "course": None,
            "completion_date": "2023-12-15",
            "technologies": json.dumps(["Computer Vision", "Deep Learning", "TensorFlow", "OpenCV", "YOLO", "Python"]),
            "key_features": json.dumps(["Real-time vehicle detection", "Traffic density estimation", "Congestion prediction", "Signal timing optimization"]),
            "achievements": json.dumps(["Best Research Project Award 2023", "Published in IEEE Transactions on Intelligent Transportation Systems"]),
            "github_link": "https://github.com/csedu/smart-traffic",
            "demo_link": "https://demo.csedu.edu/smart-traffic",
            "paper_link": "https://doi.org/10.1109/TITS.2023.12345",
            "contact_email": "shabbir@cse.du.ac.bd"
        },
        {
            "title": "Distributed Database Management System for Big Data",
            "summary": "Scalable and efficient database system for handling massive datasets",
            "type": "faculty",
            "category": "Database Systems",
            "year": 2022,
            "abstract": "This project focuses on developing a distributed database management system optimized for big data applications. The system provides efficient data partitioning, replication, and query processing across multiple nodes.",
            "supervisor_id": None,  # Will be set based on faculty data
            "tags": json.dumps(["Databases", "Big Data", "Distributed Systems", "Data Management"]),
            "team": json.dumps([{"name": "Dr. Muhammad Masroor Ali", "role": "Principal Investigator"}, {"name": "Dr. Md. Abdur Razzaque", "role": "Co-Investigator"}, {"name": "Graduate Student 1", "role": "Developer"}, {"name": "Graduate Student 2", "role": "Researcher"}]),
            "team_size": 4,
            "course": None,
            "completion_date": None,
            "technologies": json.dumps(["Distributed Systems", "Big Data", "NoSQL", "Java", "Apache Hadoop", "Apache Spark"]),
            "key_features": json.dumps(["Horizontal scaling", "Data sharding", "Fault tolerance", "High throughput query processing"]),
            "achievements": json.dumps(["Research grant from National Science Foundation", "Demo presented at VLDB 2022"]),
            "github_link": "https://github.com/csedu/distributed-dbms",
            "demo_link": "https://demo.csedu.edu/distributed-dbms",
            "paper_link": "https://arxiv.org/abs/2022.12345",
            "contact_email": "masroor@cse.du.ac.bd"
        },
        {
            "title": "Mobile Application for Mental Health Support",
            "summary": "App providing mental wellness resources for university students",
            "type": "student",
            "category": "Mobile Development",
            "year": 2023,
            "abstract": "A mobile application designed to provide mental health support to university students. The app includes features such as mood tracking, guided meditation, anonymous peer support, and professional resources.",
            "supervisor_id": None,  # Will be set based on faculty data
            "tags": json.dumps(["Mobile App", "Mental Health", "Student Wellness", "React Native"]),
            "team": json.dumps([{"name": "Student One", "role": "Team Lead"}, {"name": "Student Two", "role": "Frontend Developer"}, {"name": "Student Three", "role": "Backend Developer"}]),
            "team_size": 3,
            "course": "CSE402",
            "completion_date": "2023-05-30",
            "technologies": json.dumps(["React Native", "Firebase", "Node.js", "Express", "MongoDB"]),
            "key_features": json.dumps(["Mood tracking", "Guided meditation", "Anonymous peer support", "Resource directory"]),
            "achievements": json.dumps(["Best Student Project 2023", "Featured in University Newsletter"]),
            "github_link": "https://github.com/csedu/mental-health-app",
            "demo_link": "https://demo.csedu.edu/mental-health-app",
            "paper_link": None,
            "contact_email": "student.one@cse.du.ac.bd"
        },
        {
            "title": "Blockchain-based Supply Chain Management System",
            "summary": "Transparent and secure tracking system using blockchain technology",
            "type": "faculty",
            "category": "Blockchain",
            "year": 2023,
            "abstract": "A blockchain-based system for transparent and secure supply chain management. The system enables tracking of products from origin to consumer, ensuring authenticity and reducing fraud.",
            "supervisor_id": None,  # Will be set based on faculty data
            "tags": json.dumps(["Blockchain", "Supply Chain", "Smart Contracts", "Traceability"]),
            "team": json.dumps([{"name": "Dr. Kazi Muheymin-Us-Sakib", "role": "Principal Investigator"}, {"name": "Dr. Md. Haider Ali", "role": "Co-Investigator"}, {"name": "Graduate Student 3", "role": "Blockchain Developer"}, {"name": "Graduate Student 4", "role": "UI/UX Designer"}]),
            "team_size": 4,
            "course": None,
            "completion_date": None,
            "technologies": json.dumps(["Blockchain", "Ethereum", "Smart Contracts", "Solidity", "Web3.js", "React"]),
            "key_features": json.dumps(["Product authentication", "Real-time tracking", "Immutable record keeping", "Stakeholder verification"]),
            "achievements": json.dumps(["Industry partnership with local manufacturers", "Selected for national innovation showcase"]),
            "github_link": "https://github.com/csedu/blockchain-supply-chain",
            "demo_link": "https://demo.csedu.edu/blockchain-supply-chain",
            "paper_link": "https://doi.org/10.1109/blockchain.2023.56789",
            "contact_email": "sakib@cse.du.ac.bd"
        },
        {
            "title": "Natural Language Processing for Bangla Text",
            "summary": "NLP tools and techniques for Bangla language processing",
            "type": "faculty",
            "category": "Natural Language Processing",
            "year": 2023,
            "abstract": "This research project focuses on developing natural language processing tools and techniques specifically for the Bangla language. The project includes tasks such as part-of-speech tagging, named entity recognition, sentiment analysis, and machine translation.",
            "supervisor_id": None,  # Will be set based on faculty data
            "tags": json.dumps(["NLP", "Bangla Language", "Text Processing", "Deep Learning"]),
            "team": json.dumps([{"name": "Dr. Md. Mustafizur Rahman", "role": "Principal Investigator"}, {"name": "Research Assistant 3", "role": "Researcher"}, {"name": "Research Assistant 4", "role": "Developer"}]),
            "team_size": 3,
            "course": None,
            "completion_date": None,
            "technologies": json.dumps(["NLP", "Deep Learning", "Transformers", "PyTorch", "Python"]),
            "key_features": json.dumps(["Bangla POS tagging", "Named entity recognition", "Sentiment analysis", "Machine translation"]),
            "achievements": json.dumps(["Published in ACL 2023", "Open-source toolkit with 500+ stars"]),
            "github_link": "https://github.com/csedu/bangla-nlp",
            "demo_link": "https://demo.csedu.edu/bangla-nlp",
            "paper_link": "https://aclanthology.org/2023.acl-long.123/",
            "contact_email": "mustafizur@cse.du.ac.bd"
        },
        {
            "title": "Augmented Reality Educational Platform",
            "summary": "AR platform for creating interactive educational content",
            "type": "student",
            "category": "Augmented Reality",
            "year": 2022,
            "abstract": "An educational platform that uses augmented reality to enhance learning experiences. The platform allows teachers to create interactive AR content for various subjects.",
            "supervisor_id": None,  # Will be set based on faculty data
            "tags": json.dumps(["AR", "Education", "Interactive Learning", "Unity"]),
            "team": json.dumps([{"name": "Student One", "role": "Team Lead"}, {"name": "Student Four", "role": "AR Developer"}]),
            "team_size": 2,
            "course": "CSE400",
            "completion_date": "2022-12-10",
            "technologies": json.dumps(["AR", "Unity", "C#", "ARCore", "ARKit"]),
            "key_features": json.dumps(["3D model visualization", "Interactive quizzes", "Subject-specific AR modules", "Teacher content creation tools"]),
            "achievements": json.dumps(["University Innovation Award 2022", "Pilot program in 3 local schools"]),
            "github_link": "https://github.com/csedu/ar-education",
            "demo_link": "https://demo.csedu.edu/ar-education",
            "paper_link": None,
            "contact_email": "student.one@cse.du.ac.bd"
        }
    ]
    
    project_ids = {}
    for project in projects:
        # Find a faculty member to be supervisor if not specified
        if project["supervisor_id"] is None:
            cursor.execute("SELECT id FROM faculty ORDER BY RANDOM() LIMIT 1")
            result = cursor.fetchone()
            if result:
                project["supervisor_id"] = result[0]
        
        # Set default completion date for ongoing projects
        if project.get("completion_date") is None:
            # Set to a future date for ongoing projects
            project["completion_date"] = "2026-12-31"
        
        cursor.execute(
            """INSERT INTO projects 
            (title, summary, abstract, supervisor_id, year, category, type, tags, team, course, team_size,
            completion_date, technologies, key_features, achievements, demo_link, github_link, paper_link,
            contact_email, created_at, updated_at) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id""",
            (project["title"], project["summary"], project["abstract"], project["supervisor_id"],
             project["year"], project["category"], project["type"], project["tags"], project["team"],
             project["course"], project["team_size"], project["completion_date"], project["technologies"],
             project["key_features"], project["achievements"], project["demo_link"], project["github_link"],
             project["paper_link"], project["contact_email"], datetime.utcnow(), datetime.utcnow())
        )
        project_id = cursor.fetchone()[0]
        project_ids[project["title"]] = project_id
        print(f"Created project: {project['title']} with ID: {project_id}")
    
    conn.commit()
    print("Projects seeded successfully.")
    return project_ids

def seed_announcements():
    """Seed announcements data."""
    print("\nSeeding announcements...")
    
    # Announcements table already cleared in main function
    
    # Seed announcements
    announcements = [
        {
            "title": "Fall 2023 Registration Now Open",
            "content": "Registration for Fall 2023 semester is now open. Please log in to the student portal to register for courses. The registration deadline is August 15, 2023.",
            "type": "ACADEMIC",
            "priority": "HIGH",
            "date": datetime(2023, 7, 15),
            "image": "/assets/documents/fall_2023_registration.pdf"
        },
        {
            "title": "New Faculty Member Joining the Department",
            "content": "We are pleased to announce that Dr. Jane Smith will be joining our department as an Assistant Professor starting from September 1, 2023. Dr. Smith specializes in Artificial Intelligence and Machine Learning and comes to us from MIT.",
            "type": "GENERAL",
            "priority": "MEDIUM",
            "date": datetime(2023, 8, 1)
        },
        {
            "title": "Seminar on Recent Advances in AI",
            "content": "The Department of Computer Science and Engineering is organizing a seminar on 'Recent Advances in Artificial Intelligence' on August 20, 2023, at 3:00 PM in Room 301. The seminar will be conducted by Dr. John Doe, a renowned AI researcher from Stanford University. All students and faculty members are encouraged to attend.",
            "type": "GENERAL",
            "priority": "MEDIUM",
            "date": datetime(2023, 8, 10),
            "image": "/assets/documents/ai_seminar.pdf"
        },
        {
            "title": "Maintenance of Computer Lab 2",
            "content": "Computer Lab 2 will be closed for maintenance from August 25 to August 27, 2023. Please plan your lab work accordingly.",
            "type": "ADMIN",
            "priority": "LOW",
            "date": datetime(2023, 8, 18)
        },
        {
            "title": "Scholarship Applications for 2023-2024",
            "content": "Applications for the 2023-2024 academic year scholarships are now being accepted. Eligible students can apply through the student portal. The application deadline is September 15, 2023.",
            "type": "ACADEMIC",
            "priority": "HIGH",
            "date": datetime(2023, 8, 15),
            "image": "/assets/documents/scholarship_application.pdf"
        },
        {
            "title": "Job Fair 2023",
            "content": "The annual Job Fair will be held on September 10, 2023, from 10:00 AM to 4:00 PM at the University Auditorium. Representatives from over 50 companies will be present. All final year students are encouraged to attend with their resumes.",
            "type": "GENERAL",
            "priority": "HIGH",
            "date": datetime(2023, 8, 20),
            "image": "/assets/documents/job_fair_2023.pdf"
        },
        {
            "title": "Change in Office Hours",
            "content": "Please note that the department office hours will be changed to 9:00 AM to 3:00 PM during the month of Ramadan.",
            "type": "ADMIN",
            "priority": "MEDIUM",
            "date": datetime(2023, 3, 1)
        },
        {
            "title": "Research Grant Opportunity",
            "content": "The National Science Foundation is offering research grants for projects in Cybersecurity and Artificial Intelligence. Interested faculty members can submit their proposals by October 1, 2023.",
            "type": "GENERAL",
            "priority": "MEDIUM",
            "date": datetime(2023, 8, 25),
            "image": "/assets/documents/nsf_grant_details.pdf"
        },
        {
            "title": "Final Examination Schedule for Summer 2023",
            "content": "The final examination schedule for the Summer 2023 semester has been published. Please check the attached PDF for details.",
            "type": "ACADEMIC",
            "priority": "HIGH",
            "date": datetime(2023, 7, 1),
            "image": "/assets/documents/summer_2023_exam_schedule.pdf"
        },
        {
            "title": "Department Picnic",
            "content": "The annual department picnic will be held on September 5, 2023, at City Park. All students, faculty, and staff are invited. Please register by September 1 if you plan to attend.",
            "type": "GENERAL",
            "priority": "LOW",
            "date": datetime(2023, 8, 20)
        }
    ]
    
    announcement_ids = {}
    for announcement in announcements:
        # Prepare fields with defaults for missing values
        image = announcement.get("image", None)
        
        cursor.execute(
            """INSERT INTO announcements 
            (title, content, type, priority, date, image, created_at, updated_at) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id""",
            (announcement["title"], announcement["content"], announcement["type"], 
             announcement["priority"], announcement["date"], image, 
             datetime.utcnow(), datetime.utcnow())
        )
        announcement_id = cursor.fetchone()[0]
        announcement_ids[announcement["title"]] = announcement_id
        print(f"Created announcement: {announcement['title']} with ID: {announcement_id}")
    
    conn.commit()
    print("Announcements seeded successfully.")
    return announcement_ids

def seed_equipment():
    """Seed equipment data."""
    print("\nSeeding equipment...")
    
    # Equipment-related tables already cleared in main function
    
    # Seed labs
    labs = [
        {
            "name": "AI and Machine Learning Lab",
            "location": "Room 301",
            "capacity": 30,
            "description": "A specialized lab for artificial intelligence and machine learning research and education.",
            "facilities": json.dumps(["High-performance workstations", "NVIDIA GPUs", "AI Development Frameworks", "Smart Board"]),
            "image": "/assets/images/labs/ai_lab.jpg"
        },
        {
            "name": "Database Systems Lab",
            "location": "Room 302",
            "capacity": 25,
            "description": "A lab dedicated to database systems research and education.",
            "facilities": json.dumps(["Database Servers", "DBMS Software", "Data Storage Systems", "Projector"]),
            "image": "/assets/images/labs/db_lab.jpg"
        },
        {
            "name": "Computer Networks Lab",
            "location": "Room 303",
            "capacity": 20,
            "description": "A lab for computer networks and communication systems research and education.",
            "facilities": json.dumps(["Routers", "Switches", "Network Analyzers", "Wireless Communication Equipment"]),
            "image": "/assets/images/labs/networks_lab.jpg"
        },
        {
            "name": "Software Engineering Lab",
            "location": "Room 304",
            "capacity": 35,
            "description": "A lab for software engineering and development projects.",
            "facilities": json.dumps(["Development Workstations", "Collaboration Tools", "Version Control Systems", "Testing Frameworks"]),
            "image": "/assets/images/labs/se_lab.jpg"
        },
        {
            "name": "Graphics and Multimedia Lab",
            "location": "Room 305",
            "capacity": 25,
            "description": "A lab for computer graphics, visualization, and multimedia research and education.",
            "facilities": json.dumps(["Graphics Workstations", "3D Modeling Software", "VR/AR Equipment", "Multimedia Production Tools"]),
            "image": "/assets/images/labs/graphics_lab.jpg"
        }
    ]
    
    lab_ids = {}
    for lab in labs:
        cursor.execute(
            """INSERT INTO labs 
            (name, location, capacity, description, facilities, image) 
            VALUES (%s, %s, %s, %s, %s, %s) RETURNING id""",
            (lab["name"], lab["location"], lab["capacity"], lab["description"], 
             lab["facilities"], lab["image"])
        )
        lab_id = cursor.fetchone()[0]
        lab_ids[lab["name"]] = lab_id
        print(f"Created lab: {lab['name']} with ID: {lab_id}")
    
    # Seed equipment categories
    equipment_categories = [
        {"name": "AI Workstation"},
        {"name": "Database Server"},
        {"name": "Network Equipment"},
        {"name": "Graphics Workstation"},
        {"name": "Development System"},
        {"name": "AR Headset"},
        {"name": "VR Headset"},
        {"name": "Edge AI System"},
        {"name": "Embedded System"}
    ]
    
    category_ids = {}
    for category in equipment_categories:
        cursor.execute(
            """INSERT INTO equipment_categories (name) VALUES (%s) RETURNING id""",
            (category["name"],)
        )
        category_id = cursor.fetchone()[0]
        category_ids[category["name"]] = category_id
        print(f"Created equipment category: {category['name']} with ID: {category_id}")
    
    # Seed equipment
    equipment = [
        {
            "name": "NVIDIA DGX Station",
            "category": "AI Workstation",
            "lab": "AI and Machine Learning Lab",
            "description": "A powerful AI workstation with 4 NVIDIA V100 GPUs, ideal for deep learning research.",
            "specifications": "GPUs: 4x NVIDIA V100, CPU: 20-core Intel Xeon, RAM: 256GB, Storage: 4TB SSD",
            "quantity": 2,
            "available": 2,
            "image": "/assets/images/equipment/dgx_station.jpg",
            "location": "Room 301",
            "requires_approval": True
        },
        {
            "name": "Dell PowerEdge R740 Server",
            "category": "Database Server",
            "lab": "Database Systems Lab",
            "description": "A high-performance server for database management systems and data processing.",
            "specifications": "CPU: 2x Intel Xeon Gold 6248R, RAM: 512GB, Storage: 10TB SSD RAID, Network: 10GbE",
            "quantity": 1,
            "available": 1,
            "image": "/assets/images/equipment/poweredge_server.jpg",
            "location": "Room 302",
            "requires_approval": True
        },
        {
            "name": "Cisco Catalyst 9300 Switch",
            "category": "Network Equipment",
            "lab": "Computer Networks Lab",
            "description": "An enterprise-grade network switch for advanced networking experiments.",
            "specifications": "Ports: 48x 10/100/1000 Ethernet, Uplinks: 4x 10G SFP+, Throughput: 176 Gbps, Features: Layer 3 routing, PoE+",
            "quantity": 3,
            "available": 3,
            "image": "/assets/images/equipment/cisco_switch.jpg",
            "location": "Room 303",
            "requires_approval": False
        },
        {
            "name": "HP Z8 G4 Workstation",
            "category": "Graphics Workstation",
            "lab": "Graphics and Multimedia Lab",
            "description": "A high-end workstation for graphics rendering, 3D modeling, and visualization.",
            "specifications": "CPU: 2x Intel Xeon Gold 6136, GPU: NVIDIA Quadro RTX 6000, RAM: 128GB, Storage: 2TB SSD + 4TB HDD",
            "quantity": 5,
            "available": 5,
            "image": "/assets/images/equipment/hp_z8.jpg",
            "location": "Room 305",
            "requires_approval": False
        },
        {
            "name": "Intel NUC 11 Extreme Kit",
            "category": "Development System",
            "lab": "Software Engineering Lab",
            "description": "A compact yet powerful development system for software projects and testing.",
            "specifications": "CPU: Intel Core i9-11900KB, GPU: NVIDIA RTX 3060, RAM: 64GB, Storage: 1TB NVMe SSD",
            "quantity": 10,
            "available": 10,
            "image": "/assets/images/equipment/intel_nuc.jpg",
            "location": "Room 304",
            "requires_approval": False
        },
        {
            "name": "Fluke Networks AirCheck G2",
            "category": "Network Equipment",
            "lab": "Computer Networks Lab",
            "description": "A wireless network analyzer for Wi-Fi troubleshooting and optimization.",
            "specifications": "Supported Standards: 802.11a/b/g/n/ac/ax, Frequency: 2.4GHz and 5GHz, Features: Spectrum analysis, channel utilization, interference detection",
            "quantity": 3,
            "available": 3,
            "image": "/assets/images/equipment/aircheck.jpg",
            "location": "Room 303",
            "requires_approval": True
        },
        {
            "name": "Microsoft HoloLens 2",
            "category": "AR Headset",
            "lab": "Graphics and Multimedia Lab",
            "description": "An augmented reality headset for mixed reality development and research.",
            "specifications": "Display: 2k 3:2 light engines, Processor: Qualcomm Snapdragon 850, RAM: 4GB, Storage: 64GB",
            "quantity": 2,
            "available": 2,
            "image": "/assets/images/equipment/hololens.jpg",
            "location": "Room 305",
            "requires_approval": True
        },
        {
            "name": "NVIDIA Jetson AGX Xavier",
            "category": "Edge AI System",
            "lab": "AI and Machine Learning Lab",
            "description": "An AI computing platform for edge AI applications and robotics.",
            "specifications": "GPU: 512-core Volta GPU, CPU: 8-core ARM v8.2, RAM: 32GB, Storage: 32GB eMMC",
            "quantity": 5,
            "available": 5,
            "image": "/assets/images/equipment/jetson_xavier.jpg",
            "location": "Room 301",
            "requires_approval": True
        },
        {
            "name": "Oculus Quest 2",
            "category": "VR Headset",
            "lab": "Graphics and Multimedia Lab",
            "description": "A virtual reality headset for immersive VR development and research.",
            "specifications": "Display: 1832x1920 per eye, Processor: Qualcomm Snapdragon XR2, RAM: 6GB, Storage: 256GB",
            "quantity": 10,
            "available": 10,
            "image": "/assets/images/equipment/oculus_quest.jpg",
            "location": "Room 305",
            "requires_approval": False
        },
        {
            "name": "Raspberry Pi 4 Kit",
            "category": "Embedded System",
            "lab": "Computer Networks Lab",
            "description": "A complete Raspberry Pi 4 kit for IoT and embedded systems projects.",
            "specifications": "CPU: Quad-core Cortex-A72, RAM: 8GB, Storage: 32GB microSD, Connectivity: Wi-Fi, Bluetooth, Ethernet",
            "quantity": 20,
            "available": 20,
            "image": "/assets/images/equipment/raspberry_pi.jpg",
            "location": "Room 303",
            "requires_approval": False
        }
    ]
    
    equipment_ids = {}
    for item in equipment:
        lab_id = lab_ids.get(item["lab"])
        category_id = category_ids.get(item["category"])
        if lab_id:
            cursor.execute(
                """INSERT INTO equipment 
                (name, description, category_id, specifications, quantity, available, image, location, requires_approval) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id""",
                (item["name"], item["description"], category_id, 
                 item["specifications"], item["quantity"], item["available"], item["image"], 
                 item["location"], item["requires_approval"])
            )
            equipment_id = cursor.fetchone()[0]
            equipment_ids[item["name"]] = equipment_id
            print(f"Created equipment: {item['name']} with ID: {equipment_id}")
    
    conn.commit()
    print("Equipment and labs seeded successfully.")
    return {"labs": lab_ids, "equipment": equipment_ids}

def seed_schedules(course_data, user_ids):
    """Seed class schedules data."""
    print("\nSeeding class schedules data...")
    
    # Check if class_schedules table exists
    if not check_table_exists("class_schedules"):
        print("Table 'class_schedules' does not exist. Creating it...")
        cursor.execute("""
        CREATE TYPE class_type AS ENUM ('LECTURE', 'LAB', 'TUTORIAL', 'SEMINAR');
        CREATE TYPE class_status AS ENUM ('UPCOMING', 'ONGOING', 'COMPLETED', 'CANCELLED');
        
        CREATE TABLE class_schedules (
            id SERIAL PRIMARY KEY,
            course_code VARCHAR NOT NULL,
            course_name VARCHAR NOT NULL,
            type class_type NOT NULL,
            batch VARCHAR NOT NULL,
            semester VARCHAR NOT NULL,
            day VARCHAR NOT NULL,
            start_time TIMESTAMP NOT NULL,
            end_time TIMESTAMP NOT NULL,
            room VARCHAR NOT NULL,
            instructor_id INTEGER,
            instructor_name VARCHAR,
            instructor_designation VARCHAR,
            status class_status NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        print("Created class_schedules table.")
    
    # Check if there are existing class schedules
    cursor.execute("SELECT COUNT(*) FROM class_schedules")
    schedule_count = cursor.fetchone()[0]

    if schedule_count > 0:
        print(f"Class schedules already exist ({schedule_count} found). Deleting existing schedules...")
        cursor.execute("DELETE FROM class_schedules")
        print("Existing class schedules deleted.")
    
    # Get course codes and titles if not provided
    courses = []
    if course_data:
        cursor.execute("SELECT code, title FROM courses")
        courses = cursor.fetchall()
    else:
        cursor.execute("SELECT code, title FROM courses")
        courses = cursor.fetchall()
    
    if not courses:
        print("No courses found. Cannot create class schedules.")
        return {}
    
    print(f"Found {len(courses)} courses. Creating class schedules...")
    
    # Get faculty data from the database using user_ids
    faculty_data = []
    
    if user_ids and 'faculty' in user_ids and user_ids['faculty']:
        # Extract faculty IDs from the dictionary
        faculty_ids_list = list(user_ids['faculty'].values())
        
        # Query the database to get faculty information
        if len(faculty_ids_list) == 1:
            # Handle single faculty ID case
            cursor.execute("""
            SELECT u.id, u.name, f.designation 
            FROM users u 
            JOIN faculty f ON u.id = f.id 
            WHERE u.id = %s
            """, (faculty_ids_list[0],))
        else:
            # Handle multiple faculty IDs case
            cursor.execute("""
            SELECT u.id, u.name, f.designation 
            FROM users u 
            JOIN faculty f ON u.id = f.id 
            WHERE u.id IN %s
            """, (tuple(faculty_ids_list),))
        
        faculty_data = cursor.fetchall()
    
    # If no faculty data found, use admin user as fallback
    if not faculty_data and user_ids and 'admin' in user_ids:
        admin_id = user_ids['admin']
        cursor.execute("SELECT id, name FROM users WHERE id = %s", (admin_id,))
        admin_data = cursor.fetchone()
        if admin_data:
            faculty_data = [(admin_data[0], admin_data[1], "Administrator")]
    
    # Days of the week
    days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday"]
    
    # Rooms
    rooms = ["301", "302", "303", "304", "501", "601", "Lab 1", "Lab 2", "Lab 3", "Lab 4", "Hardware Lab"]
    
    # Batches
    batches = ["25", "24", "23", "22", "MSc", "PhD"]
    
    # Time slots
    time_slots = [
        ("08:00", "09:30"),
        ("09:30", "11:00"),
        ("11:00", "12:30"),
        ("12:30", "14:00"),
        ("14:00", "15:30"),
        ("15:30", "17:00")
    ]
    
    # Helper function to create datetime objects for time
    def create_time(time_str):
        hour, minute = map(int, time_str.split(':'))
        return datetime.combine(datetime.today(), time(hour, minute))
    
    # Create schedules for each course
    class_count = 0
    schedule_ids = []
    
    for i, (code, title) in enumerate(courses):
        # Determine batch and semester based on course code
        if "CSE" in code and any(char.isdigit() for char in code):
            course_num = int(''.join(filter(str.isdigit, code)))
            year = (course_num // 100) % 10
            
            if year <= 4:
                # Undergraduate
                batch = batches[year % len(batches)]
                semester = str((year - 1) * 2 + (i % 2) + 1)
            else:
                # Graduate
                batch = "MSc" if i % 2 == 0 else "PhD"
                semester = str(i % 4 + 1)
        else:
            # Default values
            batch = batches[i % len(batches)]
            semester = str(i % 8 + 1)
        
        # Create lecture class
        day = days[i % len(days)]
        time_slot_idx = i % len(time_slots)
        start_time_str, end_time_str = time_slots[time_slot_idx]
        
        start_time = create_time(start_time_str)
        end_time = create_time(end_time_str)
        
        room = rooms[i % len(rooms)]
        faculty_idx = i % len(faculty_data)
        faculty_id, faculty_name, faculty_designation = faculty_data[faculty_idx]
        
        # Insert lecture class - using uppercase enum values
        cursor.execute("""
        INSERT INTO class_schedules (
            course_code, course_name, type, batch, semester, day, 
            start_time, end_time, room, instructor_id, instructor_name, 
            instructor_designation, status
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        """, (
            code, title, "LECTURE", batch, semester, day,
            start_time, end_time, room, faculty_id, faculty_name,
            faculty_designation, "UPCOMING"
        ))
        schedule_id = cursor.fetchone()[0]
        schedule_ids.append(schedule_id)
        class_count += 1
        
        # For some courses, add a lab class
        if i % 3 == 0:  # Every third course has a lab
            # Use a different day and time slot for the lab
            lab_day = days[(i + 2) % len(days)]
            lab_time_slot_idx = (i + 3) % len(time_slots)
            lab_start_time_str, lab_end_time_str = time_slots[lab_time_slot_idx]
            
            lab_start_time = create_time(lab_start_time_str)
            lab_end_time = create_time(lab_end_time_str)
            
            lab_room = f"Lab {(i % 4) + 1}"
            lab_faculty_idx = (i + 1) % len(faculty_data)
            lab_faculty_id, lab_faculty_name, lab_faculty_designation = faculty_data[lab_faculty_idx]
            
            # Insert lab class - using uppercase enum values
            cursor.execute("""
            INSERT INTO class_schedules (
                course_code, course_name, type, batch, semester, day, 
                start_time, end_time, room, instructor_id, instructor_name, 
                instructor_designation, status
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
            """, (
                code, title, "LAB", batch, semester, lab_day,
                lab_start_time, lab_end_time, lab_room, lab_faculty_id, lab_faculty_name,
                lab_faculty_designation, "UPCOMING"
            ))
            schedule_id = cursor.fetchone()[0]
            schedule_ids.append(schedule_id)
            class_count += 1
    
    print(f"Successfully added {class_count} class schedules to the database.")
    return {"schedules": schedule_ids}

def seed_events(role_ids):
    """Seed events data."""
    print("\nSeeding events data...")
    
    # Check if events table exists
    if not check_table_exists("events"):
        print("Table 'events' does not exist. Creating it...")
        cursor.execute("""
        CREATE TYPE event_type AS ENUM ('seminar', 'workshop', 'conference', 'competition', 'cultural', 'academic');
        CREATE TYPE event_status AS ENUM ('upcoming', 'ongoing', 'registration_open', 'registration_closed', 'completed');
        
        CREATE TABLE events (
            id SERIAL PRIMARY KEY,
            title VARCHAR NOT NULL,
            description TEXT,
            type event_type NOT NULL,
            status event_status NOT NULL,
            start_date TIMESTAMP NOT NULL,
            end_date TIMESTAMP NOT NULL,
            venue VARCHAR NOT NULL,
            speaker VARCHAR,
            organizer_role_id INTEGER REFERENCES roles(id),
            max_participants INTEGER,
            registered_count INTEGER DEFAULT 0,
            registration_required BOOLEAN DEFAULT FALSE,
            registration_deadline TIMESTAMP,
            fee FLOAT,
            external_link VARCHAR,
            tags JSONB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE TABLE event_registrations (
            id SERIAL PRIMARY KEY,
            event_id INTEGER REFERENCES events(id) NOT NULL,
            user_id INTEGER REFERENCES users(id) NOT NULL,
            full_name VARCHAR NOT NULL,
            email VARCHAR NOT NULL,
            phone VARCHAR NOT NULL,
            student_id VARCHAR,
            department VARCHAR,
            year VARCHAR,
            special_requirements TEXT,
            registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """)
        print("Created events and event_registrations tables.")
    
    # Use the admin role ID for organizers
    admin_role_id = role_ids.get('ADMIN')
    if not admin_role_id:
        print("Error: Admin role not found. Cannot seed events.")
        return {}
        
    # For simplicity, we'll use the admin role for all events
    # In a real application, you would create specific roles for student council, programming club, etc.
    student_council_role_id = admin_role_id
    programming_club_role_id = admin_role_id
    department_role_id = admin_role_id
    
    # Sample events data
    events_data = [
        {
            "title": "AI & Machine Learning Symposium 2025",
            "description": "Join leading researchers and industry experts as they discuss the latest advances in artificial intelligence and machine learning technologies.",
            "type": "CONFERENCE",
            "status": "REGISTRATION_OPEN",
            "start_date": "2025-08-15 09:00:00",
            "end_date": "2025-08-15 17:00:00",
            "venue": "Main Auditorium, CSE Building",
            "speaker": "Dr. Sarah Ahmed, MIT",
            "organizer_role_id": department_role_id,
            "max_participants": 200,
            "registered_count": 145,
            "registration_required": True,
            "registration_deadline": "2025-08-10 23:59:59",
            "fee": 500,
            "external_link": "https://ai-symposium.csedu.ac.bd",
            "tags": ["AI", "Machine Learning", "Research"]
        },
        {
            "title": "Web Development Workshop",
            "description": "Hands-on workshop covering modern web development technologies including React, Node.js, and MongoDB.",
            "type": "WORKSHOP",
            "status": "UPCOMING",
            "start_date": "2025-07-20 14:00:00",
            "end_date": "2025-07-20 18:00:00",
            "venue": "Computer Lab 1, 3rd Floor",
            "speaker": "Md. Rafiq Hassan, Senior Developer",
            "organizer_role_id": programming_club_role_id,
            "max_participants": 30,
            "registered_count": 28,
            "registration_required": True,
            "registration_deadline": "2025-07-18 23:59:59",
            "fee": 0,
            "external_link": None,
            "tags": ["Web Development", "React", "Node.js"]
        },
        {
            "title": "Cybersecurity Awareness Seminar",
            "description": "Learn about the latest cybersecurity threats and how to protect yourself and your organization from cyber attacks.",
            "type": "SEMINAR",
            "status": "REGISTRATION_OPEN",
            "start_date": "2025-07-25 10:00:00",
            "end_date": "2025-07-25 12:30:00",
            "venue": "Room 302, CSE Building",
            "speaker": "Tasnim Kabir, Security Specialist",
            "organizer_role_id": department_role_id,
            "max_participants": 100,
            "registered_count": 45,
            "registration_required": True,
            "registration_deadline": "2025-07-23 23:59:59",
            "fee": 0,
            "external_link": None,
            "tags": ["Cybersecurity", "Digital Safety", "Hacking Prevention"]
        },
        {
            "title": "Annual Programming Contest 2025",
            "description": "Test your programming skills in this competitive event with challenging problems and exciting prizes.",
            "type": "COMPETITION",
            "status": "UPCOMING",
            "start_date": "2025-09-10 09:00:00",
            "end_date": "2025-09-10 17:00:00",
            "venue": "All Computer Labs, CSE Building",
            "speaker": None,
            "organizer_role_id": programming_club_role_id,
            "max_participants": 150,
            "registered_count": 0,
            "registration_required": True,
            "registration_deadline": "2025-09-05 23:59:59",
            "fee": 200,
            "external_link": "https://contest.csedu.ac.bd",
            "tags": ["Programming", "Algorithms", "Competition"]
        },
        {
            "title": "CSE Cultural Night 2025",
            "description": "An evening of music, dance, and performances by the talented students of the CSE department.",
            "type": "CULTURAL",
            "status": "UPCOMING",
            "start_date": "2025-10-15 18:00:00",
            "end_date": "2025-10-15 22:00:00",
            "venue": "University Auditorium",
            "speaker": None,
            "organizer_role_id": student_council_role_id,
            "max_participants": 500,
            "registered_count": 0,
            "registration_required": False,
            "registration_deadline": None,
            "fee": 100,
            "external_link": None,
            "tags": ["Cultural", "Entertainment", "Music"]
        },
        {
            "title": "Research Methodology Workshop",
            "description": "Essential workshop for graduate students covering research methodologies, paper writing, and publication strategies.",
            "type": "WORKSHOP",
            "status": "UPCOMING",
            "start_date": "2025-08-05 10:00:00",
            "end_date": "2025-08-05 16:00:00",
            "venue": "Seminar Room, CSE Building",
            "speaker": "Dr. Anisur Rahman",
            "organizer_role_id": department_role_id,
            "max_participants": 50,
            "registered_count": 0,
            "registration_required": True,
            "registration_deadline": "2025-08-01 23:59:59",
            "fee": 0,
            "external_link": None,
            "tags": ["Research", "Academic Writing", "Publication"]
        },
        {
            "title": "Mobile App Development Bootcamp",
            "description": "Intensive 3-day bootcamp on mobile app development using React Native and Flutter.",
            "type": "WORKSHOP",
            "status": "UPCOMING",
            "start_date": "2025-11-20 09:00:00",
            "end_date": "2025-11-22 17:00:00",
            "venue": "Computer Lab 2, CSE Building",
            "speaker": "Multiple Industry Experts",
            "organizer_role_id": programming_club_role_id,
            "max_participants": 40,
            "registered_count": 0,
            "registration_required": True,
            "registration_deadline": "2025-11-15 23:59:59",
            "fee": 1000,
            "external_link": "https://mobilebootcamp.csedu.ac.bd",
            "tags": ["Mobile Development", "React Native", "Flutter"]
        }
    ]
    
    # Clear existing events data
    cursor.execute("DELETE FROM event_registrations")
    cursor.execute("DELETE FROM events")
    
    event_ids = {}
    
    # Insert events data
    for event in events_data:
        cursor.execute("""
        INSERT INTO events (title, description, type, status, start_date, end_date, venue, speaker, 
                          organizer_role_id, max_participants, registered_count, registration_required, 
                          registration_deadline, fee, external_link, tags)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        """, (
            event["title"], 
            event["description"], 
            event["type"], 
            event["status"], 
            event["start_date"], 
            event["end_date"], 
            event["venue"], 
            event["speaker"], 
            event["organizer_role_id"], 
            event["max_participants"], 
            event["registered_count"], 
            event["registration_required"], 
            event["registration_deadline"], 
            event["fee"], 
            event["external_link"], 
            json.dumps(event["tags"])
        ))
        
        event_id = cursor.fetchone()[0]
        event_ids[event["title"]] = event_id
        print(f"Created event: {event['title']} with ID: {event_id}")
    
    conn.commit()
    print("Events seeded successfully.")
    return event_ids

def seed_meetings(user_ids):
    """Seed meetings data."""
    print("\nSeeding meetings...")
    
    try:
        # Get faculty and student users directly from the database based on role IDs
        cursor.execute("""
            SELECT u.id, u.email 
            FROM users u 
            WHERE u.role_id = (SELECT id FROM roles WHERE name = 'FACULTY')
        """)
        faculty_users = cursor.fetchall()
        
        cursor.execute("""
            SELECT u.id, u.email 
            FROM users u 
            WHERE u.role_id = (SELECT id FROM roles WHERE name = 'STUDENT')
        """)
        student_users = cursor.fetchall()
        
        print(f"Found {len(faculty_users)} faculty users and {len(student_users)} student users for meetings")
        
        if not faculty_users or not student_users:
            print("Warning: No faculty or student users found. Skipping meetings seeding.")
            return []
            
        # Debug output
        print("Faculty users:")
        for faculty in faculty_users[:2]:
            print(f"  ID: {faculty[0]}, Email: {faculty[1]}")
            
        print("Student users:")
        for student in student_users[:2]:
            print(f"  ID: {student[0]}, Email: {student[1]}")
    except Exception as e:
        print(f"Error getting users: {str(e)}")
        return []
    
    # Create meetings
    meetings = []
    # Use the correct enum values from the models (uppercase as stored in the database)
    meeting_types = ['ADVISING', 'THESIS', 'PROJECT', 'GENERAL', 'OTHER']
    statuses = ['SCHEDULED', 'CONFIRMED', 'CANCELLED', 'COMPLETED']
    rsvp_statuses = ['PENDING', 'CONFIRMED', 'TENTATIVE', 'DECLINED']
    
    try:
        print("Creating meetings...")
        for i in range(1, 11):
            try:
                faculty = faculty_users[i % len(faculty_users)]
                student = student_users[i % len(student_users)]
                
                meeting = {
                    'title': f'Meeting {i}: {faculty[1].split("@")[0]} with {student[1].split("@")[0]}',
                    'description': f'This is a {meeting_types[i % len(meeting_types)]} meeting between student and faculty.',
                    'faculty_id': faculty[0],
                    'date': f'2025-{7 + i // 30:02d}-{i % 28 + 1:02d}',  # Spread across July-August 2025
                    'start_time': f'{(9 + i % 8):02d}:00',  # Between 9:00 and 17:00
                    'end_time': f'{(10 + i % 6):02d}:00',   # 1-2 hour duration
                    'location': f'Room {100 + i % 20}, CSE Building',
                    'meeting_type': meeting_types[i % len(meeting_types)],
                    'status': statuses[i % len(statuses)],
                    'rsvp_status': rsvp_statuses[i % len(rsvp_statuses)],
                    'rsvp_deadline': f'2025-{7 + i // 30:02d}-{i % 28:02d}',  # Day before meeting
                    'rsvp_notes': f'Please bring your project materials for discussion.' if i % 2 == 0 else None,
                    'created_at': '2025-07-01 00:00:00',
                    'updated_at': '2025-07-01 00:00:00'
                }
                
                # Debug output for the first meeting
                if i == 1:
                    print("First meeting data:")
                    for key, value in meeting.items():
                        print(f"  {key}: {value}")
                    print(f"  student_id: {student[0]}")
                
                try:
                    cursor.execute("""
                        INSERT INTO meetings (
                            title, description, faculty_id, student_id, date, start_time, end_time,
                            location, meeting_type, status, rsvp_status, rsvp_deadline, rsvp_notes,
                            created_at, updated_at
                        ) VALUES (
                            %(title)s, %(description)s, %(faculty_id)s, %(student_id)s, %(date)s, 
                            %(start_time)s, %(end_time)s, %(location)s, %(meeting_type)s, %(status)s, 
                            %(rsvp_status)s, %(rsvp_deadline)s, %(rsvp_notes)s, %(created_at)s, %(updated_at)s
                        ) RETURNING id;
                    """, {
                        **meeting,
                        'student_id': student[0]
                    })
                    
                    meeting_id = cursor.fetchone()[0]
                    meetings.append(meeting_id)
                    print(f"Created meeting {i} with ID {meeting_id}")
                except Exception as e:
                    print(f"Error inserting meeting {i}: {str(e)}")
                    # Continue with other meetings even if one fails
            except Exception as e:
                print(f"Error creating meeting {i}: {str(e)}")
        
        # Commit the transaction
        conn.commit()
        print(f"Seeded {len(meetings)} meetings.")
    except Exception as e:
        print(f"Error in meetings creation loop: {str(e)}")
        return []
    return meetings

def main():
    """Main function to run all seeding functions in the correct order."""
    try:
        print("\n=== CSEDU Website Database Seeding ===\n")
        print("Starting master seed script...")
        
        # We need to clear tables with CASCADE to handle foreign key constraints
        print("\nClearing existing data...")
        
        # Get all tables in the database
        print("Fetching database schema...")
        all_tables = get_all_tables()
        print(f"Found {len(all_tables)} tables in the database.")
        
        # Define tables to clear in reverse dependency order
        # This is a best guess based on typical foreign key relationships
        tables_to_clear = [
            # First clear junction/relation tables
            "roles_permissions",
            "course_prerequisites",
            "course_faculty",
            "project_faculty",
            "project_students",
            "equipment_bookings",
            "lab_time_slots",
            "class_schedules",
            "event_registrations",
            "meetings",
            
            # Then clear main entity tables
            "events",
            "equipment",
            "labs",
            "announcements",
            "projects",
            "courses",
            "programs",
            "faculty",
            "users",
            "permissions",
            "roles"
        ]
        
        # Disable foreign key checks temporarily for clean truncation
        cursor.execute("BEGIN;")
        cursor.execute("SET CONSTRAINTS ALL DEFERRED;")
        
        # Clear tables that exist in the database
        for table in tables_to_clear:
            if table in all_tables:
                try:
                    cursor.execute(f"TRUNCATE TABLE {table} CASCADE;")
                    print(f"Cleared table: {table}")
                except Exception as e:
                    print(f"Error clearing table {table}: {str(e)}")
                    # Continue with other tables even if one fails
            else:
                print(f"Table {table} does not exist, skipping.")
        
        # Re-enable foreign key checks
        cursor.execute("COMMIT;")
        conn.commit()
        
        # Now seed everything in the correct order
        # Seed roles and permissions first (foundation for user access control)
        role_ids = seed_roles_and_permissions()
        
        # Seed users (depends on roles)
        user_ids = seed_users(role_ids)
        
        # Seed faculty profiles (depends on users)
        faculty_profiles = seed_faculty(user_ids["faculty"])
        
        # Seed courses and programs (independent)
        course_data = seed_courses()
        
        # Seed projects (independent)
        project_ids = seed_projects()
        
        # Seed announcements (independent)
        announcement_ids = seed_announcements()
        
        # Seed equipment and labs (independent)
        equipment_data = seed_equipment()
        
        # Seed events (depends on roles)
        event_ids = seed_events(role_ids)
        
        # Seed meetings (depends on faculty and student users)
        meeting_ids = seed_meetings(user_ids)
        
        # Seed class schedules (depends on courses and faculty users)
        schedule_data = seed_schedules(course_data, user_ids)
        
        print("\n=== Seeding Complete ===\n")
        print("All data has been successfully seeded into the database.")
        print("Summary:")
        print(f"- {len(role_ids)} roles")
        print(f"- {len(user_ids['faculty'])} faculty users")
        print(f"- {len(user_ids['students'])} student users")
        print(f"- {len(user_ids['staff'])} staff users")
        print(f"- {len(course_data['programs'])} academic programs")
        print(f"- {len(course_data['courses'])} courses")
        print(f"- {len(project_ids)} projects")
        print(f"- {len(announcement_ids)} announcements")
        print(f"- {len(equipment_data['labs'])} labs")
        print(f"- {len(equipment_data['equipment'])} equipment items")
        print(f"- {len(event_ids)} events")
        print(f"- {len(meeting_ids)} meetings")
        print(f"- {len(schedule_data.get('schedules', []))} class schedules")
        
    except Exception as e:
        print(f"\nError during seeding: {str(e)}")
        traceback.print_exc()
        conn.rollback()
        print("\nSeeding failed. Database has been rolled back.")
        return 1
    finally:
        cursor.close()
        conn.close()
        print("\nDatabase connection closed.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
