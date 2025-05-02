import uuid
from datetime import datetime, timezone


class Citizen:
    def __init__(self, name, email, password, phone=None, address=None, id_proof=None):
        self.account_info = {
            "id": str(uuid.uuid4()),
            "name": name,
            "email": email,
            "password": password,
            "phone": phone,
            "address": address,
            "id_proof": id_proof,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "user_type": "citizen",
        }

        self.wallet_info = {
            "govt_wallet": {"balance": 0, "transactions": []},
            "personal_wallet": {"balance": 0, "transactions": []},
        }

    def to_dict(self):
        return {"account_info": self.account_info, "wallet_info": self.wallet_info}

    @classmethod
    def from_dict(cls, data):
        citizen = cls(
            name=data["account_info"]["name"],
            email=data["account_info"]["email"],
            password=data["account_info"]["password"],
        )
        citizen.account_info = data["account_info"]
        citizen.wallet_info = data["wallet_info"]
        return citizen
