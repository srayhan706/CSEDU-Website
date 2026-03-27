import os
import sys
import psycopg2
from dotenv import load_dotenv
from datetime import datetime, timedelta
import random
import json

# Load environment variables
load_dotenv()

# Database connection parameters
DB_USER = os.getenv("DATABASE_USERNAME")
DB_PASSWORD = os.getenv("DATABASE_PASSWORD")
DB_HOST = os.getenv("DATABASE_HOSTNAME")
DB_PORT = os.getenv("DATABASE_PORT")
DB_NAME = os.getenv("DATABASE_NAME")

# Connect to database
try:
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    conn.autocommit = False
    cursor = conn.cursor()
    print("Connected to database successfully!")
except Exception as e:
    print(f"Error connecting to database: {e}")
    sys.exit(1)

# Clear existing data
def clear_existing_data():
    try:
        cursor.execute("DELETE FROM equipment_bookings")
        cursor.execute("DELETE FROM equipment")
        cursor.execute("DELETE FROM equipment_categories")
        conn.commit()
        print("Existing equipment data cleared.")
    except Exception as e:
        conn.rollback()
        print(f"Error clearing existing data: {e}")
        sys.exit(1)

# Seed equipment categories
def seed_equipment_categories():
    categories = [
        {
            "name": "Computing Hardware",
            "icon": "Cpu",
            "description": "High-performance computing resources including GPUs, servers, and specialized processors"
        },
        {
            "name": "Sensors & IoT",
            "icon": "Wifi",
            "description": "Various sensors, actuators, and Internet of Things devices for research and projects"
        },
        {
            "name": "Storage & Memory",
            "icon": "Database",
            "description": "Storage devices and memory modules for data-intensive applications"
        },
        {
            "name": "Mobile & Embedded",
            "icon": "Smartphone",
            "description": "Mobile devices and embedded systems for testing and development"
        },
        {
            "name": "Networking",
            "icon": "Layers",
            "description": "Networking equipment for communication and distributed systems research"
        }
    ]
    
    category_ids = {}
    
    for cat in categories:
        try:
            cursor.execute(
                "INSERT INTO equipment_categories (name, icon, description) VALUES (%s, %s, %s) RETURNING id",
                (cat["name"], cat["icon"], cat["description"])
            )
            category_id = cursor.fetchone()[0]
            category_ids[cat["name"]] = category_id
        except Exception as e:
            print(f"Error inserting category {cat['name']}: {e}")
    
    conn.commit()
    print(f"Added {len(categories)} equipment categories.")
    return category_ids

# Seed equipment
def seed_equipment(category_ids):
    equipment_data = [
        {
            "name": "NVIDIA RTX 4090 GPU",
            "description": "High-end graphics processing unit for AI and deep learning applications",
            "category_name": "Computing Hardware",
            "specifications": "24GB GDDR6X, 16384 CUDA cores, 2.52 GHz boost clock",
            "quantity": 4,
            "available": 2,
            "image": "/assets/equipment/gpu.jpg",
            "location": "AI Lab (Room 302)",
            "requires_approval": True
        },
        {
            "name": "Temperature & Humidity Sensor Kit",
            "description": "Precision sensors for environmental monitoring in IoT projects",
            "category_name": "Sensors & IoT",
            "specifications": "DHT22 sensors, -40 to 80°C range, ±0.5°C accuracy",
            "quantity": 20,
            "available": 15,
            "image": "/assets/equipment/temp-sensor.jpg",
            "location": "IoT Lab (Room 201)",
            "requires_approval": False
        },
        {
            "name": "High-Performance Server",
            "description": "Multi-core server for distributed computing and virtualization",
            "category_name": "Computing Hardware",
            "specifications": "AMD EPYC 7763, 64 cores, 128 threads, 256GB RAM",
            "quantity": 2,
            "available": 1,
            "image": "/assets/equipment/server.jpg",
            "location": "Server Room (Room 405)",
            "requires_approval": True
        },
        {
            "name": "Motion Capture System",
            "description": "Advanced motion tracking system for computer vision research",
            "category_name": "Sensors & IoT",
            "specifications": "12-camera setup, 120fps, sub-millimeter accuracy",
            "quantity": 1,
            "available": 1,
            "image": "/assets/equipment/motion-capture.jpg",
            "location": "Graphics Lab (Room 304)",
            "requires_approval": True
        },
        {
            "name": "SSD Storage Array",
            "description": "High-speed storage array for data-intensive applications",
            "category_name": "Storage & Memory",
            "specifications": "10TB total, NVMe SSDs, 7000MB/s read, 5000MB/s write",
            "quantity": 3,
            "available": 3,
            "image": "/assets/equipment/ssd-array.jpg",
            "location": "Data Science Lab (Room 303)",
            "requires_approval": False
        },
        {
            "name": "Raspberry Pi Kit",
            "description": "Complete Raspberry Pi development kit with accessories",
            "category_name": "Mobile & Embedded",
            "specifications": "Raspberry Pi 4B, 8GB RAM, 64GB SD, sensors, display",
            "quantity": 15,
            "available": 8,
            "image": "/assets/equipment/raspberry-pi.jpg",
            "location": "Embedded Systems Lab (Room 202)",
            "requires_approval": False
        },
        {
            "name": "Network Testing Kit",
            "description": "Professional networking equipment for protocol testing and research",
            "category_name": "Networking",
            "specifications": "Cisco switches, routers, packet analyzers, cables",
            "quantity": 5,
            "available": 4,
            "image": "/assets/equipment/network-kit.jpg",
            "location": "Networking Lab (Room 203)",
            "requires_approval": True
        },
        {
            "name": "Drone Development Kit",
            "description": "Programmable drone with sensors and development interface",
            "category_name": "Sensors & IoT",
            "specifications": "Quadcopter, 4K camera, programmable flight controller",
            "quantity": 3,
            "available": 2,
            "image": "/assets/equipment/drone.jpg",
            "location": "Robotics Lab (Room 305)",
            "requires_approval": True
        }
    ]
    
    equipment_ids = {}
    
    for eq in equipment_data:
        try:
            cursor.execute(
                """
                INSERT INTO equipment (name, description, category_id, specifications, 
                quantity, available, image, location, requires_approval) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id
                """,
                (
                    eq["name"], 
                    eq["description"], 
                    category_ids[eq["category_name"]], 
                    eq["specifications"],
                    eq["quantity"], 
                    eq["available"], 
                    eq["image"], 
                    eq["location"], 
                    eq["requires_approval"]
                )
            )
            equipment_id = cursor.fetchone()[0]
            equipment_ids[eq["name"]] = equipment_id
        except Exception as e:
            print(f"Error inserting equipment {eq['name']}: {e}")
    
    conn.commit()
    print(f"Added {len(equipment_data)} equipment items.")
    return equipment_ids

# Seed equipment bookings
def seed_equipment_bookings(equipment_ids):
    # Get some users
    try:
        cursor.execute("SELECT id, name, role_id FROM users LIMIT 5")
        users = cursor.fetchall()
        if not users:
            print("No users found. Please seed users first.")
            return
    except Exception as e:
        print(f"Error fetching users: {e}")
        return
    
    # Status options
    status_options = ["pending", "approved", "rejected", "completed"]
    
    # Generate bookings
    bookings_added = 0
    now = datetime.now()
    
    for i in range(10):
        try:
            # Select random equipment and user
            equipment_name = random.choice(list(equipment_ids.keys()))
            equipment_id = equipment_ids[equipment_name]
            user = random.choice(users)
            user_id, user_name, role_id = user
            
            # Generate random dates
            days_offset_start = random.randint(-5, 20)
            start_time = now + timedelta(days=days_offset_start, hours=random.randint(0, 23))
            end_time = start_time + timedelta(hours=random.randint(1, 8))
            created_at = start_time - timedelta(days=random.randint(1, 5))
            updated_at = created_at + timedelta(hours=random.randint(1, 24))
            
            # Determine status based on dates
            if start_time < now and end_time < now:
                status = "completed"
            elif start_time < now and end_time > now:
                status = "approved"
            else:
                status = random.choice(status_options)
            
            # Determine user role
            user_role = "student" if role_id == 2 else "faculty"
            
            # Create booking
            rejection_reason = None if status != "rejected" else "Conflicting schedule with higher priority research"
            purpose = f"Research project on {random.choice(['AI', 'ML', 'IoT', 'Computer Vision', 'Network Security', 'Data Science'])}"
            
            cursor.execute(
                """
                INSERT INTO equipment_bookings (equipment_id, user_id, user_name, user_role, 
                start_time, end_time, purpose, status, created_at, updated_at, rejection_reason) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    equipment_id, 
                    user_id, 
                    user_name, 
                    user_role,
                    start_time, 
                    end_time, 
                    purpose, 
                    status, 
                    created_at, 
                    updated_at, 
                    rejection_reason
                )
            )
            bookings_added += 1
        except Exception as e:
            print(f"Error inserting booking {i}: {e}")
    
    conn.commit()
    print(f"Added {bookings_added} equipment bookings.")

# Main function
def main():
    try:
        clear_existing_data()
        category_ids = seed_equipment_categories()
        equipment_ids = seed_equipment(category_ids)
        seed_equipment_bookings(equipment_ids)
        print("Equipment data seeding completed successfully!")
    except Exception as e:
        print(f"Error seeding data: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    main()
