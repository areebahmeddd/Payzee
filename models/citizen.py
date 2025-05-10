import uuid
from datetime import datetime, timezone


class Citizen:
    def __init__(
        self,
        name,
        email,
        password,
        phone=None,
        address=None,
        id_type="Aadhaar",
        id_number=None,
        location=None,
    ):
        self.account_info = {
            "id": str(uuid.uuid4()),
            "name": name,
            "email": email,
            "password": password,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "user_type": "citizen",
        }

        self.personal_info = {
            "phone": phone,
            "address": address,
            "id_type": id_type,
            "id_number": id_number,
            "location": location or {},
        }

        self.wallet_info = {
            "govt_wallet": {"balance": 0, "transactions": []},
            "personal_wallet": {"balance": 0, "transactions": []},
        }

    def to_dict(self):
        return {
            "account_info": self.account_info,
            "personal_info": self.personal_info,
            "wallet_info": self.wallet_info,
        } @ classmethod

    def from_dict(cls, data):
        citizen = cls(
            name=data["account_info"]["name"],
            email=data["account_info"]["email"],
            password=data["account_info"]["password"],
            phone=data["personal_info"].get("phone"),
            location=data["personal_info"].get("location"),
            address=data["personal_info"].get("address"),
            id_type=data["personal_info"].get("id_type", "Aadhaar"),
            id_number=data["personal_info"].get("id_number"),
        )
        citizen.account_info = data["account_info"]
        citizen.personal_info = data["personal_info"]
        citizen.wallet_info = data["wallet_info"]
        return citizen
