import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
from typing import Dict, Any, List

if not firebase_admin._apps:
    cred = credentials.Certificate("firebase-config.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

users_collection = db.collection("users")
vendors_collection = db.collection("vendors")


# User operations
def create_user(user_data: Dict[str, Any]) -> str:
    """Create a user in Firestore and return the user ID"""
    user_ref = users_collection.document()

    # Create account_info structure
    account_info = {
        "email": user_data.pop("email"),
        "username": user_data.pop("username"),
        "full_name": user_data.pop("full_name", None),
        "phone_number": user_data.pop("phone_number", None),
        "address": user_data.pop("address", None),
        "aadhaar_number": user_data.pop("aadhaar_number", None),
        "date_created": datetime.now(),
    }

    # Initialize wallet fields
    wallet_data = {
        "govt_wallet": user_data.pop("govt_wallet", []),
        "personal_wallet": user_data.pop("personal_wallet", 0),
        "allocated_amt": user_data.pop("allocated_amt", 0),
        "remaining_amt": user_data.pop("remaining_amt", 0),
        "past_transactions": user_data.pop("past_transactions", []),
    }

    # Combine data for document
    data_to_store = {
        "id": user_ref.id,
        "account_info": account_info,
        **wallet_data,
        **user_data,  # Any remaining fields
    }

    user_ref.set(data_to_store)
    return user_ref.id


def get_user_by_id(user_id: str) -> Dict[str, Any]:
    """Get a user by ID"""
    user_doc = users_collection.document(user_id).get()
    if user_doc.exists:
        return user_doc.to_dict()
    return None


def get_user_by_email(email: str) -> Dict[str, Any]:
    """Get a user by email"""
    users = users_collection.where("account_info.email", "==", email).limit(1).get()
    for user in users:
        return {**user.to_dict(), "id": user.id}
    return None


def update_user_profile(user_id: str, profile_data: Dict[str, Any]) -> None:
    """Update a user profile"""
    user_ref = users_collection.document(user_id)

    # Check if we're updating account_info fields
    account_info_fields = [
        "email",
        "username",
        "full_name",
        "phone_number",
        "address",
        "aadhaar_number",
    ]

    account_info_updates = {}
    general_updates = {}

    for key, value in profile_data.items():
        if key in account_info_fields:
            account_info_updates[f"account_info.{key}"] = value
        else:
            general_updates[key] = value

    # Update the document
    if account_info_updates:
        user_ref.update(account_info_updates)
    if general_updates:
        user_ref.update(general_updates)


# Wallet operations
def get_user_wallet(user_id: str) -> Dict[str, Any]:
    """Get a user's wallet information"""
    user = get_user_by_id(user_id)
    if not user:
        return None

    return {
        "govt_wallet": user.get("govt_wallet", []),
        "personal_wallet": user.get("personal_wallet", 0),
        "allocated_amt": user.get("allocated_amt", 0),
        "remaining_amt": user.get("remaining_amt", 0),
    }


def update_user_wallet(user_id: str, wallet_item: Dict[str, Any]) -> Dict[str, Any]:
    """Update a specific wallet item in the user's government wallet"""
    user = get_user_by_id(user_id)
    if not user:
        return None

    govt_wallet = user.get("govt_wallet", [])

    # Check if category already exists
    updated = False
    for item in govt_wallet:
        if item["category"] == wallet_item["category"]:
            item["amount"] = wallet_item["amount"]
            updated = True
            break

    # If category doesn't exist, add it
    if not updated:
        govt_wallet.append(wallet_item)

    update_user_profile(user_id, {"govt_wallet": govt_wallet})
    return govt_wallet


def get_user_transactions(user_id: str) -> List[Dict[str, Any]]:
    """Get all transactions for a user"""
    user = get_user_by_id(user_id)
    if not user:
        return None

    return user.get("past_transactions", [])


def add_user_transaction(user_id: str, transaction: Dict[str, Any]) -> Dict[str, Any]:
    """Add a transaction to the user's history and update their remaining amount"""
    user = get_user_by_id(user_id)
    if not user:
        return None

    remaining_amt = user.get("remaining_amt", 0)
    if remaining_amt < transaction["amount"]:
        return {"error": "Insufficient funds", "remaining_amt": remaining_amt}

    # Add transaction to history
    past_transactions = user.get("past_transactions", [])
    transaction["timestamp"] = datetime.now().isoformat()
    past_transactions.append(transaction)

    # Update user's remaining amount
    new_remaining_amt = remaining_amt - transaction["amount"]

    # Update in Firestore
    user_ref = users_collection.document(user_id)
    user_ref.update(
        {
            "past_transactions": past_transactions,
            "remaining_amt": firestore.Increment(-transaction["amount"]),
        }
    )

    return {
        "status": "success",
        "transaction": transaction,
        "remaining_amt": new_remaining_amt,
    }


# Vendor operations
def create_vendor(vendor_data: Dict[str, Any]) -> str:
    """Create a vendor in Firestore and return the vendor ID"""
    vendor_ref = vendors_collection.document()

    # Create account_info structure
    account_info = {
        "email": vendor_data.pop("email"),
        "username": vendor_data.pop("username"),
        "full_name": vendor_data.pop("full_name", None),
        "phone_number": vendor_data.pop("phone_number", None),
        "address": vendor_data.pop("address", None),
        "aadhaar_number": vendor_data.pop("aadhaar_number", None),
        "business_name": vendor_data.pop("business_name", ""),
        "business_description": vendor_data.pop("business_description", None),
        "category": vendor_data.pop("category", None),
        "license_type": vendor_data.pop("license_type", "regular"),
        "date_created": datetime.now(),
    }

    # Create inventory_info structure
    inventory_info = {
        "items": vendor_data.pop("inventory", []),
        "last_updated": datetime.now(),
    }

    # Combine data for document
    data_to_store = {
        "id": vendor_ref.id,
        "account_info": account_info,
        "inventory_info": inventory_info,
        "balance": vendor_data.pop("balance", 0),
        **vendor_data,  # Any remaining fields
    }

    vendor_ref.set(data_to_store)
    return vendor_ref.id


def get_vendor_by_id(vendor_id: str) -> Dict[str, Any]:
    """Get a vendor by ID"""
    vendor_doc = vendors_collection.document(vendor_id).get()
    if vendor_doc.exists:
        return vendor_doc.to_dict()
    return None


def get_vendor_by_email(email: str) -> Dict[str, Any]:
    """Get a vendor by email"""
    vendors = vendors_collection.where("account_info.email", "==", email).limit(1).get()
    for vendor in vendors:
        return {**vendor.to_dict(), "id": vendor.id}
    return None


def update_vendor_profile(vendor_id: str, profile_data: Dict[str, Any]) -> None:
    """Update a vendor profile"""
    vendor_ref = vendors_collection.document(vendor_id)

    # Check if we're updating account_info fields
    account_info_fields = [
        "email",
        "username",
        "full_name",
        "phone_number",
        "address",
        "aadhaar_number",
        "business_name",
        "business_description",
        "category",
    ]

    account_info_updates = {}
    general_updates = {}

    for key, value in profile_data.items():
        if key in account_info_fields:
            account_info_updates[f"account_info.{key}"] = value
        else:
            general_updates[key] = value

    # Update the document
    if account_info_updates:
        vendor_ref.update(account_info_updates)
    if general_updates:
        vendor_ref.update(general_updates)
