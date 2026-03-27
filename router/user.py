import utils
import database
from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status
from database import get_db
from pydantic import BaseModel, EmailStr
from dependencies import get_user_from_session
from models import User, Session as SessionModel, Faculty
from fastapi.responses import JSONResponse
from datetime import datetime
from typing import List, Optional
from middleware import permission_required
from models import Role, RolePermission, Permission, Faculty
from pydantic import BaseModel
from sqlalchemy.orm import joinedload

router = APIRouter(
    prefix="/api/user",
    tags=["user"],
    responses={404: {"description": "Route not found"}},
)


class NewUserRequest(BaseModel):
    name: str
    email: str
    password: str
    contact: str = None
    username: str = None
    role_id: int


@router.get("/allUsers")
async def all_users(
    user: User = Depends(permission_required("LIST_ALL_USERS")),
    db: Session = Depends(get_db),
):
    # Query all users and roles in a more optimized way
    users = db.query(User).all()

    response = []

    for user in users:
        role = db.query(Role).filter(Role.id == user.role_id).first()

        # Fetch permissions in a single query
        role_permissions = (
            db.query(Permission)
            .join(RolePermission)
            .filter(RolePermission.role_id == role.id)
            .all()
        )
        permissions = [permission.name for permission in role_permissions]

        # Room data removed as Room model is no longer available

        # Construct the response for each user
        user_response = {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": {"id": role.id, "name": role.name, "permissions": permissions},
            "username": user.username,
            "contact": user.contact,
            "created_at": user.created_at.strftime(
                "%Y-%m-%d %H:%M:%S"
            ),  # Convert datetime to string
        }

        # Append the user response to the list
        response.append(user_response)

    # Return the final response as JSON
    return JSONResponse(status_code=200, content={"users": response})


class FacultyMemberResponse(BaseModel):
    id: int
    name: str
    email: str
    designation: str
    department: str
    image: Optional[str] = None
    office: Optional[str] = None
    website: Optional[str] = None
    bio: Optional[str] = None
    short_bio: Optional[str] = None
    research_interests: Optional[list] = None
    office_hours: Optional[str] = None

    class Config:
        orm_mode = True
        from_attributes = True

@router.get("/faculty", response_model=List[FacultyMemberResponse])
async def get_faculty_members(
    search: Optional[str] = None,
    department: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get all faculty members with optional filtering.
    This endpoint is used by the meetings page to populate the faculty selector.
    """
    query = db.query(User).join(Faculty, User.id == Faculty.id)
    
    # Apply filters if provided
    if search:
        search = f"%{search.lower()}%"
        query = query.filter(
            (User.name.ilike(search)) |
            (User.email.ilike(search)) |
            (Faculty.department.ilike(search)) |
            (Faculty.designation.ilike(search))
        )
    
    if department:
        query = query.filter(Faculty.department == department)
    
    # Execute query and format response
    faculty_members = query.options(joinedload(User.faculty)).all()
    
    # Transform to response model
    response = []
    for user in faculty_members:
        faculty_data = user.faculty
        response.append({
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "designation": faculty_data.designation,
            "department": faculty_data.department,
            "image": faculty_data.image,
            "office": faculty_data.office,
            "website": faculty_data.website,
            "bio": faculty_data.bio,
            "short_bio": faculty_data.short_bio,
            "research_interests": faculty_data.research_interests,
            "office_hours": faculty_data.office_hours
        })
    
    return response


@router.post("/createUser")
async def create_user(
    userRequest: NewUserRequest,
    user: User = Depends(permission_required("CREATE_USER")),
    db: Session = Depends(get_db),
):
    latest_user_id = (
        0
        if db.query(User).count() == 0
        else db.query(User).order_by(User.id.desc()).first().id
    )

    # check if email already exists
    user = db.query(User).filter(User.email == userRequest.email).first()
    if user is not None:
        return JSONResponse(
            status_code=400, content={"message": "Email already exists"}
        )

    newUser = User(
        id=latest_user_id + 1,
        name=userRequest.name,
        email=userRequest.email,
        password=utils.hash(userRequest.password),  # BAD: encrypted, not hashed
        role_id=userRequest.role_id,  # role id from path parameter
        # 0 - > ADMIN
        # 1 - > CHAIRMAN
        # 2 - > TEACHER
        username=userRequest.username,
        contact=userRequest.contact,
    )
    db.add(newUser)
    db.commit()
    utils.sendEmail(
        "Welcome to our platform",
        f"Hello {userRequest.name},\n\nWelcome to our platform. You have successfully registered.\n\nBest Regards,\nTeam",
        userRequest.email,
    )

    return JSONResponse(status_code=201, content={"message": "User created"})



