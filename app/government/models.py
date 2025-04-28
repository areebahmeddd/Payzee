from pydantic import BaseModel
from typing import Optional, Literal, List, Dict, Any


class EligibilityCriteria(BaseModel):
    date_of_birth: Optional[str] = None
    gender: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None
    city: Optional[str] = None
    caste: Optional[str] = None


class GovernmentScheme(BaseModel):
    scheme_name: str
    scheme_id: str
    description: str
    amount: float
    status: Literal["active", "inactive", "draft"] = "active"
    created_at: str
    eligibility_criteria: EligibilityCriteria
    tags: List[str] = []


class GovernmentSchemeCreate(BaseModel):
    scheme_name: str
    description: str
    amount: float
    status: Literal["active", "inactive", "draft"] = "active"
    eligibility_criteria: EligibilityCriteria
    tags: List[str] = []


class GovernmentSchemeUpdate(BaseModel):
    scheme_name: Optional[str] = None
    description: Optional[str] = None
    amount: Optional[float] = None
    status: Optional[Literal["active", "inactive", "draft"]] = None
    eligibility_criteria: Optional[EligibilityCriteria] = None
    tags: Optional[List[str]] = None


class SchemeAllocation(BaseModel):
    scheme_id: str
    amount: float


class WalletAllocationResponse(BaseModel):
    status: str
    message: str
    wallet: Dict[str, Any]


class GovernmentWallet(BaseModel):
    user_id: str
    govt_wallet: List[Dict[str, Any]]
    allocated_amt: float
    remaining_amt: float
