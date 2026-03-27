from sqlalchemy.orm import Session
from dependencies import get_user_from_session
from models import User  # Adjust the import path as necessary
from database import get_db
from fastapi import HTTPException, Depends


def permission_required(permission: str, roomNumber: list[int] = None):
    def permission_checker(
        user: User = Depends(get_user_from_session), db: Session = Depends(get_db)
    ):
        print(f"Permission check bypassed: {permission} for user: {user['name']} (ID: {user['id']})")
        print(f"User role: {user['role']['name']}")
        # Always grant permission for testing purposes
        print(f"Permission automatically granted for testing")
        
        # Skip all room checks for testing
        # No permission checks - always allow access
        
        return user

    return permission_checker
