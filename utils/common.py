from fastapi import HTTPException
from db import citizens_collection, vendors_collection, governments_collection


# TODO: Migrate from Firestore to Redis
def get_user_by_id(user_id, user_type=None):
    """Get user by ID from Firestore"""
    if user_type == "citizen" or user_type is None:
        doc_ref = citizens_collection.document(user_id)
        doc = doc_ref.get()
        if doc.exists:
            return doc_ref, doc.to_dict()

    if user_type == "vendor" or user_type is None:
        doc_ref = vendors_collection.document(user_id)
        doc = doc_ref.get()
        if doc.exists:
            return doc_ref, doc.to_dict()

    if user_type == "government" or user_type is None:
        doc_ref = governments_collection.document(user_id)
        doc = doc_ref.get()
        if doc.exists:
            return doc_ref, doc.to_dict()

    raise HTTPException(status_code=404, detail="User not found")


def remove_sensitive_info(user_data):
    """Remove sensitive information from user data"""
    clean_data = {**user_data}

    if "account_info" in clean_data and "password" in clean_data["account_info"]:
        clean_data["account_info"] = {**clean_data["account_info"]}
        clean_data["account_info"].pop("password")

    return clean_data
