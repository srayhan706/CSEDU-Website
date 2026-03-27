import os
import sys
from datetime import datetime, timedelta
import random

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the models
from database import SessionLocal, engine
from models import Base, EquipmentCategory, Equipment, EquipmentBooking, User

def setup_equipment():
    db = SessionLocal()
    
    # Check if equipment categories already exist
    existing_categories = db.query(EquipmentCategory).count()
    if existing_categories > 0:
        print("Equipment categories already exist. Skipping creation.")
        db.close()
        return
    
    print("Creating equipment categories...")
    
    # Create equipment categories
    categories = [
        EquipmentCategory(
            name="Computing Hardware",
            icon="Cpu",
            description="High-performance computing resources including GPUs, servers, and specialized processors"
        ),
        EquipmentCategory(
            name="Sensors & IoT",
            icon="Wifi",
            description="Various sensors, actuators, and Internet of Things devices for research and projects"
        ),
        EquipmentCategory(
            name="Storage & Memory",
            icon="Database",
            description="Storage devices and memory modules for data-intensive applications"
        ),
        EquipmentCategory(
            name="Mobile & Embedded",
            icon="Smartphone",
            description="Mobile devices and embedded systems for testing and development"
        ),
        EquipmentCategory(
            name="Networking",
            icon="Layers",
            description="Networking equipment for communication and distributed systems research"
        )
    ]
    
    db.add_all(categories)
    db.commit()
    
    # Refresh to get the IDs
    for category in categories:
        db.refresh(category)
    
    print("Creating equipment items...")
    
    # Create equipment items
    equipment_items = [
        Equipment(
            name="NVIDIA RTX 4090 GPU",
            description="High-end graphics processing unit for AI and deep learning applications",
            category_id=categories[0].id,
            specifications="24GB GDDR6X, 16384 CUDA cores, 2.52 GHz boost clock",
            quantity=4,
            available=2,
            image="/assets/equipment/gpu.jpg",
            location="AI Lab (Room 302)",
            requires_approval=True
        ),
        Equipment(
            name="Temperature & Humidity Sensor Kit",
            description="Precision sensors for environmental monitoring in IoT projects",
            category_id=categories[1].id,
            specifications="DHT22 sensors, -40 to 80°C range, ±0.5°C accuracy",
            quantity=20,
            available=15,
            image="/assets/equipment/temp-sensor.jpg",
            location="IoT Lab (Room 201)",
            requires_approval=False
        ),
        Equipment(
            name="High-Performance Server",
            description="Multi-core server for distributed computing and virtualization",
            category_id=categories[0].id,
            specifications="AMD EPYC 7763, 64 cores, 128 threads, 256GB RAM",
            quantity=2,
            available=1,
            image="/assets/equipment/server.jpg",
            location="Server Room (Room 405)",
            requires_approval=True
        ),
        Equipment(
            name="Motion Capture System",
            description="Advanced motion tracking system for computer vision research",
            category_id=categories[1].id,
            specifications="12-camera setup, 120fps, sub-millimeter accuracy",
            quantity=1,
            available=1,
            image="/assets/equipment/motion-capture.jpg",
            location="Graphics Lab (Room 304)",
            requires_approval=True
        ),
        Equipment(
            name="SSD Storage Array",
            description="High-speed storage array for data-intensive applications",
            category_id=categories[2].id,
            specifications="10TB total, NVMe SSDs, 7000MB/s read, 5000MB/s write",
            quantity=3,
            available=3,
            image="/assets/equipment/ssd-array.jpg",
            location="Data Science Lab (Room 303)",
            requires_approval=False
        ),
        Equipment(
            name="Raspberry Pi Kit",
            description="Complete Raspberry Pi development kit with accessories",
            category_id=categories[3].id,
            specifications="Raspberry Pi 4B, 8GB RAM, 64GB SD, sensors, display",
            quantity=15,
            available=8,
            image="/assets/equipment/raspberry-pi.jpg",
            location="IoT Lab (Room 201)",
            requires_approval=False
        ),
        Equipment(
            name="Network Testing Kit",
            description="Professional network testing and analysis equipment",
            category_id=categories[4].id,
            specifications="Includes packet analyzer, cable tester, signal generator",
            quantity=5,
            available=4,
            image="/assets/equipment/network-kit.jpg",
            location="Networking Lab (Room 205)",
            requires_approval=True
        ),
        Equipment(
            name="Drone Development Platform",
            description="Programmable drone for autonomous flight research",
            category_id=categories[3].id,
            specifications="Quadcopter, 4K camera, 30min flight time, SDK access",
            quantity=3,
            available=2,
            image="/assets/equipment/drone.jpg",
            location="Robotics Lab (Room 306)",
            requires_approval=True
        ),
        Equipment(
            name="VR Development Kit",
            description="Virtual reality headset and controllers for immersive applications",
            category_id=categories[3].id,
            specifications="6DOF tracking, 2160x2160 per eye, 120Hz refresh rate",
            quantity=4,
            available=3,
            image="/assets/equipment/vr-kit.jpg",
            location="Graphics Lab (Room 304)",
            requires_approval=True
        ),
        Equipment(
            name="FPGA Development Board",
            description="Field-programmable gate array for hardware acceleration projects",
            category_id=categories[0].id,
            specifications="Xilinx Artix-7, 100K logic cells, DDR3 memory",
            quantity=10,
            available=7,
            image="/assets/equipment/fpga.jpg",
            location="Digital Systems Lab (Room 203)",
            requires_approval=False
        )
    ]
    
    db.add_all(equipment_items)
    db.commit()
    
    # Refresh to get the IDs
    for item in equipment_items:
        db.refresh(item)
    
    print("Creating sample equipment bookings...")
    
    # Get some users for sample bookings
    users = db.query(User).limit(5).all()
    if not users:
        print("No users found. Skipping booking creation.")
        db.close()
        return
    
    # Create sample bookings
    now = datetime.utcnow()
    bookings = []
    
    # Create bookings with different statuses
    statuses = ["pending", "approved", "rejected", "completed"]
    
    for i in range(10):
        user = random.choice(users)
        equipment = random.choice(equipment_items)
        start_time = now + timedelta(days=random.randint(1, 14))
        end_time = start_time + timedelta(hours=random.randint(1, 48))
        status = random.choice(statuses)
        
        booking = EquipmentBooking(
            equipment_id=equipment.id,
            user_id=user.id,
            user_name=user.name,
            user_role=user.role.name if user.role else 'STUDENT',
            start_time=start_time,
            end_time=end_time,
            purpose=f"Sample booking purpose {i+1}",
            status=status,
            created_at=now - timedelta(days=random.randint(1, 7)),
            updated_at=now - timedelta(days=random.randint(0, 3)),
            rejection_reason="Conflicting schedule with higher priority research" if status == "rejected" else None
        )
        bookings.append(booking)
    
    db.add_all(bookings)
    db.commit()
    
    print("Equipment setup completed successfully!")
    db.close()

if __name__ == "__main__":
    setup_equipment()
