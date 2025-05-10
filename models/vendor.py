import uuid
from datetime import datetime, timezone


class Vendor:
    def __init__(
        self,
        name,
        email,
        password,
        business_name=None,
        phone=None,
        address=None,
        business_id=None,
        license_type=None,
        location=None,
    ):
        self.account_info = {
            "id": str(uuid.uuid4()),
            "name": name,
            "email": email,
            "password": password,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "user_type": "vendor",
        }

        self.business_info = {
            "business_name": business_name,
            "phone": phone,
            "address": address,
            "business_id": business_id,
            "license_type": license_type,
            "location": location or {},
        }

        self.wallet_info = {"balance": 0, "transactions": []}

    def to_dict(self):
        return {
            "account_info": self.account_info,
            "business_info": self.business_info,
            "wallet_info": self.wallet_info,
        } @ classmethod

    def from_dict(cls, data):
        vendor = cls(
            name=data["account_info"]["name"],
            email=data["account_info"]["email"],
            password=data["account_info"]["password"],
            business_name=data["business_info"].get("business_name"),
            phone=data["business_info"].get("phone"),
            location=data["business_info"].get("location"),
            address=data["business_info"].get("address"),
            business_id=data["business_info"].get("business_id"),
            license_type=data["business_info"].get("license_type"),
        )
        vendor.account_info = data["account_info"]
        vendor.business_info = data["business_info"]
        vendor.wallet_info = data["wallet_info"]
        return vendor
