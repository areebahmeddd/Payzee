import uuid
from datetime import datetime, timezone


class Vendor:
    def __init__(
        self,
        name,
        password,
        email=None,
        image_url=None,
        gender=None,
        business_name=None,
        business_id=None,
        license_type=None,
        occupation=None,
        phone=None,
        address=None,
    ):
        self.account_info = {
            "id": str(uuid.uuid4()),
            "name": name,
            "email": email,
            "password": password,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "user_type": "vendor",
            "image_url": image_url,
            "gender": gender,
        }

        self.business_info = {
            "business_name": business_name,
            "business_id": business_id,
            "license_type": license_type,
            "occupation": occupation,
            "phone": phone,
            "address": address,
        }

        self.wallet_info = {
            "balance": 0,
            "transactions": [],
        }

    def to_dict(self):
        return {
            "account_info": self.account_info,
            "business_info": self.business_info,
            "wallet_info": self.wallet_info,
        }

    @classmethod
    def from_dict(cls, data):
        vendor = cls(
            name=data["account_info"]["name"],
            password=data["account_info"]["password"],
            email=data["account_info"].get("email"),
            image_url=data["account_info"].get("image_url"),
            gender=data["account_info"].get("gender"),
            business_name=data["business_info"].get("business_name"),
            business_id=data["business_info"].get("business_id"),
            license_type=data["business_info"].get("license_type"),
            occupation=data["business_info"].get("occupation"),
            phone=data["business_info"].get("phone"),
            address=data["business_info"].get("address"),
        )
        vendor.account_info = data["account_info"]
        vendor.business_info = data["business_info"]
        vendor.wallet_info = data["wallet_info"]

        return vendor
