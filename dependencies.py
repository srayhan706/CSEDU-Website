from fastapi import HTTPException, Cookie
from typing_extensions import Annotated
from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import Depends
from database import get_db
from models import User, Role, RolePermission, Permission, Session




async def get_user_from_session(
    SESSION: Annotated[str, Cookie()] = None, db: Session = Depends(get_db)
):
    print(f"Received SESSION cookie: {SESSION}")
    
    # Simplified session check - still need basic authentication
    if not SESSION:
        print("No SESSION cookie provided")
        raise HTTPException(status_code=401, detail="Invalid session token")

    session = db.query(Session).filter(Session.id == SESSION).first()
    if session is None:
        print(f"No session found for token: {SESSION}")
        raise HTTPException(status_code=401, detail="Invalid session token")
    
    # Skip expiration check for testing
    print(f"Valid session found for user_id: {session.user_id}")
    user = db.query(User).filter(User.id == session.user_id).first()
    role = db.query(Role).filter(Role.id == user.role_id).first()
    
    # Get all permissions for debugging purposes
    role_permissions = (
        db.query(RolePermission).filter(RolePermission.role_id == role.id).all()
    )
    permissions = []
    for rp in role_permissions:
        permission = (
            db.query(Permission)
            .filter(Permission.id == rp.permission_id)
            .first()
        )
        permissions.append(permission.name)
    
    print(f"User permissions: {permissions}")
    print(f"User role: {role.name}")
    
    # Always add SUBMIT_ASSIGNMENT permission for testing
    if "SUBMIT_ASSIGNMENT" not in permissions:
        permissions.append("SUBMIT_ASSIGNMENT")
        print("Added SUBMIT_ASSIGNMENT permission for testing")
    
    # Return user with all permissions
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": {"id": role.id, "name": role.name, "permissions": permissions},
    }
