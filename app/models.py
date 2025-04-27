from pydantic import BaseModel
from typing import Optional, Literal


class UserBase(BaseModel):
    email: str
    username: str


class UserCreate(UserBase):
    password: str
    user_type: Literal["user", "vendor"] = "user"


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


class UserProfile(ProfileBase):
    user_id: str


class VendorProfileBase(ProfileBase):
    business_name: str
    business_description: Optional[str] = None
    category: Optional[str] = None


class VendorProfile(VendorProfileBase):
    user_id: str
