from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from models import EquipmentCategory, Equipment, EquipmentBooking
from database import get_db
from dependencies import get_user_from_session
from middleware import permission_required
import uuid

router = APIRouter(
    prefix="/api/equipment",
    tags=["equipment"],
    responses={404: {"description": "Not found"}},
)

# Schemas
class EquipmentCategorySchema(BaseModel):
    id: int
    name: str
    icon: Optional[str] = None
    description: Optional[str] = None
    class Config:
        from_attributes = True

class EquipmentSchema(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    categoryId: int = Field(..., alias="category_id")
    specifications: Optional[str] = None
    quantity: int
    available: int
    image: Optional[str] = None
    location: Optional[str] = None
    requiresApproval: bool = Field(..., alias="requires_approval")
    class Config:
        from_attributes = True
        populate_by_name = True

class BookingSchema(BaseModel):
    id: int
    equipmentId: int = Field(..., alias="equipment_id")
    userId: int = Field(..., alias="user_id")
    userName: str = Field(..., alias="user_name")
    userRole: str = Field(..., alias="user_role")
    startTime: datetime = Field(..., alias="start_time")
    endTime: datetime = Field(..., alias="end_time")
    purpose: Optional[str] = None
    status: str
    createdAt: datetime = Field(..., alias="created_at")
    updatedAt: datetime = Field(..., alias="updated_at")
    rejectionReason: Optional[str] = Field(None, alias="rejection_reason")
    class Config:
        from_attributes = True
        populate_by_name = True

class BookingCreateSchema(BaseModel):
    equipmentId: int
    startTime: datetime
    endTime: datetime
    purpose: Optional[str] = None

# GET all categories (all roles)
@router.get("/categories", response_model=List[EquipmentCategorySchema])
def get_categories(db: Session = Depends(get_db)):
    return db.query(EquipmentCategory).all()

# PATCH update category (OFFICER only)
class EquipmentCategoryUpdateSchema(BaseModel):
    name: Optional[str] = None
    icon: Optional[str] = None
    description: Optional[str] = None

@router.patch("/categories/{category_id}", response_model=EquipmentCategorySchema, dependencies=[Depends(permission_required("MANAGE_EQUIPMENT"))])
def update_category(
    category_id: int,
    update: EquipmentCategoryUpdateSchema,
    db: Session = Depends(get_db)
):
    category = db.query(EquipmentCategory).filter(EquipmentCategory.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    for field, value in update.dict(exclude_unset=True).items():
        setattr(category, field, value)
    db.commit()
    db.refresh(category)
    return category

# DELETE category (OFFICER only)
@router.delete("/categories/{category_id}", response_model=dict, dependencies=[Depends(permission_required("MANAGE_EQUIPMENT"))])
def delete_category(
    category_id: int,
    db: Session = Depends(get_db)
):
    category = db.query(EquipmentCategory).filter(EquipmentCategory.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    db.delete(category)
    db.commit()
    return {"success": True, "message": "Category deleted."}

# GET all equipment (all roles)
@router.get("/", response_model=List[EquipmentSchema])
def get_equipment(db: Session = Depends(get_db)):
    return db.query(Equipment).all()

# POST new equipment (OFFICER only)
class EquipmentCreateSchema(BaseModel):
    name: str
    description: Optional[str] = None
    categoryId: int = Field(..., alias="category_id")
    specifications: Optional[str] = None
    quantity: int
    available: int
    image: Optional[str] = None
    location: Optional[str] = None
    requiresApproval: bool = Field(False, alias="requires_approval")
    class Config:
        from_attributes = True
        populate_by_name = True

@router.post("/", response_model=EquipmentSchema, dependencies=[Depends(permission_required("MANAGE_EQUIPMENT"))])
def create_equipment(
    equipment: EquipmentCreateSchema,
    db: Session = Depends(get_db)
):
    # Check category exists
    category = db.query(EquipmentCategory).filter(EquipmentCategory.id == equipment.categoryId).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    # Add equipment
    db_equipment = Equipment(
        name=equipment.name,
        description=equipment.description,
        category_id=equipment.categoryId,
        specifications=equipment.specifications,
        quantity=equipment.quantity,
        available=equipment.available,
        image=equipment.image,
        location=equipment.location,
        requires_approval=equipment.requiresApproval
    )
    db.add(db_equipment)
    db.commit()
    db.refresh(db_equipment)
    return db_equipment

# GET bookings for a user (all roles, but filtered by user)
from fastapi import Query

@router.get(
    "/bookings",
    response_model=List[BookingSchema],
    dependencies=[Depends(permission_required("VIEW_EQUIPMENT_BOOKINGS"))]
)
def get_user_bookings(
    userId: int = Query(None, description="User ID to filter bookings (officer only)"),
    db: Session = Depends(get_db),
    user = Depends(get_user_from_session)
):
    # Officers can search by userId, others see their own bookings
    if user["role"]["name"] == "OFFICER":
        if userId is not None:
            return db.query(EquipmentBooking).filter(EquipmentBooking.user_id == userId).all()
        else:
            return db.query(EquipmentBooking).all()
    return db.query(EquipmentBooking).filter(EquipmentBooking.user_id == user["id"]).all()


# POST booking (only TEACHER, FACULTY, STUDENT)
@router.post("/bookings", response_model=BookingSchema, dependencies=[Depends(permission_required("BOOK_EQUIPMENT"))])
def create_booking(
    booking: BookingCreateSchema,
    db: Session = Depends(get_db),
    user = Depends(get_user_from_session)
):
    equipment = db.query(Equipment).filter(Equipment.id == booking.equipmentId).first()
    if not equipment:
        raise HTTPException(status_code=404, detail="Equipment not found")
    if equipment.available <= 0:
        raise HTTPException(status_code=400, detail="Equipment not available")
    # Set status based on approval requirement
    status_val = "pending" if equipment.requires_approval else "approved"
    now = datetime.utcnow()
    booking_id = str(uuid.uuid4())
    db_booking = EquipmentBooking(
        equipment_id=booking.equipmentId,
        user_id=user["id"],
        user_name=user["name"],
        user_role=user["role"]["name"],
        start_time=booking.startTime,
        end_time=booking.endTime,
        purpose=booking.purpose,
        status=status_val,
        created_at=now,
        updated_at=now
    )
    db.add(db_booking)
    # Decrease available if instant approve
    if status_val == "approved":
        equipment.available -= 1
    db.commit()
    db.refresh(db_booking)
    return db_booking

# PATCH approve/reject (OFFICER only)
class BookingApprovalSchema(BaseModel):
    status: str  # "approved" or "rejected"
    rejectionReason: Optional[str] = None

@router.patch("/bookings/{booking_id}", response_model=BookingSchema, dependencies=[Depends(permission_required("APPROVE_EQUIPMENT_BOOKING"))])
def approve_booking(
    booking_id: str,
    approval: BookingApprovalSchema,
    db: Session = Depends(get_db),
    user = Depends(get_user_from_session)
):
    booking = db.query(EquipmentBooking).filter(EquipmentBooking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    if booking.status not in ["pending"]:
        raise HTTPException(status_code=400, detail="Booking is not pending.")
    booking.status = approval.status
    booking.updated_at = datetime.utcnow()
    if approval.status == "rejected":
        booking.rejection_reason = approval.rejectionReason
    elif approval.status == "approved":
        # Decrease available if approved now
        equipment = db.query(Equipment).filter(Equipment.id == booking.equipment_id).first()
        if equipment and equipment.available > 0:
            equipment.available -= 1
        else:
            raise HTTPException(status_code=400, detail="Equipment not available for approval.")
    db.commit()
    db.refresh(booking)
    return booking
