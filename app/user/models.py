from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class WalletItem(BaseModel):
    category: str
    amount: float


class Transaction(BaseModel):
    shop_name: str
    category: str
    amount: float
    date: str


class User(BaseModel):
    id: Optional[str] = None
    name: str
    email: str
    date_created: Optional[datetime] = None
    allocated_amt: float = 0
    remaining_amt: float = 0
    govt_wallet: List[WalletItem] = []
    personal_wallet: float = 0
    past_transactions: List[Transaction] = []
    aadhaar_number: Optional[str] = None
    phone_number: Optional[str] = None


class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    phone_number: Optional[str] = None
    aadhaar_number: Optional[str] = None
    allocated_amt: float = 0
    personal_wallet: float = 0
    govt_wallet: List[WalletItem] = []


class UserUpdate(BaseModel):
    name: Optional[str] = None
    phone_number: Optional[str] = None
    aadhaar_number: Optional[str] = None
    allocated_amt: Optional[float] = None
    personal_wallet: Optional[float] = None
    govt_wallet: Optional[List[WalletItem]] = None


class UserInDB(User):
    password: str


class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    allocated_amt: float
    remaining_amt: float
    govt_wallet: List[WalletItem]
    personal_wallet: float
    aadhaar_number: Optional[str] = None
    phone_number: Optional[str] = None
