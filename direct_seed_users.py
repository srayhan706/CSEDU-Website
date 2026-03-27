from sqlalchemy.orm import Session
from database import get_db
from models import User, Role, Permission, RolePermission
from datetime import datetime
import bcrypt

def hash_password(password):
    # Generate a salt and hash the password
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def seed_users():
    db = next(get_db())
    
    # Check if roles already exist
    admin_role = db.query(Role).filter(Role.name == "admin").first()
    faculty_role = db.query(Role).filter(Role.name == "faculty").first()
    student_role = db.query(Role).filter(Role.name == "student").first()
    
    # Create roles if they don't exist
    if not admin_role:
        admin_role = Role(name="admin")
        db.add(admin_role)
        
    if not faculty_role:
        faculty_role = Role(name="faculty")
        db.add(faculty_role)
        
    if not student_role:
        student_role = Role(name="student")
        db.add(student_role)
    
    db.commit()
    
    # Refresh roles to get their IDs
    db.refresh(admin_role)
    db.refresh(faculty_role)
    db.refresh(student_role)
    
    # Create permissions if they don't exist
    permissions = [
        {"name": "MANAGE_USERS", "category": "admin"},
        {"name": "MANAGE_ROLES", "category": "admin"},
        {"name": "MANAGE_ASSIGNMENTS", "category": "faculty"},
        {"name": "SUBMIT_ASSIGNMENT", "category": "student"},
        {"name": "VIEW_GRADES", "category": "student"},
        {"name": "MANAGE_COURSES", "category": "faculty"},
        {"name": "BOOK_EQUIPMENT", "category": "general"},
        {"name": "BOOK_LAB", "category": "general"}
    ]
    
    for perm_data in permissions:
        perm = db.query(Permission).filter(Permission.name == perm_data["name"]).first()
        if not perm:
            perm = Permission(name=perm_data["name"], category=perm_data["category"])
            db.add(perm)
    
    db.commit()
    
    # Assign permissions to roles
    # Admin gets all permissions
    admin_perms = db.query(Permission).all()
    for perm in admin_perms:
        role_perm = db.query(RolePermission).filter(
            RolePermission.role_id == admin_role.id,
            RolePermission.permission_id == perm.id
        ).first()
        if not role_perm:
            role_perm = RolePermission(role_id=admin_role.id, permission_id=perm.id)
            db.add(role_perm)
    
    # Faculty gets faculty-specific permissions
    faculty_perms = db.query(Permission).filter(
        Permission.name.in_(["MANAGE_ASSIGNMENTS", "MANAGE_COURSES", "BOOK_EQUIPMENT", "BOOK_LAB"])
    ).all()
    for perm in faculty_perms:
        role_perm = db.query(RolePermission).filter(
            RolePermission.role_id == faculty_role.id,
            RolePermission.permission_id == perm.id
        ).first()
        if not role_perm:
            role_perm = RolePermission(role_id=faculty_role.id, permission_id=perm.id)
            db.add(role_perm)
    
    # Student gets student-specific permissions
    student_perms = db.query(Permission).filter(
        Permission.name.in_(["SUBMIT_ASSIGNMENT", "VIEW_GRADES", "BOOK_EQUIPMENT", "BOOK_LAB"])
    ).all()
    for perm in student_perms:
        role_perm = db.query(RolePermission).filter(
            RolePermission.role_id == student_role.id,
            RolePermission.permission_id == perm.id
        ).first()
        if not role_perm:
            role_perm = RolePermission(role_id=student_role.id, permission_id=perm.id)
            db.add(role_perm)
    
    db.commit()
    
    # Create users if they don't exist
    admin_user = db.query(User).filter(User.email == "admin@csedu.edu").first()
    if not admin_user:
        admin_user = User(
            name="Admin User",
            email="admin@csedu.edu",
            password=hash_password("admin123"),
            role_id=admin_role.id,
            username="admin",
            contact="01700000000",
            created_at=datetime.utcnow()
        )
        db.add(admin_user)
    
    # Create faculty users
    faculty_users = [
        {
            "name": "Dr. Md. Shariful Islam",
            "email": "shariful@csedu.edu",
            "password": "faculty123",
            "username": "shariful",
            "contact": "01711111111"
        },
        {
            "name": "Dr. Anisur Rahman",
            "email": "anis@csedu.edu",
            "password": "faculty123",
            "username": "anis",
            "contact": "01722222222"
        },
        {
            "name": "Dr. Saifuddin Mahmud",
            "email": "saif@csedu.edu",
            "password": "faculty123",
            "username": "saif",
            "contact": "01733333333"
        }
    ]
    
    for faculty_data in faculty_users:
        faculty = db.query(User).filter(User.email == faculty_data["email"]).first()
        if not faculty:
            faculty = User(
                name=faculty_data["name"],
                email=faculty_data["email"],
                password=hash_password(faculty_data["password"]),
                role_id=faculty_role.id,
                username=faculty_data["username"],
                contact=faculty_data["contact"],
                created_at=datetime.utcnow()
            )
            db.add(faculty)
    
    # Create student users
    student_users = [
        {
            "name": "Fahim Ahmed",
            "email": "fahim@student.csedu.edu",
            "password": "student123",
            "username": "fahim",
            "contact": "01744444444"
        },
        {
            "name": "Tasnia Tabassum",
            "email": "tasnia@student.csedu.edu",
            "password": "student123",
            "username": "tasnia",
            "contact": "01755555555"
        },
        {
            "name": "Rakib Hasan",
            "email": "rakib@student.csedu.edu",
            "password": "student123",
            "username": "rakib",
            "contact": "01766666666"
        },
        {
            "name": "Nusrat Jahan",
            "email": "nusrat@student.csedu.edu",
            "password": "student123",
            "username": "nusrat",
            "contact": "01777777777"
        },
        {
            "name": "Karim Ahmed",
            "email": "karim@student.csedu.edu",
            "password": "student123",
            "username": "karim",
            "contact": "01788888888"
        }
    ]
    
    for student_data in student_users:
        student = db.query(User).filter(User.email == student_data["email"]).first()
        if not student:
            student = User(
                name=student_data["name"],
                email=student_data["email"],
                password=hash_password(student_data["password"]),
                role_id=student_role.id,
                username=student_data["username"],
                contact=student_data["contact"],
                created_at=datetime.utcnow()
            )
            db.add(student)
    
    db.commit()
    print("Successfully seeded users, roles, and permissions!")

if __name__ == "__main__":
    seed_users()
