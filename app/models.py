from pydantic import BaseModel
from typing import Optional, Literal, List, Dict, Any


class UserBase(BaseModel):
    email: str
    username: str


class UserCreate(UserBase):
    password: str
    user_type: Literal["user", "vendor"] = "user"
    aadhaar_number: str


class UserLogin(BaseModel):
    email: str
    password: str


class User(UserBase):
    id: str
    user_type: Literal["user", "vendor"] = "user"


class ProfileBase(BaseModel):
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    address: Optional[str] = None
    aadhaar_number: str


class UserProfile(ProfileBase):
    user_id: str


class VendorProfileBase(ProfileBase):
    business_name: str
    business_description: Optional[str] = None
    category: Optional[str] = None
    location: str
    status: str = "pending"


class VendorProfile(VendorProfileBase):
    user_id: str


# User wallet models
class WalletItem(BaseModel):
    category: str
    amount: float


class Transaction(BaseModel):
    shop_name: str
    category: str
    amount: float
    date: str


class UserWallet(BaseModel):
    govt_wallet: List[WalletItem] = []
    personal_wallet: float = 0
    allocated_amt: float = 0
    remaining_amt: float = 0
    past_transactions: List[Dict[str, Any]] = []
