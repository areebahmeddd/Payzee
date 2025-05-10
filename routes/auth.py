from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from models.api import (
    CitizenSignup,
    VendorSignup,
    GovernmentSignup,
    LoginRequest,
    MessageResponse,
)
from models.citizen import Citizen
from models.vendor import Vendor
from models.government import Government
from db import (
    save_citizen,
    save_government,
    save_vendor,
    query_citizens_by_field,
    query_vendors_by_field,
    query_governments_by_field,
)

router = APIRouter()


@router.post("/signup/citizen", response_model=MessageResponse)
async def citizen_signup(data: CitizenSignup):
    # Check if email already registered
    existing_users = query_citizens_by_field("account_info.email", data.email)
    if existing_users:
        raise HTTPException(status_code=409, detail="Email already registered")

    # Create citizen object
    citizen = Citizen(
        name=data.name,
        email=data.email,
        password=data.password,
        phone=data.phone,
        address=data.address,
        id_type=data.id_type,
        id_number=data.id_number,
    )

    # Get citizen as dictionary
    citizen_dict = citizen.to_dict()
    citizen_id = citizen_dict["account_info"]["id"]

    # Save to database
    save_citizen(citizen_id, citizen_dict)
    return JSONResponse(
        content={
            "message": "Citizen account created successfully",
            "user_id": citizen_id,
            "user_type": "citizen",
        }
    )


@router.post("/signup/vendor", response_model=MessageResponse)
async def vendor_signup(data: VendorSignup):
    existing_users = query_vendors_by_field("account_info.email", data.email)
    if existing_users:
        raise HTTPException(status_code=409, detail="Email already registered")

    vendor = Vendor(
        name=data.name,
        email=data.email,
        password=data.password,
        business_name=data.business_name,
        phone=data.phone,
        address=data.address,
        business_id=data.business_id,
        license_type=data.license_type,
    )

    vendor_dict = vendor.to_dict()
    vendor_id = vendor_dict["account_info"]["id"]

    save_vendor(vendor_id, vendor_dict)
    return JSONResponse(
        content={
            "message": "Vendor account created successfully",
            "user_id": vendor_id,
            "user_type": "vendor",
        }
    )


@router.post("/signup/government", response_model=MessageResponse)
async def government_signup(data: GovernmentSignup):
    existing_users = query_governments_by_field("account_info.email", data.email)
    if existing_users:
        raise HTTPException(status_code=409, detail="Email already registered")

    government = Government(
        name=data.name,
        email=data.email,
        password=data.password,
        department=data.department,
        jurisdiction=data.jurisdiction,
        govt_id=data.govt_id,
    )

    government_dict = government.to_dict()
    govt_id = government_dict["account_info"]["id"]

    save_government(govt_id, government_dict)
    return JSONResponse(
        content={
            "message": "Government account created successfully",
            "user_id": govt_id,
            "user_type": "government",
        }
    )


@router.post("/login", response_model=MessageResponse)
async def login(data: LoginRequest):
    # Check in citizens collection
    citizen_results = query_citizens_by_field("account_info.email", data.email)
    if citizen_results:
        citizen = citizen_results[0]
        if citizen["account_info"]["password"] == data.password:
            return JSONResponse(
                content={
                    "message": "Login successful",
                    "user_id": citizen["account_info"]["id"],
                    "user_type": "citizen",
                }
            )

    # Check in vendors collection
    vendor_results = query_vendors_by_field("account_info.email", data.email)
    if vendor_results:
        vendor = vendor_results[0]
        if vendor["account_info"]["password"] == data.password:
            return JSONResponse(
                content={
                    "message": "Login successful",
                    "user_id": vendor["account_info"]["id"],
                    "user_type": "vendor",
                }
            )

    # Check in governments collection
    govt_results = query_governments_by_field("account_info.email", data.email)
    if govt_results:
        govt = govt_results[0]
        if govt["account_info"]["password"] == data.password:
            return JSONResponse(
                content={
                    "message": "Login successful",
                    "user_id": govt["account_info"]["id"],
                    "user_type": "government",
                }
            )

    raise HTTPException(status_code=401, detail="Invalid email or password")


@router.get("/logout", response_model=MessageResponse)
async def logout():
    pass
