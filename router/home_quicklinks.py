from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from models_quicklinks import QuickLink
import database

# Create router
router = APIRouter(
    prefix="/api",
    tags=["quick-links"],
    responses={404: {"description": "Not found"}},
)

# Pydantic models for request/response validation
class QuickLinkResponse(BaseModel):
    id: int
    title: str
    description: str
    href: str
    icon: str
    category: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class QuickLinksResponse(BaseModel):
    links: List[QuickLinkResponse]

@router.get("/quick-links", response_model=QuickLinksResponse)
async def get_quick_links(
    limit: int = Query(20, description="Number of quick links to return"),
    category: Optional[str] = Query(None, description="Filter by category"),
    db: Session = Depends(database.get_db)
):
    """
    Get a list of quick links.
    
    This endpoint returns a list of quick links, with optional filtering by category.
    
    Parameters:
    - limit: Maximum number of quick links to return (default: 20)
    - category: Filter by category (e.g., 'Academic', 'Research', 'Student')
    
    Returns:
    - Object containing a list of quick link objects
    """
    try:
        query = db.query(QuickLink)
        
        # Apply filters if provided
        if category:
            query = query.filter(QuickLink.category == category)
        
        # Get quick links
        quick_links = query.limit(limit).all()
        return {"links": quick_links}
        
    except Exception as e:
        # Log the error for debugging
        print(f"Error fetching quick links: {str(e)}")
        # Return empty list if there's an error (e.g., table doesn't exist)
        return {"links": []}
