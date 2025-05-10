from pydantic import BaseModel, EmailStr
from typing import Any, Optional, Dict, List


# Signup models
class CitizenSignup(BaseModel):
    name: str
    password: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    id_type: str = "Aadhaar"
    id_number: str
    address: Optional[str] = None
    dob: Optional[str] = None
    gender: Optional[str] = None
    occupation: Optional[str] = None
    caste: Optional[str] = None
    annual_income: Optional[float] = None
    image_url: Optional[str] = None


class VendorSignup(BaseModel):
    name: str
    password: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    business_name: str
    business_id: str
    license_type: str
    address: Optional[str] = None
    gender: Optional[str] = None
    occupation: Optional[str] = None
    image_url: Optional[str] = None


class GovernmentSignup(BaseModel):
    name: str
    password: str
    email: Optional[EmailStr] = None
    department: str
    jurisdiction: str
    govt_id: str


# Login model
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
    eligibility_criteria: Dict[str, Any]
    tags: Optional[List[str]] = None

    class Config:
        schema_extra = {
            "example": {
                "name": "Pradhan Mantri Vaya Vandana Yojana",
                "description": "Monthly pension scheme for elderly citizens above 60 years",
                "amount": 3000.00,
                "status": "active",
                "eligibility_criteria": {
                    "occupation": "any",
                    "min_age": 60,
                    "max_age": 80,
                    "gender": "any",
                    "state": "Karnataka",
                    "district": "Bangalore Urban",
                    "city": "Bangalore",
                    "caste": "General",
                    "annual_income": 150000,
                },
                "tags": ["pension", "elderly", "senior citizen", "retirement"],
            }
        }


# Disbursement model
class DisbursementRequest(BaseModel):
    scheme_id: str
    amount_per_user: float


# Response models
class MessageResponse(BaseModel):
    message: str
    user_id: Optional[str] = None
    user_type: Optional[str] = None
    transaction_id: Optional[str] = None
    scheme_id: Optional[str] = None
    beneficiaries_count: Optional[int] = None
