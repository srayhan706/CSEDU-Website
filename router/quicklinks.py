from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from typing import List, Optional
from database import get_db
from models_quicklinks import QuickLink
from pydantic import BaseModel
from datetime import datetime
from dependencies import get_user_from_session
from middleware import permission_required

router = APIRouter(
    prefix="/api/quick-links",
    tags=["quick-links"],
    responses={404: {"description": "Not found"}},
)

class QuickLinkSchema(BaseModel):
    id: Optional[int]
    title: str
    description: str
    href: str
    icon: str
    category: str

    class Config:
        orm_mode = True

@router.get("/", response_model=dict)
def get_quick_links(
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get all quick links with optional filtering by category.
    """
    query = db.query(QuickLink)
    
    # Apply category filter if provided
    if category:
        query = query.filter(QuickLink.category == category)
    
    # Order by category and title
    query = query.order_by(QuickLink.category, QuickLink.title)
    
    quick_links = query.all()
    
    # Convert to response format
    result = []
    for link in quick_links:
        result.append({
            "id": link.id,
            "title": link.title,
            "description": link.description,
            "href": link.href,
            "icon": link.icon,
            "category": link.category
        })
    
    return {"links": result}

@router.get("/{link_id}", response_model=QuickLinkSchema)
def get_quick_link(link_id: int, db: Session = Depends(get_db)):
    """
    Get a specific quick link by ID.
    """
    link = db.query(QuickLink).filter(QuickLink.id == link_id).first()
    
    if not link:
        raise HTTPException(status_code=404, detail=f"Quick link with ID {link_id} not found")
    
    return {
        "id": link.id,
        "title": link.title,
        "description": link.description,
        "href": link.href,
        "icon": link.icon,
        "category": link.category
    }

@router.post("/", response_model=QuickLinkSchema)
def create_quick_link(
    link_data: QuickLinkSchema,
    db: Session = Depends(get_db),
    current_user = Depends(get_user_from_session)
):
    """
    Create a new quick link (requires admin privileges).
    """
    # Check if user has admin privileges
    if not permission_required(["admin"])(current_user):
        raise HTTPException(status_code=403, detail="Not authorized to create quick links")
    
    new_link = QuickLink(
        title=link_data.title,
        description=link_data.description,
        href=link_data.href,
        icon=link_data.icon,
        category=link_data.category,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(new_link)
    db.commit()
    db.refresh(new_link)
    
    return {
        "id": new_link.id,
        "title": new_link.title,
        "description": new_link.description,
        "href": new_link.href,
        "icon": new_link.icon,
        "category": new_link.category
    }
