from fastapi import APIRouter
from dummy_data import customers_db
from typing import List

router = APIRouter()

# Fetch allocated amount 
@router.get("/customer/{customer_id}/allocated_amount")
async def get_allocated_amount(customer_id: int):
    for customer in customers_db:
        if customer.id == customer_id:
            return {"allocated_amount": customer.allocated_amt}
    return {"error": "Customer not found"}


# Fetch remaining amount 
@router.get("/customer/{customer_id}/remaining_amount")
async def get_remaining_amount(customer_id: int):
    for customer in customers_db:
        if customer.id == customer_id:
            return {"remaining_amount": customer.remaining_amt}
    return {"error": "Customer not found"}


# Fetch past transactions 
@router.get("/customer/{customer_id}/past_transactions")
async def get_past_transactions(customer_id: int):
    for customer in customers_db:
        if customer.id == customer_id:
            return {"past_transactions": customer.past_transactions}
    return {"error": "Customer not found"}


# Fetch remaining amount in govt_wallet
@router.get("/customer/{customer_id}/govt_wallet")
async def get_govt_wallet_remaining(customer_id: int):
    for customer in customers_db:
        if customer.id == customer_id:
            remaining_govt_wallet = sum(wallet['amount'] for wallet in customer.govt_wallet)
            return {"govt_wallet": remaining_govt_wallet}
    return {"error": "Customer not found"}


# Fetch personal wallet balance
@router.get("/customer/{customer_id}/personal_wallet")
async def get_personal_wallet(customer_id: int):
    for customer in customers_db:
        if customer.id == customer_id:
            return {"personal_wallet": customer.personal_wallet}
    return {"error": "Customer not found"}


# Edit personal wallet 
@router.put("/edit_personal_wallet/{customer_id}")
async def edit_personal_wallet(customer_id: int, amount: float):
    for customer in customers_db:
        if customer.id == customer_id:
            customer.personal_wallet -= amount
            return {"message": "Personal wallet updated", "new_balance": customer.personal_wallet}
    return {"error": "Customer not found"}


# Edit govt wallet 
@router.put("/edit_govt_wallet/{customer_id}")
async def edit_govt_wallet(customer_id: int, category: str, amount: float):
    for customer in customers_db:
        if customer.id == customer_id:
            for wallet in customer.govt_wallet:
                if wallet['category'] == category:
                    wallet['amount'] -= amount
                    customer.remaining_amt -= amount
                    return {"message": "Govt wallet updated", "new_balance": wallet['amount']}
            return {"error": f"Category '{category}' not found in govt wallet"}
    return {"error": "Customer not found"}
