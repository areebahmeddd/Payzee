import io
import qrcode
import base64
from fastapi import APIRouter, HTTPException, Body, Depends
from fastapi.responses import JSONResponse
from typing import Dict, Any
from models.api import MessageResponse
from utils.auth import require_vendor
from db import (
    get_vendor,
    update_vendor,
    delete_vendor,
    get_transaction,
    query_transactions_by_field,
)

router = APIRouter()


@router.get("/{vendor_id}")
async def get_vendor_profile(
    vendor_id: str, current_user: dict = Depends(require_vendor)
) -> JSONResponse:
    vendor = get_vendor(vendor_id)
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")

    if current_user["user_id"] != vendor_id:
        raise HTTPException(
            status_code=403,
            detail="Access denied. You can only access your own profile.",
        )

    # Remove sensitive information
    if "password" in vendor["account_info"]:
        vendor["account_info"].pop("password")

    return JSONResponse(content=vendor)


@router.put("/{vendor_id}", response_model=MessageResponse)
async def update_vendor_profile(
    vendor_id: str,
    data: Dict[str, Any] = Body(...),
    current_user: dict = Depends(require_vendor),
) -> JSONResponse:
    vendor = get_vendor(vendor_id)
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")

    if current_user["user_id"] != vendor_id:
        raise HTTPException(
            status_code=403,
            detail="Access denied. You can only update your own profile.",
        )

    # Only update fields that are present
    update_data = {}
    for field, value in data.items():
        update_data[f"account_info.{field}"] = value

    if not update_data:
        raise HTTPException(status_code=400, detail="No valid fields to update")

    update_vendor(vendor_id, update_data)
    return JSONResponse(content={"message": "Profile updated successfully"})


@router.delete("/{vendor_id}", response_model=MessageResponse)
async def delete_vendor_profile(
    vendor_id: str, current_user: dict = Depends(require_vendor)
) -> JSONResponse:
    vendor = get_vendor(vendor_id)
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")

    if current_user["user_id"] != vendor_id:
        raise HTTPException(
            status_code=403,
            detail="Access denied. You can only delete your own profile.",
        )

    delete_vendor(vendor_id)
    return JSONResponse(content={"message": "Vendor profile deleted successfully"})


@router.get("/{vendor_id}/wallet")
async def get_wallet(
    vendor_id: str, current_user: dict = Depends(require_vendor)
) -> JSONResponse:
    vendor = get_vendor(vendor_id)
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")

    if current_user["user_id"] != vendor_id:
        raise HTTPException(
            status_code=403,
            detail="Access denied. You can only access your own wallet.",
        )

    return JSONResponse(content=vendor["wallet_info"])


@router.get("/{vendor_id}/generate-qr")
async def generate_qr(
    vendor_id: str, current_user: dict = Depends(require_vendor)
) -> JSONResponse:
    vendor = get_vendor(vendor_id)
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")

    if current_user["user_id"] != vendor_id:
        raise HTTPException(
            status_code=403,
            detail="Access denied. You can only generate QR for your own account.",
        )

    # Generate QR code with user ID
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(vendor_id)  # TODO: ..
    qr.make(fit=True)

    # Create an image from the QR Code
    img = qr.make_image(fill_color="black", back_color="white")

    # Convert to base64 for transport
    buffered = io.BytesIO()
    img.save(buffered)
    img_str = base64.b64encode(buffered.getvalue()).decode()

    return JSONResponse(content={"qr_code": img_str, "user_id": vendor_id})


@router.get("/{vendor_id}/transactions")
async def get_transactions(
    vendor_id: str, current_user: dict = Depends(require_vendor)
) -> JSONResponse:
    vendor = get_vendor(vendor_id)
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")

    if current_user["user_id"] != vendor_id:
        raise HTTPException(
            status_code=403,
            detail="Access denied. You can only access your own transactions.",
        )

    # Find transactions where vendor is either sender or receiver
    from_transactions = query_transactions_by_field("from_id", vendor_id)
    to_transactions = query_transactions_by_field("to_id", vendor_id)

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


@router.get("/{vendor_id}/transactions/{transaction_id}")
async def get_specific_transaction(
    vendor_id: str, transaction_id: str, current_user: dict = Depends(require_vendor)
) -> JSONResponse:
    vendor = get_vendor(vendor_id)
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")

    if current_user["user_id"] != vendor_id:
        raise HTTPException(
            status_code=403,
            detail="Access denied. You can only access your own transactions.",
        )

    transaction = get_transaction(transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    # Verify that the vendor is part of this transaction (security check)
    if transaction["from_id"] != vendor_id and transaction["to_id"] != vendor_id:
        raise HTTPException(
            status_code=403, detail="Transaction not associated with this vendor"
        )

    return JSONResponse(content=transaction)


@router.post("/{vendor_id}/application")
async def send_application(
    vendor_id: str,
    data: Dict[str, Any] = Body(...),
    current_user: dict = Depends(require_vendor),
) -> JSONResponse:
    vendor = get_vendor(vendor_id)
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")

    if current_user["user_id"] != vendor_id:
        raise HTTPException(
            status_code=403,
            detail="Access denied. You can only send applications from your own account.",
        )

    # TODO: Implement application logic
    pass
