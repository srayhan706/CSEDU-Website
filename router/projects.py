from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from database import get_db
from models import Project, User, ProjectCategory, ProjectType
from datetime import datetime
from sqlalchemy import desc

router = APIRouter(
    prefix="/api/projects",
    tags=["projects"],
    responses={404: {"description": "Not found"}},
)

# Pydantic models for request and response
class TeamMember(BaseModel):
    name: str
    role: Optional[str] = None

class ProjectResponse(BaseModel):
    id: int
    title: str
    summary: str
    abstract: str
    supervisor: str
    year: int
    category: str
    type: str
    tags: List[str] = []
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
    
    class Config:
        orm_mode = True

@router.get("", response_model=dict)
def get_projects(
    category: Optional[str] = None,
    type: Optional[str] = None,
    year: Optional[int] = None,
    supervisor_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Get all projects with optional filtering
    """
    query = db.query(Project).join(User, Project.supervisor_id == User.id)
    
    if category:
        query = query.filter(Project.category == category)
    
    if type:
        query = query.filter(Project.type == type)
    
    if year:
        query = query.filter(Project.year == year)
    
    if supervisor_id:
        query = query.filter(Project.supervisor_id == supervisor_id)
    
    # Order by most recent completion date
    query = query.order_by(desc(Project.completion_date))
    
    projects_db = query.all()
    
    # Get unique years, categories, and supervisors for filters
    years = db.query(Project.year).distinct().order_by(desc(Project.year)).all()
    years = [year[0] for year in years]
    
    categories = [cat for cat in ProjectCategory.__members__.values()]
    
    supervisors = db.query(User.id, User.name).join(
        Project, User.id == Project.supervisor_id
    ).distinct().all()
    supervisors = [{"id": sup[0], "name": sup[1]} for sup in supervisors]
    
    # Format projects for response
    projects = []
    for project in projects_db:
        # Get supervisor name
        supervisor = db.query(User).filter(User.id == project.supervisor_id).first()
        
        projects.append({
            "id": project.id,
            "title": project.title,
            "summary": project.summary,
            "abstract": project.abstract,
            "supervisor": supervisor.name if supervisor else "Unknown",
            "year": project.year,
            "category": project.category,
            "type": project.type,
            "tags": project.tags if project.tags else [],
            "team": project.team if project.team else [],
            "course": project.course,
            "team_size": project.team_size,
            "completion_date": project.completion_date,
            "technologies": project.technologies if project.technologies else [],
            "key_features": project.key_features if project.key_features else [],
            "achievements": project.achievements if project.achievements else [],
            "demo_link": project.demo_link,
            "github_link": project.github_link,
            "paper_link": project.paper_link,
            "contact_email": project.contact_email
        })
    
    return {
        "projects": projects,
        "filters": {
            "years": years,
            "categories": categories,
            "supervisors": supervisors
        }
    }

@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: int, db: Session = Depends(get_db)):
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
    supervisor = db.query(User).filter(User.id == project.supervisor_id).first()
    
    # Create response
    response = {
        "id": project.id,
        "title": project.title,
        "summary": project.summary,
        "abstract": project.abstract,
        "supervisor": supervisor.name if supervisor else "Unknown",
        "year": project.year,
        "category": project.category,
        "type": project.type,
        "tags": project.tags if project.tags else [],
        "team": project.team if project.team else [],
        "course": project.course,
        "team_size": project.team_size,
        "completion_date": project.completion_date,
        "technologies": project.technologies if project.technologies else [],
        "key_features": project.key_features if project.key_features else [],
        "achievements": project.achievements if project.achievements else [],
        "demo_link": project.demo_link,
        "github_link": project.github_link,
        "paper_link": project.paper_link,
        "contact_email": project.contact_email
    }
    
    return response
