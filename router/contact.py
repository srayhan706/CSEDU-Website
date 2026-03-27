from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from database import get_db
from models_contact import ContactMessage

router = APIRouter(
    prefix="/api",
    tags=["contact"],
)

class ContactMessageCreate(BaseModel):
    name: str
    email: EmailStr
    subject: str
    message: str
    phone: Optional[str] = None

class ContactMessageResponse(BaseModel):
    id: str
    name: str
    email: str
    subject: str
    message: str
    phone: Optional[str] = None
    created_at: datetime
    
    class Config:
        orm_mode = True

@router.post("/contact", response_model=ContactMessageResponse, status_code=status.HTTP_201_CREATED)
def create_contact_message(message: ContactMessageCreate, db: Session = Depends(get_db)):
    """
    Create a new contact message
    """
    db_message = ContactMessage(
        name=message.name,
        email=message.email,
        subject=message.subject,
        message=message.message,
        phone=message.phone
    )
    
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    
    return db_message

@router.get("/contact", response_model=List[ContactMessageResponse])
def get_contact_messages(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Get all contact messages (for admin use)
    """
    return db.query(ContactMessage).order_by(ContactMessage.created_at.desc()).offset(skip).limit(limit).all()
