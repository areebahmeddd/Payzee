import io
import qrcode
import base64
from fastapi import APIRouter, HTTPException, Body
from fastapi.responses import JSONResponse
from models.api import PaymentRequest, MessageResponse
from models.transaction import Transaction
from db import (
    get_citizen,
    update_citizen,
    get_vendor,
    update_vendor,
    get_scheme,
    save_transaction,
    query_transactions_by_field,
    array_union,
)
from db.redis_config import SCHEMES_PREFIX, CITIZENS_PREFIX, VENDORS_PREFIX

router = APIRouter()


# Get citizen profile
@router.get("/{citizen_id}")
async def get_citizen_profile(citizen_id: str):
    # Check if citizen exists
    citizen = get_citizen(citizen_id)
    if not citizen:
        raise HTTPException(status_code=404, detail="Citizen not found")

    # Remove sensitive information
    if "password" in citizen["account_info"]:
        citizen["account_info"].pop("password")

    return JSONResponse(content=citizen)


# Update citizen profile
@router.put("/{citizen_id}", response_model=MessageResponse)
async def update_citizen_profile(citizen_id: str, data: dict = Body(...)):
    citizen = get_citizen(citizen_id)
    if not citizen:
        raise HTTPException(status_code=404, detail="Citizen not found")

    # Only update fields that are present
    update_data = {}
    for field, value in data.items():
        update_data[f"account_info.{field}"] = value

    if not update_data:
        raise HTTPException(status_code=400, detail="No valid fields to update")

    update_citizen(citizen_id, update_data)
    return JSONResponse(content={"message": "Profile updated successfully"})


# Get wallet information
@router.get("/{citizen_id}/wallet")
async def get_wallet(citizen_id: str):
    citizen = get_citizen(citizen_id)
    if not citizen:
        raise HTTPException(status_code=404, detail="Citizen not found")

    return JSONResponse(content=citizen["wallet_info"])


# Generate QR code for payment
@router.get("/{citizen_id}/generate-qr")
async def generate_qr(citizen_id: str):
    citizen = get_citizen(citizen_id)
    if not citizen:
        raise HTTPException(status_code=404, detail="Citizen not found")

    # Generate QR code with user ID
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(citizen_id)  # TODO: Not enough data for QR code
    qr.make(fit=True)

    # Create an image from the QR Code
    img = qr.make_image(fill_color="black", back_color="white")

    # Convert to base64 for transport
    buffered = io.BytesIO()
    img.save(buffered)
    img_str = base64.b64encode(buffered.getvalue()).decode()

    return JSONResponse(content={"qr_code": img_str, "user_id": citizen_id})


# Get transaction history
@router.get("/{citizen_id}/transactions")
async def get_transactions(citizen_id: str):
    # Find transactions where user is either sender or receiver
    from_transactions = query_transactions_by_field("from_id", citizen_id)
    to_transactions = query_transactions_by_field("to_id", citizen_id)

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


# Transfer money to vendor
@router.post("/{citizen_id}/pay", response_model=MessageResponse)
async def pay_vendor(citizen_id: str, payment: PaymentRequest):
    # Check if citizen exists
    citizen = get_citizen(citizen_id)
    if not citizen:
        raise HTTPException(status_code=404, detail="Citizen not found")

    # Validate wallet type
    wallet_type = payment.wallet_type
    if wallet_type not in ["personal_wallet", "govt_wallet"]:
        raise HTTPException(status_code=400, detail="Invalid wallet type")

    # Check if payment amount is valid
    if payment.amount <= 0:
        raise HTTPException(
            status_code=400, detail="Payment amount must be greater than zero"
        )

    # Check if citizen has sufficient balance
    if citizen["wallet_info"][wallet_type]["balance"] < payment.amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")

    # Check if vendor exists
    vendor = get_vendor(payment.vendor_id)
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")

    # Create a transaction
    transaction = Transaction(
        from_id=citizen_id,
        to_id=payment.vendor_id,
        amount=payment.amount,
        tx_type="citizen-to-vendor",
        description=payment.description or "Payment to vendor",
    )
    transaction_dict = transaction.to_dict()

    # Update citizen's wallet (reduce balance)
    update_citizen(
        citizen_id,
        {
            f"wallet_info.{wallet_type}.balance": citizen["wallet_info"][wallet_type][
                "balance"
            ]
            - payment.amount,
        },
    )

    # Add transaction to citizen's transactions list
    array_union(
        CITIZENS_PREFIX,
        citizen_id,
        f"wallet_info.{wallet_type}.transactions",
        [transaction.id],
    )

    # Update vendor's wallet (increase balance)
    update_vendor(
        payment.vendor_id,
        {
            "wallet_info.balance": vendor["wallet_info"]["balance"] + payment.amount,
        },
    )

    # Add transaction to vendor's transactions list
    array_union(
        VENDORS_PREFIX, payment.vendor_id, "wallet_info.transactions", [transaction.id]
    )

    # Save transaction to database
    save_transaction(transaction.id, transaction_dict)
    return JSONResponse(
        content={"message": "Payment successful", "transaction_id": transaction.id}
    )


# View eligible schemes
@router.get("/{citizen_id}/eligible-schemes")
async def get_eligible_schemes(citizen_id: str):
    citizen = get_citizen(citizen_id)
    if not citizen:
        raise HTTPException(status_code=404, detail="Citizen not found")

    # Get all active schemes
    active_schemes = query_transactions_by_field("status", "active")

    # Filter schemes based on eligibility criteria
    eligible_schemes = []
    for scheme in active_schemes:
        # Check if user is already a beneficiary
        if "beneficiaries" in scheme and citizen_id in scheme["beneficiaries"]:
            scheme["already_enrolled"] = True
            eligible_schemes.append(scheme)
            continue

        # Basic eligibility check
        eligible = (
            True  # TODO: Implement actual eligibility checks based on scheme criteria
        )
        if eligible:
            scheme["already_enrolled"] = False
            eligible_schemes.append(scheme)

    return JSONResponse(content=eligible_schemes)


# Enroll in a scheme
@router.post("/{citizen_id}/enroll-scheme/{scheme_id}", response_model=MessageResponse)
async def enroll_scheme(citizen_id: str, scheme_id: str):
    # Check if citizen exists
    citizen = get_citizen(citizen_id)
    if not citizen:
        raise HTTPException(status_code=404, detail="Citizen not found")

    # Check if scheme exists
    scheme = get_scheme(scheme_id)
    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")

    # Check if already enrolled
    if "beneficiaries" in scheme and citizen_id in scheme["beneficiaries"]:
        raise HTTPException(status_code=409, detail="Already enrolled in this scheme")

    # Update scheme to add citizen as a beneficiary
    array_union(SCHEMES_PREFIX, scheme_id, "beneficiaries", [citizen_id])
    return JSONResponse(content={"message": "Successfully enrolled in scheme"})
