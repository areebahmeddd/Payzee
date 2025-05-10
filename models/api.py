from pydantic import BaseModel, EmailStr
from typing import Any, Optional, Dict, List


# Signup models
class CitizenSignup(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    password: str
    phone: Optional[str] = None
    address: Optional[str] = None
    id_type: str = "Aadhaar"
    id_number: str


class VendorSignup(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    password: str
    phone: Optional[str] = None
    address: Optional[str] = None
    business_name: str
    business_id: Optional[str] = None
    license_type: str


class GovernmentSignup(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    password: str
    department: str
    jurisdiction: str
    govt_id: str


class LoginRequest(BaseModel):
    id_number: str
    password: str


# Transaction models
class PaymentRequest(BaseModel):
    vendor_id: str
    amount: float
    wallet_type: str  # "personal_wallet" or "govt_wallet"
    description: Optional[str] = None


# Scheme models
class SchemeCreate(BaseModel):
    name: str
    description: str
    amount: float
    status: str = "active"  # active, inactive, completed
    eligibility_criteria: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None

    class Config:
        schema_extra = {
            "example": {
                "name": "Senior Citizen Pension Scheme",
                "description": "Monthly pension for elderly citizens",
                "amount": 3000.00,
                "status": "active",
                "eligibility_criteria": {
                    "min_age": 65,
                    "gender": "any",  # "male", "female", "other", "any"
                    "state": "all",  # specific state name or "all"
                    "district": "all",  # specific district name or "all"
                    "city": "all",  # specific city name or "all"
                    "caste": "all"  # specific caste category or "all"
                },
                "tags": ["pension", "elderly", "monthly"]
            }
        }


# Disbursement model
class DisbursementRequest(BaseModel):
    scheme_id: str
    amount_per_user: float
    # test_mode: bool = False


# Response models
class MessageResponse(BaseModel):
    message: str
    user_id: Optional[str] = None
    user_type: Optional[str] = None
    transaction_id: Optional[str] = None
    scheme_id: Optional[str] = None
    beneficiaries_count: Optional[int] = None
