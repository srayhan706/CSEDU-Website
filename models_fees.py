from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB
from database import Base
import enum
from datetime import datetime

# We'll use string references for foreign keys to avoid circular imports

class FeeStatus(enum.Enum):
    PAID = "PAID"
    PENDING = "PENDING"
    OVERDUE = "OVERDUE"

class TransactionStatus(enum.Enum):
    COMPLETED = "COMPLETED"
    PENDING = "PENDING"
    FAILED = "FAILED"

class PaymentMethod(enum.Enum):
    ONLINE_BANKING = "ONLINE_BANKING"
    MOBILE_BANKING = "MOBILE_BANKING"
    CARD = "CARD"
    CASH = "CASH"
    OTHER = "OTHER"

class FeeCategory(Base):
    __tablename__ = "fee_categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    fees = relationship("Fee", back_populates="category")

class Fee(Base):
    __tablename__ = "fees"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    description = Column(Text, nullable=True)
    deadline = Column(DateTime, nullable=False)
    status = Column(SQLEnum(FeeStatus), nullable=False, default=FeeStatus.PENDING)
    semester = Column(String, nullable=False)
    batch = Column(String, nullable=False)
    category_id = Column(Integer, ForeignKey("fee_categories.id"), nullable=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    paid_date = Column(DateTime, nullable=True)
    paid_amount = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    category = relationship("FeeCategory", back_populates="fees")
    student = relationship("User")
    transactions = relationship("Transaction", back_populates="fee")

class Transaction(Base):
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, default=datetime.utcnow)
    amount = Column(Float, nullable=False)
    description = Column(Text, nullable=True)
    payment_method = Column(SQLEnum(PaymentMethod), nullable=False)
    status = Column(SQLEnum(TransactionStatus), nullable=False, default=TransactionStatus.PENDING)
    receipt_url = Column(String, nullable=True)
    transaction_id = Column(String, nullable=True, unique=True)
    fee_id = Column(Integer, ForeignKey("fees.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    fee = relationship("Fee", back_populates="transactions")
    student = relationship("User")
