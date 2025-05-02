from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from models.api import (
    ProfileUpdate,
    ProcessPaymentRequest,
    WithdrawRequest,
    MessageResponse,
)
from db import vendors_collection, transactions_collection

router = APIRouter()


# Get vendor profile
@router.get("/{vendor_id}")
async def get_vendor_profile(vendor_id: str):
    doc_ref = vendors_collection.document(vendor_id)
    doc = doc_ref.get()

    if not doc.exists:
        raise HTTPException(status_code=404, detail="Vendor not found")

    vendor = doc.to_dict()
    # Remove sensitive information
    if "password" in vendor["account_info"]:
        vendor["account_info"].pop("password")

    return JSONResponse(content=vendor)


# Update vendor profile
@router.put("/{vendor_id}", response_model=MessageResponse)
async def update_vendor_profile(vendor_id: str, data: ProfileUpdate):
    doc_ref = vendors_collection.document(vendor_id)
    doc = doc_ref.get()

    if not doc.exists:
        raise HTTPException(status_code=404, detail="Vendor not found")

    update_data = {}
    for field, value in data.dict(exclude_none=True).items():
        update_data[f"account_info.{field}"] = value

    if not update_data:
        raise HTTPException(status_code=400, detail="No valid fields to update")

    doc_ref.update(update_data)
    return JSONResponse(content={"message": "Profile updated successfully"})


# Get wallet information
@router.get("/{vendor_id}/wallet")
async def get_wallet(vendor_id: str):
    doc_ref = vendors_collection.document(vendor_id)
    doc = doc_ref.get()

    if not doc.exists:
        raise HTTPException(status_code=404, detail="Vendor not found")

    vendor = doc.to_dict()
    return JSONResponse(content=vendor["wallet_info"])


# Get transaction history
@router.get("/{vendor_id}/transactions")
async def get_transactions(vendor_id: str):
    # Find transactions where vendor is either sender or receiver
    from_transactions = transactions_collection.where(
        "from_id", "==", vendor_id
    ).stream()
    to_transactions = transactions_collection.where("to_id", "==", vendor_id).stream()

    transactions = []

    for doc in from_transactions:
        transaction = doc.to_dict()
        transaction["id"] = doc.id
        transactions.append(transaction)

    for doc in to_transactions:
        # Only add if not already in the list (avoid duplicates)
        transaction = doc.to_dict()
        transaction["id"] = doc.id
        if not any(t["id"] == transaction["id"] for t in transactions):
            transactions.append(transaction)

    # Sort by timestamp, newest first
    transactions.sort(key=lambda x: x["timestamp"], reverse=True)

    return JSONResponse(content=transactions)


# Process payment from citizen (via QR code)
@router.post("/{vendor_id}/process-payment", response_model=MessageResponse)
async def process_payment(vendor_id: str, payment: ProcessPaymentRequest):
    # TODO: Validate payment details (e.g., amount, citizen ID)
    vendor_doc = vendors_collection.document(vendor_id).get()
    if not vendor_doc.exists:
        raise HTTPException(status_code=404, detail="Vendor not found")

    return JSONResponse(
        content={
            "message": "Payment request initiated",
            "vendor_id": vendor_id,
            "citizen_id": payment.citizen_id,
            "amount": payment.amount,
        }
    )


# Withdraw funds to bank account
@router.post("/{vendor_id}/withdraw", response_model=MessageResponse)
async def withdraw_funds(vendor_id: str, withdraw: WithdrawRequest):
    # Get vendor
    vendor_doc = vendors_collection.document(vendor_id).get()
    if not vendor_doc.exists:
        raise HTTPException(status_code=404, detail="Vendor not found")

    vendor = vendor_doc.to_dict()

    # Check if vendor has sufficient balance
    if vendor["wallet_info"]["balance"] < withdraw.amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")

    # Update vendor's wallet (reduce balance)
    vendors_collection.document(vendor_id).update(
        {"wallet_info.balance": vendor["wallet_info"]["balance"] - withdraw.amount}
    )

    # TODO: Process the withdrawal to the bank account
    return JSONResponse(
        content={
            "message": "Withdrawal initiated",
            "amount": withdraw.amount,
            "bank_account": withdraw.bank_account,
        }
    )
