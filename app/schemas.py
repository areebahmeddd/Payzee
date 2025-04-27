from pydantic import BaseModel, EmailStr, constr
from typing import List, Optional
from datetime import datetime, date
from uuid import UUID

# User Schemas
class UserBase(BaseModel):
    aadhaar_number: constr(min_length=12, max_length=12)
    name: str
    date_of_birth: date
    gender: str
    state: str
    district: str
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None
    caste_category: str
    income_group: str
    tags: Optional[List[str]] = None

class UserCreate(UserBase):
    pass

class UserUpdate(BaseModel):
    name: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None
    state: Optional[str] = None
    district: Optional[str] = None
    caste_category: Optional[str] = None
    income_group: Optional[str] = None
    tags: Optional[List[str]] = None

class User(UserBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Vendor Schemas
class VendorBase(BaseModel):
    name: str
    aadhaar_number: Optional[constr(min_length=12, max_length=12)] = None
    gst_number: Optional[str] = None
    phone_number: str
    state: str
    district: str
    services_offered: List[str]
    kyc_status: str

class VendorCreate(VendorBase):
    pass

class VendorUpdate(BaseModel):
    name: Optional[str] = None
    aadhaar_number: Optional[constr(min_length=12, max_length=12)] = None
    gst_number: Optional[str] = None
    phone_number: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None
    services_offered: Optional[List[str]] = None
    kyc_status: Optional[str] = None

class Vendor(VendorBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

# Scheme Schemas
class SchemeBase(BaseModel):
    name: str
    description: str
    amount_per_user: float
    eligibility_criteria: dict

class SchemeCreate(SchemeBase):
    pass

class SchemeUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    amount_per_user: Optional[float] = None
    eligibility_criteria: Optional[dict] = None

class Scheme(SchemeBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

# Transaction Schemas
class TransactionBase(BaseModel):
    user_id: UUID
    vendor_id: UUID
    scheme_id: UUID
    amount: float
    status: str
    used_for: Optional[str] = None

class TransactionCreate(TransactionBase):
    pass

class Transaction(TransactionBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True 