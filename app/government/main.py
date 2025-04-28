from fastapi import APIRouter, HTTPException
from typing import List, Optional
import uuid

from .models import (
    GovernmentScheme,
    GovernmentSchemeCreate,
    GovernmentSchemeUpdate,
    SchemeAllocation,
    WalletAllocationResponse,
    GovernmentWallet,
)
from ..db import (
    create_government_scheme,
    get_government_scheme,
    get_all_government_schemes,
    update_government_scheme,
    delete_government_scheme,
    get_schemes_by_status,
    get_schemes_by_eligibility,
    get_user_by_id,
    get_vendor_by_id,
    get_user_transactions,
    update_user_wallet,
    get_user_wallet,
    get_all_vendors,
    get_all_transactions,
)

router = APIRouter(tags=["government"])


@router.post("/schemes", response_model=GovernmentScheme)
async def create_scheme(scheme: GovernmentSchemeCreate):
    """Create a new government scheme"""
    scheme_data = scheme.dict()
    scheme_data["scheme_id"] = str(uuid.uuid4())
    scheme_id = create_government_scheme(scheme_data)
    return get_government_scheme(scheme_id)


@router.get("/schemes", response_model=List[GovernmentScheme])
async def list_schemes(status: Optional[str] = None):
    """Get all government schemes, optionally filtered by status"""
    if status:
        return get_schemes_by_status(status)
    return get_all_government_schemes()


@router.get("/schemes/{scheme_id}", response_model=GovernmentScheme)
async def get_scheme(scheme_id: str):
    """Get a specific government scheme by ID"""
    scheme = get_government_scheme(scheme_id)
    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")
    return scheme


@router.put("/schemes/{scheme_id}", response_model=GovernmentScheme)
async def update_scheme(scheme_id: str, scheme: GovernmentSchemeUpdate):
    """Update a government scheme"""
    existing_scheme = get_government_scheme(scheme_id)
    if not existing_scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")

    update_data = scheme.dict(exclude_unset=True)
    update_government_scheme(scheme_id, update_data)
    return get_government_scheme(scheme_id)


@router.delete("/schemes/{scheme_id}")
async def delete_scheme(scheme_id: str):
    """Delete a government scheme"""
    existing_scheme = get_government_scheme(scheme_id)
    if not existing_scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")

    delete_government_scheme(scheme_id)
    return {"message": "Scheme deleted successfully"}


@router.get("/schemes/eligibility", response_model=List[GovernmentScheme])
async def get_eligible_schemes(
    date_of_birth: Optional[str] = None,
    gender: Optional[str] = None,
    state: Optional[str] = None,
    district: Optional[str] = None,
    city: Optional[str] = None,
    caste: Optional[str] = None,
):
    """Get schemes matching specific eligibility criteria"""
    criteria = {k: v for k, v in locals().items() if k != "self" and v is not None}
    return get_schemes_by_eligibility(criteria)


@router.get("/users/{user_id}")
async def get_user_info(user_id: str):
    """Get detailed information about a user"""
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/vendors/{vendor_id}")
async def get_vendor_info(vendor_id: str):
    """Get detailed information about a vendor"""
    vendor = get_vendor_by_id(vendor_id)
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return vendor


@router.get("/transactions/{user_id}")
async def get_user_transaction_history(user_id: str):
    """Get transaction history for a specific user"""
    transactions = get_user_transactions(user_id)
    if transactions is None:
        raise HTTPException(status_code=404, detail="User not found")
    return transactions


@router.post("/wallet/{user_id}/allocate", response_model=WalletAllocationResponse)
async def allocate_scheme_amount(user_id: str, allocation: SchemeAllocation):
    """Allocate scheme amount to a user's government wallet"""
    # Check if user exists
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if scheme exists
    scheme = get_government_scheme(allocation.scheme_id)
    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")

    # Check if scheme is active
    if scheme.get("status") != "active":
        raise HTTPException(status_code=400, detail="Scheme is not active")

    # Check if amount is valid
    if allocation.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be greater than 0")

    # Check if amount is within scheme limits
    if allocation.amount > scheme.get("amount", 0):
        raise HTTPException(status_code=400, detail="Amount exceeds scheme limit")

    # Create wallet item
    wallet_item = {"category": scheme.get("scheme_name"), "amount": allocation.amount}

    # Update user's wallet
    updated_wallet = update_user_wallet(user_id, wallet_item)
    if not updated_wallet:
        raise HTTPException(status_code=500, detail="Failed to update wallet")

    return WalletAllocationResponse(
        status="success",
        message=f"Successfully allocated {allocation.amount} to {scheme.get('scheme_name')}",
        wallet=updated_wallet,
    )


@router.get("/wallet/{user_id}", response_model=GovernmentWallet)
async def get_user_government_wallet(user_id: str):
    """Get a user's government wallet information"""
    wallet = get_user_wallet(user_id)
    if not wallet:
        raise HTTPException(status_code=404, detail="User not found")

    return GovernmentWallet(
        user_id=user_id,
        govt_wallet=wallet.get("govt_wallet", []),
        allocated_amt=wallet.get("allocated_amt", 0),
        remaining_amt=wallet.get("remaining_amt", 0),
    )


@router.get("/vendor-profiles")
async def get_all_vendor_profiles():
    """Get account information for all vendors"""
    vendors_account_info = get_all_vendors()
    if not vendors_account_info:
        return {"message": "No vendors found"}

    return vendors_account_info


@router.get("/transactions")
async def get_all_transaction_data():
    """Get all transactions"""
    transactions = get_all_transactions()
    if not transactions:
        return {"message": "No transactions found"}

    return transactions
