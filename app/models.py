from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Enum, ARRAY, JSON, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    aadhaar_number = Column(String(12), unique=True, nullable=False)
    name = Column(String, nullable=False)
    date_of_birth = Column(Date, nullable=False)
    gender = Column(Enum('Male', 'Female', 'Other', name='gender_enum'), nullable=False)
    state = Column(String, nullable=False)
    district = Column(String, nullable=False)
    phone_number = Column(String, nullable=True)
    email = Column(String, nullable=True)
    caste_category = Column(Enum('General', 'OBC', 'SC', 'ST', name='caste_enum'), nullable=False)
    income_group = Column(Enum('Low', 'Middle', 'High', name='income_enum'), nullable=False)
    tags = Column(ARRAY(String), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    transactions = relationship("Transaction", back_populates="user")

class Vendor(Base):
    __tablename__ = "vendors"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    aadhaar_number = Column(String(12), nullable=True)
    gst_number = Column(String, nullable=True)
    phone_number = Column(String, nullable=False)
    state = Column(String, nullable=False)
    district = Column(String, nullable=False)
    services_offered = Column(ARRAY(String), nullable=False)
    kyc_status = Column(Enum('Pending', 'Verified', 'Rejected', name='kyc_status_enum'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    transactions = relationship("Transaction", back_populates="vendor")

class Scheme(Base):
    __tablename__ = "schemes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    amount_per_user = Column(Float, nullable=False)
    eligibility_criteria = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    transactions = relationship("Transaction", back_populates="scheme")

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    vendor_id = Column(UUID(as_uuid=True), ForeignKey("vendors.id"), nullable=False)
    scheme_id = Column(UUID(as_uuid=True), ForeignKey("schemes.id"), nullable=False)
    amount = Column(Float, nullable=False)
    status = Column(Enum('Pending', 'Completed', 'Failed', name='transaction_status_enum'), nullable=False)
    used_for = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="transactions")
    vendor = relationship("Vendor", back_populates="transactions")
    scheme = relationship("Scheme", back_populates="transactions") 