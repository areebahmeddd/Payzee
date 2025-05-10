import uuid
from datetime import datetime, timezone


class Scheme:
    def __init__(
        self,
        name,
        description,
        govt_id,
        amount,
        eligibility_criteria=None,
        tags=None,
        status="active",
    ):
        self.id = str(uuid.uuid4())
        self.name = name
        self.description = description
        self.govt_id = govt_id  # Reference to the government that created this scheme
        self.amount = amount
        self.eligibility_criteria = eligibility_criteria or {}
        self.tags = tags or []
        self.beneficiaries = []  # List of citizen IDs who are beneficiaries
        self.created_at = datetime.now(timezone.utc)
        self.updated_at = datetime.now(timezone.utc)
        self.status = status  # active, inactive, completed

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "govt_id": self.govt_id,
            "amount": self.amount,
            "eligibility_criteria": self.eligibility_criteria,
            "tags": self.tags,
            "beneficiaries": self.beneficiaries,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "status": self.status,
        }

    @classmethod
    def from_dict(cls, data):
        scheme = cls(
            name=data["name"],
            description=data["description"],
            govt_id=data["govt_id"],
            amount=data["amount"],
            eligibility_criteria=data.get("eligibility_criteria"),
            tags=data.get("tags"),
            status=data.get("status", "active"),
        )
        scheme.id = data["id"]
        scheme.beneficiaries = data["beneficiaries"]
        scheme.created_at = data["created_at"]
        scheme.updated_at = data["updated_at"]
        return scheme
