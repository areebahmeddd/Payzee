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
async def citizen_signup(data: CitizenSignup) -> JSONResponse:
    # Check if email already registered
    existing_users = query_citizens_by_field("account_info.email", data.email)
    if existing_users:
        raise HTTPException(status_code=409, detail="Email already registered")

    # Create citizen object
    citizen = Citizen(
        name=data.name,
        password=data.password,
        email=data.email,
        phone=data.phone,
        id_type=data.id_type,
        id_number=data.id_number,
        address=data.address,
        dob=data.dob,
        gender=data.gender,
        occupation=data.occupation,
        caste=data.caste,
        annual_income=data.annual_income,
        image_url=data.image_url,
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
async def vendor_signup(data: VendorSignup) -> JSONResponse:
    existing_users = query_vendors_by_field("account_info.email", data.email)
    if existing_users:
        raise HTTPException(status_code=409, detail="Email already registered")

    vendor = Vendor(
        name=data.name,
        password=data.password,
        email=data.email,
        gender=data.gender,
        business_name=data.business_name,
        business_id=data.business_id,
        license_type=data.license_type,
        occupation=data.occupation,
        phone=data.phone,
        address=data.address,
        image_url=data.image_url,
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
async def government_signup(data: GovernmentSignup) -> JSONResponse:
    existing_users = query_governments_by_field("account_info.email", data.email)
    if existing_users:
        raise HTTPException(status_code=409, detail="Email already registered")

    government = Government(
        name=data.name,
        password=data.password,
        email=data.email,
        jurisdiction=data.jurisdiction,
        govt_id=data.govt_id,
        image_url=data.image_url,
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
async def login(data: LoginRequest) -> JSONResponse:
    # Check in citizens collection
    citizen_results = query_citizens_by_field("personal_info.id_number", data.id_number)
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
    vendor_results = query_vendors_by_field("business_info.business_id", data.id_number)
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
    govt_results = query_governments_by_field("account_info.govt_id", data.id_number)
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

    raise HTTPException(status_code=401, detail="Invalid ID number or password")


@router.post("/logout", response_model=MessageResponse)
async def logout() -> JSONResponse:
    return JSONResponse(content={"message": "Logged out successfully"})
