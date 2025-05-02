from pydantic import BaseModel, EmailStr
from typing import Any, Optional, Dict, Literal, List


# Common base models
class UserBase(BaseModel):
    """Base model for user authentication"""

    email: EmailStr
    password: str


class ProfileUpdate(BaseModel):
    """Common model for profile updates"""

    name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None


# Auth models
class UserSignup(UserBase):
    name: str
    user_type: Literal["citizen", "vendor", "government"]
    phone: Optional[str] = None
    address: Optional[str] = None
    # Vendor specific
    business_name: Optional[str] = None
    business_id: Optional[str] = None
    # Government specific
    department: Optional[str] = None
    jurisdiction: Optional[str] = None
    govt_id: Optional[str] = None


class UserLogin(UserBase):
    user_type: Literal["citizen", "vendor", "government"]


# Transaction models
class PaymentRequest(BaseModel):
    vendor_id: str
    amount: float
    wallet_type: str  # "personal_wallet" or "govt_wallet"
    description: Optional[str] = None


class ProcessPaymentRequest(BaseModel):
    citizen_id: str
    amount: float


class WithdrawRequest(BaseModel):
    amount: float
    bank_account: str


# Scheme models
class SchemeModel(BaseModel):
    name: str
    description: str
    amount: float
    eligibility_criteria: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None


# Response models
class MessageResponse(BaseModel):
    message: str


class LoginResponse(MessageResponse):
    user_id: str
    # user_type: str
