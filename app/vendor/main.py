import io
import json
import base64
from datetime import datetime, timezone
from typing import Any, Dict, List

import qrcode
import firebase_admin
from fastapi import APIRouter, HTTPException
from firebase_admin import credentials, firestore

from .models import InventoryItem, TransactionCreate

if not firebase_admin._apps:
    cred = credentials.Certificate("firebase-config.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

router = APIRouter(tags=["vendor"])


@router.get("/profile/{vendor_id}")
async def get_vendor_profile(vendor_id: str) -> Dict[str, Any]:
    """Get vendor profile information."""
    vendor_doc = db.collection("vendors").document(vendor_id).get()
    if not vendor_doc.exists:
        raise HTTPException(status_code=404, detail="Vendor not found")

    return vendor_doc.to_dict()


@router.get("/balance/{vendor_id}")
async def get_vendor_balance(vendor_id: str) -> Dict[str, Any]:
    """Get vendor balance information."""
    vendor_doc = db.collection("vendors").document(vendor_id).get()
    if not vendor_doc.exists:
        raise HTTPException(status_code=404, detail="Vendor not found")
    vendor_data = vendor_doc.to_dict()

    return {
        "vendor_id": vendor_id,
        "balance": vendor_data.get("balance", 0),
    }


@router.get("/inventory/{vendor_id}")
async def get_vendor_inventory(vendor_id: str) -> List[Dict[str, Any]]:
    """Get all inventory items for a vendor."""
    inventory_ref = db.collection("inventory").where("vendor_id", "==", vendor_id)
    items = [doc.to_dict() for doc in inventory_ref.stream()]

    return items


@router.post("/inventory/{vendor_id}")
async def add_inventory_item(vendor_id: str, item: InventoryItem) -> Dict[str, Any]:
    """Add a new inventory item for a vendor."""
    vendor_doc = db.collection("vendors").document(vendor_id).get()
    if not vendor_doc.exists:
        raise HTTPException(status_code=404, detail="Vendor not found")

    new_item = item.model_dump()
    new_item.update(
        {
            "vendor_id": vendor_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
    )

    doc_ref = db.collection("inventory").document()
    new_item["item_id"] = doc_ref.id
    doc_ref.set(new_item)

    return {"status": "success", "item_id": doc_ref.id}


@router.get("/qr-code/{vendor_id}")
async def generate_vendor_qr_code(vendor_id: str) -> Dict[str, Any]:
    """Generate a QR code containing vendor metadata."""
    vendor_doc = db.collection("vendors").document(vendor_id).get()
    if not vendor_doc.exists:
        raise HTTPException(status_code=404, detail="Vendor not found")
    vendor_data = vendor_doc.to_dict()

    qr_data = {
        "vendor_id": vendor_id,
        "license": vendor_data.get("license", ""),
        "name": vendor_data.get("name", ""),
        "categories": vendor_data.get("categories", []),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "location": vendor_data.get("location", {}),
    }

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(json.dumps(qr_data))
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    buffered = io.BytesIO()
    img.save(buffered)
    img_str = base64.b64encode(buffered.getvalue()).decode()

    return {
        "qr_code_base64": img_str,
        "vendor_id": vendor_id,
        "timestamp": qr_data["timestamp"],
    }


@router.post("/transactions/verify/{vendor_id}")
async def verify_transaction(
    vendor_id: str, transaction: TransactionCreate
) -> Dict[str, Any]:
    """Verify and process a new transaction."""
    vendor_doc = db.collection("vendors").document(vendor_id).get()
    if not vendor_doc.exists:
        raise HTTPException(status_code=404, detail="Vendor not found")

    transaction_data = transaction.model_dump()
    transaction_data.update(
        {
            "vendor_id": vendor_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "completed",
        }
    )

    transaction_ref = db.collection("transactions").document()
    transaction_data["transaction_id"] = transaction_ref.id
    transaction_ref.set(transaction_data)

    vendor_ref = db.collection("vendors").document(vendor_id)
    vendor_ref.update({"balance": firestore.Increment(transaction.amount)})

    return {
        "status": "success",
        "transaction_id": transaction_ref.id,
        "amount": transaction.amount,
    }
