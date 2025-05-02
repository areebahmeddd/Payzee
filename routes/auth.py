from fastapi import APIRouter, HTTPException, Body
from models.api import UserSignup, UserLogin, LoginResponse
from models.citizen import Citizen
from models.vendor import Vendor
from models.government import Government
from db import citizens_collection, vendors_collection, governments_collection

router = APIRouter()


@router.post("/signup", status_code=201)
async def signup(data: UserSignup = Body(...)):
    # Check email uniqueness based on user type
    user_type = data.user_type
    email = data.email

    if user_type == "citizen":
        # Check if email already exists
        existing_user = citizens_collection.where(
            "account_info.email", "==", email
        ).get()
        if len(list(existing_user)) > 0:
            raise HTTPException(status_code=409, detail="Email already in use")

        # Create citizen
        citizen = Citizen(
            name=data.name,
            email=email,
            password=data.password,
            phone=data.phone,
            address=data.address,
        )

        citizens_collection.document(citizen.account_info["id"]).set(citizen.to_dict())
        return {
            "message": "Citizen registered successfully",
            "user_id": citizen.account_info["id"],
        }

    elif user_type == "vendor":
        existing_user = vendors_collection.where(
            "account_info.email", "==", email
        ).get()
        if len(list(existing_user)) > 0:
            raise HTTPException(status_code=409, detail="Email already in use")

        vendor = Vendor(
            name=data.name,
            email=email,
            password=data.password,
            business_name=data.business_name,
            phone=data.phone,
            address=data.address,
            business_id=data.business_id,
        )

        vendors_collection.document(vendor.account_info["id"]).set(vendor.to_dict())
        return {
            "message": "Vendor registered successfully",
            "user_id": vendor.account_info["id"],
        }

    elif user_type == "government":
        existing_user = governments_collection.where(
            "account_info.email", "==", email
        ).get()
        if len(list(existing_user)) > 0:
            raise HTTPException(status_code=409, detail="Email already in use")

        government = Government(
            name=data.name,
            email=email,
            password=data.password,
            department=data.department,
            jurisdiction=data.jurisdiction,
            govt_id=data.govt_id,
        )

        governments_collection.document(government.account_info["id"]).set(
            government.to_dict()
        )
        return {
            "message": "Government registered successfully",
            "user_id": government.account_info["id"],
        }

    else:
        raise HTTPException(status_code=400, detail="Invalid user type")


@router.post("/signin", response_model=LoginResponse)
async def signin(data: UserLogin):
    email = data.email
    password = data.password
    user_type = data.user_type

    if user_type == "citizen":
        users_ref = (
            citizens_collection.where("account_info.email", "==", email)
            .limit(1)
            .stream()
        )
    elif user_type == "vendor":
        users_ref = (
            vendors_collection.where("account_info.email", "==", email)
            .limit(1)
            .stream()
        )
    elif user_type == "government":
        users_ref = (
            governments_collection.where("account_info.email", "==", email)
            .limit(1)
            .stream()
        )
    else:
        raise HTTPException(status_code=400, detail="Invalid user type")

    # Get the first (and should be only) user
    user_data = None
    for doc in users_ref:
        user_data = doc.to_dict()
        break

    if (
        not user_data or user_data["account_info"]["password"] != password
    ):  # TODO: Hash and verify password
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # TODO: Generate JWT token here
    return {
        "message": "Logged in successfully",
        "user_id": user_data["account_info"]["id"],
        # "user_type": user_type,
    }
