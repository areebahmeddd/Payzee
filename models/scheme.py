import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional


class Scheme:
    def __init__(
        self,
        name: str,
        description: str,
        govt_id: str,
        amount: float,
        eligibility_criteria: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
        status: str = "active",
    ):
        self.id: str = str(uuid.uuid4())
        self.name: str = name
        self.description: str = description
        self.govt_id: str = (
            govt_id  # Reference to the government that created this scheme
        )
        self.amount: float = amount
        self.status: str = status  # active, inactive, completed
        self.eligibility_criteria: Dict[str, Any] = eligibility_criteria or {}
        self.tags: List[str] = tags or []
        self.beneficiaries: List[str] = []  # List of citizen IDs who are beneficiaries
        self.created_at: datetime = datetime.now(timezone.utc)
        self.updated_at: datetime = datetime.now(timezone.utc)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "govt_id": self.govt_id,
            "amount": self.amount,
            "status": self.status,
            "eligibility_criteria": self.eligibility_criteria,
            "tags": self.tags,
            "beneficiaries": self.beneficiaries,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Scheme":
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
