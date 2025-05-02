from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from firebase_admin import firestore
from models.api import ProfileUpdate, SchemeModel, MessageResponse
from models.scheme import Scheme
from models.transaction import Transaction
from db import (
    governments_collection,
    citizens_collection,
    vendors_collection,
    schemes_collection,
    transactions_collection,
)

router = APIRouter()


# Get government profile
@router.get("/{govt_id}")
async def get_government_profile(govt_id: str):
    # Check if government exists
    doc_ref = governments_collection.document(govt_id)
    doc = doc_ref.get()

    if not doc.exists:
        raise HTTPException(status_code=404, detail="Government account not found")

    govt = doc.to_dict()
    # Remove sensitive information
    if "password" in govt["account_info"]:
        govt["account_info"].pop("password")

    return JSONResponse(content=govt)


# Update government profile
@router.put("/{govt_id}", response_model=MessageResponse)
async def update_government_profile(govt_id: str, data: ProfileUpdate):
    doc_ref = governments_collection.document(govt_id)
    doc = doc_ref.get()

    if not doc.exists:
        raise HTTPException(status_code=404, detail="Government account not found")

    # Update fields that are present
    update_data = {}
    for field, value in data.dict(exclude_none=True).items():
        update_data[f"account_info.{field}"] = value

    if not update_data:
        raise HTTPException(status_code=400, detail="No valid fields to update")

    doc_ref.update(update_data)
    return JSONResponse(content={"message": "Profile updated successfully"})


# Get wallet information
@router.get("/{govt_id}/wallet")
async def get_wallet(govt_id: str):
    doc_ref = governments_collection.document(govt_id)
    doc = doc_ref.get()

    if not doc.exists:
        raise HTTPException(status_code=404, detail="Government account not found")

    govt = doc.to_dict()
    return JSONResponse(content=govt["wallet_info"])


# Get all schemes
@router.get("/{govt_id}/schemes")
async def get_schemes(govt_id: str):
    schemes_docs = schemes_collection.where("govt_id", "==", govt_id).stream()

    schemes = []
    for doc in schemes_docs:
        scheme = doc.to_dict()
        scheme["id"] = doc.id
        schemes.append(scheme)

    return JSONResponse(content=schemes)


# Create new scheme
@router.post("/{govt_id}/schemes", status_code=201, response_model=MessageResponse)
async def create_scheme(govt_id: str, scheme_data: SchemeModel):
    govt_doc = governments_collection.document(govt_id).get()
    if not govt_doc.exists:
        raise HTTPException(status_code=404, detail="Government account not found")

    # Create new scheme
    scheme = Scheme(
        name=scheme_data.name,
        description=scheme_data.description,
        govt_id=govt_id,
        amount=scheme_data.amount,
        eligibility_criteria=scheme_data.eligibility_criteria,
        tags=scheme_data.tags,
    )

    # Save scheme to database
    scheme_ref = schemes_collection.document(scheme.id)
    scheme_ref.set(scheme.to_dict())

    # Update government account to reference this scheme
    governments_collection.document(govt_id).update(
        {"wallet_info.schemes": firestore.ArrayUnion([scheme.id])}
    )

    return JSONResponse(
        content={"message": "Scheme created successfully", "scheme_id": scheme.id},
        status_code=201,
    )


# Update existing scheme
@router.put("/{govt_id}/schemes/{scheme_id}", response_model=MessageResponse)
async def update_scheme(govt_id: str, scheme_id: str, data: SchemeModel):
    # Check if scheme exists and belongs to this government
    scheme_doc = schemes_collection.document(scheme_id).get()
    if not scheme_doc.exists or scheme_doc.to_dict().get("govt_id") != govt_id:
        raise HTTPException(
            status_code=404, detail="Scheme not found or you don't have permission"
        )

    # Update scheme details
    update_data = {}
    for field, value in data.dict(exclude_none=True).items():
        update_data[field] = value

    if not update_data:
        raise HTTPException(status_code=400, detail="No valid fields to update")

    schemes_collection.document(scheme_id).update(update_data)
    return JSONResponse(content={"message": "Scheme updated successfully"})


# Get beneficiaries of a scheme
@router.get("/{govt_id}/schemes/{scheme_id}/beneficiaries")
async def get_scheme_beneficiaries(govt_id: str, scheme_id: str):
    scheme_doc = schemes_collection.document(scheme_id).get()
    if not scheme_doc.exists or scheme_doc.to_dict().get("govt_id") != govt_id:
        raise HTTPException(
            status_code=404, detail="Scheme not found or you don't have permission"
        )

    scheme = scheme_doc.to_dict()
    beneficiaries = []

    for citizen_id in scheme.get("beneficiaries", []):
        citizen_doc = citizens_collection.document(citizen_id).get()
        if citizen_doc.exists:
            citizen = citizen_doc.to_dict()
            # Remove sensitive information
            if "password" in citizen["account_info"]:
                citizen["account_info"].pop("password")
            beneficiaries.append(citizen)

    return JSONResponse(content=beneficiaries)


# Disburse funds to citizens enrolled in a scheme
@router.post("/{govt_id}/schemes/{scheme_id}/disburse", response_model=MessageResponse)
async def disburse_funds(govt_id: str, scheme_id: str):
    scheme_doc = schemes_collection.document(scheme_id).get()
    if not scheme_doc.exists or scheme_doc.to_dict().get("govt_id") != govt_id:
        raise HTTPException(
            status_code=404, detail="Scheme not found or you don't have permission"
        )

    scheme = scheme_doc.to_dict()

    # Get government account
    govt_doc = governments_collection.document(govt_id).get()
    if not govt_doc.exists:
        raise HTTPException(status_code=404, detail="Government account not found")

    govt = govt_doc.to_dict()

    # Check if government has enough balance
    beneficiaries = scheme.get("beneficiaries", [])
    total_amount_needed = scheme["amount"] * len(beneficiaries)

    if govt["wallet_info"]["balance"] < total_amount_needed:
        raise HTTPException(
            status_code=400,
            detail=f"Insufficient funds in government wallet. Required: {total_amount_needed}, Available: {govt['wallet_info']['balance']}",
        )

    # Process disbursement for each beneficiary
    successful_transfers = []
    failed_transfers = []

    for citizen_id in beneficiaries:
        try:
            # Create transaction
            transaction = Transaction(
                from_id=govt_id,
                to_id=citizen_id,
                amount=scheme["amount"],
                transaction_type="govt-to-citizen",
                scheme_id=scheme_id,
                description=f"Disbursement for scheme: {scheme['name']}",
            )

            # Update citizen wallet
            citizen_doc = citizens_collection.document(citizen_id)
            citizen = citizen_doc.get().to_dict()

            citizen_doc.update(
                {
                    "wallet_info.govt_wallet.balance": citizen["wallet_info"][
                        "govt_wallet"
                    ]["balance"]
                    + scheme["amount"],
                    "wallet_info.govt_wallet.transactions": firestore.ArrayUnion(
                        [transaction.id]
                    ),
                }
            )

            # Save transaction to database
            transactions_collection.document(transaction.id).set(transaction.to_dict())

            successful_transfers.append(
                {
                    "citizen_id": citizen_id,
                    "amount": scheme["amount"],
                    "transaction_id": transaction.id,
                }
            )
        except Exception as e:
            failed_transfers.append({"citizen_id": citizen_id, "error": str(e)})

    # Update government wallet balance
    governments_collection.document(govt_id).update(
        {"wallet_info.balance": govt["wallet_info"]["balance"] - total_amount_needed}
    )

    return JSONResponse(
        content={
            "message": "Disbursement completed",
            "successful_transfers": successful_transfers,
            "failed_transfers": failed_transfers,
            "total_disbursed": scheme["amount"] * len(successful_transfers),
        }
    )


# View citizen profile
@router.get("/{govt_id}/citizens/{citizen_id}")
async def view_citizen_profile(govt_id: str, citizen_id: str):
    govt_doc = governments_collection.document(govt_id).get()
    if not govt_doc.exists:
        raise HTTPException(status_code=404, detail="Government account not found")

    # Get citizen profile
    citizen_doc = citizens_collection.document(citizen_id).get()
    if not citizen_doc.exists:
        raise HTTPException(status_code=404, detail="Citizen not found")

    citizen = citizen_doc.to_dict()
    if "password" in citizen["account_info"]:
        citizen["account_info"].pop("password")

    return JSONResponse(content=citizen)


# Get all citizens
@router.get("/{govt_id}/citizens")
async def get_all_citizens(govt_id: str):
    govt_doc = governments_collection.document(govt_id).get()
    if not govt_doc.exists:
        raise HTTPException(status_code=404, detail="Government account not found")

    citizens_docs = citizens_collection.stream()
    citizens = []

    for doc in citizens_docs:
        citizen = doc.to_dict()
        if "password" in citizen["account_info"]:
            citizen["account_info"].pop("password")
        citizen["id"] = doc.id
        citizens.append(citizen)

    return JSONResponse(content=citizens)


# View vendor profile
@router.get("/{govt_id}/vendors/{vendor_id}")
async def view_vendor_profile(govt_id: str, vendor_id: str):
    govt_doc = governments_collection.document(govt_id).get()
    if not govt_doc.exists:
        raise HTTPException(status_code=404, detail="Government account not found")

    # Get vendor profile
    vendor_doc = vendors_collection.document(vendor_id).get()
    if not vendor_doc.exists:
        raise HTTPException(status_code=404, detail="Vendor not found")

    vendor = vendor_doc.to_dict()
    if "password" in vendor["account_info"]:
        vendor["account_info"].pop("password")

    return JSONResponse(content=vendor)


# Get all vendors
@router.get("/{govt_id}/vendors")
async def get_all_vendors(govt_id: str):
    govt_doc = governments_collection.document(govt_id).get()
    if not govt_doc.exists:
        raise HTTPException(status_code=404, detail="Government account not found")

    vendors_docs = vendors_collection.stream()
    vendors = []

    for doc in vendors_docs:
        vendor = doc.to_dict()
        if "password" in vendor["account_info"]:
            vendor["account_info"].pop("password")
        vendor["id"] = doc.id
        vendors.append(vendor)

    return JSONResponse(content=vendors)


# Get all transactions
@router.get("/{govt_id}/transactions")
async def get_all_transactions(govt_id: str):
    govt_doc = governments_collection.document(govt_id).get()
    if not govt_doc.exists:
        raise HTTPException(status_code=404, detail="Government account not found")

    # Get all transactions from the collection
    transactions_docs = transactions_collection.stream()
    transactions = []

    for doc in transactions_docs:
        transaction = doc.to_dict()
        transaction["id"] = doc.id
        transactions.append(transaction)

    return JSONResponse(content=transactions)
