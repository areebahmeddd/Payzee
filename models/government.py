import uuid
from datetime import datetime, timezone


class Government:
    def __init__(
        self,
        name,
        password,
        email=None,
        department=None,
        jurisdiction=None,
        govt_id=None,
    ):
        self.account_info = {
            "id": str(uuid.uuid4()),
            "name": name,
            "email": email,
            "password": password,
            "department": department,
            "jurisdiction": jurisdiction,
            "govt_id": govt_id,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "user_type": "government",
        }

        self.wallet_info = {
            "balance": 0,
            "schemes": [],  # References to scheme IDs managed by this government account
            "transactions": [],
        }

    def to_dict(self):
        return {
            "account_info": self.account_info,
            "wallet_info": self.wallet_info,
        }

    @classmethod
    def from_dict(cls, data):
        govt = cls(
            name=data["account_info"]["name"],
            password=data["account_info"]["password"],
            email=data["account_info"].get("email"),
            department=data["account_info"].get("department"),
            jurisdiction=data["account_info"].get("jurisdiction"),
            govt_id=data["account_info"].get("govt_id"),
        )
        govt.account_info = data["account_info"]
        govt.wallet_info = data["wallet_info"]

        return govt
