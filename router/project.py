from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime
from enum import Enum

from database import get_db
from models import Project, ProjectCategory, ProjectType
from middleware import permission_required

# Project router
project_router = APIRouter(
    prefix="/api/projects",
    tags=["projects"]
)

# Valid project categories and types
VALID_PROJECT_CATEGORIES = [
    "machine_learning", "web_development", "mobile_app", 
    "algorithms", "iot", "security", "robotics", "graphics"
]

VALID_PROJECT_TYPES = ["student", "faculty"]

# Project schemas
class TeamMember(BaseModel):
    name: str
    role: Optional[str] = None

class ProjectBase(BaseModel):
    title: str
    summary: str
    abstract: str
    supervisor_id: int
    year: int
    category: str
    type: str
    tags: Optional[List[str]] = None
    team: Optional[List[TeamMember]] = None
    course: Optional[str] = None
    team_size: Optional[int] = None
    completion_date: datetime
    technologies: Optional[List[str]] = None
    key_features: Optional[List[str]] = None
    achievements: Optional[List[str]] = None
    demo_link: Optional[str] = None
    github_link: Optional[str] = None
    paper_link: Optional[str] = None
    contact_email: Optional[str] = None
    
    @validator('category')
    def validate_category(cls, v):
        if v not in VALID_PROJECT_CATEGORIES:
            raise ValueError(f"Category must be one of {VALID_PROJECT_CATEGORIES}")
        return v
    
    @validator('type')
    def validate_type(cls, v):
        if v not in VALID_PROJECT_TYPES:
            raise ValueError(f"Type must be one of {VALID_PROJECT_TYPES}")
        return v


class ProjectCreate(ProjectBase):
    pass


class ProjectResponse(BaseModel):
    id: int
    title: str
    summary: str
    abstract: str
    supervisor: str  # Frontend expects supervisor as an name
    year: int
    category: str
    type: str
    tags: Optional[List[str]] = None
    team: Optional[List[TeamMember]] = None
    course: Optional[str] = None
    teamSize: Optional[int] = None
    completionDate: datetime
    technologies: Optional[List[str]] = None
    keyFeatures: Optional[List[str]] = None
    achievements: Optional[List[str]] = None
    demoLink: Optional[str] = None
    githubLink: Optional[str] = None
    paperLink: Optional[str] = None
    contactEmail: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        
    # Map snake_case database fields to camelCase response fields
    @classmethod
    def from_orm(cls, obj):
        # Create a dict from the ORM object
        data = {
            "id": obj.id,
            "title": obj.title,
            "summary": obj.summary,
            "abstract": obj.abstract,
            "supervisor": str(obj.supervisor_id),  # Convert ID to string as a placeholder
            "year": obj.year,
            "category": obj.category,
            "type": obj.type,
            "tags": obj.tags,
            "team": obj.team,
            "course": obj.course,
            "teamSize": obj.team_size,  # Map team_size to teamSize
            "completionDate": obj.completion_date,  # Map completion_date to completionDate
            "technologies": obj.technologies,
            "keyFeatures": obj.key_features,  # Map key_features to keyFeatures
            "achievements": obj.achievements,
            "demoLink": obj.demo_link,  # Map demo_link to demoLink
            "githubLink": obj.github_link,  # Map github_link to githubLink
            "paperLink": obj.paper_link,  # Map paper_link to paperLink
            "contactEmail": obj.contact_email,  # Map contact_email to contactEmail
            "created_at": obj.created_at,
            "updated_at": obj.updated_at
        }
        return cls(**data)


# Project endpoints
class ProjectsListResponse(BaseModel):
    projects: List[ProjectResponse]

@project_router.get("", response_model=ProjectsListResponse)
async def get_projects(db: Session = Depends(get_db)):
    """
    Get all projects
    """
    projects = db.query(Project).all()
    # Import User model here to avoid circular imports
    from models import User
    
    # Convert each project to ProjectResponse format with supervisor name
    project_responses = []
    for project in projects:
        # Get supervisor for each project
        supervisor = db.query(User).filter(User.id == project.supervisor_id).first()
        supervisor_name = supervisor.name if supervisor else "Unknown"
        
        # Create response with supervisor name
        response = ProjectResponse.from_orm(project)
        response.supervisor = supervisor_name
        project_responses.append(response)
        
    return {"projects": project_responses}

@project_router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(project_id: int, db: Session = Depends(get_db)):
    """
    Get a specific project by ID
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID {project_id} not found"
        )
    
    # Get supervisor name
    from models import User
    supervisor = db.query(User).filter(User.id == project.supervisor_id).first()
    supervisor_name = supervisor.name if supervisor else "Unknown"
    
    # Convert the project to ProjectResponse format and set supervisor name
    response = ProjectResponse.from_orm(project)
    response.supervisor = supervisor_name
    return response


@project_router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(permission_required("MANAGE_PROJECTS"))
):
    """
    Create a new project (requires MANAGE_PROJECTS permission)
    """
    # Check if supervisor exists
    from models import User
    supervisor = db.query(User).filter(User.id == project.supervisor_id).first()
    print(supervisor.name)
    if not supervisor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Supervisor with ID {project.supervisor_id} not found"
        )
    
    # Create project
    db_project = Project(**project.model_dump())
    
    db.add(db_project)
    db.commit()
    db.refresh(db_project)

    # Convert to ProjectResponse format and set supervisor name
    response = ProjectResponse.from_orm(db_project)
    response.supervisor = supervisor.name
    return response


@project_router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    project: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(permission_required("MANAGE_PROJECTS"))
):
    """
    Update a project (requires MANAGE_PROJECTS permission)
    """
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if not db_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID {project_id} not found"
        )
    
    # Check if supervisor exists
    from models import User
    supervisor = db.query(User).filter(User.id == project.supervisor_id).first()
    if not supervisor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Supervisor with ID {project.supervisor_id} not found"
        )
    
    # Update project attributes
    for key, value in project.model_dump().items():
        setattr(db_project, key, value)
    
    db.commit()
    db.refresh(db_project)
    
    # Get supervisor name
    supervisor = db.query(User).filter(User.id == db_project.supervisor_id).first()
    supervisor_name = supervisor.name if supervisor else "Unknown"
    
    # Convert to ProjectResponse format and set supervisor name
    response = ProjectResponse.from_orm(db_project)
    response.supervisor = supervisor_name
    return response


@project_router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(permission_required("MANAGE_PROJECTS"))
):
    """
    Delete a project (requires MANAGE_PROJECTS permission)
    """
    db_project = db.query(Project).filter(Project.id == project_id).first()
    if not db_project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID {project_id} not found"
        )
    
    db.delete(db_project)
    db.commit()
    
    return None
