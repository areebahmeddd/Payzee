from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from datetime import datetime

from app.db import (
    get_user_by_id,
    get_user_wallet,
    update_user_wallet,
    get_user_transactions,
    add_user_transaction,
)
from app.vendor.utils import get_vendor_by_id
from app.db import vendors_collection, db
from google.cloud import firestore

router = APIRouter(tags=["user"])


@router.get("/profile/{user_id}")
async def get_user_profile(user_id: str) -> Dict[str, Any]:
    """Get user profile information."""
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user.get("account_info", {})


@router.get("/balance/{user_id}")
async def get_user_balance(user_id: str) -> Dict[str, Any]:
    """Get user balance information."""
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "user_id": user_id,
        "allocated_amt": user.get("allocated_amt", 0),
        "remaining_amt": user.get("remaining_amt", 0),
        "personal_wallet": user.get("personal_wallet", 0),
    }


@router.get("/wallet/{user_id}")
async def get_user_wallet_endpoint(user_id: str) -> Dict[str, Any]:
    """Get user's wallet information."""
    wallet = get_user_wallet(user_id)
    if not wallet:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "user_id": user_id,
        "govt_wallet": wallet["govt_wallet"],
        "personal_wallet": wallet["personal_wallet"],
        "allocated_amt": wallet["allocated_amt"],
        "remaining_amt": wallet["remaining_amt"],
    }


# TODO: This should be done by government admin
@router.post("/wallet/{user_id}")
async def update_wallet_item(
    user_id: str, wallet_item: Dict[str, Any]
) -> Dict[str, Any]:
    """Add or update a wallet item for a user."""
    if "category" not in wallet_item or "amount" not in wallet_item:
        raise HTTPException(status_code=400, detail="Category and amount are required")

    updated_wallet = update_user_wallet(user_id, wallet_item)
    if not updated_wallet:
        raise HTTPException(status_code=404, detail="User not found")

    return {"status": "success", "wallet": updated_wallet}


# TODO: Broken as hell
@router.get("/transactions/{user_id}")
async def get_user_transactions_endpoint(user_id: str) -> List[Dict[str, Any]]:
    """Get all transactions for a user."""
    transactions = get_user_transactions(user_id)
    if transactions is None:
        raise HTTPException(status_code=404, detail="User not found")

    return transactions


@router.post("/transactions/{user_id}")
async def add_transaction_endpoint(
    user_id: str, transaction: Dict[str, Any]
) -> Dict[str, Any]:
    """Record a new transaction for a user."""
    if not all(
        key in transaction for key in ["shop_name", "category", "amount", "date"]
    ):
        raise HTTPException(
            status_code=400, detail="Missing required transaction fields"
        )

    result = add_user_transaction(user_id, transaction)
    if not result:
        raise HTTPException(status_code=404, detail="User not found")

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    return result


# TODO: 422 Unprocessable Entity??
@router.post("/scan-qr")
async def process_qr_code(
    qr_data: Dict[str, Any], user_id: str, amount: float, category: str
) -> Dict[str, Any]:
    """Process a scanned QR code and validate the transaction."""
    # Get user data to check wallet allowances
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Validate vendor exists
    vendor_id = qr_data.get("vendor_id")
    if not vendor_id:
        raise HTTPException(
            status_code=400, detail="Invalid QR code: missing vendor ID"
        )

    vendor = get_vendor_by_id(vendor_id)
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")

    # Check if vendor has a government license
    account_info = vendor.get("account_info", {})
    vendor_category = account_info.get("category")
    is_govt_licensed = account_info.get("license_type") == "government"

    if not is_govt_licensed:
        return {
            "status": "failed",
            "message": "Vendor does not have a government license for subsidized transactions",
        }

    # Check if vendor's category matches the one in QR code
    if vendor_category != qr_data.get("category"):
        return {
            "status": "failed",
            "message": "QR code data mismatch with vendor information",
        }

    # Check if user is allowed to spend in this category
    allowed_to_spend = False
    govt_wallet = user.get("govt_wallet", [])

    for wallet_item in govt_wallet:
        if wallet_item.get("category") == category:
            # Category exists in user's government wallet
            allowed_to_spend = True
            wallet_amount = wallet_item.get("amount", 0)

            # Check if sufficient funds are available
            if wallet_amount < amount:
                return {
                    "status": "failed",
                    "message": f"Insufficient funds in {category} wallet",
                    "available": wallet_amount,
                }
            break

    if not allowed_to_spend:
        return {
            "status": "failed",
            "message": f"Your government allocation does not allow spending in {category} category",
        }

    # If we reach here, the transaction is valid
    # Create a transaction object
    transaction = {
        "shop_name": account_info.get("business_name", ""),
        "category": category,
        "amount": amount,
        "date": datetime.now().isoformat(),
    }

    # Process the transaction
    result = add_user_transaction(user_id, transaction)

    # Also record transaction on vendor side
    # vendor_transaction = TransactionCreate(
    #     user_id=user_id, amount=amount, category=category
    # )

    # Use the vendor API to verify the transaction
    vendor_ref = vendors_collection.document(vendor_id)
    vendor_ref.update({"balance": firestore.Increment(amount)})

    # Add transaction to transactions collection
    transaction_data = {
        "vendor_id": vendor_id,
        "user_id": user_id,
        "amount": amount,
        "category": category,
        "timestamp": datetime.now().isoformat(),
        "status": "completed",
    }

    transaction_ref = db.collection("transactions").document()
    transaction_data["transaction_id"] = transaction_ref.id
    transaction_ref.set(transaction_data)

    return {
        "status": "success",
        "transaction_id": transaction_ref.id,
        "amount": amount,
        "vendor": account_info.get("business_name", ""),
        "category": category,
        "remaining_wallet_amount": result.get("remaining_amt", 0),
    }
