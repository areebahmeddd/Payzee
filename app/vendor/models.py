from pydantic import BaseModel
from typing import Optional


# Inventory models
class InventoryItem(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    category: str
    available: bool = True
    image_url: Optional[str] = None


# Transaction models
class TransactionItem(BaseModel):
    name: str
    quantity: str
    unit_price: float
    total_price: float


class TransactionCreate(BaseModel):
    user_id: str
    amount: float
    category: str
