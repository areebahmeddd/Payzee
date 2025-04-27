from pydantic import BaseModel
from typing import List


# Inventory models
class InventoryItem(BaseModel):
    name: str
    category: str
    quantity: float
    unit: str
    unit_price: float


# Transaction models
class TransactionItem(BaseModel):
    name: str
    quantity: str
    unit_price: float
    total_price: float


class TransactionCreate(BaseModel):
    token_id: str
    user_id: str
    amount: float
    items: List[TransactionItem]
