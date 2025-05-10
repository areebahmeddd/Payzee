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
    delete_citizen,
    get_vendor,
    update_vendor,
    get_scheme,
    save_transaction,
    query_transactions_by_field,
    array_union,
    get_all_schemes,
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


# Delete citizen profile
@router.delete("/{citizen_id}", response_model=MessageResponse)
async def delete_citizen_profile(citizen_id: str):
    citizen = get_citizen(citizen_id)
    if not citizen:
        raise HTTPException(status_code=404, detail="Citizen not found")

    # Delete the citizen
    delete_citizen(citizen_id)
    return JSONResponse(content={"message": "Citizen profile deleted successfully"})


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
            required_gender = eligibility_criteria["gender"]
            citizen_gender = personal_info.get("gender", "")

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
            required_caste = eligibility_criteria["caste"]
            citizen_caste = personal_info.get("caste", "")

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
            max_annual_income = eligibility_criteria["annual_income"]
            citizen_annual_income = personal_info.get("annual_income", float("inf"))

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

            dob_str = personal_info.get("dob", "")
            if dob_str:
                try:
                    # Parse DOB string (format might be different, adjust as needed)
                    dob = parser.parse(
                        dob_str, dayfirst=True
                    )  # assuming format like "15-05-1990"
                    today = datetime.datetime.now()
                    age = (
                        today.year
                        - dob.year
                        - ((today.month, today.day) < (dob.month, dob.day))
                    )

                    min_age = eligibility_criteria.get("min_age", 0)
                    max_age = eligibility_criteria.get("max_age", float("inf"))

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
        address = personal_info.get("address", "")

        if "state" in eligibility_criteria:
            required_state = eligibility_criteria["state"]
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
            required_district = eligibility_criteria["district"]
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
            required_city = eligibility_criteria["city"]
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
        scheme_result = {
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


# Get a specific scheme by ID
@router.get("/{citizen_id}/scheme/{scheme_id}")
async def get_scheme_by_id(citizen_id: str, scheme_id: str):
    # Check if citizen exists
    citizen = get_citizen(citizen_id)
    if not citizen:
        raise HTTPException(status_code=404, detail="Citizen not found")

    # Check if scheme exists
    scheme = get_scheme(scheme_id)
    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")

    # Check if citizen is enrolled in this scheme
    is_enrolled = "beneficiaries" in scheme and citizen_id in scheme["beneficiaries"]

    # Check enrollment status in citizen's scheme_info
    in_citizen_scheme_info = (
        "scheme_info" in citizen and scheme_id in citizen["scheme_info"]
    )

    # Add enrollment status to the response
    scheme_response = dict(scheme)  # Create a copy to avoid modifying the original
    scheme_response["is_enrolled"] = is_enrolled or in_citizen_scheme_info

    # Check eligibility
    personal_info = citizen.get("personal_info", {})
    eligibility_criteria = scheme.get("eligibility_criteria", {})

    # Perform eligibility checks
    eligibility_check = {}
    is_eligible = True

    # Check occupation
    if "occupation" in eligibility_criteria:
        required_occupation = eligibility_criteria["occupation"]
        citizen_occupation = personal_info.get("occupation", "")
        occupation_match = (
            required_occupation == "any" or required_occupation == citizen_occupation
        )
        eligibility_check["occupation"] = {
            "required": required_occupation,
            "actual": citizen_occupation,
            "passed": occupation_match,
        }
        if not occupation_match:
            is_eligible = False

    # Check gender
    if "gender" in eligibility_criteria:
        required_gender = eligibility_criteria["gender"]
        citizen_gender = personal_info.get("gender", "")
        gender_match = required_gender == "any" or required_gender == citizen_gender
        eligibility_check["gender"] = {
            "required": required_gender,
            "actual": citizen_gender,
            "passed": gender_match,
        }
        if not gender_match:
            is_eligible = False

    # Check caste
    if "caste" in eligibility_criteria:
        required_caste = eligibility_criteria["caste"]
        citizen_caste = personal_info.get("caste", "")
        caste_match = required_caste == "all" or required_caste == citizen_caste
        eligibility_check["caste"] = {
            "required": required_caste,
            "actual": citizen_caste,
            "passed": caste_match,
        }
        if not caste_match:
            is_eligible = False

    # Check annual income
    if "annual_income" in eligibility_criteria:
        max_annual_income = eligibility_criteria["annual_income"]
        citizen_annual_income = personal_info.get("annual_income", float("inf"))
        income_match = citizen_annual_income <= max_annual_income
        eligibility_check["annual_income"] = {
            "required": f"<= {max_annual_income}",
            "actual": citizen_annual_income,
            "passed": income_match,
        }
        if not income_match:
            is_eligible = False

    # Check age if min_age and max_age are specified
    if "min_age" in eligibility_criteria or "max_age" in eligibility_criteria:
        import datetime
        from dateutil import parser

        dob_str = personal_info.get("dob", "")
        if dob_str:
            try:
                dob = parser.parse(dob_str, dayfirst=True)
                today = datetime.datetime.now()
                age = (
                    today.year
                    - dob.year
                    - ((today.month, today.day) < (dob.month, dob.day))
                )

                min_age = eligibility_criteria.get("min_age", 0)
                max_age = eligibility_criteria.get("max_age", float("inf"))

                age_match = min_age <= age <= max_age
                eligibility_check["age"] = {
                    "required": f"{min_age}-{max_age} years",
                    "actual": age,
                    "passed": age_match,
                }
                if not age_match:
                    is_eligible = False
            except Exception as e:
                eligibility_check["age"] = {
                    "error": f"Could not determine age: {str(e)}",
                    "passed": False,
                }
                is_eligible = False

    # Check location (state, district, city)
    address = personal_info.get("address", "")

    # Check state
    if "state" in eligibility_criteria:
        required_state = eligibility_criteria["state"]
        state_match = required_state == "all" or required_state in address
        eligibility_check["state"] = {
            "required": required_state,
            "actual": address,
            "passed": state_match,
        }
        if not state_match:
            is_eligible = False

    # Check district
    if "district" in eligibility_criteria:
        required_district = eligibility_criteria["district"]
        district_match = required_district == "all" or required_district in address
        eligibility_check["district"] = {
            "required": required_district,
            "actual": address,
            "passed": district_match,
        }
        if not district_match:
            is_eligible = False

    # Check city
    if "city" in eligibility_criteria:
        required_city = eligibility_criteria["city"]
        city_match = required_city == "all" or required_city in address
        eligibility_check["city"] = {
            "required": required_city,
            "actual": address,
            "passed": city_match,
        }
        if not city_match:
            is_eligible = False

    # Add eligibility info to the response
    scheme_response["eligibility_check"] = eligibility_check
    scheme_response["is_eligible"] = is_eligible

    return JSONResponse(content=scheme_response)


# Enroll in a scheme
@router.post("/{citizen_id}/enroll-scheme/{scheme_id}", response_model=MessageResponse)
async def enroll_scheme(citizen_id: str, scheme_id: str):
    citizen = get_citizen(citizen_id)
    if not citizen:
        raise HTTPException(status_code=404, detail="Citizen not found")

    scheme = get_scheme(scheme_id)
    if not scheme:
        raise HTTPException(status_code=404, detail="Scheme not found")

    if "beneficiaries" in scheme and citizen_id in scheme["beneficiaries"]:
        raise HTTPException(status_code=409, detail="Already enrolled in this scheme")

    # Check eligibility before enrolling
    eligibility_criteria = scheme.get("eligibility_criteria", {})
    personal_info = citizen.get("personal_info", {})

    # Check if the citizen is eligible based on criteria
    eligible = True
    failure_reasons = []

    # Check occupation
    if "occupation" in eligibility_criteria:
        required_occupation = eligibility_criteria["occupation"]
        citizen_occupation = personal_info.get("occupation", "")
        if required_occupation != "any" and required_occupation != citizen_occupation:
            eligible = False
            failure_reasons.append(
                f"Occupation: required {required_occupation}, but you have {citizen_occupation}"
            )

    # Check gender
    if "gender" in eligibility_criteria:
        required_gender = eligibility_criteria["gender"]
        citizen_gender = personal_info.get("gender", "")
        if required_gender != "any" and required_gender != citizen_gender:
            eligible = False
            failure_reasons.append(
                f"Gender: required {required_gender}, but you have {citizen_gender}"
            )

    # Check caste
    if "caste" in eligibility_criteria:
        required_caste = eligibility_criteria["caste"]
        citizen_caste = personal_info.get("caste", "")
        if required_caste != "all" and required_caste != citizen_caste:
            eligible = False
            failure_reasons.append(
                f"Caste: required {required_caste}, but you have {citizen_caste}"
            )

    # Check annual income
    if "annual_income" in eligibility_criteria:
        max_annual_income = eligibility_criteria["annual_income"]
        citizen_annual_income = personal_info.get("annual_income", float("inf"))
        if citizen_annual_income > max_annual_income:
            eligible = False
            failure_reasons.append(
                f"Annual income: required <= {max_annual_income}, but you have {citizen_annual_income}"
            )

    # Check age if min_age and max_age are specified
    if "min_age" in eligibility_criteria or "max_age" in eligibility_criteria:
        import datetime
        from dateutil import parser

        dob_str = personal_info.get("dob", "")
        if dob_str:
            try:
                # Parse DOB string (format might be different, adjust as needed)
                dob = parser.parse(
                    dob_str, dayfirst=True
                )  # assuming format like "15-05-1990"
                today = datetime.datetime.now()
                age = (
                    today.year
                    - dob.year
                    - ((today.month, today.day) < (dob.month, dob.day))
                )

                min_age = eligibility_criteria.get("min_age", 0)
                max_age = eligibility_criteria.get("max_age", float("inf"))

                if age < min_age or age > max_age:
                    eligible = False
                    failure_reasons.append(
                        f"Age: required {min_age}-{max_age} years, but you are {age} years old"
                    )
            except Exception as e:
                eligible = False
                failure_reasons.append(f"Could not determine age: {str(e)}")

    # Check location (state)
    address = personal_info.get("address", "")
    if "state" in eligibility_criteria:
        required_state = eligibility_criteria["state"]
        if required_state != "all" and required_state not in address:
            eligible = False
            failure_reasons.append(
                f"State: required {required_state}, but your address is {address}"
            )

    # Check district
    if "district" in eligibility_criteria:
        required_district = eligibility_criteria["district"]
        if required_district != "all" and required_district not in address:
            eligible = False
            failure_reasons.append(
                f"District: required {required_district}, but your address is {address}"
            )

    # Check city
    if "city" in eligibility_criteria:
        required_city = eligibility_criteria["city"]
        if required_city != "all" and required_city not in address:
            eligible = False
            failure_reasons.append(
                f"City: required {required_city}, but your address is {address}"
            )

    # Only allow enrollment if eligible
    if not eligible:
        raise HTTPException(
            status_code=403,
            detail={
                "message": "You are not eligible for this scheme",
                "reasons": failure_reasons,
            },
        )

    # Update scheme to add citizen as a beneficiary
    array_union(SCHEMES_PREFIX, scheme_id, "beneficiaries", [citizen_id])

    # Update citizen's scheme_info to include this scheme
    citizen_data = get_citizen(citizen_id)
    if "scheme_info" not in citizen_data:
        citizen_data["scheme_info"] = []

    if scheme_id not in citizen_data["scheme_info"]:
        citizen_data["scheme_info"].append(scheme_id)
        update_citizen(citizen_id, {"scheme_info": citizen_data["scheme_info"]})

    return JSONResponse(content={"message": "Successfully enrolled in scheme"})


# Delete citizen profile
@router.delete("/{citizen_id}", response_model=MessageResponse)
async def delete_profile(citizen_id: str):
    # Check if citizen exists
    citizen = get_citizen(citizen_id)
    if not citizen:
        raise HTTPException(status_code=404, detail="Citizen not found")

    # Delete the citizen
    delete_citizen(citizen_id)

    return JSONResponse(content={"message": "Citizen profile deleted successfully"})
