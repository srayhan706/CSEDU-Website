from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime
from database import get_db
from models import FeeCategory, Fee, Transaction, FeeStatus, TransactionStatus, PaymentMethod, User
import enum

router = APIRouter(
    prefix="/api/student/fees",
    tags=["fees"]
)

# Pydantic models for request and response
class FeeStatusEnum(str, enum.Enum):
    PAID = "PAID"
    PENDING = "PENDING"
    OVERDUE = "OVERDUE"

class TransactionStatusEnum(str, enum.Enum):
    COMPLETED = "COMPLETED"
    PENDING = "PENDING"
    FAILED = "FAILED"

class PaymentMethodEnum(str, enum.Enum):
    ONLINE_BANKING = "ONLINE_BANKING"
    MOBILE_BANKING = "MOBILE_BANKING"
    CARD = "CARD"
    CASH = "CASH"
    OTHER = "OTHER"

class FeeCategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None

class FeeCategoryResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True

class FeeCreate(BaseModel):
    name: str
    amount: float
    description: Optional[str] = None
    deadline: datetime
    semester: str
    batch: str
    category_id: Optional[int] = None
    student_id: int

class FeeResponse(BaseModel):
    id: int
    name: str
    amount: float
    description: Optional[str] = None
    deadline: datetime
    status: FeeStatusEnum
    semester: str
    batch: str
    category_id: Optional[int] = None
    student_id: int
    paid_date: Optional[datetime] = None
    paid_amount: Optional[float] = None
    created_at: datetime
    updated_at: datetime
    category: Optional[FeeCategoryResponse] = None

    class Config:
        from_attributes = True

class TransactionCreate(BaseModel):
    amount: float
    description: Optional[str] = None
    payment_method: PaymentMethodEnum
    fee_id: int
    student_id: int
    receipt_url: Optional[str] = None
    transaction_id: Optional[str] = None

class TransactionResponse(BaseModel):
    id: int
    date: datetime
    amount: float
    description: Optional[str] = None
    payment_method: PaymentMethodEnum
    status: TransactionStatusEnum
    receipt_url: Optional[str] = None
    transaction_id: Optional[str] = None
    fee_id: int
    student_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class StudentFeesResponse(BaseModel):
    current_semester: str
    fees: List[FeeResponse]
    transactions: List[TransactionResponse]

# API endpoints
@router.get("/", response_model=StudentFeesResponse)
def get_student_fees(
    student_id: Optional[int] = None,
    semester: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get all fees for a student. If student_id is not provided, it will return fees for all students.
    If semester is provided, it will filter fees by semester.
    """
    # For simplicity, we're not implementing authentication checks
    # In a real app, you'd verify the user has permission to view these fees
    
    query = db.query(Fee)
    
    if student_id:
        query = query.filter(Fee.student_id == student_id)
    
    if semester:
        query = query.filter(Fee.semester == semester)
    
    fees = query.all()
    
    # Get transactions for the student
    transactions_query = db.query(Transaction)
    if student_id:
        transactions_query = transactions_query.filter(Transaction.student_id == student_id)
    
    transactions = transactions_query.all()
    
    # Determine current semester (in a real app, this would come from a settings table)
    current_semester = "2025 Summer"
    if fees and semester is None:
        # Use the most recent semester from the fees
        semesters = set([fee.semester for fee in fees])
        if semesters:
            current_semester = max(semesters)  # This assumes semester names are comparable
    
    return StudentFeesResponse(
        current_semester=current_semester,
        fees=fees,
        transactions=transactions
    )

@router.post("/categories/", response_model=FeeCategoryResponse)
def create_fee_category(
    category: FeeCategoryCreate,
    db: Session = Depends(get_db)
):
    """Create a new fee category"""
    db_category = FeeCategory(**category.dict())
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category

@router.post("/", response_model=FeeResponse)
def create_fee(
    fee: FeeCreate,
    db: Session = Depends(get_db)
):
    """Create a new fee for a student"""
    # Check if student exists
    student = db.query(User).filter(User.id == fee.student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with id {fee.student_id} not found"
        )
    
    # Create fee with default status PENDING
    db_fee = Fee(
        **fee.dict(),
        status=FeeStatus.PENDING
    )
    
    db.add(db_fee)
    db.commit()
    db.refresh(db_fee)
    return db_fee

@router.post("/pay/", response_model=TransactionResponse)
def pay_fee(
    transaction: TransactionCreate,
    db: Session = Depends(get_db)
):
    """Record a payment for a fee"""
    # Check if fee exists
    fee = db.query(Fee).filter(Fee.id == transaction.fee_id).first()
    if not fee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Fee with id {transaction.fee_id} not found"
        )
    
    # Check if student exists
    student = db.query(User).filter(User.id == transaction.student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with id {transaction.student_id} not found"
        )
    
    # Create transaction
    db_transaction = Transaction(
        **transaction.dict(),
        date=datetime.utcnow(),
        status=TransactionStatus.COMPLETED
    )
    
    # Update fee status
    fee.status = FeeStatus.PAID
    fee.paid_date = datetime.utcnow()
    fee.paid_amount = transaction.amount
    
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

@router.get("/categories/", response_model=List[FeeCategoryResponse])
def get_fee_categories(db: Session = Depends(get_db)):
    """Get all fee categories"""
    return db.query(FeeCategory).all()

@router.get("/transactions/", response_model=List[TransactionResponse])
def get_transactions(
    student_id: Optional[int] = None,
    fee_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get all transactions, optionally filtered by student or fee"""
    query = db.query(Transaction)
    
    if student_id:
        query = query.filter(Transaction.student_id == student_id)
    
    if fee_id:
        query = query.filter(Transaction.fee_id == fee_id)
    
    return query.all()
