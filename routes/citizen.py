import io
import qrcode
import base64
from fastapi import APIRouter, HTTPException, Body
from fastapi.responses import JSONResponse
from typing import Dict, Any
from models.api import PaymentRequest, MessageResponse
from models.transaction import Transaction
from db import (
    get_citizen,
    update_citizen,
    delete_citizen,
    get_vendor,
    update_vendor,
    save_transaction,
    query_transactions_by_field,
    array_union,
    get_all_schemes,
)
from db.redis_config import CITIZENS_PREFIX, VENDORS_PREFIX

router = APIRouter()


# Get citizen profile
@router.get("/{citizen_id}")
async def get_citizen_profile(citizen_id: str) -> JSONResponse:
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
async def update_citizen_profile(
    citizen_id: str, data: Dict[str, Any] = Body(...)
) -> JSONResponse:
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


# Delete citizen profile
@router.delete("/{citizen_id}", response_model=MessageResponse)
async def delete_citizen_profile(citizen_id: str) -> JSONResponse:
    citizen = get_citizen(citizen_id)
    if not citizen:
        raise HTTPException(status_code=404, detail="Citizen not found")

    # Delete the citizen
    delete_citizen(citizen_id)
    return JSONResponse(content={"message": "Citizen profile deleted successfully"})


# Get wallet information
@router.get("/{citizen_id}/wallet")
async def get_wallet(citizen_id: str) -> JSONResponse:
    citizen = get_citizen(citizen_id)
    if not citizen:
        raise HTTPException(status_code=404, detail="Citizen not found")

    return JSONResponse(content=citizen["wallet_info"])


# Generate QR code for payment
@router.get("/{citizen_id}/generate-qr")
async def generate_qr(citizen_id: str) -> JSONResponse:
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
async def get_transactions(citizen_id: str) -> JSONResponse:
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
async def pay_vendor(citizen_id: str, payment: PaymentRequest) -> JSONResponse:
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
async def get_eligible_schemes(citizen_id: str) -> JSONResponse:
    citizen = get_citizen(citizen_id)
    if not citizen:
        raise HTTPException(status_code=404, detail="Citizen not found")

    # Get all active schemes
    active_schemes = get_all_schemes()

    # Filter for active schemes
    active_schemes = [
        scheme for scheme in active_schemes if scheme.get("status") == "active"
    ]

    # Filter schemes based on eligibility criteria
    eligible_schemes = []
    for scheme in active_schemes:
        # Check if user is already a beneficiary
        already_enrolled = (
            "beneficiaries" in scheme and citizen_id in scheme["beneficiaries"]
        )

        # Get eligibility criteria from the scheme
        eligibility_criteria = scheme.get("eligibility_criteria", {})

        # Check each eligibility criterion against citizen's personal info
        eligible = True
        eligibility_results = {}

        # Personal info checks
        personal_info = citizen.get("personal_info", {})

        # Check occupation
        if "occupation" in eligibility_criteria:
            required_occupation = eligibility_criteria["occupation"]
            citizen_occupation = personal_info.get("occupation", "")

            # If "any" is specified or exact match
            if (
                required_occupation != "any"
                and required_occupation != citizen_occupation
            ):
                eligible = False
                eligibility_results["occupation"] = {
                    "required": required_occupation,
                    "actual": citizen_occupation,
                    "passed": False,
                }
            else:
                eligibility_results["occupation"] = {
                    "required": required_occupation,
                    "actual": citizen_occupation,
                    "passed": True,
                }

        # Check gender
        if "gender" in eligibility_criteria:
            required_gender: str = eligibility_criteria["gender"]
            citizen_gender: str = personal_info.get("gender", "")

            # If "any" is specified or exact match
            if required_gender != "any" and required_gender != citizen_gender:
                eligible = False
                eligibility_results["gender"] = {
                    "required": required_gender,
                    "actual": citizen_gender,
                    "passed": False,
                }
            else:
                eligibility_results["gender"] = {
                    "required": required_gender,
                    "actual": citizen_gender,
                    "passed": True,
                }

        # Check caste
        if "caste" in eligibility_criteria:
            required_caste: str = eligibility_criteria["caste"]
            citizen_caste: str = personal_info.get("caste", "")

            # If "all" is specified or exact match
            if required_caste != "all" and required_caste != citizen_caste:
                eligible = False
                eligibility_results["caste"] = {
                    "required": required_caste,
                    "actual": citizen_caste,
                    "passed": False,
                }
            else:
                eligibility_results["caste"] = {
                    "required": required_caste,
                    "actual": citizen_caste,
                    "passed": True,
                }

        # Check annual income
        if "annual_income" in eligibility_criteria:
            max_annual_income: float = eligibility_criteria["annual_income"]
            citizen_annual_income: float = personal_info.get(
                "annual_income", float("inf")
            )

            if citizen_annual_income > max_annual_income:
                eligible = False
                eligibility_results["annual_income"] = {
                    "required": f"<= {max_annual_income}",
                    "actual": citizen_annual_income,
                    "passed": False,
                }
            else:
                eligibility_results["annual_income"] = {
                    "required": f"<= {max_annual_income}",
                    "actual": citizen_annual_income,
                    "passed": True,
                }

        # Check age if min_age and max_age are specified
        if "min_age" in eligibility_criteria or "max_age" in eligibility_criteria:
            import datetime
            from dateutil import parser

            dob_str: str = personal_info.get("dob", "")
            if dob_str:
                try:
                    # Parse DOB string (format might be different, adjust as needed)
                    dob = parser.parse(
                        dob_str, dayfirst=True
                    )  # assuming format like "15-05-1990"
                    today = datetime.datetime.now()
                    age: int = (
                        today.year
                        - dob.year
                        - ((today.month, today.day) < (dob.month, dob.day))
                    )

                    min_age: int = eligibility_criteria.get("min_age", 0)
                    max_age: int = eligibility_criteria.get("max_age", float("inf"))

                    if age < min_age or age > max_age:
                        eligible = False
                        eligibility_results["age"] = {
                            "required": f"{min_age}-{max_age} years",
                            "actual": age,
                            "passed": False,
                        }
                    else:
                        eligibility_results["age"] = {
                            "required": f"{min_age}-{max_age} years",
                            "actual": age,
                            "passed": True,
                        }
                except Exception as e:
                    # Handle date parsing errors
                    eligibility_results["age"] = {
                        "error": f"Could not determine age: {str(e)}",
                        "passed": False,
                    }
                    eligible = False

        # Check location (state, district, city) if specified
        address: str = personal_info.get("address", "")

        if "state" in eligibility_criteria:
            required_state: str = eligibility_criteria["state"]
            if required_state != "all" and required_state not in address:
                eligible = False
                eligibility_results["state"] = {
                    "required": required_state,
                    "actual": address,
                    "passed": False,
                }
            else:
                eligibility_results["state"] = {
                    "required": required_state,
                    "actual": address,
                    "passed": True,
                }

        # Check district
        if "district" in eligibility_criteria:
            required_district: str = eligibility_criteria["district"]
            if required_district != "all" and required_district not in address:
                eligible = False
                eligibility_results["district"] = {
                    "required": required_district,
                    "actual": address,
                    "passed": False,
                }
            else:
                eligibility_results["district"] = {
                    "required": required_district,
                    "actual": address,
                    "passed": True,
                }

        # Check city
        if "city" in eligibility_criteria:
            required_city: str = eligibility_criteria["city"]
            if required_city != "all" and required_city not in address:
                eligible = False
                eligibility_results["city"] = {
                    "required": required_city,
                    "actual": address,
                    "passed": False,
                }
            else:
                eligibility_results["city"] = {
                    "required": required_city,
                    "actual": address,
                    "passed": True,
                }

        # Create result object with all eligibility details
        scheme_result: Dict[str, Any] = {
            "id": scheme["id"],
            "name": scheme["name"],
            "description": scheme["description"],
            "amount": scheme["amount"],
            "govt_id": scheme["govt_id"],
            "eligibility_criteria": scheme["eligibility_criteria"],
            "eligibility_check": eligibility_results,
            "eligible": eligible,
            "already_enrolled": already_enrolled,
        }

        # Add to eligible schemes list if already enrolled or eligible
        if already_enrolled or eligible:
            eligible_schemes.append(scheme_result)

    return JSONResponse(content=eligible_schemes)
