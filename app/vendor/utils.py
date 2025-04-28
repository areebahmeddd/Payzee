from fastapi import HTTPException
from firebase_admin import firestore

db = firestore.client()


def get_vendor_by_id(vendor_id: str):
    """Get vendor by ID from Firestore."""
    vendor_doc = db.collection("vendors").document(vendor_id).get()
    if not vendor_doc.exists:
        raise HTTPException(status_code=404, detail="Vendor not found")

    return vendor_doc.to_dict()
