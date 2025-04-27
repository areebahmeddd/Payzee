import firebase_admin
from firebase_admin import credentials, firestore
from typing import Dict, Any

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
    user_data["id"] = user_ref.id
    user_ref.set(user_data)
    return user_ref.id


def get_user_by_id(user_id: str) -> Dict[str, Any]:
    """Get a user by ID"""
    user_doc = users_collection.document(user_id).get()
    if user_doc.exists:
        return user_doc.to_dict()
    return None


def get_user_by_email(email: str) -> Dict[str, Any]:
    """Get a user by email"""
    users = users_collection.where("email", "==", email).limit(1).get()
    for user in users:
        return {**user.to_dict(), "id": user.id}
    return None


def update_user_profile(user_id: str, profile_data: Dict[str, Any]) -> None:
    """Update a user profile"""
    user_ref = users_collection.document(user_id)
    user_ref.update(profile_data)


# Vendor operations
def create_vendor(vendor_data: Dict[str, Any]) -> str:
    """Create a vendor in Firestore and return the vendor ID"""
    vendor_ref = vendors_collection.document()
    vendor_data["id"] = vendor_ref.id
    vendor_ref.set(vendor_data)
    return vendor_ref.id


def get_vendor_by_id(vendor_id: str) -> Dict[str, Any]:
    """Get a vendor by ID"""
    vendor_doc = vendors_collection.document(vendor_id).get()
    if vendor_doc.exists:
        return vendor_doc.to_dict()
    return None


def get_vendor_by_email(email: str) -> Dict[str, Any]:
    """Get a vendor by email"""
    vendors = vendors_collection.where("email", "==", email).limit(1).get()
    for vendor in vendors:
        return {**vendor.to_dict(), "id": vendor.id}
    return None


def update_vendor_profile(vendor_id: str, profile_data: Dict[str, Any]) -> None:
    """Update a vendor profile"""
    vendor_ref = vendors_collection.document(vendor_id)
    vendor_ref.update(profile_data)
