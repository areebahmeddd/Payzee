from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class Customer(BaseModel):
    id: int
    name: str
    date: Optional[datetime] = None
    allocated_amt: float
    remaining_amt: float
    govt_wallet: List[dict] = []
    personal_wallet: float
    past_transactions: List[dict] = []
    aadhaar_number: str

# Dummy Database
customers_db = [
    Customer(
        id=1,
        name="Allen",
        date=datetime.now(),
        allocated_amt=10000.0,
        remaining_amt=8000.0,
        govt_wallet=[{"category": "food", "amount": 5000}, {"category": "education", "amount": 3000}],
        personal_wallet=2000.0,
        past_transactions=[{"shop_name": "SuperMart", "category": "grocery", "amount": 1200, "date": "2024-04-15"}],
        aadhaar_number="123456789012"
    ),
    Customer(
        id=2,
        name="Raghu",
        date=datetime.now(),
        allocated_amt=15000.0,
        remaining_amt=12000.0,
        govt_wallet=[{"category": "health", "amount": 7000}, {"category": "food", "amount": 5000}],
        personal_wallet=3000.0,
        past_transactions=[{"shop_name": "MedPlus", "category": "health", "amount": 3000, "date": "2024-04-05"}],
        aadhaar_number="987654321012"
    )
]
