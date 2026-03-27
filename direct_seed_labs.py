import os
import psycopg2
from psycopg2.extras import Json
from dotenv import load_dotenv
from datetime import datetime, timedelta, date
import random
import uuid

# Load environment variables from .env file
load_dotenv()

# Database connection parameters
DB_HOST = os.getenv("DATABASE_HOSTNAME")
DB_PORT = os.getenv("DATABASE_PORT")
DB_NAME = os.getenv("DATABASE_NAME")
DB_USER = os.getenv("DATABASE_USERNAME")
DB_PASS = os.getenv("DATABASE_PASSWORD")

# Connect to the database
conn = psycopg2.connect(
    host=DB_HOST,
    port=DB_PORT,
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASS
)

# Create a cursor
cur = conn.cursor()

# Function to clear existing data
def clear_existing_data():
    print("Clearing existing lab data...")
    cur.execute("DELETE FROM lab_bookings")
    cur.execute("DELETE FROM lab_time_slots")
    cur.execute("DELETE FROM labs")
    conn.commit()
    print("Existing lab data cleared.")

# Function to seed labs
def seed_labs():
    print("Seeding labs...")
    
    # Lab data
    labs = [
        {
            "name": "AI & Machine Learning Lab",
            "description": "Equipped with high-performance GPUs and specialized hardware for AI research and development",
            "location": "Building A, 3rd Floor, Room 302",
            "capacity": 30,
            "facilities": ["NVIDIA RTX GPUs", "High-performance workstations", "AI development frameworks", "Research datasets"],
            "image": "/assets/labs/ai-lab.jpg"
        },
        {
            "name": "Networking & Security Lab",
            "description": "Specialized lab for network configuration, security testing, and protocol analysis",
            "location": "Building B, 2nd Floor, Room 203",
            "capacity": 25,
            "facilities": ["Cisco networking equipment", "Security testing tools", "Protocol analyzers", "Firewall systems"],
            "image": "/assets/labs/network-lab.jpg"
        },
        {
            "name": "Software Development Lab",
            "description": "Modern lab for software engineering projects and collaborative development",
            "location": "Building A, 2nd Floor, Room 201",
            "capacity": 40,
            "facilities": ["Development workstations", "Collaboration tools", "Version control systems", "Testing frameworks"],
            "image": "/assets/labs/software-lab.jpg"
        },
        {
            "name": "IoT & Embedded Systems Lab",
            "description": "Specialized lab for IoT device development and embedded systems programming",
            "location": "Building B, 3rd Floor, Room 305",
            "capacity": 20,
            "facilities": ["Arduino kits", "Raspberry Pi devices", "Sensor arrays", "Embedded development tools"],
            "image": "/assets/labs/iot-lab.jpg"
        },
        {
            "name": "Database & Data Science Lab",
            "description": "Lab equipped for database management, data analysis, and visualization",
            "location": "Building A, 1st Floor, Room 105",
            "capacity": 35,
            "facilities": ["Database servers", "Data visualization tools", "Statistical software", "Big data frameworks"],
            "image": "/assets/labs/database-lab.jpg"
        }
    ]
    
    # Insert labs and get their IDs
    lab_ids = []
    for lab in labs:
        cur.execute(
            """
            INSERT INTO labs (name, description, location, capacity, facilities, image)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
            """,
            (
                lab["name"],
                lab["description"],
                lab["location"],
                lab["capacity"],
                Json(lab["facilities"]),
                lab["image"]
            )
        )
        lab_id = cur.fetchone()[0]
        lab_ids.append(lab_id)
        
    conn.commit()
    print(f"Seeded {len(labs)} labs.")
    return lab_ids

# Function to seed lab time slots
def seed_lab_time_slots(lab_ids):
    print("Seeding lab time slots...")
    
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    time_slots = [
        {"start": "09:00", "end": "11:00"},
        {"start": "11:00", "end": "13:00"},
        {"start": "14:00", "end": "16:00"},
        {"start": "16:00", "end": "18:00"}
    ]
    
    time_slot_ids = []
    
    for lab_id in lab_ids:
        # Assign 3-4 random time slots to each lab
        num_slots = random.randint(3, 4)
        selected_slots = []
        
        for _ in range(num_slots):
            day = random.choice(days)
            slot = random.choice(time_slots)
            
            # Avoid duplicate day+time combinations for the same lab
            slot_key = f"{day}-{slot['start']}"
            if slot_key in selected_slots:
                continue
                
            selected_slots.append(slot_key)
            
            cur.execute(
                """
                INSERT INTO lab_time_slots (lab_id, day, start_time, end_time)
                VALUES (%s, %s, %s, %s)
                RETURNING id
                """,
                (
                    lab_id,
                    day,
                    slot["start"],
                    slot["end"]
                )
            )
            time_slot_id = cur.fetchone()[0]
            time_slot_ids.append((lab_id, time_slot_id))
    
    conn.commit()
    print(f"Seeded {len(time_slot_ids)} lab time slots.")
    return time_slot_ids

# Function to seed lab bookings
def seed_lab_bookings(lab_time_slots):
    print("Seeding lab bookings...")
    
    # Get some user IDs from the database
    try:
        cur.execute("SELECT id, name, role_id FROM users LIMIT 10")
        users = cur.fetchall()
        
        if not users:
            print("No users found in the database. Creating a default user for bookings.")
            # Create a default user if none exists
            cur.execute(
                """
                INSERT INTO roles (name) 
                VALUES ('student') 
                ON CONFLICT (name) DO NOTHING 
                RETURNING id
                """
            )
            role_id = cur.fetchone()
            if not role_id:
                cur.execute("SELECT id FROM roles WHERE name = 'student'")
                role_id = cur.fetchone()
            
            role_id = role_id[0] if role_id else 1
            
            cur.execute(
                """
                INSERT INTO users (name, email, password, role_id, created_at) 
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (email) DO NOTHING
                RETURNING id, name
                """,
                ("Default User", "default@csedu.edu", "password", role_id, datetime.now())
            )
            user_result = cur.fetchone()
            
            if not user_result:
                cur.execute("SELECT id, name FROM users LIMIT 1")
                user_result = cur.fetchone()
            
            if user_result:
                users = [(user_result[0], user_result[1], role_id)]
            else:
                print("Could not create or find any users. Skipping lab booking seeding.")
                return
            
            conn.commit()
    except Exception as e:
        print(f"Error getting users: {e}")
        return
    
    # Get role names for users
    user_roles = {}
    for user in users:
        try:
            cur.execute("SELECT name FROM roles WHERE id = %s", (user[2],))
            role = cur.fetchone()
            if role:
                user_roles[user[0]] = role[0]
            else:
                user_roles[user[0]] = "student"  # Default role
        except Exception as e:
            print(f"Error getting role for user {user[0]}: {e}")
            user_roles[user[0]] = "student"  # Default role
    
    # Generate booking dates (next 30 days)
    today = date.today()
    booking_dates = [(today + timedelta(days=i)) for i in range(1, 31)]
    
    # Status options
    statuses = ["pending", "approved", "rejected"]
    
    # Create bookings
    bookings_count = 0
    for lab_id, time_slot_id in lab_time_slots:
        # 50% chance to create a booking for this time slot
        if random.random() < 0.5:
            try:
                user_id, user_name, role_id = random.choice(users)
                booking_date = random.choice(booking_dates)
                status = random.choices(statuses, weights=[0.3, 0.6, 0.1])[0]
                user_role = user_roles.get(user_id, "student")
                
                cur.execute(
                    """
                    INSERT INTO lab_bookings 
                    (lab_id, user_id, time_slot_id, date, purpose, status, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        lab_id,
                        user_id,
                        time_slot_id,
                        booking_date,
                        f"Research project work: {random.choice(['Data analysis', 'Algorithm testing', 'System development', 'Prototype testing'])}",
                        status,
                        datetime.now(),
                        datetime.now()
                    )
                )
                bookings_count += 1
            except Exception as e:
                print(f"Error creating booking: {e}")
                continue
    
    conn.commit()
    print(f"Seeded {bookings_count} lab bookings.")

# Main execution
try:
    clear_existing_data()
    lab_ids = seed_labs()
    lab_time_slots = seed_lab_time_slots(lab_ids)
    seed_lab_bookings(lab_time_slots)
    print("Lab data seeding completed successfully!")
except Exception as e:
    conn.rollback()
    print(f"Error seeding lab data: {e}")
finally:
    cur.close()
    conn.close()
