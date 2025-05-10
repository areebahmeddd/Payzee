from fastapi import APIRouter, HTTPException, Body
from fastapi.responses import JSONResponse
from models.api import DisbursementRequest, SchemeCreate, MessageResponse
from models.transaction import Transaction
from models.scheme import Scheme
from db import (
    get_government,
    update_government,
    get_citizen,
    update_citizen,
    get_scheme,
    save_scheme,
    save_transaction,
    query_schemes_by_field,
    get_all_citizens,
    get_all_vendors,
    get_all_transactions,
    array_union,
    get_vendor,
    get_transaction,
)
from db.redis_config import GOVERNMENTS_PREFIX, CITIZENS_PREFIX

router = APIRouter()


# Get government profile
@router.get("/{government_id}")
async def get_government_profile(government_id: str):
    # Check if government exists
    govt = get_government(government_id)
    if not govt:
        raise HTTPException(status_code=404, detail="Government not found")

    # Remove sensitive information
    if "password" in govt["account_info"]:
        govt["account_info"].pop("password")

    return JSONResponse(content=govt)


# Update government profile
@router.put("/{government_id}", response_model=MessageResponse)
async def update_government_profile(government_id: str, data: dict = Body(...)):
    govt = get_government(government_id)
    if not govt:
        raise HTTPException(status_code=404, detail="Government not found")

    # Only update fields that are present
    update_data = {}
    for field, value in data.items():
        update_data[f"account_info.{field}"] = value

    if not update_data:
        raise HTTPException(status_code=400, detail="No valid fields to update")

    update_government(government_id, update_data)
    return JSONResponse(content={"message": "Profile updated successfully"})


# Get wallet information
@router.get("/{government_id}/wallet")
async def get_wallet(government_id: str):
    govt = get_government(government_id)
    if not govt:
        raise HTTPException(status_code=404, detail="Government not found")

    return JSONResponse(content=govt["wallet_info"])


# Get all citizens
@router.get("/{government_id}/all-citizens")
async def get_all_citizen_profiles(government_id: str):
    govt = get_government(government_id)
    if not govt:
        raise HTTPException(status_code=404, detail="Government not found")

    citizens = get_all_citizens()

    for citizen in citizens:
        if "account_info" in citizen and "password" in citizen["account_info"]:
            citizen["account_info"].pop("password")

    return JSONResponse(content=citizens)


# Get specific citizen by ID
@router.get("/{government_id}/citizen/{citizen_id}")
async def get_specific_citizen(government_id: str, citizen_id: str):
    govt = get_government(government_id)
    if not govt:
        raise HTTPException(status_code=404, detail="Government not found")

    citizen = get_citizen(citizen_id)
    if not citizen:
        raise HTTPException(status_code=404, detail="Citizen not found")

    if "account_info" in citizen and "password" in citizen["account_info"]:
        citizen["account_info"].pop("password")

    return JSONResponse(content=citizen)


# Get all vendors
@router.get("/{government_id}/all-vendors")
async def get_all_vendor_profiles(government_id: str):
    govt = get_government(government_id)
    if not govt:
        raise HTTPException(status_code=404, detail="Government not found")

    vendors = get_all_vendors()

    for vendor in vendors:
        if "account_info" in vendor and "password" in vendor["account_info"]:
            vendor["account_info"].pop("password")

    return JSONResponse(content=vendors)


# Get specific vendor by ID
@router.get("/{government_id}/vendor/{vendor_id}")
async def get_specific_vendor(government_id: str, vendor_id: str):
    govt = get_government(government_id)
    if not govt:
        raise HTTPException(status_code=404, detail="Government not found")

    vendor = get_vendor(vendor_id)
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")

    if "account_info" in vendor and "password" in vendor["account_info"]:
        vendor["account_info"].pop("password")

    return JSONResponse(content=vendor)


# Get all transactions
@router.get("/{government_id}/all-transactions")
async def get_all_system_transactions(government_id: str):
    govt = get_government(government_id)
    if not govt:
        raise HTTPException(status_code=404, detail="Government not found")

    transactions = get_all_transactions()

    # Sort by timestamp, newest first
    transactions.sort(
        key=lambda x: x["timestamp"] if "timestamp" in x else "", reverse=True
    )
    return JSONResponse(content=transactions)


# Get specific transaction by ID
@router.get("/{government_id}/transaction/{transaction_id}")
async def get_specific_transaction(government_id: str, transaction_id: str):
    govt = get_government(government_id)
    if not govt:
        raise HTTPException(status_code=404, detail="Government not found")

    transaction = get_transaction(transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    return JSONResponse(content=transaction)


# Create a new scheme
@router.post("/{government_id}/schemes", response_model=MessageResponse)
async def create_scheme(government_id: str, scheme_data: SchemeCreate):
    govt = get_government(government_id)
    if not govt:
        raise HTTPException(status_code=404, detail="Government not found")

    # Create a new scheme
    scheme = Scheme(
        name=scheme_data.name,
        description=scheme_data.description,
        govt_id=government_id,
        amount=scheme_data.amount,
        status=scheme_data.status,
        eligibility_criteria=scheme_data.eligibility_criteria,
        tags=scheme_data.tags or [],
    )

    scheme_dict = scheme.to_dict()
    # Save scheme to database
    save_scheme(scheme.id, scheme_dict)

    # Add scheme to government's schemes list
    array_union(GOVERNMENTS_PREFIX, government_id, "wallet_info.schemes", [scheme.id])
    return JSONResponse(
        content={"message": "Scheme created successfully", "scheme_id": scheme.id}
    )


# Get all schemes created by this government
@router.get("/{government_id}/schemes")
async def get_schemes(government_id: str):
    govt = get_government(government_id)
    if not govt:
        raise HTTPException(status_code=404, detail="Government not found")

    # Get schemes created by this government
    schemes = query_schemes_by_field("govt_id", government_id)
    return JSONResponse(content=schemes)


# Get beneficiaries of a specific scheme
@router.get("/{government_id}/schemes/{scheme_id}/beneficiaries")
async def get_scheme_beneficiaries(government_id: str, scheme_id: str):
    # Check if the government exists
    govt = get_government(government_id)
    if not govt:
        raise HTTPException(status_code=404, detail="Government not found")

    # Get the scheme
    scheme = get_scheme(scheme_id)
    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")

    # Check if this government owns the scheme
    if scheme["govt_id"] != government_id:
        raise HTTPException(
            status_code=403, detail="Not authorized to access this scheme"
        )

    # Get the beneficiaries
    beneficiaries = []
    if "beneficiaries" in scheme:
        for citizen_id in scheme["beneficiaries"]:
            citizen = get_citizen(citizen_id)
            if citizen:
                # Remove sensitive info
                if "password" in citizen["account_info"]:
                    citizen["account_info"].pop("password")
                beneficiaries.append(citizen)

    return JSONResponse(content=beneficiaries)


# Disburse funds to beneficiaries
@router.post("/{government_id}/disburse", response_model=MessageResponse)
async def disburse_funds(government_id: str, disbursement: DisbursementRequest):
    # Check if the government exists
    govt = get_government(government_id)
    if not govt:
        raise HTTPException(status_code=404, detail="Government not found")

    # Check if the scheme exists
    scheme = get_scheme(disbursement.scheme_id)
    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")

    # Check if this government owns the scheme
    if scheme["govt_id"] != government_id:
        raise HTTPException(
            status_code=403, detail="Not authorized to access this scheme"
        )

    # Check if there's enough balance in the government wallet
    if govt["wallet_info"]["balance"] < disbursement.amount_per_user * len(
        scheme["beneficiaries"]
    ):
        raise HTTPException(status_code=400, detail="Insufficient balance")

    # Disburse funds to each beneficiary
    successful_disbursements = 0
    for citizen_id in scheme["beneficiaries"]:
        # Skip if citizen doesn't exist
        citizen = get_citizen(citizen_id)
        if not citizen:
            continue

        # Create a transaction for this disbursement
        transaction = Transaction(
            from_id=government_id,
            to_id=citizen_id,
            amount=disbursement.amount_per_user,
            tx_type="government-to-citizen",
            scheme_id=disbursement.scheme_id,
            description=f"Disbursement for {scheme['name']}",
        )
        transaction_dict = transaction.to_dict()

        # Update citizen's wallet
        update_citizen(
            citizen_id,
            {
                "wallet_info.govt_wallet.balance": citizen["wallet_info"][
                    "govt_wallet"
                ]["balance"]
                + disbursement.amount_per_user,
            },
        )

        # Add transaction to citizen's transactions
        array_union(
            CITIZENS_PREFIX,
            citizen_id,
            "wallet_info.govt_wallet.transactions",
            [transaction.id],
        )

        # Deduct from government wallet
        update_government(
            government_id,
            {
                "wallet_info.balance": govt["wallet_info"]["balance"]
                - disbursement.amount_per_user,
            },
        )

        # Add transaction to government's transactions
        array_union(
            GOVERNMENTS_PREFIX,
            government_id,
            "wallet_info.transactions",
            [transaction.id],
        )

        # Save transaction
        save_transaction(transaction.id, transaction_dict)
        successful_disbursements += 1

    return JSONResponse(
        content={
            "message": "Funds disbursed successfully",
            "beneficiaries_count": successful_disbursements,
        }
    )
