import io
import json
import base64
from datetime import datetime, timezone
from typing import Any, Dict, List

import qrcode
import firebase_admin
from fastapi import APIRouter
from firebase_admin import credentials, firestore

from .models import InventoryItem, TransactionCreate
from .utils import get_vendor_by_id

if not firebase_admin._apps:
    cred = credentials.Certificate("firebase-config.json")
    firebase_admin.initialize_app(cred)

db = firestore.client()

router = APIRouter(tags=["vendor"])


@router.get("/profile/{vendor_id}")
async def get_vendor_profile(vendor_id: str) -> Dict[str, Any]:
    """Get vendor profile information."""
    vendor_data = get_vendor_by_id(vendor_id)
    return vendor_data.get("account_info", {})


@router.get("/balance/{vendor_id}")
async def get_vendor_balance(vendor_id: str) -> Dict[str, Any]:
    """Get vendor balance information."""
    vendor_data = get_vendor_by_id(vendor_id)

    return {
        "vendor_id": vendor_id,
        "balance": vendor_data.get("balance", 0),
    }


@router.get("/inventory/{vendor_id}")
async def get_vendor_inventory(vendor_id: str) -> List[Dict[str, Any]]:
    """Get all inventory items for a vendor."""
    vendor_data = get_vendor_by_id(vendor_id)

    inventory_info = vendor_data.get("inventory_info", {})
    return inventory_info.get("items", [])


@router.post("/inventory/{vendor_id}")
async def add_inventory_item(vendor_id: str, item: InventoryItem) -> Dict[str, Any]:
    """Add a new inventory item for a vendor."""
    vendor_data = get_vendor_by_id(vendor_id)

    inventory_info = vendor_data.get("inventory_info", {})
    items = inventory_info.get("items", [])

    # Generate an item_id for the new inventory item
    item_id = f"item_{len(items) + 1}_{datetime.now(timezone.utc).timestamp():.0f}"

    new_item = item.model_dump()
    new_item.update(
        {
            "item_id": item_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
    )

    # Add to inventory items
    items.append(new_item)

    # Update vendor document with the new inventory
    db.collection("vendors").document(vendor_id).update(
        {
            "inventory_info.items": items,
            "inventory_info.last_updated": datetime.now(timezone.utc).isoformat(),
        }
    )

    return {"status": "success", "item_id": item_id}


@router.get("/qr-code/{vendor_id}")
async def generate_vendor_qr_code(vendor_id: str) -> Dict[str, Any]:
    """Generate a QR code containing vendor metadata."""
    vendor_data = get_vendor_by_id(vendor_id)

    account_info = vendor_data.get("account_info", {})

    qr_data = {
        "vendor_id": vendor_id,
        "business_name": account_info.get("business_name", ""),
        "category": account_info.get("category", ""),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "location": {
            "latitude": vendor_data.get("location", {}).get("latitude", 0.0),
            "longitude": vendor_data.get("location", {}).get("longitude", 0.0),
        },
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
    # Just verify vendor exists
    get_vendor_by_id(vendor_id)

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
