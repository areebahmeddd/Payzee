import io
import qrcode
import base64
from fastapi import APIRouter, HTTPException, Body
from fastapi.responses import JSONResponse
from models.api import MessageResponse
from db import get_vendor, update_vendor, query_transactions_by_field

router = APIRouter()


# Get vendor profile
@router.get("/{user_id}")
async def get_vendor_profile(user_id: str):
    # Check if vendor existss
    vendor = get_vendor(user_id)
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")

    # Remove sensitive information
    if "password" in vendor["account_info"]:
        vendor["account_info"].pop("password")

    return JSONResponse(content=vendor)


# Update vendor profile
@router.put("/{user_id}", response_model=MessageResponse)
async def update_vendor_profile(user_id: str, data: dict = Body(...)):
    vendor = get_vendor(user_id)
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")

    # Only update fields that are present
    update_data = {}
    for field, value in data.items():
        update_data[f"account_info.{field}"] = value

    if not update_data:
        raise HTTPException(status_code=400, detail="No valid fields to update")

    update_vendor(user_id, update_data)
    return JSONResponse(content={"message": "Profile updated successfully"})


# Get wallet information
@router.get("/{user_id}/wallet")
async def get_wallet(user_id: str):
    vendor = get_vendor(user_id)
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")

    return JSONResponse(content=vendor["wallet_info"])


# Generate QR code for payment
@router.get("/{user_id}/generate-qr")
async def generate_qr(user_id: str):
    vendor = get_vendor(user_id)
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")

    # Generate QR code with user ID
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(user_id)  # TODO: ..
    qr.make(fit=True)

    # Create an image from the QR Code
    img = qr.make_image(fill_color="black", back_color="white")

    # Convert to base64 for transport
    buffered = io.BytesIO()
    img.save(buffered)
    img_str = base64.b64encode(buffered.getvalue()).decode()

    return JSONResponse(content={"qr_code": img_str, "user_id": user_id})


# Get transaction history
@router.get("/{user_id}/transactions")
async def get_transactions(user_id: str):
    # Find transactions where vendor is either sender or receiver
    from_transactions = query_transactions_by_field("from_id", user_id)
    to_transactions = query_transactions_by_field("to_id", user_id)

    transactions = []

    # Add from transactions
    for transaction in from_transactions:
        transactions.append(transaction)

    # Add to transactions (avoiding duplicates)
    for transaction in to_transactions:
        if not any(t["id"] == transaction["id"] for t in transactions):
            transactions.append(transaction)

    # Sort by timestamp, newest first
    transactions.sort(key=lambda x: x["timestamp"], reverse=True)
    return JSONResponse(content=transactions)
