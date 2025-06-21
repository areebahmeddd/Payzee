from fastapi import APIRouter, HTTPException, Body, Depends
from fastapi.responses import JSONResponse
from typing import Dict, Any
from models.api import SchemeCreate, MessageResponse
from models.scheme import Scheme
from utils.auth import require_government
from db import (
    get_government,
    update_government,
    delete_government,
    get_citizen,
    get_scheme,
    save_scheme,
    query_schemes_by_field,
    get_all_citizens,
    get_all_vendors,
    get_all_transactions,
    array_union,
    get_vendor,
    get_transaction,
)
from db.redis_config import GOVERNMENTS_PREFIX

router = APIRouter()


@router.get("/{government_id}")
async def get_government_profile(
    government_id: str, current_user: dict = Depends(require_government)
) -> JSONResponse:
    govt = get_government(government_id)
    if not govt:
        raise HTTPException(status_code=404, detail="Government not found")

    if current_user["user_id"] != government_id:
        raise HTTPException(
            status_code=403,
            detail="Access denied. You can only access your own profile.",
        )

    # Remove sensitive information
    if "password" in govt["account_info"]:
        govt["account_info"].pop("password")

    return JSONResponse(content=govt)


@router.put("/{government_id}", response_model=MessageResponse)
async def update_government_profile(
    government_id: str,
    data: Dict[str, Any] = Body(...),
    current_user: dict = Depends(require_government),
) -> JSONResponse:
    govt = get_government(government_id)
    if not govt:
        raise HTTPException(status_code=404, detail="Government not found")

    if current_user["user_id"] != government_id:
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

    update_government(government_id, update_data)
    return JSONResponse(content={"message": "Profile updated successfully"})


@router.delete("/{government_id}", response_model=MessageResponse)
async def delete_government_profile(
    government_id: str, current_user: dict = Depends(require_government)
) -> JSONResponse:
    govt = get_government(government_id)
    if not govt:
        raise HTTPException(status_code=404, detail="Government not found")

    if current_user["user_id"] != government_id:
        raise HTTPException(
            status_code=403,
            detail="Access denied. You can only delete your own profile.",
        )

    delete_government(government_id)
    return JSONResponse(content={"message": "Government profile deleted successfully"})


@router.get("/{government_id}/wallet")
async def get_wallet(
    government_id: str, current_user: dict = Depends(require_government)
) -> JSONResponse:
    if current_user["user_id"] != government_id:
        raise HTTPException(
            status_code=403,
            detail="Access denied. You can only access your own wallet.",
        )

    govt = get_government(government_id)
    if not govt:
        raise HTTPException(status_code=404, detail="Government not found")

    return JSONResponse(content=govt["wallet_info"])


@router.get("/{government_id}/citizens")
async def get_all_citizen_profiles(
    government_id: str, current_user: dict = Depends(require_government)
) -> JSONResponse:
    if current_user["user_id"] != government_id:
        raise HTTPException(
            status_code=403,
            detail="Access denied. You can only access your own government data.",
        )

    govt = get_government(government_id)
    if not govt:
        raise HTTPException(status_code=404, detail="Government not found")

    citizens = get_all_citizens()
    for citizen in citizens:
        if "account_info" in citizen and "password" in citizen["account_info"]:
            citizen["account_info"].pop("password")

    return JSONResponse(content=citizens)


@router.get("/{government_id}/citizens/{citizen_id}")
async def get_specific_citizen(
    government_id: str,
    citizen_id: str,
    current_user: dict = Depends(require_government),
) -> JSONResponse:
    if current_user["user_id"] != government_id:
        raise HTTPException(
            status_code=403,
            detail="Access denied. You can only access your own government data.",
        )

    govt = get_government(government_id)
    if not govt:
        raise HTTPException(status_code=404, detail="Government not found")

    citizen = get_citizen(citizen_id)
    if not citizen:
        raise HTTPException(status_code=404, detail="Citizen not found")

    if "account_info" in citizen and "password" in citizen["account_info"]:
        citizen["account_info"].pop("password")

    return JSONResponse(content=citizen)


@router.get("/{government_id}/vendors")
async def get_all_vendor_profiles(
    government_id: str, current_user: dict = Depends(require_government)
) -> JSONResponse:
    if current_user["user_id"] != government_id:
        raise HTTPException(
            status_code=403,
            detail="Access denied. You can only access your own government data.",
        )

    govt = get_government(government_id)
    if not govt:
        raise HTTPException(status_code=404, detail="Government not found")

    vendors = get_all_vendors()
    for vendor in vendors:
        if "account_info" in vendor and "password" in vendor["account_info"]:
            vendor["account_info"].pop("password")

    return JSONResponse(content=vendors)


@router.get("/{government_id}/vendors/{vendor_id}")
async def get_specific_vendor(government_id: str, vendor_id: str) -> JSONResponse:
    govt = get_government(government_id)
    if not govt:
        raise HTTPException(status_code=404, detail="Government not found")

    vendor = get_vendor(vendor_id)
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")

    if "account_info" in vendor and "password" in vendor["account_info"]:
        vendor["account_info"].pop("password")

    return JSONResponse(content=vendor)


@router.get("/{government_id}/transactions")
async def get_all_system_transactions(
    government_id: str, current_user: dict = Depends(require_government)
) -> JSONResponse:
    if current_user["user_id"] != government_id:
        raise HTTPException(
            status_code=403,
            detail="Access denied. You can only access your own government data.",
        )

    govt = get_government(government_id)
    if not govt:
        raise HTTPException(status_code=404, detail="Government not found")

    transactions = get_all_transactions()
    # Sort by timestamp, newest first
    transactions.sort(
        key=lambda x: x["timestamp"] if "timestamp" in x else "", reverse=True
    )
    return JSONResponse(content=transactions)


@router.get("/{government_id}/transactions/{transaction_id}")
async def get_specific_transaction(
    government_id: str, transaction_id: str
) -> JSONResponse:
    govt = get_government(government_id)
    if not govt:
        raise HTTPException(status_code=404, detail="Government not found")

    transaction = get_transaction(transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    return JSONResponse(content=transaction)


@router.post("/{government_id}/schemes", response_model=MessageResponse)
async def create_scheme(government_id: str, scheme_data: SchemeCreate) -> JSONResponse:
    govt = get_government(government_id)
    if not govt:
        raise HTTPException(status_code=404, detail="Government not found")

    # Create a new scheme
    scheme = Scheme(
        name=scheme_data.name,
        description=scheme_data.description,
        govt_id=government_id,
        amount=scheme_data.amount,
        eligibility_criteria=scheme_data.eligibility_criteria,
        tags=scheme_data.tags or [],
        status=scheme_data.status,
    )

    scheme_dict = scheme.to_dict()
    # Save scheme to database
    save_scheme(scheme.id, scheme_dict)

    # Add scheme to government's schemes list
    array_union(GOVERNMENTS_PREFIX, government_id, "wallet_info.schemes", [scheme.id])
    return JSONResponse(
        content={"message": "Scheme created successfully", "scheme_id": scheme.id}
    )


@router.get("/{government_id}/schemes")
async def get_schemes(government_id: str) -> JSONResponse:
    govt = get_government(government_id)
    if not govt:
        raise HTTPException(status_code=404, detail="Government not found")

    schemes = query_schemes_by_field("govt_id", government_id)
    return JSONResponse(content=schemes)


@router.get("/{government_id}/schemes/{scheme_id}")
async def get_specific_scheme(government_id: str, scheme_id: str) -> JSONResponse:
    govt = get_government(government_id)
    if not govt:
        raise HTTPException(status_code=404, detail="Government not found")

    scheme = get_scheme(scheme_id)
    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")

    if scheme["govt_id"] != government_id:
        raise HTTPException(
            status_code=403, detail="Not authorized to access this scheme"
        )

    return JSONResponse(content=scheme)


@router.put("/{government_id}/schemes/{scheme_id}", response_model=MessageResponse)
async def update_scheme(
    government_id: str, scheme_id: str, scheme_data: SchemeCreate
) -> JSONResponse:
    govt = get_government(government_id)
    if not govt:
        raise HTTPException(status_code=404, detail="Government not found")

    existing_scheme = get_scheme(scheme_id)
    if not existing_scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")

    if existing_scheme["govt_id"] != government_id:
        raise HTTPException(
            status_code=403, detail="Not authorized to update this scheme"
        )

    updated_scheme = Scheme(
        name=scheme_data.name,
        description=scheme_data.description,
        govt_id=government_id,
        amount=scheme_data.amount,
        eligibility_criteria=scheme_data.eligibility_criteria,
        tags=scheme_data.tags or [],
        status=scheme_data.status,
    )

    # Preserve the original ID and beneficiaries
    updated_scheme.id = scheme_id
    updated_scheme.beneficiaries = existing_scheme["beneficiaries"]
    updated_scheme.created_at = existing_scheme["created_at"]

    # Update and save
    scheme_dict = updated_scheme.to_dict()
    save_scheme(scheme_id, scheme_dict)

    return JSONResponse(
        content={"message": "Scheme updated successfully", "scheme_id": scheme_id}
    )


@router.delete("/{government_id}/schemes/{scheme_id}", response_model=MessageResponse)
async def soft_delete_scheme(government_id: str, scheme_id: str) -> JSONResponse:
    govt = get_government(government_id)
    if not govt:
        raise HTTPException(status_code=404, detail="Government not found")

    existing_scheme = get_scheme(scheme_id)
    if not existing_scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")

    if existing_scheme["govt_id"] != government_id:
        raise HTTPException(
            status_code=403, detail="Not authorized to delete this scheme"
        )

    # Update only the status field to inactive
    existing_scheme["status"] = "inactive"
    save_scheme(scheme_id, existing_scheme)

    return JSONResponse(
        content={"message": "Scheme marked as inactive", "scheme_id": scheme_id}
    )


@router.get("/{government_id}/schemes/{scheme_id}/beneficiaries")
async def get_scheme_beneficiaries(government_id: str, scheme_id: str) -> JSONResponse:
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
                if "password" in citizen["account_info"]:
                    citizen["account_info"].pop("password")

                beneficiaries.append(citizen)

    return JSONResponse(content=beneficiaries)
