import uuid
from datetime import datetime, timezone


class Citizen:
    def __init__(
        self,
        name,
        password,
        email=None,
        phone=None,
        id_type="Aadhaar",
        id_number=None,
        address=None,
        dob=None,
        gender=None,
        occupation=None,
        caste=None,
        annual_income=None,
        image_url=None,
    ):
        self.account_info = {
            "id": str(uuid.uuid4()),
            "name": name,
            "email": email,
            "password": password,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "user_type": "citizen",
            "image_url": image_url,
        }

        self.personal_info = {
            "phone": phone,
            "id_type": id_type,
            "id_number": id_number,
            "address": address,
            "dob": dob,
            "gender": gender,
            "occupation": occupation,
            "caste": caste,
            "annual_income": annual_income,
        }

        self.wallet_info = {
            "govt_wallet": {"balance": 0, "transactions": []},
            "personal_wallet": {"balance": 0, "transactions": []},
        }

        self.scheme_info = []

    def to_dict(self):
        return {
            "account_info": self.account_info,
            "personal_info": self.personal_info,
            "wallet_info": self.wallet_info,
            "scheme_info": self.scheme_info,
        }

    @classmethod
    def from_dict(cls, data):
        citizen = cls(
            name=data["account_info"]["name"],
            password=data["account_info"]["password"],
            email=data["account_info"].get("email"),
            phone=data["personal_info"].get("phone"),
            id_type=data["personal_info"].get("id_type", "Aadhaar"),
            id_number=data["personal_info"].get("id_number"),
            address=data["personal_info"].get("address"),
            dob=data["personal_info"].get("dob"),
            gender=data["personal_info"].get("gender"),
            occupation=data["personal_info"].get("occupation"),
            caste=data["personal_info"].get("caste"),
            annual_income=data["personal_info"].get("annual_income"),
            image_url=data["account_info"].get("image_url"),
        )
        citizen.account_info = data["account_info"]
        citizen.personal_info = data["personal_info"]
        citizen.wallet_info = data["wallet_info"]
        citizen.scheme_info = data.get("scheme_info", [])

        return citizen
