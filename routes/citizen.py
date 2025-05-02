import io
import qrcode
import base64
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from firebase_admin import firestore
from models.api import ProfileUpdate, PaymentRequest, MessageResponse
from models.transaction import Transaction
from db import (
    citizens_collection,
    vendors_collection,
    schemes_collection,
    transactions_collection,
)

router = APIRouter()


# Get citizen profile
@router.get("/{user_id}")
async def get_citizen_profile(user_id: str):
    doc_ref = citizens_collection.document(user_id)
    doc = doc_ref.get()

    if not doc.exists:
        raise HTTPException(status_code=404, detail="Citizen not found")

    citizen = doc.to_dict()
    # Remove sensitive information
    if "password" in citizen["account_info"]:
        citizen["account_info"].pop("password")

    return JSONResponse(content=citizen)


# Update citizen profile
@router.put("/{user_id}", response_model=MessageResponse)
async def update_citizen_profile(user_id: str, data: ProfileUpdate):
    doc_ref = citizens_collection.document(user_id)
    doc = doc_ref.get()

    if not doc.exists:
        raise HTTPException(status_code=404, detail="Citizen not found")

    # Only update fields that are present
    update_data = {}
    for field, value in data.dict(exclude_none=True).items():
        update_data[f"account_info.{field}"] = value

    if not update_data:
        raise HTTPException(status_code=400, detail="No valid fields to update")

    doc_ref.update(update_data)
    return JSONResponse(content={"message": "Profile updated successfully"})


# Get wallet information
@router.get("/{user_id}/wallet")
async def get_wallet(user_id: str):
    doc_ref = citizens_collection.document(user_id)
    doc = doc_ref.get()

    if not doc.exists:
        raise HTTPException(status_code=404, detail="Citizen not found")

    citizen = doc.to_dict()
    return JSONResponse(content=citizen["wallet_info"])


# Generate QR code for payment
@router.get("/{user_id}/generate-qr")
async def generate_qr(user_id: str):
    doc_ref = citizens_collection.document(user_id)
    doc = doc_ref.get()

    if not doc.exists:
        raise HTTPException(status_code=404, detail="Citizen not found")

    # Generate QR code with user ID
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(user_id)
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
    # Find transactions where user is either sender or receiver
    from_transactions = transactions_collection.where("from_id", "==", user_id).stream()
    to_transactions = transactions_collection.where("to_id", "==", user_id).stream()

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


# Transfer money to vendor
@router.post("/{user_id}/pay", response_model=MessageResponse)
async def pay_vendor(user_id: str, payment: PaymentRequest):
    # Get citizen
    citizen_doc = citizens_collection.document(user_id).get()
    if not citizen_doc.exists:
        raise HTTPException(status_code=404, detail="Citizen not found")

    citizen = citizen_doc.to_dict()

    # Validate wallet type
    wallet_type = payment.wallet_type
    if wallet_type not in ["personal_wallet", "govt_wallet"]:
        raise HTTPException(status_code=400, detail="Invalid wallet type")

    # Check if citizen has sufficient balance
    if citizen["wallet_info"][wallet_type]["balance"] < payment.amount:
        raise HTTPException(status_code=400, detail="Insufficient balance")

    # Check if vendor exists
    vendor_doc = vendors_collection.document(payment.vendor_id).get()
    if not vendor_doc.exists:
        raise HTTPException(status_code=404, detail="Vendor not found")

    # Create a transaction
    transaction = Transaction(
        from_id=user_id,
        to_id=payment.vendor_id,
        amount=payment.amount,
        transaction_type="citizen-to-vendor",
        description=payment.description or "Payment to vendor",
    )

    # Update citizen's wallet (reduce balance)
    citizens_collection.document(user_id).update(
        {
            f"wallet_info.{wallet_type}.balance": citizen["wallet_info"][wallet_type][
                "balance"
            ]
            - payment.amount,
            f"wallet_info.{wallet_type}.transactions": firestore.ArrayUnion(
                [transaction.id]
            ),
        }
    )

    # Update vendor's wallet (increase balance)
    vendor = vendor_doc.to_dict()
    vendors_collection.document(payment.vendor_id).update(
        {
            "wallet_info.balance": vendor["wallet_info"]["balance"] + payment.amount,
            "wallet_info.transactions": firestore.ArrayUnion([transaction.id]),
        }
    )

    # Save transaction to database
    transaction_dict = transaction.to_dict()
    transactions_collection.document(transaction.id).set(transaction_dict)

    return JSONResponse(
        content={"message": "Payment successful", "transaction_id": transaction.id}
    )


# View eligible schemes
@router.get("/{user_id}/eligible-schemes")
async def get_eligible_schemes(user_id: str):
    # Check if citizen exists
    citizen_doc = citizens_collection.document(user_id).get()
    if not citizen_doc.exists:
        raise HTTPException(status_code=404, detail="Citizen not found")

    # Get all active schemes
    active_schemes = schemes_collection.where("status", "==", "active").stream()

    # Filter schemes based on eligibility criteria
    eligible_schemes = []
    for doc in active_schemes:
        scheme = doc.to_dict()
        scheme["id"] = doc.id

        # Check if user is already a beneficiary
        if user_id in scheme.get("beneficiaries", []):
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
@router.post("/{user_id}/enroll-scheme/{scheme_id}", response_model=MessageResponse)
async def enroll_scheme(user_id: str, scheme_id: str):
    # Check if citizen exists
    citizen_doc = citizens_collection.document(user_id).get()
    if not citizen_doc.exists:
        raise HTTPException(status_code=404, detail="Citizen not found")

    # Check if scheme exists
    scheme_doc = schemes_collection.document(scheme_id).get()
    if not scheme_doc.exists:
        raise HTTPException(status_code=404, detail="Scheme not found")

    scheme = scheme_doc.to_dict()

    # Check if already enrolled
    if user_id in scheme.get("beneficiaries", []):
        raise HTTPException(status_code=409, detail="Already enrolled in this scheme")

    # Update scheme to add citizen as a beneficiary
    schemes_collection.document(scheme_id).update(
        {"beneficiaries": firestore.ArrayUnion([user_id])}
    )

    return JSONResponse(content={"message": "Successfully enrolled in scheme"})
