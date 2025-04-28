from fastapi import APIRouter, HTTPException, status
from firebase_admin import auth
from typing import Dict, Any

from app.models import UserCreate, UserLogin
from app.db import (
    create_user,
    create_vendor,
    get_user_by_email,
    get_user_by_id,
    get_vendor_by_email,
    get_vendor_by_id,
    update_user_profile,
    update_vendor_profile,
)

router = APIRouter(tags=["authentication"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate):
    try:
        user_type = user_data.user_type
        if user_type == "user":
            existing_user = get_user_by_email(user_data.email)
        else:
            existing_user = get_vendor_by_email(user_data.email)

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

        auth.create_user(
            email=user_data.email,
            password=user_data.password,
            display_name=user_data.username,
        )

        user_dict = {
            "email": user_data.email,
            "username": user_data.username,
            "full_name": None,
            "phone_number": None,
            "address": None,
            "aadhaar_number": user_data.aadhaar_number,
        }

        if user_type == "user":
            user_id = create_user(user_dict)
        else:  # vendor
            user_dict["business_name"] = ""
            user_dict["business_description"] = None
            user_dict["category"] = None
            user_dict[
                "inventory"
            ] = []  # Initialize empty inventory within vendor document
            user_id = create_vendor(user_dict)

        return {
            "id": user_id,
            "message": f"{user_type.capitalize()} registered successfully",
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Registration failed: {str(e)}",
        )


@router.post("/login")
async def login(user_data: UserLogin):
    try:
        user = get_user_by_email(user_data.email) or get_vendor_by_email(
            user_data.email
        )
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )

        return {
            "id": user.get("id"),
            "email": user.get("email"),
            "username": user.get("username"),
            "message": "Login successful",
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Login failed: {str(e)}"
        )


@router.post("/user-profile", status_code=status.HTTP_200_OK)
async def update_user_profile_endpoint(profile_data: Dict[str, Any], user_id: str):
    try:
        user = get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

        update_user_profile(user_id, profile_data)
        return {"message": "User profile updated successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update profile: {str(e)}",
        )


@router.post("/vendor-profile", status_code=status.HTTP_200_OK)
async def update_vendor_profile_endpoint(profile_data: Dict[str, Any], vendor_id: str):
    try:
        vendor = get_vendor_by_id(vendor_id)
        if not vendor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Vendor not found"
            )

        if "business_name" in profile_data and not profile_data["business_name"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Business name is required for vendors",
            )

        update_vendor_profile(vendor_id, profile_data)
        return {"message": "Vendor profile updated successfully"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update profile: {str(e)}",
        )


@router.get("/user/{user_id}", status_code=status.HTTP_200_OK)
async def get_user_profile(user_id: str):
    user = get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return user


@router.get("/vendor/{vendor_id}", status_code=status.HTTP_200_OK)
async def get_vendor_profile(vendor_id: str):
    vendor = get_vendor_by_id(vendor_id)
    if not vendor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Vendor not found"
        )

    return vendor
